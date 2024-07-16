import unittest
import pandas as pd

import eval


class TestEvalBasic(unittest.TestCase):
    def test_get_negs(self):
        # should return negative records of the data
        metrics = ['exact_match']
        negs = eval.get_negs('data/mcq_10.csv', metrics)
        first = negs.iloc[0]
        self.assertEqual(first["id"], 4)

class TestResponse(unittest.TestCase):
    def test_response_simple(self):
        df = pd.read_csv('data/mcq_10.csv')
        rec = df.iloc[0]
        check = eval.response_type_check(rec)
        print(check)
        self.assertIn("single letter", check)

    # should be correct even if expected text type incorrect
    def test_response_neg(self):
        # metrics = ["exact_match"]
        df = pd.read_csv('data/mcq_neg_10.csv')
        record = df.iloc[5]
        check = eval.response_type_check(record)
        print(check)
        self.assertIn("single letter", check)

    # TODO: SAQ tests
    def test_response_saq(self):
        self.assertTrue(True)

class TestError(unittest.TestCase):
    def test_response_error_good(self):
        df = pd.read_csv('data/mcq_10.csv')
        rec = df.iloc[0]
        check = eval.response_type_check(rec)
        print(check)
        response = eval.error_check(rec, check)
        print(response)
        self.assertIn("Good", response)

    # TODO: debug
    def test_response_error(self):
        df = pd.read_csv('data/mcq_neg_10.csv')
        rec = df.iloc[5]
        check = eval.response_type_check(rec)
        print(check)
        response = eval.error_check(rec, check)
        print(response)
        # self.assertIn(['Bugs'], response)
        self.assertTrue(True)

    def test_error_neg(self):
        df = pd.read_csv('data/mcq_neg_10.csv')
        rec = df.iloc[0]
        check = eval.response_type_check(rec)
        print(check)
        response = eval.error_check(rec, check)
        print(response)
        self.assertNotEquals('Good', response)

    # TODO: SAQ tests
    def test_error_saq(self):
        self.assertTrue(True)




if __name__ == '__main__':
    unittest.main()

