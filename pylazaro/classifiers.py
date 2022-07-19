import logging
import os
import pathlib
import re
from abc import ABC, abstractmethod
from typing import List

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
from transformers import AutoModelForTokenClassification, AutoTokenizer, pipeline

from pylazaro.output import (
    LazaroOutput
)
from pylazaro.utils import (
    BiasFeature,
    CRFsuiteEntityRecognizer_CoNLL,
    EmailFeature,
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
)

from .constants import *

if os.name == "nt":
    temp = pathlib.PosixPath
    pathlib.PosixPath = pathlib.WindowsPath


class LazaroClassifier(ABC):
    @abstractmethod
    def predict(self, text) -> LazaroOutput:
        raise NotImplementedError

    @abstractmethod
    def load_model(self):
        raise NotImplementedError


@attr.s
class FlairClassifier(LazaroClassifier):
    model_name = attr.ib(type=str, default=FLAIR_DEFAULT_MODEL)
    model = attr.ib()

    @model.default
    def load_model(self):
        tagger = SequenceTagger.load(self.model_name)
        return tagger

    def predict(self, text: str) -> LazaroOutput:
        sentence = Sentence(text)
        self.model.predict(sentence, force_token_predictions=True)
        sentence = LazaroOutput.from_Flair(sentence)
        return sentence


@attr.s
class TransformersClassifier(LazaroClassifier):
    model_name = attr.ib(type=str, default=TRANSFORMERS_DEFAULT_MODEL)
    model = attr.ib()
    tokenizer = attr.ib()

    @model.default
    def load_model(self) -> AutoModelForTokenClassification:
        model = AutoModelForTokenClassification.from_pretrained(self.model_name)
        return model

    @tokenizer.default
    def load_tokenizer(self) -> AutoTokenizer:
        tokenizer = AutoTokenizer.from_pretrained(self.model_name, do_lower_case=False)
        return tokenizer

    def predict(self, text: str) -> LazaroOutput:
        inputs = self.tokenizer(text, return_tensors="pt")
        tokens = inputs.tokens()
        outputs = self.model(**inputs).logits
        predictions = torch.argmax(outputs, dim=2)
        output = [
            (token, self.model.config.id2label[prediction])
            for token, prediction in zip(tokens, predictions[0].numpy())
        ]
        return LazaroOutput.from_Transformers(output)


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
        logging.info("Loading model... (this may take a while)")
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
        try:
            crf.tagger.open(path_to_model.as_posix())
        except:
            print(
                "CRF model file does not exist. Extended installation needed! Please install the extended version of pylazaro (See https://pylazaro.readthedocs.io/en/latest/install.html)"
            )
        return crf

    @spacy_model.default
    def load_spacy(self) -> Language:
        try:
            spacy_model = spacy.load("es_core_news_md", exclude=["ner"])
        except:
            print(
                "Spacy model not installed. Extended installation needed! Please install the extended version of pylazaro (See https://pylazaro.readthedocs.io/en/latest/install.html)"
            )
        spacy_model.tokenizer = CRFClassifier.custom_tokenizer(spacy_model)
        return spacy_model

    def predict(self, text: str) -> LazaroOutput:
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
                if i < len(tags) - 1 and tags[i + 1].startswith("I"):
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
