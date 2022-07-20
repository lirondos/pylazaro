import attr
from typing import List, Tuple, Dict



from pylazaro.utils import fuse_spans
from .borrowing import Borrowing
from .token import Token

@attr.s
class LazaroOutput():
    """The object that stores the output produced by Lazaro tagger

    Attributes:
            tokens (obj): a list of Tokens with the tokenized sentence
            spans (obj): a list of Borrowings (spans) contained in the output.
                         Each Borrowing is made of Tokens

    """
    tokens = attr.ib(type=List[Token])
    spans = attr.ib(type=List[Borrowing])

    @property
    def text(self) -> str:
        return " ".join([token.text for token in self.tokens])

    @classmethod
    def from_CRF(cls, crf_output):
        tokens = [Token(token.text, tag, i, None) for i, (token, tag) in enumerate(zip(list(
            crf_output), crf_output.user_data["tags"]))]
        spans = fuse_spans(tokens)
        return cls(tokens, spans)


    @classmethod
    def from_Flair(cls, flair_output):
        def align_labels() -> List[Token]:
            aligned_labels = []
            for i, token in enumerate(flair_output.tokens):
                if not token.labels:
                    aligned_labels.append(Token(token.text, "O", i, None))
                else:
                    aligned_labels.append(Token(token.text, token.labels[0].value, i, token.score))
            return aligned_labels

        tokens = align_labels()
        spans = fuse_spans(tokens)
        return cls(tokens, spans)

    @classmethod
    def from_Transformers(cls, transformers_output):
        def align_labels() -> List[Token]:
            i = 0
            new_output = []
            half_boiled_token = ""
            half_boiled_label = ""
            for tok, label in transformers_output:
                if tok == "[CLS]" or tok == "[SEP]":
                    if half_boiled_token.strip():
                        new_output.append(Token(half_boiled_token, half_boiled_label, i))
                        half_boiled_token = ""
                        half_boiled_label = ""
                        i = i + 1
                    continue
                if tok.startswith("##"):
                    half_boiled_token = half_boiled_token + tok[2:]
                else:
                    if half_boiled_token.strip():
                        new_output.append(Token(half_boiled_token, half_boiled_label, i))
                        i = i + 1
                    half_boiled_token = tok
                    half_boiled_label = label
            return new_output

        tokens = align_labels()
        spans = fuse_spans(tokens)
        return cls(tokens, spans)

    @property
    def borrowings(self) -> List[Borrowing]:
        """Returns the list of borrowings found in the text

                Returns:
                        `List[Borrowing]`: List of Borrowings

                Example:
                        .. code-block:: python

                                >>> from pylazaro import Lazaro
                                >>> tagger = Lazaro()
                                >>> text = "Fue un look sencillo. Se celebra un festival de 'anime'."
                                >>> output = tagger.analyze(text)
                                >>> output.borrowings
                                [Borrowing(tokens=[Token(text='look', label='B-ENG', position=2)], start_pos=2, end_pos=3, language='en'), Borrowing(tokens=[Token(text='anime', label='B-OTHER', position=11)], start_pos=11, end_pos=12, language='other')]

                """
        return self.spans

    @property
    def anglicisms(self):
        """Returns the list of borrowings from English (aka anglicisms) found in the text

        Returns:
                `List[Tuple[str, str]]`: List of tuples containing the borrowing and the language tag

        Example:
                .. code-block:: python

                        >>> from pylazaro import Lazaro
                        >>> tagger = Lazaro()
                        >>> text = "Fue un look sencillo. Se celebra un festival de 'anime'."
                        >>> output = tagger.analyze(text)
                        >>> output.anglicisms
                        [Borrowing(tokens=[Token(text='look', label='B-ENG', position=2)], start_pos=2, end_pos=3, language='en')]
        """
        return [
            bor for bor in self.spans if bor.is_anglicism()
        ]

    @property
    def other_borrowings(self):
        """Returns the list of borrowings from languages other than English found in the text

        Returns:
                `List[Tuple[str, str]]`: List of tuples containing the borrowing and the language tag

        Example:
                .. code-block:: python

                        >>> from pylazaro import Lazaro
                        >>> tagger = Lazaro()
                        >>> text = "Fue un look sencillo. Se celebra un festival de 'anime'."
                        >>> output = tagger.analyze(text)
                        >>> output.other_borrowings
                        [Borrowing(tokens=[Token(text='anime', label='B-OTHER', position=11)], start_pos=11, end_pos=12, language='other')]
        """
        return [
            bor for bor in self.spans if bor.is_other()
        ]

    def borrowings_to_tuple(self) -> List[Tuple[str, str]]:
        """Returns the list of borrowings found in the text

                Returns:
                        `List[Borrowing]`: List of Borrowings

                Example:
                        .. code-block:: python

                                >>> from pylazaro import Lazaro
                                >>> tagger = Lazaro()
                                >>> text = "Fue un look sencillo. Se celebra un festival de 'anime'."
                                >>> output = tagger.analyze(text)
                                >>> output.borrowings_to_tuple()
                                [('look', 'en'), ('anime', 'other')]

                """
        return [bor.to_tuple() for bor in self.borrowings]

    def anglicisms_to_tuple(self) -> List[Tuple[str, str]]:
        """Returns the list of borrowings from English (aka anglicisms) found in the text

        Returns:
                `List[Tuple[str, str]]`: List of tuples containing the borrowing and the language tag

        Example:
                .. code-block:: python

                        >>> from pylazaro import Lazaro
                        >>> tagger = Lazaro()
                        >>> text = "Fue un look sencillo. Se celebra un festival de 'anime'."
                        >>> output = tagger.analyze(text)
                        >>> output.anglicisms_to_tuple()
                        [('look', 'en')]
        """
        return [bor.to_tuple() for bor in self.anglicisms]


    def other_to_tuple(self) -> List[Tuple[str, str]]:
        """Returns the list of borrowings from languages other than English found in the text

        Returns:
                `List[Tuple[str, str]]`: List of tuples containing the borrowing and the language tag

        Example:
                .. code-block:: python

                        >>> from pylazaro import Lazaro
                        >>> tagger = Lazaro()
                        >>> text = "Fue un look sencillo. Se celebra un festival de 'anime'."
                        >>> output = tagger.analyze(text)
                        >>> output.other_to_tuple()
                        [('anime', 'other')]
        """
        return [bor.to_tuple() for bor in self.other_borrowings]

    def borrowings_to_dict(self) -> List[Dict]:
        """Returns the list of borrowings found in the text

                Returns:
                        `List[Borrowing]`: List of Borrowings

                Example:
                        .. code-block:: python

                                >>> from pylazaro import Lazaro
                                >>> tagger = Lazaro()
                                >>> text = "Fue un look sencillo. Se celebra un festival de 'anime'."
                                >>> output = tagger.analyze(text)
                                >>> output.borrowings_to_dict()
                                [{'borrowing': 'look', 'language': 'en', 'start_pos': 2, 'end_pos': 3}, {'borrowing': 'anime', 'language': 'other', 'start_pos': 11, 'end_pos': 12}]`

                """
        return [bor.to_dict() for bor in self.borrowings]

    def anglicisms_to_dict(self) -> List[Dict]:
        """Returns the list of borrowings from English (aka anglicisms) found in the text

        Returns:
                `List[Tuple[str, str]]`: List of tuples containing the borrowing and the language tag

        Example:
                .. code-block:: python

                        >>> from pylazaro import Lazaro
                        >>> tagger = Lazaro()
                        >>> text = "Fue un look sencillo. Se celebra un festival de 'anime'."
                        >>> output = tagger.analyze(text)
                        >>> output.anglicisms_to_dict()
                        [{'borrowing': 'look', 'language': 'en', 'start_pos': 2, 'end_pos': 3}]
        """
        return [bor.to_dict() for bor in self.anglicisms]


    def other_to_dict(self) -> List[Dict]:
        """Returns the list of borrowings from languages other than English found in the text

        Returns:
                `List[Tuple[str, str]]`: List of tuples containing the borrowing and the language tag

        Example:
                .. code-block:: python

                        >>> from pylazaro import Lazaro
                        >>> tagger = Lazaro()
                        >>> text = "Fue un look sencillo. Se celebra un festival de 'anime'."
                        >>> output = tagger.analyze(text)
                        >>> output.other_to_dict()
                        [{'borrowing': 'anime', 'language': 'other', 'start_pos': 11, 'end_pos': 12}]
        """
        return [bor.to_dict() for bor in self.other_borrowings]


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
                         [('Fue', 'O'), ('un', 'O'), ('look', 'B-ENG'), ('sencillo', 'O'), ('.', 'O'), ('Se', 'O'), ('celebra', 'O'), ('un', 'O'), ('festival', 'O'), ('de', 'O'), ("'", 'O'), ('anime', 'B-OTHER'), ("'", 'O'), ('.', 'O')]
        """
        return [(token.text, token.label) for token in self.tokens]




