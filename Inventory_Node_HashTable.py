
class InventoryItem:
    def __init__(self, code, name, price, quantity, max_capacity):
        self.code = code
        self.name = name
        self.price = price
        self.quantity = quantity
        self.max_capacity = max_capacity
    # A class variable, shared by all instances
    def update_quantity(self, quantity):
        self.quantity = quantity

    def update_price(self, price):
        self.price = price

    def update_code(self, code):
        self.code = code

    def update_name(self, name):
        self.name = name

    def update_max_capacity(self, max_capacity):
        self.max_capacity = max_capacity

    def print_inventory(self):
        print(f"{self.code}, {self.name}, {self.quantity}, {self.max_capacity}")


