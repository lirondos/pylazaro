import sys

from pylazaro import Lazaro

model = sys.argv[1]

tagger = Lazaro(model_type=model)
text = "Inteligencia artificial aplicada al sector del digital health, la e-mobility, las smarts grids y las apps entre otros; favoreciendo las interacciones colaborativas."

# We run our tagger on the text we want to analyze
result = tagger.analyze(text)

# We get results
print(result.borrowings())
print(result.anglicisms())
print(result.other_borrowings())
print(result.count())
print(result.tag_per_token())

"""
from transformers import pipeline, AutoModelForTokenClassification, AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("lirondos/anglicisms-spanish-mbert")
model = AutoModelForTokenClassification.from_pretrained("lirondos/anglicisms-spanish-mbert")
nlp = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")
example = "Buscamos data scientist para proyecto de machine learning."

borrowings = nlp(example)
print(borrowings)
for borrowing in borrowings:
    print(borrowing)


from flair.data import Sentence
from flair.models import SequenceTagger
import pathlib
import os

if os.name == 'nt':
    temp = pathlib.PosixPath
    pathlib.PosixPath = pathlib.WindowsPath
  
tagger = SequenceTagger.load("lirondos/anglicisms-spanish-flair-cs")

text = "Las fake news sobre la celebrity se reprodujeron por los mass media en prime time."

sentence = Sentence(text)

# predict tags
tagger.predict(sentence)

# print sentence
print(sentence)

# print predicted borrowing spans
print('The following borrowing were found:')
for entity in sentence.get_spans():
    print(entity)
"""
