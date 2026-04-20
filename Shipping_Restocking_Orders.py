class BaseOrder:
    def __init__(self, number, items, order_type):
        self.number = number
        self.type = order_type

        if not isinstance(items, list):
            raise TypeError("The 'items' argument must be a list.")

        # Initialize and validate that items is a list
        self.items = []
        self.total_cost = 0
        for item in items:
            self.add_item(item)

    def _validate_item(self, item):
        if not isinstance(item, dict):
            raise TypeError("Item must be a dictionary.")
        if not all(key in item for key in ('code', 'cost', 'quantity')):
            raise ValueError("Item must contain 'code', 'cost', and 'quantity' keys.")

    def add_item(self, item):
        self._validate_item(item)
        self.items.append(item)
        self.total_cost += (item['cost'] * item['quantity'])

    def remove_item(self, item_code):
        for item in self.items:
            if item['code'] == item_code:
                self.items.remove(item)
                self.total_cost -= (item['cost'] * item['quantity'])
                return
        print(f"Warning: Item code '{item_code}' not found.")


# --- Child Classes ---

class ShippingOrder(BaseOrder):
    def __init__(self, number, recipient, items):
        self.recipient = recipient
        # super() calls the __init__ of BaseOrder
        super().__init__(number, items, "shipping")


class RestockingOrder(BaseOrder):
    def __init__(self, number, supplier, items):
        self.supplier = supplier
        super().__init__(number, items, "restocking")