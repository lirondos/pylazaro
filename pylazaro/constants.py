import os
from pathlib import Path

EMBEDDINGS_DB = "embeddings.db"
EMBEDDINGS_COMPRESS = "embeddings.txt.bz2"
EMBEDDINGS_DECOMPRESS = "embeddings.txt"

MODELS_DIR = "models"
EMBEDDINGS_DIR = "embeddings"

CRF_FILENAME = "crf.model"

PACKAGE_DIR = Path(os.path.dirname(os.path.realpath(__file__)))


def _user_data_dir() -> Path:
    """Directory where the files downloaded by the extended installation are stored.

    Can be overriden through the ``PYLAZARO_HOME`` environment variable. Writing outside
    of ``site-packages`` means the downloads survive a reinstall and work on read-only
    installations.
    """
    override = os.environ.get("PYLAZARO_HOME")
    if override:
        return Path(override)
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA")
        return Path(base if base else Path.home() / "AppData" / "Local", "pylazaro")
    base = os.environ.get("XDG_CACHE_HOME")
    return Path(base if base else Path.home() / ".cache", "pylazaro")


def _resolve_data_dir(dir_name: str, filenames) -> Path:
    """Return the directory that holds ``dir_name``.

    Earlier versions of ``pylazaro`` downloaded into the package folder itself. That
    location is still honoured when it already contains data, so that an extended
    installation performed with a previous version keeps working after an upgrade.
    """
    legacy_dir = Path(PACKAGE_DIR, dir_name)
    if any(Path(legacy_dir, filename).exists() for filename in filenames):
        return legacy_dir
    return Path(_user_data_dir(), dir_name)


PATH_TO_EMBEDDINGS_DIR = _resolve_data_dir(
    EMBEDDINGS_DIR, (EMBEDDINGS_DB, EMBEDDINGS_DECOMPRESS, EMBEDDINGS_COMPRESS)
)
PATH_TO_EMBEDDINGS_COMPRESS = Path(PATH_TO_EMBEDDINGS_DIR, EMBEDDINGS_COMPRESS)
PATH_TO_EMBEDDINGS_DB = Path(PATH_TO_EMBEDDINGS_DIR, EMBEDDINGS_DB)
PATH_TO_EMBEDDINGS_DECOMPRESS = Path(PATH_TO_EMBEDDINGS_DIR, EMBEDDINGS_DECOMPRESS)

PATH_TO_MODELS_DIR = _resolve_data_dir(MODELS_DIR, (CRF_FILENAME,))
PATH_TO_CRF_MODEL = Path(PATH_TO_MODELS_DIR, CRF_FILENAME)

DATA_DIRS = {
    MODELS_DIR: PATH_TO_MODELS_DIR,
    EMBEDDINGS_DIR: PATH_TO_EMBEDDINGS_DIR,
}

CS_MODEL = "lirondos/anglicisms-spanish-flair-cs"
BETO_BERT_MODEL = "lirondos/anglicisms-spanish-flair-bert-beto"
FLAIR_DEFAULT_MODEL = CS_MODEL
BILSTM_MODELS = [BETO_BERT_MODEL, CS_MODEL]

MBERT_MODEL = "lirondos/anglicisms-spanish-mbert"
BETO_MODEL = "lirondos/anglicisms-spanish-beto"
TRANSFORMERS_DEFAULT_MODEL = BETO_MODEL
TRANSFORMERS_MODELS = [MBERT_MODEL, BETO_MODEL]

MODELS_FILES = TRANSFORMERS_MODELS + BILSTM_MODELS

# BIO tag given to tokens that are not part of a borrowing
OUTSIDE_LABEL = "O"

URL_TO_CRF_MODEL = (
    "https://github.com/lirondos/pylazaro/releases/download/v0.2/crf.model"
)

URL_TO_EMBEDDINGS = (
    "http://cs.famaf.unc.edu.ar/~ccardellino/SBWCE/SBW-vectors-300-min5.txt.bz2"
)

EXTENDED_INSTALL_URL = "https://pylazaro.readthedocs.io/en/latest/install.html"

CRF_MODEL_MISSING_MESSAGE = (
    "CRF model file does not exist. Extended installation needed! Please install the "
    "extended version of pylazaro by running \"python -m pylazaro extended\" "
    "(See " + EXTENDED_INSTALL_URL + ")"
)

EMBEDDINGS_MISSING_MESSAGE = (
    "Embeddings file does not exist. Extended installation needed! Please install the "
    "extended version of pylazaro by running \"python -m pylazaro extended\" "
    "(See " + EXTENDED_INSTALL_URL + ")"
)

SPACY_MODEL_MISSING_MESSAGE = (
    "Spacy model not installed. Did you forget to run the \"python -m spacy download "
    "es_core_news_md\" command from the extended installation? Please see the extended "
    "version of pylazaro (See " + EXTENDED_INSTALL_URL + ")"
)
