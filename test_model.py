from datetime import date, timedelta
import pytest

from model import AllocationError, Batch, OrderLine

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


def test_prefers_warehouse_batches_to_shipments():
    pytest.fail("todo")


def test_prefers_earlier_batches():
    pytest.fail("todo")
