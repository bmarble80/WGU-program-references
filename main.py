import Inventory_Node_HashTable
import Shipping_Restocking_Orders
import queue

# Hash Table Values for Inventory
inventory = {}
inventoryCode = 0
warehouse_max_item_capacity = 5

# Hash Table values for Completed orders
restock_orders = {}
shipping_orders = {}

# Order tracking system
order_queue = queue.Queue()
backOrder_queue = queue.Queue()

# Create separate trackers for each order type
shipping_order_number = 1000
restocking_order_number = 5000


def create_inventory(quantity, name="", price=0.0, max_capacity=100):
    global inventory
    global inventoryCode
    global warehouse_max_item_capacity

    try:
        if len(inventory) < warehouse_max_item_capacity:
            code = inventoryCode
            new_item = Inventory_Node_HashTable.InventoryItem(code, name, price, quantity, max_capacity)
            inventory[code] = new_item
            inventoryCode += 1
            print(f"Success: {name} (Code: {code}) added to inventory!")
        else:
            print(f"Inventory is full! Cannot add {name}.")
    except Exception as e:
        print(f"CRITICAL ERROR creating inventory item {name}: {e}")


def print_inventory():
    print("\n--- CURRENT INVENTORY STATUS ---")
    for code, item in inventory.items():
        # Calculate percent full.
        # Using a try/except to prevent ZeroDivisionError if max_capacity is somehow 0
        try:
            percent_full = (item.quantity / item.max_capacity) * 100
        except ZeroDivisionError:
            percent_full = 0.0

        print(f"Code {code} | {item.name}: {item.quantity}/{item.max_capacity} in stock ({percent_full:.1f}% full)")


def create_shipping_order(recipient, items):
    global shipping_order_number
    try:
        # This will raise TypeError or ValueError from BaseOrder if data is bad
        new_order = Shipping_Restocking_Orders.ShippingOrder(shipping_order_number, recipient, items)
        order_queue.put(new_order)
        print(f"Success: Shipping Order #{shipping_order_number} for {recipient} added to queue.")
        shipping_order_number += 1
    except (TypeError, ValueError) as e:
        print(f"DATA VALIDATION ERROR on Shipping Order for {recipient}: {e}")
    except Exception as e:
        print(f"UNEXPECTED ERROR processing Shipping Order: {e}")


def create_restocking_order(supplier, items):
    global restocking_order_number
    try:
        # This will raise TypeError or ValueError from BaseOrder if data is bad
        new_order = Shipping_Restocking_Orders.RestockingOrder(restocking_order_number, supplier, items)
        order_queue.put(new_order)
        print(f"Success: Restocking Order #{restocking_order_number} from {supplier} added to queue.")
        restocking_order_number += 1
    except (TypeError, ValueError) as e:
        print(f"DATA VALIDATION ERROR on Restock Order for {supplier}: {e}")
    except Exception as e:
        print(f"UNEXPECTED ERROR processing Restock Order: {e}")


def process_next_order():
    if order_queue.empty():
        print("The order queue is empty. Nothing to process!")
        return

    try:
        current_order = order_queue.get()
        is_shipping = isinstance(current_order, Shipping_Restocking_Orders.ShippingOrder)
        is_restocking = isinstance(current_order, Shipping_Restocking_Orders.RestockingOrder)

        print(f"\n--- Processing Order #{current_order.number} ---")

        for order_item in current_order.items:
            item_code = order_item['code']

            if item_code in inventory:
                inv_item = inventory[item_code]

                if is_shipping:
                    if inv_item.quantity >= order_item['quantity']:
                        new_quantity = inv_item.quantity - order_item['quantity']
                        inv_item.update_quantity(new_quantity)
                        shipping_orders[current_order.number] = current_order
                        print(f"Shipped {order_item['quantity']}x {inv_item.name}. New stock: {inv_item.quantity}")
                    else:
                        backOrder_queue.put(current_order)
                        print(
                            f"ERROR: Not enough {inv_item.name} in stock! (Have {inv_item.quantity}, need {order_item['quantity']}) - Sent to Backorder.")

                elif is_restocking:
                    if inv_item.quantity + order_item['quantity'] <= inv_item.max_capacity:
                        new_quantity = inv_item.quantity + order_item['quantity']
                        inv_item.update_quantity(new_quantity)
                        restock_orders[current_order.number] = current_order
                        print(f"Restocked {order_item['quantity']}x {inv_item.name}. New stock: {inv_item.quantity}")
                    else:
                        space_left = inv_item.max_capacity - inv_item.quantity
                        excess_returned = order_item['quantity'] - space_left
                        inv_item.update_quantity(inv_item.max_capacity)
                        restock_orders[current_order.number] = current_order
                        print(
                            f"WARNING: Exceeds Max Capacity for {inv_item.name}! Filled {space_left} units to hit max. Returning {excess_returned} units to vendor.")
            else:
                print(f"ERROR: Item with code '{item_code}' does not exist in the inventory system!")

    except Exception as e:
        print(f"CRITICAL SYSTEM ERROR while processing queue: {e}")


def search_order_status(order_number):
    """Searches all queues and hash tables to locate a specific order by its number."""
    print(f"\n--- Searching for Order #{order_number} ---")

    # 1. Check Completed Hash Tables (O(1) time complexity)
    if order_number in shipping_orders:
        return f"Status: Order #{order_number} is COMPLETED (Successfully Shipped)."
    if order_number in restock_orders:
        return f"Status: Order #{order_number} is COMPLETED (Successfully Restocked)."

    # 2. Check Processing Queue
    # use .queue to peek at the underlying deque without removing items from the actual queue
    for order in list(order_queue.queue):
        if order.number == order_number:
            return f"Status: Order #{order_number} is PENDING in the Processing Queue."

    # 3. Check Backorder Queue
    for order in list(backOrder_queue.queue):
        if order.number == order_number:
            return f"Status: Order #{order_number} is STALLED in the Backorder Queue."

    return f"Status: Order #{order_number} NOT FOUND in any system."

# ==========================================
#               TEST CASES
# ==========================================

print("\n--- TEST 1: INVENTORY SETUP ---")
# This creates items with codes 0, 1, and 2
create_inventory(quantity=50, name="Mechanical Keyboard", price=85.00)
create_inventory(quantity=10, name="Wireless Mouse", price=25.00)
create_inventory(quantity=100, name="Mousepad", price=12.00)
# Test 1b: Setting max_capacity to 0 to test the ZeroDivisionError try/except block
create_inventory(quantity=0, name="Discontinued Item", price=5.00, max_capacity=0)

print("\n--- TEST 2: QUEUING ORDERS ---")
# 1. Normal Shipping: Alice buys 2 Mice (Code 1) and 5 Mousepads (Code 2)
create_shipping_order("Alice Smith", [
    {'code': 1, 'cost': 25.00, 'quantity': 2},
    {'code': 2, 'cost': 12.00, 'quantity': 5}
])

# 2. Insufficient Stock: Bob tries to buy 60 Keyboards, but only have 50 in stock (Code 0)
create_shipping_order("Bob Jones", [
    {'code': 0, 'cost': 85.00, 'quantity': 60}
])

# 3. Normal Restocking: buy 30 more Mice from our vendor (Code 1)
create_restocking_order("Tech Distro", [
    {'code': 1, 'cost': 15.00, 'quantity': 30}
])

# 4. Invalid Item Code: Charlie tries to buy an item that doesn't exist (Code 99)
create_shipping_order("Charlie Brown", [
    {'code': 99, 'cost': 10.00, 'quantity': 1}
])

print("\n--- TEST 3: PROCESSING QUEUE ---")
# We added 4 orders, so we need to call the process function 4 times
process_next_order() # Processes Alice's order (Order 1000 - Should succeed)
process_next_order() # Processes Bob's order (Order 1001 - Should throw stock error and go to backorder)
process_next_order() # Processes Tech Distro's order (Order 5000 - Should succeed)
process_next_order() # Processes Charlie's order (Order 1002 - Should throw invalid code error)

# Call it one extra time to test what happens when the queue is empty
process_next_order()

print("\n--- TEST 4: FINAL INVENTORY CHECK (PERCENTAGES & ZERO DIVISION) ---")
# verify the math worked correctly and percentages display properly
print_inventory()

print("\n--- TEST 5: WAREHOUSE CAPACITY LIMIT ---")
# Already have 4 unique items in inventory (Codes 0, 1, 2, 3). current max is 5 unique items.
create_inventory(quantity=20, name="Webcam", price=45.00) # Should succeed (Item 5 - Code 4)
create_inventory(quantity=15, name="Microphone", price=90.00) # Should throw "Inventory is full!" error

print("\n--- TEST 6: RESTOCKING EXCEEDS MAX CAPACITY ---")
# Webcams (Code 4) currently have 20 in stock (Max default 100). We will try to add 100.
create_restocking_order("Audio Gear Inc", [
    {'code': 4, 'cost': 12.00, 'quantity': 100}
])
# Process the newly queued restock order (Order 5001)
process_next_order() # Should throw the "Exceeds Max Capacity" error and return 20 units

print("\n--- TEST 7: EXCEPTION HANDLING FOR INVALID DATA ---")
# Purposely passing a string instead of a list of dictionaries to trigger the try/except blocks
create_shipping_order("Dave Crash", "This is bad data that would normally crash the program.")
create_restocking_order("Bad Vendor", [{'wrong_key': 5, 'cost': 10}]) # Missing required keys

print("\n--- TEST 8: ORDER SEARCH FUNCTIONALITY ---")
# One more order to the queue but NOT process it, so it stays pending to test this status
create_shipping_order("Pending Pete", [{'code': 1, 'cost': 25.00, 'quantity': 1}])

# Test the search function across all possible statuses
print(search_order_status(1000))  # Alice's successful order (Completed Shipping)
print(search_order_status(5000))  # Tech Distro's successful order (Completed Restock)
print(search_order_status(1001))  # Bob's failed order (Backordered)
print(search_order_status(1003))  # Pete's new order (Pending in Queue)
print(search_order_status(9999))  # A fake order number (Not Found)