from typing import List, Tuple
from flair.data import Sentence
import attr
from attr import attrs
from collections import Counter
from abc import ABC, abstractmethod


class LazaroOutput(ABC):
	"""The object that stores the output produced by Lazaro tagger

		Attributes:
			output (obj): the output

		"""

	@abstractmethod
	def borrowings(self) -> List[Tuple[str, str]]:
		"""Returns the list of borrowings found in the text

		Returns:
			`List[Tuple[str, str]]`: List of tuples containing the borrowing and the language tag

		Example:
			.. code-block:: python

				>>> from pylazaro import Lazaro
				>>> tagger = Lazaro()
				>>> text = "Fue un look sencillo. Se celebra un festival de 'anime'."
				>>> output = tagger.analyze(text)
				>>> output.borrowings()
				[('look', 'ENG'), ('anime', 'OTHER')]`

		"""
		raise NotImplementedError

	@abstractmethod
	def anglicisms(self) -> List[Tuple[str, str]]:
		"""Returns the list of borrowings from English (aka anglicisms) found in the text

		Returns:
			`List[Tuple[str, str]]`: List of tuples containing the borrowing and the language tag

		Example:
			.. code-block:: python

				>>> from pylazaro import Lazaro
				>>> tagger = Lazaro()
				>>> text = "Fue un look sencillo. Se celebra un festival de 'anime'."
				>>> output = tagger.analyze(text)
				>>> output.anglicisms()
				[('look', 'ENG')]
		"""
		raise NotImplementedError

	@abstractmethod
	def other_borrowings(self) -> List[Tuple[str, str]]:
		"""Returns the list of borrowings from languages other than English found in the text

		Returns:
			`List[Tuple[str, str]]`: List of tuples containing the borrowing and the language tag

		Example:
			.. code-block:: python

				>>> from pylazaro import Lazaro
				>>> tagger = Lazaro()
				>>> text = "Fue un look sencillo. Se celebra un festival de 'anime'."
				>>> output = tagger.analyze(text)
				>>> output.other_borrowings()
				[('anime', 'OTHER')]
		"""
		raise NotImplementedError

	@abstractmethod
	def count(self) -> Counter:
		"""A method that counts over the list of borrowings found in the text

		Returns:
			`collections.Counter`: Counter over the list of borrowings

		Example:
			.. code-block:: python

				>>> from pylazaro import Lazaro
				>>> tagger = Lazaro()
				>>> text = "Fue un look sencillo. Se celebra un festival de 'anime'."
				>>> output = tagger.analyze(text)
				>>> output.count()
				Counter({('look', 'ENG'): 1, ('anime', 'OTHER'): 1})
		"""

		raise NotImplementedError

	@abstractmethod
	def tag_per_token(self) -> List[Tuple[str, str]]:
		"""Returns the input text as a list with one tag per token

		Returns:
			`List[Tuple[str, str]]`: List of tuples containing the word and its tag

		Example:
			.. code-block:: python

				>>> from pylazaro import Lazaro
				>>> tagger = Lazaro()
				>>> text = "Fue un look sencillo. Se celebra un festival de 'anime'."
				>>> output = tagger.analyze(text)
				>>> output.tag_per_token()
				 [('Fue', 'O'), ('un', 'O'), ('look', 'B-ENG'), ('sencillo', 'O')]
		"""
		raise NotImplementedError


@attrs
class LazaroOutputCRF(LazaroOutput):
	output = attr.ib()

	def borrowings(self):
		"""

		Returns:

		"""
		return [(ent.text, ent.label_) for ent in self.output.ents]

	def anglicisms(self):
		return [(ent.text, ent.label_) for ent in self.output.ents if ent.label_=="ENG"]

	def other_borrowings(self):
		return [(ent.text, ent.label_) for ent in self.output.ents if ent.label_=="OTHER"]

	def count(self):
		return Counter(self.borrowings())

	def tag_per_token(self):
		return [(token.text, tag) for token, tag in zip(list(self.output), self.output.user_data[
			"tags"])]


class LazaroOutputFlair(LazaroOutput):
	def __init__(self, text):
		self.output = text

	def borrowings(self):
		return [(span.text, span.get_labels()[0].value) for span in self.output.get_spans()]

	def anglicisms(self):
		return [(span.text, span.get_labels()[0].value) for span in self.output.get_spans() if
				span.get_labels()[0].value == "ENG"]

	def other_borrowings(self):
		return [(span.text, span.get_labels()[0].value) for span in self.output.get_spans() if
				span.get_labels()[0].value == "OTHER"]

	def count(self):
		return Counter(self.borrowings())

	def tagged_string(self):
		return self.output.to_tagged_string()

	def tag_per_token(self):
		return [(token.text, token.get_labels()[0].value) for token in self.output]


class LazaroOutputTransformers(LazaroOutput):
	def __init__(self, output):
		self.output_tokens = self.align_labels(output)
		self.output_spans = self.fuse_spans()

	def fuse_spans(self):
		new_output = []
		half_boiled_label = None
		half_boiled_token = []

		for token, label in self.output_tokens:
			if label == "O":
				if half_boiled_label:
					new_output.append((" ".join(half_boiled_token), half_boiled_label))
					half_boiled_label = None
					half_boiled_token = []
				new_output.append((token, label))
			if label.startswith("B"):
				if half_boiled_label:
					new_output.append((" ".join(half_boiled_token), half_boiled_label))
				half_boiled_label = label.split("-")[1]
				half_boiled_token = [token]
			if label.startswith("I"):
				half_boiled_label = label.split("-")[1]
				half_boiled_token.append(token)
		if half_boiled_label:
			new_output.append((" ".join(half_boiled_token), half_boiled_label))
		return new_output

	def align_labels(self, output):
		new_output = []
		suffix = ""
		for tok, label in output[::-1]:
			if tok == '[CLS]' or tok == '[SEP]':
				continue
			if tok.startswith("##"):
				suffix = tok[2:] + suffix  
			else:
				new_output.insert(0, (tok+suffix, label))
				suffix = ""
		return new_output

	def borrowings(self):
		return [(token, label) for (token, label) in self.output_spans if label != "O"]

	def anglicisms(self):
		return [(token, label) for (token, label) in self.output_spans if label == "ENG"]

	def other_borrowings(self):
		return [(token, label) for (token, label) in self.output_spans if label == "OTHER"]

	def count(self):
		return Counter(self.borrowings())

	def tag_per_token(self):
		return self.output_tokens
