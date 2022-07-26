import os
import pathlib
from typing import List, Tuple, Dict
from collections import defaultdict
from .token import Token


import attr

LANGUAGE_CODES = defaultdict(lambda: 'other')
LANGUAGE_CODES["ENG"] = "en"

if os.name == "nt":
    temp = pathlib.PosixPath
    pathlib.PosixPath = pathlib.WindowsPath


@attr.s
class Borrowing(object):
    """The Borrowing object: a span of text that represents a borrowing.
    A borrowing will be made of several tokens and have a context assigned

    Attributes:
            tokens (List[`pylazaro.token.Token`]): list of Tokens that form the Borrowing
            language (str): language (the @property language follows iso codes)
            start_pos (int): start position of the borrowing spans (refers to context_tokens)
            end_pos (int): end position of the borrowing spans (refers context tokens)
            context_tokens (List[`pylazaro.token.Token`]): list of Tokens that form the sentence
    """
    tokens = attr.ib(type=List[Token])
    start_pos = attr.ib(type=int)
    end_pos = attr.ib(type=int)
    language = attr.ib(type=str)
    context_tokens = attr.ib(type=List[Token], default=None, repr=False)


    @property
    def length(self) -> int:
        """

        Returns: token length of the borrowings (1 token borrowing, 2 token borrowings, etc)

        """
        return len(self.tokens)

    @property
    def text(self) -> str:
        """

        Returns: The borrowing as a string of text

        """

        return " ".join([token.text for token in self.tokens])

    @property
    def context_text(self) -> str:
        """
        Returns:
                The context of the borrowing as a string of text
        """

        return " ".join([token.text for token in self.context_tokens])

    @classmethod
    def from_span(cls, tokens: List[Token], label: str, start_pos: int,
                  end_pos: int, output_tokens: List[Token]):
        return cls(tokens, start_pos, end_pos, language_to_iso(label),
                  output_tokens)

    def is_anglicism(self) -> bool:
        """

        Returns: Whether the borrowing is an anglicism

        """
        return self.language == "en"

    def is_other(self) -> bool:
        """

        Returns: Whether the borrowing is of type other (not an anglicism)

        """
        return self.language == "other"

    def has_quotation(self) -> bool:
        """

        Returns: Whether the given borrowing is surrounded by quotation marks in the context

        """
        if self.start_pos == 0 or self.end_pos == len(self.context_tokens):
            # if borrowing is sentence initial or end of sentence, no quot marks possible
            return False
        prev_token = self.context_tokens[self.start_pos - 1]
        following_token = self.context_tokens[self.end_pos]
        return prev_token.is_quotation() and following_token.is_quotation()




    def to_tuple(self) -> Tuple[str, str]:
        """

        Returns:
            The borrowing formatted as a tuple of form (borrowing, language)

        """

        return (self.text, self.language)


    def to_dict(self) -> Dict:
        """

        Returns:
                The borrowing formatted as a dict

        """

        return {"borrowing": self.text, "language": self.language, "start_pos": self.start_pos,
                "end_pos": self.end_pos}


def language_to_iso(lang) -> str:
    """

    Returns: language of the borrowing as 2 letter iso code (or other)

    """
    return LANGUAGE_CODES[lang.upper()]