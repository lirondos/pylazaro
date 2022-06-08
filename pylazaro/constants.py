import os
from pathlib import Path

EMBEDDINGS_DB = "embeddings.db"
EMBEDDINGS_COMPRESS = "embeddings.txt.bz2"
EMBEDDINGS_DECOMPRESS = "embeddings.txt"

PATH_TO_EMBEDDINGS_DIR = Path(os.path.dirname(os.path.realpath(__file__)), "embeddings")
PATH_TO_EMBEDDINGS_COMPRESS = Path(PATH_TO_EMBEDDINGS_DIR, EMBEDDINGS_COMPRESS)
PATH_TO_EMBEDDINGS_DB = Path(PATH_TO_EMBEDDINGS_DIR, EMBEDDINGS_DB)
PATH_TO_EMBEDDINGS_DECOMPRESS = Path(PATH_TO_EMBEDDINGS_DIR, EMBEDDINGS_DECOMPRESS)

PATH_TO_MODELS_DIR = Path(os.path.dirname(os.path.realpath(__file__)), "models")

CS_MODEL = "lirondos/anglicisms-spanish-flair-cs"
FLAIR_DEFAULT_MODEL = CS_MODEL

MBERT_MODEL = "lirondos/anglicisms-spanish-mbert"
TRANSFORMERS_DEFAULT_MODEL = MBERT_MODEL

URL_TO_CRF_MODEL = (
    "https://github.com/lirondos/pylazaro/releases/download/v0.1/crf.model"
)
CRF_FILENAME = "crf.model"
PATH_TO_CRF_MODEL = Path(PATH_TO_MODELS_DIR, CRF_FILENAME)

MODELS_DIR = "models"

URL_TO_EMBEDDINGS = (
    "http://cs.famaf.unc.edu.ar/~ccardellino/SBWCE/SBW-vectors-300-min5.txt.bz2"
)
