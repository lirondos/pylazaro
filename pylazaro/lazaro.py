import attr
import pathlib
import logging
from pylazaro.classifiers import LazaroClassifier, CRFClassifier, FlairClassifier
from pylazaro.outputs import LazaroOutput

logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("flair").setLevel(logging.ERROR)
logging.getLogger("numpy").setLevel(logging.ERROR)
logging.getLogger("gensim").setLevel(logging.ERROR)
logging.getLogger("filelock").setLevel(logging.ERROR)
logging.basicConfig(level=logging.INFO)

temp = pathlib.PosixPath
pathlib.PosixPath = pathlib.WindowsPath


@attr.s
class Lazaro(object):
	model_type = attr.ib(type=str, default="crf", validator=attr.validators.in_(["crf", "flair"]))
	model_file = attr.ib(type=str, default=None)
	classifier = attr.ib(validator=attr.validators.instance_of(LazaroClassifier))

	@classifier.default
	def get_classifier(self) -> LazaroClassifier:
		"""
		Sets the classifier model according to the model_type attribute (flair/crf)
		:return: a LazaroClassifier (FlairClassifier or CRFClassifier)
		"""
		if self.model_type == 'flair':
			if self.model_file:
				return FlairClassifier(model_file=self.model_file)
			return FlairClassifier()
		elif self.model_type == 'crf':
			if self.model_file:
				return CRFClassifier(model_file=self.model_file)
			return CRFClassifier()

	def analyze(self, text: str) -> LazaroOutput:
		return self.classifier.predict(text)
