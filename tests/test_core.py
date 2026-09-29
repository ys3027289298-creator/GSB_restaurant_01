import unittest

import core


class TestCore(unittest.TestCase):
    def test_01_no_duplicate_order(self):
        state = core.new_game()
        self.assertTrue(core.create_order(state, 1))
        self.assertFalse(core.create_order(state, 1))

    def test_02_kitchen_capacity(self):
        state = core.new_game()
        core.create_order(state, 1)
        core.create_order(state, 2)
        core.add_item(state, 1, "A")
        core.add_item(state, 2, "B")
        core.create_order(state, 3)
        result = core.add_item(state, 3, "C")
        self.assertFalse(result)

    def test_03_bill_exact(self):
        state = core.new_game()
        core.create_order(state, 1)
        self.assertEqual(core.bill(state, 1, 3), 2)

    def test_04_cancel_item_refunds(self):
        state = core.new_game()
        core.create_order(state, 1)
        core.add_item(state, 1, "A")
        core.cancel_item(state, 1, "A")
        self.assertEqual(state["ingredients"], 100)

    def test_05_discount_once(self):
        state = core.new_game()
        core.create_order(state, 1, member=True)
        self.assertEqual(core.discount(state, 1, 100), 90)

    def test_06_checkout_failure_keeps_order(self):
        state = core.new_game()
        core.create_order(state, 1)
        result = core.checkout(state, 1, False)
        self.assertFalse(result)
        self.assertIn(1, state["orders"])

    def test_07_expire_releases_table(self):
        state = core.new_game()
        core.reserve(state, 1, "T1", 1)
        core.expire(state, 5)
        self.assertIsNone(state["tables"]["T1"])

    def test_08_load_preserves_order_id(self):
        state = core.new_game()
        state["order_id"] = 7
        loaded = core.load_state(core.save_state(state))
        self.assertEqual(loaded["order_id"], 7)


if __name__ == "__main__":
    unittest.main()
