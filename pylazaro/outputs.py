from typing import List, Tuple
from flair.data import Sentence
import attr
from attr import attrs
from collections import Counter
from abc import ABC, abstractmethod


class LazaroOutput(ABC):
	@abstractmethod
	def borrowings(self) -> List[Tuple[str, str]]:
		"""
		Returns a list with the borrowings found in the text with their corresponding tag
		Ex: [('look', 'ENG'), ('online', 'ENG'), ('prime time', 'ENG')]
		"""
		raise NotImplementedError

	@abstractmethod
	def anglicisms(self) -> List[Tuple[str, str]]:
		"""
		Returns a list with the borrowings found in the text with their corresponding tag
		Ex: [('look', 'ENG'), ('online', 'ENG'), ('prime time', 'ENG')]
		"""
		raise NotImplementedError

	def other_borrowings(self) -> List[Tuple[str, str]]:
		"""
		Returns a list with the borrowings found in the text with their corresponding tag
		Ex: [('anime', 'OTHER'), ('manga', 'OTHER')]
		"""
		raise NotImplementedError

	@abstractmethod
	def count(self) -> Counter:
		raise NotImplementedError

	@abstractmethod
	def tag_per_token(self) -> List[Tuple[str, str]]:
		"""
		Returns the input text as a list with one tag per token
		Ex: [('Fue', 'O'), ('un', 'O'), ('look', 'B-ENG'), ('sencillo', 'O')]
		"""
		raise NotImplementedError


@attrs
class LazaroOutputCRF(LazaroOutput):
	output = attr.ib()

	def borrowings(self):
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
		self.output = Sentence(text)

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
