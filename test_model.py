from datetime import date, timedelta
import pytest

from model import AllocationError, Batch, OrderLine

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch = Batch(reference="test", stock_keeping_unit="SMALL-TABLE", available_quantity=20)
    order_line = OrderLine(stock_keeping_unit="SMALL-TABLE", quantity=2)

    batch.allocate(order_line)

    assert batch.available_quantity == 18


def test_can_allocate_if_available_greater_than_required():
    batch = Batch(reference="test", stock_keeping_unit="BLUE-CUSHION", available_quantity=2)
    order_line = OrderLine(stock_keeping_unit="BLUE-CUSHION", quantity=1)

    batch.allocate(order_line)

    assert batch.available_quantity == 1


def test_cannot_allocate_if_available_smaller_than_required():
    batch = Batch(reference="test", stock_keeping_unit="BLUE-CUSHION", available_quantity=1)
    order_line = OrderLine(stock_keeping_unit="BLUE-CUSHION", quantity=2)

    with pytest.raises(AllocationError):
        batch.allocate(order_line)


def test_can_allocate_if_available_equal_to_required():
    batch = Batch(reference="test", stock_keeping_unit="BLUE-CUSHION", available_quantity=1)
    order_line = OrderLine(stock_keeping_unit="BLUE-CUSHION", quantity=1)

    batch.allocate(order_line)

    assert batch.available_quantity == 0


def test_allocation_idempotent():
    """Allocating the same line twice decreases quantity only once."""
    batch = Batch(reference="test", stock_keeping_unit="BLUE-VASE", available_quantity=10)
    order_line = OrderLine(stock_keeping_unit="BLUE-VASE", quantity=2)

    batch.allocate(order_line)

    assert batch.available_quantity == 8

    batch.allocate(order_line)

    assert batch.available_quantity == 8


def test_prefers_warehouse_batches_to_shipments():
    pytest.fail("todo")


def test_prefers_earlier_batches():
    pytest.fail("todo")
