"""餐厅核心逻辑：点餐、后厨、桌台和结账。"""

import json

COMMAND_PROMPT = "餐厅 - 命令: order/add/cancel/bill/discount/checkout/reserve/expire/quit"


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
    if not isinstance(text, str) or not text.strip():
        return new_game()
    try:
        data = json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return new_game()
    if not isinstance(data, dict):
        return new_game()
    state = new_game()
    state.update(data)
    return state


def create_order(state, order_id, member=False):
    if order_id in state["orders"]:
        return False
    state["orders"][order_id] = {"items": [], "member": bool(member)}
    return True


def add_item(state, order_id, item):
    if order_id not in state["orders"]:
        return False
    if item is None or (isinstance(item, str) and not item.strip()):
        return False
    if state["kitchen"] >= state["kitchen_capacity"]:
        return False
    if state["ingredients"] <= 0:
        return False
    state["orders"][order_id]["items"].append(item)
    state["kitchen"] += 1
    state["ingredients"] -= 1
    return True


def cancel_item(state, order_id, item):
    if order_id not in state["orders"]:
        return False
    items = state["orders"][order_id]["items"]
    if item not in items:
        return False
    items.remove(item)
    if state["kitchen"] > 0:
        state["kitchen"] -= 1
    state["ingredients"] += 1
    return True


def bill(state, order_id, end_day):
    if order_id not in state["orders"]:
        return 0
    if end_day < state["day"]:
        return 0
    return end_day - state["day"]


def discount(state, order_id, base):
    if order_id not in state["orders"]:
        return base
    if state["orders"][order_id]["member"]:
        return max(0, base - 10)
    return base


def checkout(state, order_id, paid):
    if order_id not in state["orders"]:
        return False
    if not paid:
        return False
    items = state["orders"].pop(order_id)["items"]
    if state["kitchen"] >= len(items):
        state["kitchen"] -= len(items)
    else:
        state["kitchen"] = 0
    reservation = state["reservations"].pop(order_id, None)
    if reservation is not None:
        table = reservation["table"]
        if state["tables"].get(table) == order_id:
            state["tables"][table] = None
    return True


def reserve(state, order_id, table, days):
    if order_id not in state["orders"]:
        return False
    if table not in state["tables"]:
        return False
    if state["tables"][table] is not None:
        return False
    state["tables"][table] = order_id
    state["reservations"][order_id] = {"table": table, "expires": state["day"] + days}
    return True


def expire(state, current_day):
    expired = [
        order_id
        for order_id, info in state["reservations"].items()
        if current_day >= info["expires"]
    ]
    for order_id in expired:
        info = state["reservations"].pop(order_id)
        table = info["table"]
        if state["tables"].get(table) == order_id:
            state["tables"][table] = None
    return True


def _next_order_id(state):
    state["order_id"] += 1
    return state["order_id"]


def _parse_bool(text):
    return str(text).strip().lower() in ("1", "true", "yes", "y")


def run_command(state, raw):
    parts = raw.strip().split()
    if not parts:
        return True, state
    command = parts[0]
    args = parts[1:]
    if command == "quit":
        return False, state
    if command == "order":
        member = len(args) > 1 and _parse_bool(args[1])
        order_id = _next_order_id(state)
        create_order(state, order_id, member)
        print("order", order_id)
    elif command == "add":
        if len(args) < 2:
            print("error: add <order_id> <item>")
        else:
            try:
                order_id = int(args[0])
            except ValueError:
                print("error: invalid order_id")
            else:
                print("ok" if add_item(state, order_id, args[1]) else "rejected")
    elif command == "cancel":
        if len(args) < 2:
            print("error: cancel <order_id> <item>")
        else:
            try:
                order_id = int(args[0])
            except ValueError:
                print("error: invalid order_id")
            else:
                print("ok" if cancel_item(state, order_id, args[1]) else "rejected")
    elif command == "bill":
        if len(args) < 2:
            print("error: bill <order_id> <end_day>")
        else:
            try:
                order_id = int(args[0])
                end_day = int(args[1])
            except ValueError:
                print("error: invalid number")
            else:
                print("bill", bill(state, order_id, end_day))
    elif command == "discount":
        if len(args) < 2:
            print("error: discount <order_id> <base>")
        else:
            try:
                order_id = int(args[0])
                base = int(args[1])
            except ValueError:
                print("error: invalid number")
            else:
                print("total", discount(state, order_id, base))
    elif command == "checkout":
        if len(args) < 2:
            print("error: checkout <order_id> <paid>")
        else:
            try:
                order_id = int(args[0])
            except ValueError:
                print("error: invalid order_id")
            else:
                paid = _parse_bool(args[1])
                print("ok" if checkout(state, order_id, paid) else "rejected")
    elif command == "reserve":
        if len(args) < 3:
            print("error: reserve <order_id> <table> <days>")
        else:
            try:
                order_id = int(args[0])
                days = int(args[2])
            except ValueError:
                print("error: invalid number")
            else:
                print("ok" if reserve(state, order_id, args[1], days) else "rejected")
    elif command == "expire":
        if len(args) < 1:
            print("error: expire <current_day>")
        else:
            try:
                current_day = int(args[0])
            except ValueError:
                print("error: invalid number")
            else:
                expire(state, current_day)
                print("ok")
    else:
        print("error: unknown command")
    return True, state


def main():
    print(COMMAND_PROMPT)
    state = new_game()
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not raw:
            continue
        keep_going, state = run_command(state, raw)
        if not keep_going:
            break


if __name__ == "__main__":
    main()
