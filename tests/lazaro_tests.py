import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(".."))
sys.path.insert(0, os.path.abspath("."))

from pylazaro import Lazaro
from pylazaro.classifiers import *
from pylazaro.output import *
from pylazaro.utils import *
from pylazaro.token import Token
from pylazaro.borrowing import Borrowing

EXAMPLE = "La 'app' de 'machine learning' fue un éxito en el festival de 'anime'"
TOKENIZED_SENTENCE = [
    Token(text='La', label='O', position=0, probability=None),
    Token(text="'", label='O', position=1, probability=None),
    Token(text='app', label='B-ENG', position=2, probability=None),
    Token(text="'", label='O', position=3, probability=None),
    Token(text='de', label='O', position=4, probability=None),
    Token(text="'", label='O', position=5, probability=None),
    Token(text='machine', label='B-ENG', position=6, probability=None),
    Token(text='learning', label='I-ENG', position=7, probability=None),
    Token(text="'", label='O', position=8, probability=None),
    Token(text='fue', label='O', position=9, probability=None),
    Token(text='un', label='O', position=10, probability=None),
    Token(text='éxito', label='O', position=11, probability=None),
    Token(text='en', label='O', position=12, probability=None),
    Token(text='el', label='O', position=13, probability=None),
    Token(text='festival', label='O', position=14, probability=None),
    Token(text='de', label='O', position=15, probability=None),
    Token(text="'", label='O', position=16, probability=None),
    Token(text='anime', label='B-OTHER', position=17, probability=None),
    Token(text="'", label='O', position=18, probability=None)
]

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


BORROWINGS = [
    Borrowing(tokens=[Token('app', "B-ENG", 2)], language='ENG', start_pos=2, end_pos=3,
              context_tokens=TOKENIZED_SENTENCE),
    Borrowing(tokens=[Token('machine', "B-ENG", 6), Token('learning', "I-ENG", 7)], language='ENG',
              start_pos=6,
              end_pos=8,
              context_tokens=TOKENIZED_SENTENCE),
    Borrowing(tokens=[Token('anime', "B-OTHER", 17)], language='OTHER', start_pos=17, end_pos=18,
              context_tokens=TOKENIZED_SENTENCE)
]

ANGLICISMS = [
    Borrowing(tokens=[Token('app', "B-ENG", 2)], language='ENG', start_pos=2, end_pos=3,
              context_tokens=TOKENIZED_SENTENCE),
    Borrowing(tokens=[Token('machine', "B-ENG", 6), Token('learning', "I-ENG", 7)], language='ENG',
              start_pos=6,
              end_pos=8,
              context_tokens=TOKENIZED_SENTENCE)
]

OTHER = [
    Borrowing(tokens=[Token('anime', "B-OTHER", 17)], language='OTHER', start_pos=17, end_pos=18,
              context_tokens=TOKENIZED_SENTENCE)]


class LazaroCRFTestCase(unittest.TestCase):
    def setUp(self):
        self.lazaro = Lazaro(model_type="crf")
        self.prediction = self.lazaro.analyze(EXAMPLE)

    def test_classifier_is_CRFClassifier(self):
        self.assertIsInstance(self.lazaro._classifier, CRFClassifier)

    def test_model_is_CRFsuiteEntityRecognizer_CoNLL(self):
        self.assertIsInstance(
            self.lazaro._classifier.model, CRFsuiteEntityRecognizer_CoNLL
        )

    def test_model_has_spacy(self):
        self.assertIsInstance(self.lazaro._classifier.spacy_model, Language)

    def test_crf_is_LazaroOutput(self):
        self.assertIsInstance(self.prediction, LazaroOutput)

    def test_borrowings(self):
        self.assertEqual(self.prediction.borrowings, BORROWINGS)

    def test_anglicisms(self):
        self.assertEqual(self.prediction.anglicisms, ANGLICISMS)

    def test_other_borrowings(self):
        self.assertEqual(self.prediction.other_borrowings, OTHER)

    def test_tag_per_token(self):
        self.assertEqual(self.prediction.tag_per_token(), TAG_PER_TOKEN)

class LazaroFlairTestCase(unittest.TestCase):
    def setUp(self):
        self.lazaro = Lazaro(model_type="bilstm")
        self.prediction = self.lazaro.analyze(EXAMPLE)

    def test_classifier_is_FlairClassifier(self):
        self.assertIsInstance(self.lazaro._classifier, FlairClassifier)

    def test_is_LazaroOutput(self):
        self.assertIsInstance(self.prediction, LazaroOutput)

    def test_borrowings(self):
        self.assertEqual(self.prediction.borrowings, BORROWINGS)

    def test_anglicisms(self):
        self.assertEqual(self.prediction.anglicisms, ANGLICISMS)

    def test_other_borrowings(self):
        self.assertEqual(self.prediction.other_borrowings, OTHER)

    def test_tag_per_token(self):
        self.assertEqual(self.prediction.tag_per_token(), TAG_PER_TOKEN)




class LazaroTransformersTestCase(unittest.TestCase):
    #maxDiff = None

    def setUp(self):
        self.lazaro = Lazaro(model_type="transformers")
        self.prediction = self.lazaro.analyze(EXAMPLE)

    def test_classifier_is_TransformersClassifier(self):
        self.assertIsInstance(self.lazaro._classifier, TransformersClassifier)

    def test_is_LazaroOutput(self):
        self.assertIsInstance(self.prediction, LazaroOutput)

    def test_borrowings(self):
        self.assertEqual(self.prediction.borrowings, BORROWINGS)

    def test_anglicisms(self):
        self.assertEqual(self.prediction.anglicisms, ANGLICISMS)

    def test_other_borrowings(self):
        self.assertEqual(self.prediction.other_borrowings, OTHER)

    def test_tag_per_token(self):
        self.assertEqual(self.prediction.tag_per_token(), TAG_PER_TOKEN)


if __name__ == "__main__":
    unittest.main()
