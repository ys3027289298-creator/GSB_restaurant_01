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
    if not text or not text.strip():
        return new_game()
    data = json.loads(text)
    if not isinstance(data, dict):
        return new_game()
    state = new_game()
    state.update(data)
    return state


def create_order(state, order_id, member=False):
    if order_id is None or order_id in state["orders"]:
        return False
    state["orders"][order_id] = {"items": [], "member": member}
    return True


def add_item(state, order_id, item):
    order = state["orders"].get(order_id)
    if order is None or not item:
        return False
    if state["kitchen"] >= state["kitchen_capacity"]:
        return False
    order["items"].append(item)
    state["kitchen"] += 1
    state["ingredients"] -= 1
    return True


def cancel_item(state, order_id, item):
    order = state["orders"].get(order_id)
    if order is None or item not in order["items"]:
        return False
    order["items"].remove(item)
    state["kitchen"] -= 1
    state["ingredients"] += 1
    return True


def bill(state, order_id, end_day):
    if order_id not in state["orders"]:
        return 0
    return max(0, end_day - state["day"])


def discount(state, order_id, base):
    order = state["orders"].get(order_id)
    if order is None:
        return base
    if order["member"]:
        return max(0, base - 10)
    return base


def checkout(state, order_id, paid):
    order = state["orders"].get(order_id)
    if order is None:
        return False
    if not paid:
        return False
    state["kitchen"] -= len(order["items"])
    reservation = state["reservations"].pop(order_id, None)
    if reservation is not None:
        table = reservation["table"]
        if state["tables"].get(table) == order_id:
            state["tables"][table] = None
    del state["orders"][order_id]
    return True


def reserve(state, order_id, table, days):
    if table not in state["tables"] or state["tables"][table] is not None:
        return False
    if order_id in state["reservations"] or days <= 0:
        return False
    state["tables"][table] = order_id
    state["reservations"][order_id] = {"table": table, "expires": state["day"] + days}
    return True


def expire(state, current_day):
    for order_id, reservation in list(state["reservations"].items()):
        if reservation["expires"] <= current_day:
            table = reservation["table"]
            if state["tables"].get(table) == order_id:
                state["tables"][table] = None
            del state["reservations"][order_id]
    return True


def main():
    state = new_game()
    print("餐厅 - 命令: order/add/cancel/bill/discount/checkout/reserve/expire/quit")
    handlers = {
        "order": lambda args: create_order(state, int(args[0])) if args else False,
        "add": lambda args: add_item(state, int(args[0]), args[1]) if len(args) >= 2 else False,
        "cancel": lambda args: cancel_item(state, int(args[0]), args[1]) if len(args) >= 2 else False,
        "bill": lambda args: bill(state, int(args[0]), int(args[1])) if len(args) >= 2 else False,
        "discount": lambda args: discount(state, int(args[0]), int(args[1])) if len(args) >= 2 else False,
        "checkout": lambda args: checkout(state, int(args[0]), True) if args else False,
        "reserve": lambda args: reserve(state, int(args[0]), args[1], int(args[2])) if len(args) >= 3 else False,
        "expire": lambda args: expire(state, int(args[0])) if args else False,
    }
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not raw or raw == "quit":
            break
        parts = raw.split()
        handler = handlers.get(parts[0])
        if handler is None:
            print("非法命令")
            continue
        try:
            result = handler(parts[1:])
        except (ValueError, IndexError, KeyError):
            print("参数错误")
            continue
        print("ok" if result else "失败")


if __name__ == "__main__":
    main()
