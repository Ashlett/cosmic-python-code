from datetime import date, timedelta
import pytest

from model import allocate, AllocationError, Batch, OrderLine

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def make_batch_and_line(stock_keeping_unit, batch_quantity, line_quantity):
    batch = Batch(reference="test", stock_keeping_unit=stock_keeping_unit, available_quantity=batch_quantity)
    order_line = OrderLine(stock_keeping_unit=stock_keeping_unit, quantity=line_quantity)
    return batch, order_line


def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch, order_line = make_batch_and_line("SMALL-TABLE", batch_quantity=20, line_quantity=2)
    batch.allocate(order_line)
    assert batch.available_quantity == 18


def test_can_allocate_if_available_greater_than_required():
    batch, order_line = make_batch_and_line("BLUE-CUSHION", batch_quantity=2, line_quantity=1)
    batch.allocate(order_line)
    assert batch.available_quantity == 1


def test_cannot_allocate_if_available_smaller_than_required():
    batch, order_line = make_batch_and_line("BLUE-CUSHION", batch_quantity=1, line_quantity=2)
    with pytest.raises(AllocationError):
        batch.allocate(order_line)


def test_can_allocate_if_available_equal_to_required():
    batch, order_line = make_batch_and_line("BLUE-CUSHION", batch_quantity=1, line_quantity=1)
    batch.allocate(order_line)
    assert batch.available_quantity == 0


def test_cannot_allocate_if_products_do_not_match():
    batch = Batch(reference="test", stock_keeping_unit="UNCOMFORTABLE-CHAIR", available_quantity=100)
    different_sku_line = OrderLine(stock_keeping_unit="EXPENSIVE-TOASTER", quantity=10)
    with pytest.raises(AllocationError):
        batch.allocate(different_sku_line)


def test_allocation_idempotent():
    """Allocating the same line twice decreases quantity only once."""
    batch, order_line = make_batch_and_line("BLUE-VASE", batch_quantity=10, line_quantity=2)
    batch.allocate(order_line)
    assert batch.available_quantity == 8
    batch.allocate(order_line)
    assert batch.available_quantity == 8


def test_can_only_deallocate_allocated_lines():
    batch, unallocated_line = make_batch_and_line("DECORATIVE-TRINKET", 20, 2)
    batch.deallocate(unallocated_line)
    assert batch.available_quantity == 20


def test_prefers_warehouse_batches_to_shipments():
    warehouse_batch = Batch(reference="warehouse", stock_keeping_unit="RETRO-CLOCK", available_quantity=100, eta=None)
    ships_tomorrow = Batch(reference="shipment", stock_keeping_unit="RETRO-CLOCK", available_quantity=100, eta=tomorrow)
    order_line = OrderLine(stock_keeping_unit="RETRO-CLOCK", quantity=10)

    allocate(order_line, [warehouse_batch, ships_tomorrow])

    assert warehouse_batch.available_quantity == 90
    assert ships_tomorrow.available_quantity == 100
    assert order_line.batch_reference == "warehouse"


def test_prefers_earlier_batches():
    earliest = Batch(reference="batch1", stock_keeping_unit="MINIMALIST-SPOON", available_quantity=50, eta=today)
    medium = Batch(reference="batch2", stock_keeping_unit="MINIMALIST-SPOON", available_quantity=50, eta=tomorrow)
    latest = Batch(reference="batch3", stock_keeping_unit="MINIMALIST-SPOON", available_quantity=50, eta=later)
    order_line = OrderLine(stock_keeping_unit="MINIMALIST-SPOON", quantity=10)

    allocate(order_line, [medium, latest, earliest])

    assert earliest.available_quantity == 40
    assert medium.available_quantity == 50
    assert latest.available_quantity == 50
    assert order_line.batch_reference == "batch1"
