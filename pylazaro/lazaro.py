import logging
import os
import pathlib

import attr

from pylazaro.classifiers import (
    CRFClassifier,
    FlairClassifier,
    LazaroClassifier,
    TransformersClassifier,
)
from pylazaro.output import LazaroOutput

logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("flair").setLevel(logging.ERROR)
logging.getLogger("numpy").setLevel(logging.ERROR)
logging.getLogger("gensim").setLevel(logging.ERROR)
logging.getLogger("filelock").setLevel(logging.ERROR)
logging.basicConfig(level=logging.INFO)

if os.name == "nt":
    temp = pathlib.PosixPath
    pathlib.PosixPath = pathlib.WindowsPath


@attr.s
class Lazaro(object):
    """The tagger object that will label words as being borrowings or not

    Attributes:
            model_type (str, optional): type of model.
            model_file (str, optional): model to be used.
            _classifier (:obj:`pylazaro.classifiers.LazaroClassifier` optional)

    """

    model_type = attr.ib(
        type=str,
        default="bilstm",
        validator=attr.validators.in_(["crf", "bilstm", "transformers"]),
    )
    model_file = attr.ib(type=str, default=None)
    _classifier = attr.ib(validator=attr.validators.instance_of(LazaroClassifier))

    @_classifier.default
    def _get_classifier(self) -> LazaroClassifier:
        """Sets the classifier model according to the model_type attribute (bilstm/transformers/crf).
        This is a private method that is automatically called upon the Lazaro object creation

        Returns:
                `pylazaro.classifiers.LazaroClassifier`: The LazaroClassifier (FlairClassifier or CRFClassifier).

        """

        if self.model_type == "bilstm":
            if self.model_file:
                return FlairClassifier(model_file=self.model_file)
            return FlairClassifier()
        elif self.model_type == "crf":
            if self.model_file:
                return CRFClassifier(model_file=self.model_file)
            return CRFClassifier()
        elif self.model_type == "transformers":
            if self.model_file:
                return TransformersClassifier(model_file=self.model_file)
            return TransformersClassifier()

    def analyze(self, text: str) -> LazaroOutput:
        """The method that calls the tagger on a given text to detect borrowings.

        Args:
                text (str): The text that we want to analyze for borrowings

        Returns:
                `pylazaro.classifiers.LazaroOutput`: The LazaroOutput object that contains the output produced by Lazaro tagger (the output where the automatic detection of borrowings is stored)

        Example:
                .. code-block:: python

                        >>> from pylazaro import Lazaro
                        >>> tagger = Lazaro()
                        >>> text = "Fue un look sencillo. Se celebra un festival de 'anime'."
                        >>> output = tagger.analyze(text)
                        >>> output.borrowings()
                        [('look', 'ENG'), ('anime', 'OTHER')]`

        """

        return self._classifier.predict(text)
