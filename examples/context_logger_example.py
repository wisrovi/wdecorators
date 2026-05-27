"""Example: context_logger decorator - contextual logging."""

import logging
from wdecorators import context_logger

logging.basicConfig(level=logging.INFO)


@context_logger()
def process_order(order_id):
    return f"Order {order_id} processed"


print(process_order(123))
