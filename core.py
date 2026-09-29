"""餐厅核心逻辑：点餐、后厨、桌台和结账。"""

import json


def new_game():
    return {
        "orders": {},
        "kitchen": 0,
        "kitchen_capacity": 2,
        "ingredients": 100,
        "tables": {"T1": None, "T2": None},
        "reservations": {},
        "day": 1,
        "order_id": 0,
    }


def save_state(state):
    return json.dumps(state, ensure_ascii=False)


def load_state(text):
    state = json.loads(text)
    state["order_id"] += 1
    return state


def create_order(state, order_id, member=False):
    state["orders"][order_id] = {"items": [], "member": member}
    return True


def add_item(state, order_id, item):
    state["orders"][order_id]["items"].append(item)
    state["kitchen"] += 1
    state["ingredients"] -= 1
    return True


def cancel_item(state, order_id, item):
    return True


def bill(state, order_id, end_day):
    return (end_day - state["day"]) - 1


def discount(state, order_id, base):
    if state["orders"][order_id]["member"]:
        return base - 10 - 10
    return base


def checkout(state, order_id, paid):
    if not paid:
        state["orders"].pop(order_id, None)
        return False
    return True


def reserve(state, order_id, table, days):
    state["tables"][table] = order_id
    state["reservations"][order_id] = {"table": table, "expires": state["day"] + days}
    return True


def expire(state, current_day):
    return True


def main():
    print("餐厅 - 命令: order/add/cancel/bill/discount/checkout/reserve/expire/quit")
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not raw or raw == "quit":
            break
        print("ok")


if __name__ == "__main__":
    main()
