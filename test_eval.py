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
        check = eval.response_type(rec)
        print(check)
        self.assertIn("single letter", check)

    # should be correct even if expected text type incorrect
    def test_response_neg(self):
        # metrics = ["exact_match"]
        df = pd.read_csv('data/mcq_neg_10.csv')
        record = df.iloc[5]
        check = eval.response_type(record)
        print(check)
        self.assertIn("single letter", check)

    """TODO: SAQ tests"""

    def test_response_saq(self):
        self.assertTrue(True)


class TestError(unittest.TestCase):
    def test_response_error_good(self):
        df = pd.read_csv('data/mcq_10.csv')
        rec = df.iloc[0]
        check = eval.response_type(rec)
        print(check)
        tag, justification = eval.error_check(rec, check)
        print(tag, justification)
        self.assertIn("Good", tag)
        self.assertIn("1. Yes", justification)
        self.assertIn("2. Yes", justification)

    """TODO: debug"""

    def test_response_error(self):
        df = pd.read_csv('data/mcq_neg_10.csv')
        rec = df.iloc[5]
        check = eval.response_type(rec)
        print(check)
        self.assertIn("multiple-choice", check)
        # self.assertIn("letter", check)

        tag, response = eval.error_check(rec, check)
        print(tag, response)
        self.assertEqual(['Bugs'], tag)

        # checks that generated text was a letter (even if expected text is a number)
        self.assertIn("1. Yes", response)
        self.assertIn("2. No", response)
        # self.assertTrue(True)

    def test_error_neg(self):
        df = pd.read_csv('data/mcq_neg_10.csv')
        rec = df.iloc[0]
        check = eval.response_type(rec)
        print(check)
        response = eval.error_check(rec, check)
        print(response)
        self.assertNotEqual('Good', response)

    """TODO: SAQ tests"""

    def test_error_saq(self):
        self.assertTrue(True)


class TestProcesses(unittest.TestCase):
    """TODO: tests for process_row and process_batch"""""


if __name__ == '__main__':
    unittest.main()
