import unittest
import pandas as pd

from eval import response_type_check, error_check, get_negs


class TestEvalBasic(unittest.TestCase):
    def test_get_negs(self):
        # should return negative records of the data
        metrics = ['exact_match']
        negs = get_negs('data/mcq_10.csv', metrics)
        first = negs.iloc[0]
        self.assertEqual(first["id"], 4)

class TestResponse(unittest.TestCase):
    def test_response_type_check_simple(self):
        metrics = ["exact_match"]
        check = response_type_check('data/mcq_10.csv', metrics)
        # print(check)
        self.assertIn("multiple-choice", check)

    # will need more complex and in-depth tests
    def test_response_error(self):
        # df = pd.read_csv('arc_challenge_lite.csv')
        metrics = ["exact_match"]
        check = response_type_check('data/mcq_10.csv', metrics)
        # print(check)
        response = error_check('data/mcq_10.csv', metrics, check)
        # print(response)
        self.assertIn("1. Yes", response)
        self.assertIn("2. No", response)

    # should be correct even if expected text type incorrect
    def test_response_type_check_1(self):
        metrics = ["exact_match"]
        neg = get_negs('data/mcq_10.csv', metrics)

        record = neg.loc[44]

        check = response_type_check(record)
        self.assertIn("single letter", check)


if __name__ == '__main__':
    unittest.main()

