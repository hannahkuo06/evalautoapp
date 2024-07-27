import os
import unittest
import time
import pandas as pd

import app.eval as eval


def csv_to_bytes(file_path) -> bytes:
    """
    Converts csv file into bytes object
    :param file_path:
    :return: bytes object
    """
    with open(file_path, 'rb') as file:
        file_bytes = file.read()
    return file_bytes


class TestEvalBasic(unittest.TestCase):
    def test_get_negs(self):
        """
        Tests that get_negs returns the negative records of a table.
        """
        metrics = ['exact_match']
        negs = eval.get_negs('data/mcq_10.csv', metrics)
        first = negs.iloc[0]
        self.assertEqual(first["id"], 4)

    def test_negs(self):
        start_time = time.perf_counter()
        metrics = ['exact_match', 'quasi_exact_match', 'prefix_exact_match', 'quasi_prefix_exact_match',
                   'contains_match']

        df = pd.read_csv('data/mcq_10.csv')
        df = eval.get_negs(df, metrics)
        end_time = time.perf_counter()
        print("Computation runtime: ", end_time-start_time)
        print(df)
        self.assertTrue(len(df) == 1)


class TestGetType(unittest.TestCase):
    def test_get_type_simple(self):
        """
        Tests get_type with a multiple choice question
        """
        df = pd.read_csv('data/mcq_10.csv')
        rec = df.iloc[0]
        check = eval.get_type(rec['inputs_pretokenized'])
        print(check)
        self.assertIn("(A, B, C, or D)", check)


    def test_get_type_saq(self):
        """
        Tests get_type with a short answer question
        """
        df = pd.read_csv('data/saq_10.csv')
        rec = df.iloc[0]
        # print(rec)
        check = eval.get_type(rec['inputs_pretokenized'])
        print(check)
        self.assertIn("individual", check)



class TestCheckType(unittest.TestCase):
    def test_check_type_simple(self):
        """
        Tests check_type when it should include 'Yes' in its response
        """
        df = pd.read_csv('data/mcq_neg_10.csv')
        rec = df.iloc[0]
        q_type = eval.get_type(rec['inputs_pretokenized'])
        check = eval.check_type(rec['generated_text'], q_type)
        print(check)
        self.assertIn("Yes", check)

    def test_check_type_no(self):
        """
        Tests check_type when it should include 'No' in its response
        """
        df = pd.read_csv('data/saq_10.csv')
        rec = df.iloc[7]
        q_type = eval.get_type(rec['inputs_pretokenized'])
        check = eval.check_type(rec['generated_text'], q_type)
        print(check)
        self.assertIn("No", check)

class TestParseTaxonomy(unittest.TestCase):
    def test_parse_good(self):
        """
        Tests parse_taxonomy on correct record
        """
        df = pd.read_csv('data/mcq_10.csv')
        rec = df.iloc[0]
        q_type= eval.get_type(rec['inputs_pretokenized'])
        check = eval.check_type(rec, q_type)
        tag, justification = eval.parse_taxonomy(q_type + check, rec['generated_text'], rec['expected_text'])
        print(tag)
        print(justification)
        self.assertIn("GOOD", tag)
        self.assertEqual([], justification)

    def test_parse_full(self):
        """
        Tests parse_taxonomy on a buggy record
        """
        df = pd.read_csv('data/mcq_neg_10.csv')
        rec = df.iloc[5]
        q_type = eval.get_type(rec['inputs_pretokenized'])
        self.assertIn("(A, B, C, or D)", q_type)

        check = eval.check_type(rec['generated_text'], q_type)
        self.assertIn("Yes", check)

        tag, justification = eval.parse_taxonomy(q_type + check, rec['generated_text'], rec['expected_text'])
        print(tag, justification)
        self.assertEqual(['Bugs'], tag)

        # checks that generated text was a letter (even if expected text is a number)
        self.assertIn("2", justification[0])


    def test_parse_saq(self):
        """
        Tests parse_taxonomy on SAQ
        """
        df = pd.read_csv('data/saq_10.csv')
        rec = df.iloc[1]
        q_type = eval.get_type(rec['inputs_pretokenized'])
        self.assertIn("numerical", q_type)

        check = eval.check_type(rec['generated_text'], q_type)
        self.assertIn("Yes", check)

        tag, justification = eval.parse_taxonomy(q_type + check, rec['generated_text'], rec['expected_text'])
        print(tag, justification)
        self.assertEqual(['Bugs', 'Incorrect'], tag)



class TestConverse(unittest.TestCase):
    def test_converse_full(self):
        """
        Tests full integration of converse on a buggy record
        """
        df = pd.read_csv('data/mcq_neg_10.csv')
        rec = df.iloc[5]

        tag, justification = eval.converse(rec)
        print(tag)
        print(justification)
        self.assertEqual(['Bugs'], tag)
        self.assertIn("2", justification[0])


    def test_converse_simple(self):
        """
        Tests converse on simple incorrect MCQ record
        """
        df = pd.read_csv('data/mcq_neg_10.csv')
        rec = df.iloc[0]

        tag, justification = eval.converse(rec)
        print(tag)
        print(justification)
        self.assertEqual(['Incorrect'], tag)
        self.assertIn('Yes', justification[0])


    def test_converse_saq(self):
        """
        Tests converse on simple incorrect SAQ record
        """
        df = pd.read_csv('data/saq_10.csv')
        rec = df.iloc[7]

        tag, justification = eval.converse(rec)
        print(tag)
        print(justification)
        self.assertIn('Bugs', tag)

    def test_converse_good(self):
        """
        Tests converse on a correct record
        """
        df = pd.read_csv('data/fake_data.csv')
        rec = df.iloc[0]

        tag, justification = eval.converse(rec)
        print(tag)
        print(justification)
        self.assertEqual('GOOD', tag)
        self.assertEqual([], justification)

class TestParallelize(unittest.TestCase):
    def test_para_cols(self):
        """
        Tests that parallelize returns df with 'Errors' and 'Justification' columns
        """
        df = pd.read_csv('data/fake_data.csv')
        self.assertNotIn('Errors', df.columns)
        self.assertNotIn('Justification', df.columns)

        file_bytes = csv_to_bytes('data/fake_data.csv')
        df = eval.parallel(file_bytes)
        self.assertIn('Errors', df.columns)
        self.assertIn('Justification', df.columns)

class TestMetrics(unittest.TestCase):
    def test_metrics_good(self):
        df = pd.read_csv('data/fake_data.csv')
        rec = df.iloc[0]

        lst = ['exact_match', 'prefix_exact_match', 'quasi_exact_match', 'quasi_prefix_exact_match', 'contains_match']

        check = eval.analyze_metrics(rec, lst)
        print(check)
        self.assertIn('GOOD', check[0])

    def test_metrics_neg(self):
        df = pd.read_csv('data/saq_10.csv')
        rec = df.iloc[6]
        print(rec)

        lst = ['exact_match', 'prefix_exact_match', 'quasi_exact_match', 'quasi_prefix_exact_match', 'contains_match']

        check = eval.analyze_metrics(rec, lst)
        print(check)
        self.assertIn('METRIC ERROR', check[0])

    def test_metrics_error(self):
        df = pd.read_csv('data/fake_data.csv')
        rec = df.iloc[5]
        # print(rec)

        lst = ['exact_match', 'prefix_exact_match', 'quasi_exact_match', 'quasi_prefix_exact_match', 'contains_match']

        check = eval.analyze_metrics(rec, lst)
        print(check)
        self.assertEqual(lst, check[0])


if __name__ == '__main__':
    unittest.main()
