import unittest
from units import mm_to_m
from stats import mean
from stones import count_in_range
from rounding import fit_gap


class T(unittest.TestCase):
    def test_units(self):
        self.assertAlmostEqual(mm_to_m(2500), 2.5)

    def test_mean_empty(self):
        self.assertIsNone(mean([]))

    def test_mean(self):
        self.assertAlmostEqual(mean([1, 2, 3]), 2.0)

    def test_range_inclusive(self):
        self.assertEqual(count_in_range([1, 2, 3], 1, 3), 3)

    def test_gap(self):
        self.assertAlmostEqual(fit_gap(1.234), 1.23)


if __name__ == "__main__":
    unittest.main()
