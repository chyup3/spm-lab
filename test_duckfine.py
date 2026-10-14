import unittest

from duckfine import DuckFine


class TestDuckFine(unittest.TestCase):
    def setUp(self):
        self.fine = DuckFine("M001")

    def test_charge_returns_a_fee_for_a_late_duck(self):
        self.assertEqual(self.fine.charge(5), 1.50)

    def test_fine_is_capped_at_five_dollars(self):
        self.assertEqual(self.fine.charge(100), 5.00)


if __name__ == "__main__":
    unittest.main()
