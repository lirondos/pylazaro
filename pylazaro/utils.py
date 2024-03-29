import bz2
import logging
import os
import re
import string
from abc import ABC, abstractmethod
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
import pycrfsuite
import regex
import requests
from quickvec import SqliteWordEmbedding
from spacy.tokens import Doc, Span, Token
from tqdm import tqdm
from collections import OrderedDict

from .constants import *
from .borrowing import Borrowing
from .token import Token

UPPERCASE_RE = regex.compile(r"[\p{Lu}\p{Lt}]")
LOWERCASE_RE = regex.compile(r"\p{Ll}")
DIGIT_RE = re.compile(r"\d")

PUNC_REPEAT_RE = regex.compile(r"\p{P}+")

PATH_TO_DICT_ES = "lexicon/es.txt"
PATH_TO_DICT_EN = "lexicon/en.txt"
PATH_TO_LEXICON_ES = "lexicon/spanish_lexicon.csv"

# VECTORS_FOLDER = "embeddings_db/"
VECTORS_PATH = {
    "fasttext_SUC": "embeddings-l-model.vec",
    "fasttext_wiki": "wiki.es.vec",
    "w2v_SBWC": "SBW-vectors-300-min5.txt",
    "glove_SBWC": "glove-sbwc.i25.vec",
    "fasttext_SBWC": "fasttext-sbwc.3.6.e20.vec",
    "fasttext_crawl": "cc.es.300.vec",
}


class FeatureExtractor(ABC):
    @abstractmethod
    def extract(
        self,
        token: str,
        current_idx: int,
        relative_idx: int,
        tokens: Sequence[str],
        features: Dict[str, float],
    ) -> None:
        raise NotImplementedError


class EntityEncoder(ABC):
    @abstractmethod
    def encode(self, tokens: Sequence[Token]) -> List[str]:
        raise NotImplementedError


class WindowedTokenFeatureExtractor:
    def __init__(
        self, feature_extractors: Sequence[FeatureExtractor], window_size: int
    ):
        self.extractors = feature_extractors
        self.window_size = window_size

    def extract(self, tokens: Sequence[str]) -> List[Dict[str, float]]:
        featurized = []
        for i in range(0, len(tokens)):
            dict_feat = dict()
            token = tokens[i]
            for extractor in self.extractors:
                extractor.extract(token, i, 0, tokens, dict_feat)
                for j in range(1, self.window_size + 1):
                    if i - j >= 0:
                        extractor.extract(tokens[i - j], i - j, -j, tokens, dict_feat)
                    if i + j < len(tokens):
                        extractor.extract(tokens[i + j], i + j, j, tokens, dict_feat)
            featurized.append(dict_feat)
        return featurized


class CRFsuiteEntityRecognizer_CoNLL:
    def __init__(self, feature_extractor: WindowedTokenFeatureExtractor) -> None:
        self.feature_extractor = feature_extractor
        # self._encoder = encoder

    """
    @property
    def encoder(self) -> EntityEncoder:
        return self._encoder

    def set_encoder(self, encoder):
        self._encoder = encoder
    """

    def train(
        self, corpus, algorithm: str, params: dict, path: str, verbose=False
    ) -> None:
        trainer = pycrfsuite.Trainer(algorithm, verbose=verbose)
        trainer.set_params(params)
        for tokens, labels in corpus:
            # tokens = [token for token in doc if token.text.strip()]
            # print(tokens)
            features = self.feature_extractor.extract(tokens)
            # for feature in features:
            # print(feature)
            # features = self.feature_extractor.extract([token.text for token in tokens])
            # encoded_labels = self._encoder.encode(tokens)
            # print(list(zip(tokens, encoded_labels)))
            try:
                trainer.append(features, labels)
            except:
                print(tokens)
                print(labels)
                print(len(tokens))
                print(len(labels))
        trainer.train(path)
        self.tagger = pycrfsuite.Tagger()
        self.tagger.open(path)

    def __call__(self, doc):
        tokens = list(doc)
        if not self.tagger:
            raise ValueError("train() method should be called first!")
        # tokens = doc[0]
        tags = self.predict_labels(tokens)
        return tags

    def predict_labels(self, doc) -> List[str]:
        tokens = list(doc)
        features = self.feature_extractor.extract(tokens)
        # features = self.feature_extractor.extract([str(token) for token in tokens])
        tags = self.tagger.tag(features)
        return tags


class CRFsuiteEntityRecognizer:
    def __init__(
        self, feature_extractor: WindowedTokenFeatureExtractor, encoder: EntityEncoder
    ) -> None:
        self.feature_extractor = feature_extractor
        self._encoder = encoder

    @property
    def encoder(self) -> EntityEncoder:
        return self._encoder

    def set_encoder(self, encoder):
        self._encoder = encoder

    def train(
        self,
        docs: Iterable[Doc],
        algorithm: str,
        params: dict,
        path: str,
        verbose=False,
    ) -> None:
        trainer = pycrfsuite.Trainer(algorithm, verbose=verbose)
        trainer.set_params(params)
        for doc in docs:
            # print(doc)
            for sent in doc.sents:
                tokens = list(sent)
                features = self.feature_extractor.extract(tokens)
                # for feature in features:
                # print(feature)
                # features = self.feature_extractor.extract([token.text for token in tokens])
                encoded_labels = self._encoder.encode(tokens)
                # print(list(zip(tokens, encoded_labels)))
                trainer.append(features, encoded_labels)
        trainer.train(path)
        self.tagger = pycrfsuite.Tagger()
        self.tagger.open(path)

    def __call__(self, doc: Doc) -> Doc:
        if not self.tagger:
            raise ValueError("train() method should be called first!")
        entities = list()
        # print(doc.ents)
        for sent in doc.sents:
            tokens = list(sent)
            tags = self.predict_labels(tokens)
            entities.append(decode_bilou(tags, tokens, doc))
        doc.ents = [item for sublist in entities for item in sublist]
        # print(doc.ents)
        return doc

    def predict_labels(self, tokens: Sequence[str]) -> List[str]:
        features = self.feature_extractor.extract(tokens)
        # features = self.feature_extractor.extract([str(token) for token in tokens])
        tags = self.tagger.tag(features)
        return tags


class BILOUEncoder(EntityEncoder):
    def encode(self, tokens: Sequence[Token]) -> List[str]:
        encoded = []
        labels = [token.ent_iob_ + "-" + token.ent_type_ for token in tokens]
        spans = decode_bilou(labels, tokens, tokens[0].doc)
        for span in spans:
            if self.is_unitary(span):
                encoded.append("U-" + span.label_)
            elif self.is_empty(span):
                for i in range(span.start, span.end):
                    encoded.append("O")
            else:
                encoded.append("B-" + span.label_)
                for i in range(span.start + 1, span.end - 1):
                    encoded.append("I-" + span.label_)
                encoded.append("L-" + span.label_)
        return encoded

    def is_unitary(self, span):
        return span.end == span.start + 1 and span.label > 0

    def is_empty(self, span):
        return span.label == 0


class BMESEncoder(EntityEncoder):
    def encode(self, tokens: Sequence[Token]) -> List[str]:
        encoded = []
        labels = [token.ent_iob_ + "-" + token.ent_type_ for token in tokens]
        spans = decode_bilou(labels, tokens, tokens[0].doc)
        for span in spans:
            if self.is_unitary(span):
                encoded.append("S-" + span.label_)
            elif self.is_empty(span):
                for i in range(span.start, span.end):
                    encoded.append("O")
            else:
                encoded.append("B-" + span.label_)
                for i in range(span.start + 1, span.end - 1):
                    encoded.append("M-" + span.label_)
                encoded.append("E-" + span.label_)
        return encoded

    def is_unitary(self, span):
        return span.end == span.start + 1 and span.label > 0

    def is_empty(self, span):
        return span.label == 0


class BIOESEncoder(EntityEncoder):
    def encode(self, tokens: Sequence[Token]) -> List[str]:
        encoded = []
        labels = [token.ent_iob_ + "-" + token.ent_type_ for token in tokens]
        spans = decode_bilou(labels, tokens, tokens[0].doc)
        for span in spans:
            if self.is_unitary(span):
                encoded.append("S-" + span.label_)
            elif self.is_empty(span):
                for i in range(span.start, span.end):
                    encoded.append("O")
            else:
                encoded.append("B-" + span.label_)
                for i in range(span.start + 1, span.end - 1):
                    encoded.append("I-" + span.label_)
                encoded.append("E-" + span.label_)
        return encoded

    def is_unitary(self, span):
        return span.end == span.start + 1 and span.label > 0

    def is_empty(self, span):
        return span.label == 0


class BIOEncoder(EntityEncoder):
    def encode(self, tokens: Sequence[Token]) -> List[str]:
        labels = [token.ent_iob_ + "-" + token.ent_type_ for token in tokens]
        spans = decode_bilou(labels, tokens, tokens[0].doc)
        encoded = []
        for span in spans:
            if self.is_empty(span):
                for i in range(span.start, span.end):
                    encoded.append("O")
            else:
                encoded.append("B-" + span.label_)
                for i in range(span.start + 1, span.end):
                    encoded.append("I-" + span.label_)
        return encoded

    def is_empty(self, span):
        return span.label == 0


class IOEncoder(EntityEncoder):
    def encode(self, tokens: Sequence[Token]) -> List[str]:
        labels = [token.ent_iob_ + "-" + token.ent_type_ for token in tokens]
        spans = decode_bilou(labels, tokens, tokens[0].doc)
        encoded = []
        for span in spans:
            if self.is_empty(span):
                for i in range(span.start, span.end):
                    encoded.append("O")
            else:
                for i in range(span.start, span.end):
                    encoded.append("I-" + span.label_)
        return encoded

    def is_empty(self, span):
        return span.label == 0


def decode_bilou(
    labels: Sequence[str], tokens: Sequence[Token], doc: Doc
) -> List[Span]:
    spans = []
    tag_interruptus = False
    span_type = None
    i = 0
    initial = None
    while i < len(labels):
        label = labels[i]
        if label == "O":  # The current label is O
            if (
                tag_interruptus
            ):  # If we were in the middle of a span, we create it and append it
                spans.append(Span(doc, tokens[initial].i, tokens[i].i, span_type))
            tag_interruptus = False  # We are no longer in the middle of a tag
        else:  # The current label is B I L or U
            label_type = label.split("-")[1]  # We get the type (PER, MISC, etc)
            if tag_interruptus:  # if we were in the middle of a tag
                if label_type != span_type:  # and the types dont match
                    spans.append(
                        Span(doc, tokens[initial].i, tokens[i].i, span_type)
                    )  # we close the previous span and append it
                    span_type = label_type  # we are now in the middle of a new span
                    initial = i
            else:  # we were not in the middle of a span
                initial = i  # initial position will be the current position
                tag_interruptus = True  # we are now in the middle of a span
                span_type = label_type
        i = i + 1
    if (
        tag_interruptus
    ):  # this covers entities at the end of the sentence (we left a tag_interruptus at the end of the list)
        spans.append(Span(doc, tokens[initial].i, tokens[i - 1].i + 1, span_type))
    return spans


class BiasFeature(FeatureExtractor):
    def extract(
        self,
        token: str,
        current_idx: int,
        relative_idx: int,
        tokens: Sequence[str],
        features: Dict[str, float],
    ):
        if relative_idx == 0:
            features["bias"] = 1.0


class TokenFeature(FeatureExtractor):
    def extract(
        self,
        token: str,
        current_idx: int,
        relative_idx: int,
        tokens: Sequence[str],
        features: Dict[str, float],
    ):
        features["tok[" + str(relative_idx) + "]=" + token.text] = 1.0


class UppercaseFeature(FeatureExtractor):
    def extract(
        self,
        token: str,
        current_idx: int,
        relative_idx: int,
        tokens: Sequence[str],
        features: Dict[str, float],
    ):
        if token.text.isupper():
            features["uppercase[" + str(relative_idx) + "]"] = 1.0


class HasApostrophe(FeatureExtractor):
    def extract(
        self,
        token: str,
        current_idx: int,
        relative_idx: int,
        tokens: Sequence[str],
        features: Dict[str, float],
    ):
        if token.endswith("'s"):
            features["has_apostrophe[" + str(relative_idx) + "]"] = 1.0


class IsShortWord(FeatureExtractor):
    def extract(
        self,
        token: str,
        current_idx: int,
        relative_idx: int,
        tokens: Sequence[str],
        features: Dict[str, float],
    ):
        if len(token) < 4:
            features["is_short[" + str(relative_idx) + "]"] = 1.0


class WordEnding(FeatureExtractor):
    def extract(
        self,
        token: str,
        current_idx: int,
        relative_idx: int,
        tokens: Sequence[str],
        features: Dict[str, float],
    ):
        if relative_idx == 0:
            features["ending[" + str(relative_idx) + "]=" + token.text[-3:]] = 1.0


class TitlecaseFeature(FeatureExtractor):
    def extract(
        self,
        token: str,
        current_idx: int,
        relative_idx: int,
        tokens: Sequence[str],
        features: Dict[str, float],
    ):
        if token.text.istitle():
            features["titlecase[" + str(relative_idx) + "]"] = 1.0


class URLFeature(FeatureExtractor):
    def extract(
        self,
        token: str,
        current_idx: int,
        relative_idx: int,
        tokens: Sequence[str],
        features: Dict[str, float],
    ):
        if relative_idx == 0 and token.like_url:
            features["URL[" + str(relative_idx) + "]"] = 1.0


class EmailFeature(FeatureExtractor):
    def extract(
        self,
        token: str,
        current_idx: int,
        relative_idx: int,
        tokens: Sequence[str],
        features: Dict[str, float],
    ):
        if relative_idx == 0 and token.like_email:
            features["email[" + str(relative_idx) + "]"] = 1.0


class TwitterFeature(FeatureExtractor):
    def extract(
        self,
        token: str,
        current_idx: int,
        relative_idx: int,
        tokens: Sequence[str],
        features: Dict[str, float],
    ):
        if relative_idx == 0 and (token.text[0] == "#" or token.text[0] == "@"):
            features["twitter[" + str(relative_idx) + "]"] = 1.0


class InitialTitlecaseFeature(FeatureExtractor):
    def extract(
        self,
        token: str,
        current_idx: int,
        relative_idx: int,
        tokens: Sequence[str],
        features: Dict[str, float],
    ):
        if (token.text.istitle() and current_idx == 0) or (
            token.is_title and token.i == 1 and tokens[0].is_punct
        ):
            features["initialtitlecase[" + str(relative_idx) + "]"] = 1.0


class PunctuationFeature(FeatureExtractor):
    def extract(
        self,
        token: str,
        current_idx: int,
        relative_idx: int,
        tokens: Sequence[str],
        features: Dict[str, float],
    ):
        if PUNC_REPEAT_RE.match(token.text):
            features["punc[" + str(relative_idx) + "]"] = 1.0


class QuotationFeature(FeatureExtractor):
    def extract(
        self,
        token: str,
        current_idx: int,
        relative_idx: int,
        tokens: Sequence[str],
        features: Dict[str, float],
    ):
        if token.text in ['"', "'", "«", "“", "‘"]:
            features["quot[" + str(relative_idx) + "]"] = 1.0


class DigitFeature(FeatureExtractor):
    def extract(
        self,
        token: str,
        current_idx: int,
        relative_idx: int,
        tokens: Sequence[str],
        features: Dict[str, float],
    ):
        if DIGIT_RE.search(token.text):
            features["digit[" + str(relative_idx) + "]"] = 1.0


class AllCapsFeature(FeatureExtractor):
    def extract(
        self,
        token: str,
        current_idx: int,
        relative_idx: int,
        tokens: Sequence[str],
        features: Dict[str, float],
    ):
        if token.text.isupper():
            features["isupper[" + str(relative_idx) + "]"] = 1.0


class LemmaFeature(FeatureExtractor):
    def extract(
        self,
        token: str,
        current_idx: int,
        relative_idx: int,
        tokens: Sequence[str],
        features: Dict[str, float],
    ):
        features["lemma[" + str(relative_idx) + "]=" + token.lemma_] = 1.0


class POStagFeature(FeatureExtractor):
    def extract(
        self,
        token: str,
        current_idx: int,
        relative_idx: int,
        tokens: Sequence[str],
        features: Dict[str, float],
    ):
        if relative_idx == 0:
            features["postag[" + str(relative_idx) + "]=" + token.pos_] = 1.0


class WordShapeFeature(FeatureExtractor):
    def extract(
        self,
        token: str,
        current_idx: int,
        relative_idx: int,
        tokens: Sequence[str],
        features: Dict[str, float],
    ):
        """
        shape = []
        for letter in token:
                if DIGIT_RE.search(letter):
                        shape.append("0")
                elif LOWERCASE_RE.search(letter):
                        shape.append('x')
                elif UPPERCASE_RE.search(letter):
                        shape.append('X')
                else:
                        shape.append(letter)
        """
        features["shape[" + str(relative_idx) + "]=" + token.shape_] = 1.0


class GraphotacticFeature(FeatureExtractor):
    def extract(
        self,
        token: str,
        current_idx: int,
        relative_idx: int,
        tokens: Sequence[str],
        features: Dict[str, float],
    ):
        if relative_idx == 0:
            graphotactic = []
            i = 0
            while i < (len(token.text) - 1):
                letter = token.text[i].lower()
                if letter in "aeiouáéíóúü":
                    graphotactic.append("v")
                elif letter in string.punctuation:
                    graphotactic.append("_")
                else:
                    if (
                        (letter in "tpdfgc" and token.text[i + 1].lower() in "rl")
                        or (letter == "c" and token.text[i + 1].lower() == "h")
                        or (letter == "r" and token.text[i + 1].lower() == "r")
                        or (letter == "l" and token.text[i + 1].lower() == "l")
                        or (letter in "pc" and token.text[i + 1].lower() in "ct")
                        or (letter == "m" and token.text[i + 1].lower() in "pbn")
                        or (letter == "g" and token.text[i + 1].lower() == "n")
                        or (
                            letter in "bx"
                            and token.text[i + 1].lower() not in "aeiouáéíóúü"
                        )
                    ):
                        graphotactic.extend(["b", "r"])
                        i = i + 2
                        continue
                    else:
                        graphotactic.append("c")
                i += 1
            if token.text[-1] in "aeiouáéíóúürslindz":
                graphotactic.append("e")
            else:
                graphotactic.append("c")
            graphotactic_string = "".join(graphotactic)
            features[
                "graphotactic[" + str(relative_idx) + "]=" + graphotactic_string
            ] = 1.0
            if relative_idx == 0 and len(graphotactic_string) >= 2:
                for i in range(-1, len(graphotactic_string) - 1):
                    if i == -1:
                        trigram = (
                            "START" + graphotactic_string[0] + graphotactic_string[1]
                        )
                    if i == len(graphotactic_string) - 2:
                        trigram = (
                            graphotactic_string[len(graphotactic_string) - 2]
                            + graphotactic_string[len(graphotactic_string) - 1]
                            + "END"
                        )
                    if i >= 0 and i < len(graphotactic_string) - 2:
                        trigram = (
                            graphotactic_string[i]
                            + graphotactic_string[i + 1]
                            + graphotactic_string[i + 2]
                        )
                    # print(trigram)
                    features[
                        "trigram_grapho[" + str(relative_idx) + "]=" + trigram
                    ] = 1.0


class TrigramFeature(FeatureExtractor):
    def extract(
        self,
        token: str,
        current_idx: int,
        relative_idx: int,
        tokens: Sequence[str],
        features: Dict[str, float],
    ):
        my_token = token.text
        if relative_idx == 0 and len(my_token) >= 2:
            for i in range(-1, len(my_token) - 1):
                if i == -1:
                    trigram = "START" + my_token[0] + my_token[1]
                if i == len(my_token) - 2:
                    trigram = (
                        my_token[len(my_token) - 2]
                        + my_token[len(my_token) - 1]
                        + "END"
                    )
                if i >= 0 and i < len(my_token) - 2:
                    trigram = my_token[i] + my_token[i + 1] + my_token[i + 2]
                features["trigram[" + str(relative_idx) + "]=" + trigram] = 1.0


class QuatrigramFeature(FeatureExtractor):
    def extract(
        self,
        token: str,
        current_idx: int,
        relative_idx: int,
        tokens: Sequence[str],
        features: Dict[str, float],
    ):
        my_token = token.text
        if relative_idx == 0 and len(my_token) >= 3:
            for i in range(-1, len(my_token) - 1):
                if i == -1:
                    quatrigram = "START" + my_token[0] + my_token[1] + my_token[2]
                if i == len(my_token) - 3:
                    quatrigram = (
                        my_token[len(my_token) - 3]
                        + my_token[len(my_token) - 2]
                        + my_token[len(my_token) - 1]
                        + "END"
                    )
                if i >= 0 and i < len(my_token) - 3:
                    quatrigram = (
                        my_token[i]
                        + my_token[i + 1]
                        + my_token[i + 2]
                        + my_token[i + 3]
                    )
                # print(trigram)
                features["quatrigram[" + str(relative_idx) + "]=" + quatrigram] = 1.0


class SentencePositionFeature(FeatureExtractor):
    def extract(
        self,
        token: str,
        current_idx: int,
        relative_idx: int,
        tokens: Sequence[str],
        features: Dict[str, float],
    ):
        if relative_idx == 0:
            if token.i == 0 or (token.i == 1 and tokens[0].is_punct):
                features["isFirstPosition[" + str(relative_idx) + "]="] = 1.0


# https://github.com/dwyl/english-words/blob/master/words_alpha.txt
class IsInDict(FeatureExtractor):
    def __init__(self, dict_path: str) -> None:
        self.lang = "EN" if dict_path == PATH_TO_DICT_EN else "ES"
        with open(dict_path, mode="r", encoding="utf-8") as f:
            self.lemmas = {word.rstrip("\n") for word in f.readlines()}

    def extract(
        self,
        token: str,
        current_idx: int,
        relative_idx: int,
        tokens: Sequence[str],
        features: Dict[str, float],
    ):
        if relative_idx == 0:
            if token.lemma_.lower() in self.lemmas:
                features["is_in_Dict" + self.lang + "[" + str(relative_idx) + "]"] = 1.0


class HigherEnglishProbability(FeatureExtractor):
    def __init__(self, wordprobabilityEN, wordprobabilityES) -> None:
        self.word_probability_ES = wordprobabilityES
        self.word_probability_EN = wordprobabilityEN

    def extract(
        self,
        token: str,
        current_idx: int,
        relative_idx: int,
        tokens: Sequence[str],
        features: Dict[str, float],
    ):
        if relative_idx == 0:
            prob_es = self.word_probability_ES.get_word_probability(token.text)
            prob_en = self.word_probability_EN.get_word_probability(token.text)
            if prob_en > prob_es:
                features["EN_prob_is_higher[" + str(relative_idx) + "]"] = 1.0


class PerplexityFeature(FeatureExtractor):
    def __init__(self, wordprobabilityES) -> None:
        self.word_probability_ES = wordprobabilityES
        self.perplexity_dict = defaultdict(lambda: list())
        self.perplexities = list()
        for lemma in self.word_probability_ES.lemmas:
            perplexity = self.get_perplexity(lemma)
            self.perplexity_dict[perplexity].append(lemma)
            self.perplexities.append(perplexity)

        self.perplexities = np.array(self.perplexities)
        self.threashold = np.percentile(self.perplexities, 80)
        """
        standard = np.std(self.perplexities)
        mean = np.average(self.perplexities)
        floor = mean - standard
        ceiling = mean + standard
        for perplexity, words in self.perplexity_dict.items():
            if perplexity >= floor and perplexity <= ceiling:
                print(words)
        """

    def get_perplexity(self, lemma):
        l = self.word_probability_ES.get_word_probability(lemma) / len(lemma)
        return np.power(2, l * (-1))

    def extract(
        self,
        token: str,
        current_idx: int,
        relative_idx: int,
        tokens: Sequence[str],
        features: Dict[str, float],
    ):
        perplexity = self.get_perplexity(token.text)
        if perplexity >= self.threashold:
            # print(token)
            # print(perplexity)
            # print(self.threashold)
            features["high_perplexity[" + str(relative_idx) + "]"] = 1.0


# https://raw.githubusercontent.com/julox/spanish_lexicon/master/spanish_lexicon.csv
class WordProbability(FeatureExtractor):
    def __init__(self, dict_path: str) -> None:
        with open(dict_path, mode="r", encoding="utf-8") as f:
            if dict_path == PATH_TO_LEXICON_ES:
                self.lemmas = {line.split(";")[0][1:-1] for line in f.readlines()[1:]}
                self.lang = "ES"
            else:
                self.lemmas = {word.rstrip("\n") for word in f.readlines()}
                self.lang = "EN"
            self.trigram_counts = defaultdict(lambda: defaultdict(int))
            self.bigram_counts = defaultdict(int)
            for lemma in self.lemmas:
                if len(lemma) > 1:
                    self.trigram_counts[("START", lemma[0])][lemma[1]] += 1
                    self.bigram_counts[("START", lemma[0])] += 1
                    self.trigram_counts[(lemma[-2], lemma[-1])]["END"] += 1
                    self.bigram_counts[(lemma[-2], lemma[-1])] += 1
                    for index, letter in enumerate(lemma[1:-1]):
                        self.trigram_counts[(lemma[index - 1], letter)][
                            lemma[index + 1]
                        ] += 1
                        self.bigram_counts[(lemma[index - 1], letter)] += 1
                    else:
                        self.trigram_counts[("START", lemma[0])]["END"] += 1
                        self.bigram_counts[("START", lemma[0])] += 1

    def get_trigram_prob(self, char0, char1, char2):
        if self.bigram_counts[(char0, char1)] == 0:
            return 1e-10
        return np.log2(
            self.trigram_counts[(char0, char1)][char2]
            / self.bigram_counts[(char0, char1)]
        )

    def get_word_probability(self, word):
        if len(word) > 1:
            probability = self.get_trigram_prob("START", word[0], word[1])
            probability = probability + self.get_trigram_prob(word[-2], word[-1], "END")
            for index, letter in enumerate(word[1:-1]):
                probability = probability + self.get_trigram_prob(
                    word[index - 1], letter, word[index + 1]
                )
        else:
            probability = self.get_trigram_prob("START", word[0], "END")
        return probability

    def extract(
        self,
        token: str,
        current_idx: int,
        relative_idx: int,
        tokens: Sequence[str],
        features: Dict[str, float],
    ):
        # if relative_idx == 0:
        features[
            self.lang + "_prob[" + str(relative_idx) + "]"
        ] = self.get_word_probability(token.text.lower())


class BigramFeature(FeatureExtractor):
    def extract(
        self,
        token: str,
        current_idx: int,
        relative_idx: int,
        tokens: Sequence[str],
        features: Dict[str, float],
    ):
        token = token.text
        if relative_idx == 0 and len(token) >= 2:
            for i in range(len(token) - 2):
                if i == 0:
                    bigram = "START" + token[0]
                if i > 0 and i < len(token) - 2:
                    bigram = token[i] + token[i + 1]
                # print(trigram)
                features["bigram[" + str(relative_idx) + "]=" + bigram] = 1.0
            bigram = token[len(token) - 1] + "END"
            features["bigram[" + str(relative_idx) + "]=" + bigram] = 1.0


class WordVectorFeatureNerpy(FeatureExtractor):
    def __init__(
        self, vectors: str = "spacy", scaling: float = 1.0, cache_size: int = 10000
    ) -> None:
        self.vectors_id = vectors
        self.scale = scaling
        path_to_vectors_db = PATH_TO_EMBEDDINGS_DB
        try:
            self.word_vectors = SqliteWordEmbedding.open(path_to_vectors_db)
        except:
            print(
                "Embeddings file does not exist. Extended installation needed! Please install the extended version of pylazaro (See https://pylazaro.readthedocs.io/en/latest/install.html)"
            )

    def extract(
        self,
        token: str,
        current_idx: int,
        relative_idx: int,
        tokens: Sequence[str],
        features: Dict[str, float],
    ) -> None:
        if relative_idx == 0:
            if self.vectors_id == "spacy":
                word_vector = token.vector
            else:
                try:
                    # word_vector = self._embedding_cache(token.text.lower())
                    word_vector = self.word_vectors[token.text.lower()]
                except KeyError:
                    word_vector = np.zeros(self.word_vectors.dim)
            keys = self.get_keys(word_vector)
            features.update(zip(keys, word_vector))

    def get_keys(self, word_vector):
        return ["v" + str(i) for i in range(len(word_vector))]

    def _scaled_word_vector(self, word: str) -> Sequence[float]:
        vec = self.word_vectors[word]
        # We cannot use in-place multiply because vec is read-only
        # Ignore type warning because we know this is an ndarray even though the formal return type is
        # Sequence[float]. Things are this way because it's hard to type annotate an ndarray return.
        return vec * self.scale  # type: ignore


def download(model_url, dir_name, filename):
    dir_to_save = Path(os.path.dirname(os.path.realpath(__file__)), dir_name)
    if not os.path.exists(dir_to_save):
        os.makedirs(dir_to_save)
    logging.info(
        "Preparing to download "
        + filename
        + "... (this only needs to happen the first time you import the model)"
    )
    path_to_file = Path(dir_to_save, filename)
    fetch_file(model_url, path_to_file)


def fetch_file(url: str, my_path: str):
    resp = requests.get(url, stream=True)
    total = int(resp.headers.get("content-length", 0))
    fname = my_path.as_posix()
    with open(fname, "wb") as file, tqdm(
        desc=fname,
        total=total,
        unit="iB",
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in resp.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)


def decompress_embeddings(path_to_embeddings_decompress, path_to_embeddings_compress):
    with open(path_to_embeddings_decompress, "wb") as new_file, bz2.BZ2File(
        path_to_embeddings_compress, "rb"
    ) as file:
        for data in iter(lambda: file.read(100 * 1024), b""):
            new_file.write(data)


def set_embeddings_with_quickvec(path_to_embeddings, path_to_embeddings_db):
    SqliteWordEmbedding.convert_text_format_to_db(
        path_to_embeddings, path_to_embeddings_db
    )


def fuse_spans(output_tokens: List[Token]) -> List[Borrowing]:
    new_output = []
    half_boiled_label = None
    half_boiled_token = []
    start_pos = 0

    for i, token in enumerate(output_tokens):
        if token.is_outside_label():
            if half_boiled_label:
                bor = Borrowing.from_span(half_boiled_token, half_boiled_label, start_pos, i,
                                   output_tokens)
                new_output.append(bor)
                half_boiled_label = None
                half_boiled_token = []
            start_pos = i
            #new_output.append((token, label))
        if token.is_begin_label():
            if half_boiled_label:
                bor = Borrowing.from_span(half_boiled_token, half_boiled_label, start_pos, i, output_tokens)
                new_output.append(bor)
            half_boiled_label = token.lang_label
            half_boiled_token = [token]
            start_pos = i
        if token.is_inside_label():
            half_boiled_label = token.lang_label
            if not half_boiled_token:
                start_pos = i
            half_boiled_token.append(token)
    if half_boiled_label:
        bor = Borrowing.from_span(half_boiled_token, half_boiled_label, start_pos, len(output_tokens), output_tokens)
        new_output.append(bor)
    return new_output
