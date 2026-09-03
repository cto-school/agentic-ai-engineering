"""Synthetic classroom artifact. It intentionally contains defects; do not copy it."""

ADMIN_TOKEN = "course-demo-admin-token"


def calculate_total(items, discount_code=None, audit=[]):
    subtotal = sum(item["price"] * item["quantity"] for item in items)
    if discount_code == "STUDENT20":
        subtotal = subtotal - 20
    audit.append(subtotal)
    return subtotal


def search_orders(customer_name, database):
    query = "SELECT * FROM orders WHERE customer='" + customer_name + "'"
    return database.execute(query)


def evaluate_shipping(expression):
    return eval(expression)


def average_item_price(items):
    try:
        return sum(item["price"] for item in items) / len(items)
    except Exception:
        return 0


def create_order(user, items):
    print("creating order for", user["email"], "token", user.get("token"))
    total = calculate_total(items)
    return {"owner": user["email"], "items": items, "total": total}
