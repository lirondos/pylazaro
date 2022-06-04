import unittest
from pylazaro import Lazaro
from pylazaro.classifiers import *
from pylazaro.utils import *
from spacy.language import Language
from pylazaro.outputs import *


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


class LazaroFlairTestCase(unittest.TestCase):

	def setUp(self):
		self.lazaro = Lazaro(model_type="flair")
		self.text = "La 'app' fue un éxito"
		self.prediction = self.lazaro.analyze(self.text)

	def test_classifier_is_CRFClassifier(self):
		self.assertIsInstance(self.lazaro._classifier, FlairClassifier)

	def test_crf_is_Flairoutput(self):
		self.assertIsInstance(self.prediction, LazaroOutputFlair)

	def test_get_borrowings(self):
		self.assertEqual(self.prediction.borrowings(), [("app", 'ENG')])
		
	def test_get_borrowings(self):
		self.assertEqual(self.prediction.anglicisms(), [("app", 'ENG')])

	def test_get_tuples(self):
		expected_result = [("La", 'O'), ("'", 'O'), ("app", 'B-ENG'), ("'", 'O'), ("fue", 'O'),
																		("un", 'O'), ("éxito", 'O')]
		self.assertEqual(self.prediction.tag_per_token(), expected_result)

class LazaroTransformersTestCase(unittest.TestCase):

	def setUp(self):
		self.lazaro = Lazaro(model_type="transformers")
		self.text = "La 'app' fue un éxito"
		self.prediction = self.lazaro.analyze(self.text)

	def test_classifier_is_CRFClassifier(self):
		self.assertIsInstance(self.lazaro._classifier, TransformersClassifier)

	def test_crf_is_Flairoutput(self):
		self.assertIsInstance(self.prediction, LazaroOutputTransformers)

	def test_get_borrowings(self):
		self.assertEqual(self.prediction.borrowings(), [("app", 'ENG')])
		
	def test_get_borrowings(self):
		self.assertEqual(self.prediction.anglicisms(), [("app", 'ENG')])

	def test_get_tuples(self):
		expected_result = [("La", 'O'), ("'", 'O'), ("app", 'B-ENG'), ("'", 'O'), ("fue", 'O'),
																		("un", 'O'), ("éxito", 'O')]
		self.assertEqual(self.prediction.tag_per_token(), expected_result)
        
if __name__ == '__main__':
	unittest.main()
