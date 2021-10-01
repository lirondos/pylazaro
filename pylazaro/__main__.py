import pathlib
from pathlib import Path
from .utils import download, decompress_embeddings, set_embeddings_with_quickvec
import logging
import sys
import os
from .constants import *

temp = pathlib.PosixPath
pathlib.PosixPath = pathlib.WindowsPath
"""
EMBEDDINGS_DB = "embeddings.db"
EMBEDDINGS_COMPRESS = "embeddings.txt.bz2"
EMBEDDINGS_DECOMPRESS = "embeddings.txt"

PATH_TO_EMBEDDINGS_DIR =  Path(os.path.dirname(os.path.realpath(__file__)), "embeddings")
PATH_TO_EMBEDDINGS_COMPRESS = Path(PATH_TO_EMBEDDINGS_DIR, EMBEDDINGS_COMPRESS)
PATH_TO_EMBEDDINGS_DB = Path(PATH_TO_EMBEDDINGS_DIR, EMBEDDINGS_DB)
PATH_TO_EMBEDDINGS_DECOMPRESS = Path(PATH_TO_EMBEDDINGS_DIR, EMBEDDINGS_DECOMPRESS)

PATH_TO_MODELS_DIR =  Path(os.path.dirname(os.path.realpath(__file__)), "models")

URL_TO_FLAIR_MODEL = "https://github.com/lirondos/pylazaro/releases/download/v.0.1/bert-beto-bpe-char.pt"
FLAIR_MODEL = "bert-beto-bpe-char.pt"
PATH_TO_FLAIR_MODEL = Path(PATH_TO_MODELS_DIR, FLAIR_MODEL)

CRF_FILENAME = "crf.model"
PATH_TO_CRF_MODEL = Path(PATH_TO_MODELS_DIR, CRF_FILENAME)

URL_TO_MODEL = "https://github.com/lirondos/pylazaro/releases/download/v.0.1/bert-beto-bpe-char.pt"
MODELS_DIR =  "models"
MODEL = "lazaro.pt"
PATH_TO_MODEL = Path(PATH_TO_MODELS_DIR, MODEL)

URL_TO_EMBEDDINGS = "http://cs.famaf.unc.edu.ar/~ccardellino/SBWCE/SBW-vectors-300-min5.txt.bz2"
"""
def main():
	download_crf()
	download_embeddings()
	if len(sys.argv)>1 and sys.argv[1] == "flair":
		download_flair()

def download_crf():
	if not os.path.exists(PATH_TO_CRF_MODEL):
		logging.info("Preparing to download model...")
		download(URL_TO_FLAIR_MODEL, "models", CRF_FILENAME)
	else:
		print(PATH_TO_CRF_MODEL)

def download_embeddings():
	if not os.path.exists(PATH_TO_EMBEDDINGS_DB):
		if not os.path.exists(PATH_TO_EMBEDDINGS_DECOMPRESS):
			if not os.path.exists(PATH_TO_EMBEDDINGS_COMPRESS):
				logging.info("Preparing to download embeddings... (this may take a while)")
				download(URL_TO_EMBEDDINGS, "embeddings", EMBEDDINGS_COMPRESS)
			logging.info("Preparing to decompress embeddings... (this may take a while)")
			decompress_embeddings(PATH_TO_EMBEDDINGS_DECOMPRESS, PATH_TO_EMBEDDINGS_COMPRESS)
		logging.info("Calling quickvec to convert embeddings to database... (this may also take a "
		             "while)")
		set_embeddings_with_quickvec(PATH_TO_EMBEDDINGS_DECOMPRESS, PATH_TO_EMBEDDINGS_DB)
		remove_file(PATH_TO_EMBEDDINGS_DECOMPRESS)
		remove_file(PATH_TO_EMBEDDINGS_COMPRESS)
	else:
		print(PATH_TO_EMBEDDINGS_DB)

def remove_file(filename):
	try:
		os.remove(filename)
	except OSError:
		pass

def download_flair():
	if not os.path.exists(PATH_TO_FLAIR_MODEL):
		logging.info("Preparing to download flair model... (this may take a while)")
		download(URL_TO_FLAIR_MODEL, "models", FLAIR_MODEL)
	else:
		print(PATH_TO_FLAIR_MODEL)
"""
if __name__ == "__main__":
	main()
"""

