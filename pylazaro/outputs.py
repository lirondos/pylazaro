from typing import List, Tuple
from flair.data import Sentence
import attr
from attr import attrs
from collections import Counter
from abc import ABC, abstractmethod


class LazaroOutput(ABC):
	@abstractmethod
	def get_borrowings(self) -> List[Tuple[str, str]]:
		"""
		Returns a list with the borrowings found in the text with their corresponding tag
		Ex: [('look', 'ENG'), ('online', 'ENG'), ('prime time', 'ENG')]
		"""
		raise NotImplementedError

	@abstractmethod
	def get_anglicisms(self) -> List[Tuple[str, str]]:
		"""
		Returns a list with the borrowings found in the text with their corresponding tag
		Ex: [('look', 'ENG'), ('online', 'ENG'), ('prime time', 'ENG')]
		"""
		raise NotImplementedError

	def get_other_borrowings(self) -> List[Tuple[str, str]]:
		"""
		Returns a list with the borrowings found in the text with their corresponding tag
		Ex: [('anime', 'OTHER'), ('manga', 'OTHER')]
		"""
		raise NotImplementedError

	@abstractmethod
	def get_borrowings_counter(self) -> Counter:
		raise NotImplementedError

	@abstractmethod
	def get_tuples(self) -> List[Tuple[str, str]]:
		"""
		Returns the input text as a list with one tag per token
		Ex: [('Fue', 'O'), ('un', 'O'), ('look', 'B-ENG'), ('sencillo', 'O')]
		"""
		raise NotImplementedError


@attrs
class LazaroOutputCRF(LazaroOutput):
	output = attr.ib()

	def get_borrowings(self):
		return [(ent.text, ent.label_) for ent in self.output.ents]

	def get_anglicisms(self):
		return [(ent.text, ent.label_) for ent in self.output.ents if ent.label_=="ENG"]

	def get_other_borrowings(self):
		return [(ent.text, ent.label_) for ent in self.output.ents if ent.label_=="OTHER"]

	def get_borrowings_counter(self):
		return Counter(self.get_borrowings())

	def get_tuples(self):
		return [(token.text, tag) for token, tag in zip(list(self.output), self.output.user_data[
			"tags"])]


class LazaroOutputFlair(LazaroOutput):
	def __init__(self, text):
		self.output = Sentence(text)

	def get_borrowings(self):
		return [(span.text, span.get_labels()[0].value) for span in self.output.get_spans()]

	def get_anglicisms(self):
		return [(span.text, span.get_labels()[0].value) for span in self.output.get_spans() if
		        span.get_labels()[0].value == "ENG"]

	def get_other_borrowings(self):
		return [(span.text, span.get_labels()[0].value) for span in self.output.get_spans() if
		        span.get_labels()[0].value == "OTHER"]

	def get_borrowings_counter(self):
		return Counter(self.get_borrowings())

	def get_tagged_string(self):
		return self.output.to_tagged_string()

	def get_tuples(self):
		return [(token.text, token.get_labels()[0].value) for token in self.output]
