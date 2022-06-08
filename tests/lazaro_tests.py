import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(".."))
from spacy.language import Language

from pylazaro import Lazaro
from pylazaro.classifiers import *
from pylazaro.outputs import *
from pylazaro.utils import *

EXAMPLE = "La 'app' de 'machine learning' fue un éxito en el festival de 'anime'"
TAG_PER_TOKEN = [
    ("La", "O"),
    ("'", "O"),
    ("app", "B-ENG"),
    ("'", "O"),
    ("de", "O"),
    ("'", "O"),
    ("machine", "B-ENG"),
    ("learning", "I-ENG"),
    ("'", "O"),
    ("fue", "O"),
    ("un", "O"),
    ("éxito", "O"),
    ("en", "O"),
    ("el", "O"),
    ("festival", "O"),
    ("de", "O"),
    ("'", "O"),
    ("anime", "B-OTHER"),
    ("'", "O"),
]

BORROWINGS = [("app", "ENG"), ("machine learning", "ENG"), ("anime", "OTHER")]
ANGLICISMS = [("app", "ENG"), ("machine learning", "ENG")]
OTHER = [("anime", "OTHER")]

"""
class LazaroCRFTestCase(unittest.TestCase):

	def setUp(self):
		self.lazaro_crf = Lazaro(model_type="crf")
		self.text = "La 'app' fue un éxito"
		self.prediction = self.lazaro_crf.analyze(self.text)

	def test_classifier_is_CRFClassifier(self):
		self.assertIsInstance(self.lazaro_crf._classifier, CRFClassifier)

	def test_model_is_CRFsuiteEntityRecognizer_CoNLL(self):
		self.assertIsInstance(self.lazaro_crf._classifier.model, CRFsuiteEntityRecognizer_CoNLL)

	def test_model_has_spacy(self):
		self.assertIsInstance(self.lazaro_crf._classifier.spacy_model, Language)

	def test_crf_is_CRFoutput(self):
		self.assertIsInstance(self.prediction, LazaroOutputCRF)

	def test_get_borrowings(self):
		self.assertEqual(self.prediction.borrowings(), [("app", 'ENG')])

	def test_get_anglicisms(self):
		self.assertEqual(self.prediction.borrowings(), [("app", 'ENG')])

	def test_get_tuples(self):
		expected_result = [("La", 'O'), ("'", 'O'), ("app", 'B-ENG'), ("'", 'O'), ("fue", 'O'),
																		("un", 'O'), ("éxito", 'O')]
		self.assertEqual(self.prediction.tag_per_token(), expected_result)
"""


class LazaroFlairTestCase(unittest.TestCase):
    def setUp(self):
        self.lazaro = Lazaro(model_type="bilstm")
        self.prediction = self.lazaro.analyze(EXAMPLE)

    def test_classifier_is_FlairClassifier(self):
        self.assertIsInstance(self.lazaro._classifier, FlairClassifier)

    def test_is_FlairOutput(self):
        self.assertIsInstance(self.prediction, LazaroOutputFlair)

    def test_borrowings(self):
        self.assertEqual(self.prediction.borrowings(), BORROWINGS)

    def test_anglicisms(self):
        self.assertEqual(self.prediction.anglicisms(), ANGLICISMS)

    def test_other_borrowings(self):
        self.assertEqual(self.prediction.other_borrowings(), OTHER)

    def test_tag_per_token(self):
        self.assertEqual(self.prediction.tag_per_token(), TAG_PER_TOKEN)


class LazaroTransformersTestCase(unittest.TestCase):
    def setUp(self):
        self.lazaro = Lazaro(model_type="transformers")
        self.prediction = self.lazaro.analyze(EXAMPLE)

    def test_classifier_is_TransformersClassifier(self):
        self.assertIsInstance(self.lazaro._classifier, TransformersClassifier)

    def test_is_TransformersOutput(self):
        self.assertIsInstance(self.prediction, LazaroOutputTransformers)

    def test_borrowings(self):
        self.assertEqual(self.prediction.borrowings(), BORROWINGS)

    def test_anglicisms(self):
        self.assertEqual(self.prediction.anglicisms(), ANGLICISMS)

    def test_other_borrowings(self):
        self.assertEqual(self.prediction.other_borrowings(), OTHER)

    def test_tag_per_token(self):
        self.assertEqual(self.prediction.tag_per_token(), TAG_PER_TOKEN)


if __name__ == "__main__":
    unittest.main()
