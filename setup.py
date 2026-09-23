# Always prefer setuptools over distutils
# To use a consistent encoding
from codecs import open
from os import path

from setuptools import setup

# The directory containing this file
HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(HERE, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# This call to setup() does all the work
setup(
    name="pylazaro",
    version="1.2.0",
    description="A Python library for detecting lexical borrowings (with a focus on anglicisms in Spanish language)",
    long_description_content_type="text/markdown",
    long_description=long_description,
    url="https://pylazaro.readthedocs.io/",
    author="Elena Álvarez Mellado",
    author_email="ealvarezmellado@gmail.com",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    packages=["pylazaro"],
    include_package_data=True,
    python_requires=">=3.8",
    # Upper bounds are deliberate. The BiLSTM checkpoints are pickles that reference
    # flair.embeddings.token.BPEmbSerializable, which was removed in flair 0.14, and
    # flair < 0.14 in turn calls torch.load() without weights_only=False (the default
    # flipped in torch 2.6) and does not import against transformers >= 4.46.
    install_requires=[
        "transformers>=4.30,<4.46",
        "flair>=0.12,<0.14",
        "attrs",
        "torch>=1.13,<2.6",
        "spacy>=3.2,<4",
        "python-crfsuite",
        "quickvec>=0.2",
        "numpy",
        "regex",
        "requests",
        "tqdm",
    ],
)
