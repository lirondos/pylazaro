import logging
import os
import re
from abc import ABC, abstractmethod
from typing import List
from collections import Counter

import attr
import pycrfsuite
import spacy
import torch
from flair.data import Sentence
from flair.models import SequenceTagger
from spacy.lang.tokenizer_exceptions import URL_PATTERN
from spacy.language import Language
from spacy.tokenizer import Tokenizer
from spacy.training import biluo_tags_to_spans
from spacy.tokens import Doc
from transformers import AutoModelForTokenClassification, AutoTokenizer

from pylazaro.output import (
    LazaroOutput
)
from pylazaro.utils import (
    BiasFeature,
    CRFsuiteEntityRecognizer_CoNLL,
    EmailFeature,
    ExtendedInstallationRequired,
    POStagFeature,
    QuotationFeature,
    TitlecaseFeature,
    TokenFeature,
    TrigramFeature,
    TwitterFeature,
    UppercaseFeature,
    URLFeature,
    WindowedTokenFeatureExtractor,
    WordEnding,
    WordShapeFeature,
    WordVectorFeatureNerpy,
    posix_paths_on_windows,
)

from .constants import *

logger = logging.getLogger(__name__)

# Number of special tokens ([CLS] and [SEP]) added around every Transformers input
NUM_SPECIAL_TOKENS = 2
DEFAULT_MAX_LENGTH = 512


class LazaroClassifier(ABC):
    @abstractmethod
    def predict(self, text) -> LazaroOutput:
        raise NotImplementedError

    @abstractmethod
    def load_model(self):
        raise NotImplementedError


@attr.s
class FlairClassifier(LazaroClassifier):
    model_file = attr.ib(type=str, default=FLAIR_DEFAULT_MODEL, validator=attr.validators.in_(BILSTM_MODELS))
    model = attr.ib()

    @model.default
    def load_model(self):
        with posix_paths_on_windows():
            tagger = SequenceTagger.load(self.model_file)
        return tagger

    def predict(self, text: str) -> LazaroOutput:
        sentence = Sentence(text)
        self.model.predict(sentence, force_token_predictions=True)
        sentence = LazaroOutput.from_Flair(sentence)
        return sentence


@attr.s
class TransformersClassifier(LazaroClassifier):
    model_file = attr.ib(type=str, default=TRANSFORMERS_DEFAULT_MODEL, validator=attr.validators.in_(TRANSFORMERS_MODELS))
    model = attr.ib()
    tokenizer = attr.ib()

    @model.default
    def load_model(self) -> AutoModelForTokenClassification:
        model = AutoModelForTokenClassification.from_pretrained(self.model_file)
        return model

    @tokenizer.default
    def load_tokenizer(self) -> AutoTokenizer:
        tokenizer = AutoTokenizer.from_pretrained(self.model_file, do_lower_case=False)
        return tokenizer

    @property
    def max_subtokens_per_window(self) -> int:
        """Largest number of subtokens that fits in a single forward pass.

        Inputs longer than this are split into consecutive windows instead of
        overflowing the model's positional embeddings.
        """
        limits = [
            getattr(self.model.config, "max_position_embeddings", DEFAULT_MAX_LENGTH),
            getattr(self.tokenizer, "model_max_length", DEFAULT_MAX_LENGTH),
        ]
        limits = [limit for limit in limits if isinstance(limit, int) and 0 < limit < 1e6]
        max_length = min(limits) if limits else DEFAULT_MAX_LENGTH
        return max(1, max_length - NUM_SPECIAL_TOKENS)

    def predict(self, text) -> LazaroOutput:
        if isinstance(text, list): # text is already tokenized
            output = self.predict_on_tokenized(text)
        else:
            output = self.predict_on_text(text)
        return LazaroOutput.from_Transformers(output)

    def predict_on_text(self, text: str) -> list:
        words, subtokens_per_word = self.split_into_words(text)
        if not words:
            return []
        labels_per_word = self.predict_labels_per_word(subtokens_per_word)
        # The label of a word is the label of its first subtoken, which is how the
        # output of this classifier has always been read.
        return [
            (word, labels[0] if labels else OUTSIDE_LABEL)
            for word, labels in zip(words, labels_per_word)
        ]

    def split_into_words(self, text: str) -> tuple:
        """Split ``text`` the way the model's tokenizer does, keeping surface forms.

        Returns the list of words as they appear in ``text`` together with the subtoken
        ids of each word. Taking the words from the original string (rather than from
        the tokenizer's vocabulary) keeps characters that are outside the vocabulary,
        such as quotation marks, which used to come back as ``[UNK]``.
        """
        if self.tokenizer.is_fast:
            return self.split_into_words_with_offsets(text)
        return self.split_into_words_without_offsets(text)

    def split_into_words_with_offsets(self, text: str) -> tuple:
        """Group subtokens into words and read every word off the original string."""
        encoding = self.tokenizer(
            text, add_special_tokens=False, return_offsets_mapping=True
        )
        input_ids = encoding["input_ids"]
        if not input_ids:
            return [], []
        offsets = encoding["offset_mapping"]
        word_ids = encoding.word_ids()

        word_spans, subtokens_per_word = [], []
        previous_word_id = None
        for input_id, (start, end), word_id in zip(input_ids, offsets, word_ids):
            if not word_spans or word_id != previous_word_id:
                word_spans.append([start, end])
                subtokens_per_word.append([input_id])
                previous_word_id = word_id
            else:
                word_spans[-1][1] = end
                subtokens_per_word[-1].append(input_id)
        words = [text[start:end] for start, end in word_spans]
        return words, subtokens_per_word

    def split_into_words_without_offsets(self, text: str) -> tuple:
        """Group subtokens into words for tokenizers that cannot report offsets.

        Slow (pure Python) tokenizers do not support ``return_offsets_mapping``, so the
        words have to be rebuilt from the vocabulary using the ``##`` continuation
        convention. Characters outside the vocabulary still come back as ``[UNK]``;
        the models shipped with ``pylazaro`` all provide a fast tokenizer.
        """
        input_ids = self.tokenizer.encode(text, add_special_tokens=False)
        if not input_ids:
            return [], []
        subtokens = self.tokenizer.convert_ids_to_tokens(input_ids)

        words, subtokens_per_word = [], []
        for input_id, subtoken in zip(input_ids, subtokens):
            if subtoken.startswith("##") and words:
                words[-1] += subtoken[2:]
                subtokens_per_word[-1].append(input_id)
            else:
                words.append(subtoken)
                subtokens_per_word.append([input_id])
        return words, subtokens_per_word

    def predict_on_tokenized(self, tokenized_text: list) -> list:
        subtokens_per_word = [
            self.tokenizer.encode(token, add_special_tokens=False)
            for token in tokenized_text
        ]
        labels_per_word = self.predict_labels_per_word(subtokens_per_word)
        # The label of a word is the most frequent label among its subtokens
        output = [
            (
                token,
                Counter(labels).most_common(1)[0][0] if labels else OUTSIDE_LABEL,
            )
            for token, labels in zip(tokenized_text, labels_per_word)
        ]
        return output

    def predict_labels_per_word(self, subtokens_per_word: List[List[int]]) -> List[List[str]]:
        """Label every subtoken, grouped per word.

        The input is split into windows that fit the model so that long texts are
        labelled in full instead of raising a tensor size error. Words are never split
        across two windows.
        """
        labels_per_word = []
        for window in self.build_windows(subtokens_per_word):
            labels_per_word.extend(self.predict_window(window))
        return labels_per_word

    def build_windows(self, subtokens_per_word: List[List[int]]) -> List[List[List[int]]]:
        max_subtokens = self.max_subtokens_per_window
        windows, current, current_size = [], [], 0
        for subtokens in subtokens_per_word:
            # A single word longer than the window has to be truncated on its own
            subtokens = subtokens[:max_subtokens]
            if current and current_size + len(subtokens) > max_subtokens:
                windows.append(current)
                current, current_size = [], 0
            current.append(subtokens)
            current_size += len(subtokens)
        if current:
            windows.append(current)
        return windows

    def predict_window(self, window: List[List[int]]) -> List[List[str]]:
        flattened = [
            subtoken for subtokens in window for subtoken in subtokens
        ]
        input_ids = torch.LongTensor(
            [[self.tokenizer.cls_token_id] + flattened + [self.tokenizer.sep_token_id]]
        )
        with torch.no_grad():
            predictions_tensor = self.model(input_ids)[0]
        predictions_tensor = torch.argmax(predictions_tensor, dim=2)
        predictions = [
            self.model.config.id2label[prediction]
            for prediction in predictions_tensor[0].numpy()
        ]
        # Remove special tokens [CLS] and [SEP]
        predictions = predictions[1:-1]

        labels_per_word, ptr = [], 0
        for subtokens in window:
            labels_per_word.append(predictions[ptr:ptr + len(subtokens)])
            ptr += len(subtokens)
        return labels_per_word



@attr.s
class CRFClassifier(LazaroClassifier):
    model_file = attr.ib(
        default=CRF_FILENAME, validator=attr.validators.instance_of(str)
    )
    model = attr.ib()
    spacy_model = attr.ib()

    @model.default
    def load_model(self):
        path_to_model = Path(PATH_TO_MODELS_DIR, self.model_file)
        if not path_to_model.exists():
            raise ExtendedInstallationRequired(CRF_MODEL_MISSING_MESSAGE)
        logger.info("Loading model... (this may take a while)")
        window_size = 2
        features = [
            WordVectorFeatureNerpy("w2v", scaling=0.5),
            BiasFeature(),
            TokenFeature(),
            UppercaseFeature(),
            TitlecaseFeature(),
            TrigramFeature(),
            QuotationFeature(),
            WordEnding(),
            POStagFeature(),
            WordShapeFeature(),
            URLFeature(),
            EmailFeature(),
            TwitterFeature(),
        ]
        crf = CRFsuiteEntityRecognizer_CoNLL(
            WindowedTokenFeatureExtractor(
                features,
                window_size,
            )
        )
        crf.tagger = pycrfsuite.Tagger()
        crf.tagger.open(path_to_model.as_posix())
        return crf

    @spacy_model.default
    def load_spacy(self) -> Language:
        try:
            spacy_model = spacy.load("es_core_news_md", exclude=["ner"])
        except (OSError, IOError) as error:
            raise ExtendedInstallationRequired(SPACY_MODEL_MISSING_MESSAGE) from error
        # Built once here rather than on every call to predict()
        spacy_model.tokenizer = CRFClassifier.custom_tokenizer(spacy_model)
        return spacy_model

    def predict(self, text: str) -> LazaroOutput:
        if isinstance(text, list): # text is already tokenized
            text = Doc(self.spacy_model.vocab, words=text)
        doc = self.spacy_model(text)
        predicted_tags = [tag for sent in doc.sents for tag in self.model(sent)]
        doc.user_data["tags"] = predicted_tags
        predicted_tags_biluo = CRFClassifier.to_biluo(predicted_tags)
        predicted_spans = biluo_tags_to_spans(doc, predicted_tags_biluo)
        doc.ents = predicted_spans
        return LazaroOutput.from_CRF(doc)

    @staticmethod
    def to_biluo(tags: List[str]) -> List[str]:
        new_tags = []
        for i, tag in enumerate(tags):
            if tag.startswith("B"):
                if i < len(tags) - 1 and tags[i + 1].startswith("I"):
                    new_tags.append(tag)
                else:
                    new_tag = "U" + tag[1:]
                    new_tags.append(new_tag)
            elif tag.startswith("I"):
                if i==0 or tags[i - 1].startswith("O") or tags[i - 1].startswith("L"): # invalid sequence
                    new_tag = "B" + tag[1:]
                    new_tags.append(new_tag)
                elif i < len(tags) - 1 and tags[i + 1].startswith("I"):
                    new_tags.append(tag)
                else:
                    new_tag = "L" + tag[1:]
                    new_tags.append(new_tag)
            else:
                new_tags.append(tag)
        return new_tags

    @staticmethod
    def custom_tokenizer(nlp: Language) -> Tokenizer:
        prefix_re = re.compile(
            spacy.util.compile_prefix_regex(
                Language.Defaults.prefixes + [r"""^-"""]
            ).pattern.replace("#", "!")
        )
        infix_re = spacy.util.compile_infix_regex(Language.Defaults.infixes)
        suffix_re = spacy.util.compile_suffix_regex(
            Language.Defaults.suffixes + [r"""-$"""]
        )

        hashtag_pattern = r"""|^(#[\w_-]+)$"""
        url_and_hashtag = URL_PATTERN + hashtag_pattern
        url_and_hashtag_re = re.compile(url_and_hashtag)

        return Tokenizer(
            nlp.vocab,
            prefix_search=prefix_re.search,
            suffix_search=suffix_re.search,
            infix_finditer=infix_re.finditer,
            token_match=url_and_hashtag_re.match,
        )
