import logging
import os
import pathlib
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
    model_file = attr.ib(type=str, default=FLAIR_DEFAULT_MODEL, validator=attr.validators.in_(BILSTM_MODELS))
    model = attr.ib()

    @model.default
    def load_model(self):
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

    def predict(self, text) -> LazaroOutput:
        if isinstance(text, list): # text is already tokenized
            output = self.predict_on_tokenized(text)
            return LazaroOutput.from_Transformers(output)
        else:
            inputs = self.tokenizer(text, return_tensors="pt")
            tokens = inputs.tokens()
            outputs = self.model(**inputs).logits
            predictions = torch.argmax(outputs, dim=2)
            output = [
                (token, self.model.config.id2label[prediction])
                for token, prediction in zip(tokens, predictions[0].numpy())
            ]
        return LazaroOutput.from_Transformers(output)
        
    def predict_on_tokenized(self, tokenized_text: list) -> list:
        grouped_inputs = [torch.LongTensor([self.tokenizer.cls_token_id])]
        subtokens_per_token = []

        for token in tokenized_text:
            tokens = self.tokenizer.encode(
                token,
                return_tensors="pt",
                add_special_tokens=False,
            ).squeeze(axis=0)
            grouped_inputs.append(tokens)
            subtokens_per_token.append(len(tokens))

        grouped_inputs.append(torch.LongTensor([self.tokenizer.sep_token_id]))

        flattened_inputs = torch.cat(grouped_inputs)
        flattened_inputs = torch.unsqueeze(flattened_inputs, 0)

        # Predict
        predictions_tensor = self.model(flattened_inputs)[0]
        predictions_tensor = torch.argmax(predictions_tensor, dim=2)


        predictions = [self.model.config.id2label[prediction] for prediction in predictions_tensor[0].numpy()]

        # Align tokens

        # Remove special tokens [CLS] and [SEP]
        predictions = predictions[1:-1]

        aligned_predictions = []

        # assert len(predictions) == sum(subtokens_per_token)

        ptr = 0
        for size in subtokens_per_token:
            group = predictions[ptr:ptr + size]
            #assert len(group) == size

            aligned_predictions.append(group)
            ptr += size

        #assert len(tokenized_text) == len(aligned_predictions)

        output = [(token, Counter(prediction_group).most_common(1)[0][0]) for token, prediction_group in zip(tokenized_text, aligned_predictions)]
        return output



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
                "Spacy model not installed. Did you forget to run the \"python -m spacy download es_core_news_md\" command from the extended installation? Please see the extended version of pylazaro (See https://pylazaro.readthedocs.io/en/latest/install.html)"
            )
        #spacy_model.tokenizer = CRFClassifier.custom_tokenizer(spacy_model)
        return spacy_model

    def predict(self, text: str) -> LazaroOutput:
        if isinstance(text, list): # text is already tokenized
            text = Doc(self.spacy_model.vocab, words=text)
        else:
            self.spacy_model.tokenizer = CRFClassifier.custom_tokenizer(self.spacy_model)
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
