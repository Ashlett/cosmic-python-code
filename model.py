from dataclasses import dataclass


class AllocationError(Exception):
    pass


@dataclass
class OrderLine:
    stock_keeping_unit: str
    quantity: int
    batch_reference: str = ""


class Batch:
    def __init__(self, reference: str, stock_keeping_unit: str, available_quantity: int):
        self.reference = reference
        self.stock_keeping_unit = stock_keeping_unit
        self.available_quantity = available_quantity

    def allocate(self, order_line:OrderLine):
        if order_line.batch_reference:
            if order_line.batch_reference == self.reference:
                return
            else:
                raise AllocationError("order line already allocated to a different batch")

        if order_line.stock_keeping_unit != self.stock_keeping_unit:
            raise AllocationError("different product between batch and order line")

        if order_line.quantity > self.available_quantity:
            raise AllocationError("quantity exceeds available quantity")

        self.available_quantity -= order_line.quantity
        order_line.batch_reference = self.reference
