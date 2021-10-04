# Always prefer setuptools over distutils
from setuptools import setup

# To use a consistent encoding
from codecs import open
from os import path

# The directory containing this file
HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
	long_description = f.read()

# This call to setup() does all the work
setup(
	name="pylazaro",
	version="0.1.34",
	description="A Python library for lexical borrowing detection",
	long_description_content_type="text/markdown",
	long_description=long_description,
	url="https://pylazaro.readthedocs.io/",
	author="Elena Álvarez Mellado",
	author_email="ealvarezmellado@gmail.com",
	license="MIT",
	classifiers=[
		"Intended Audience :: Developers",
		"License :: OSI Approved :: MIT License",
		"Programming Language :: Python :: 3.6",
		"Programming Language :: Python :: 3.7",
		"Programming Language :: Python :: 3.8",
		"Operating System :: OS Independent"
	],
	packages=["pylazaro"],
	include_package_data=True,
	install_requires=["flair", "attrs"],
)
