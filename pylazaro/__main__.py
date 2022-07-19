import logging
import pathlib
import sys

from .constants import *
from .utils import decompress_embeddings, download, set_embeddings_with_quickvec

if os.name == "nt":
    temp = pathlib.PosixPath
    pathlib.PosixPath = pathlib.WindowsPath


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "extended":
        download_crf()
        download_embeddings()
        logging.info("Done downloading!")
        # download_flair()


def download_crf():
    if not os.path.exists(PATH_TO_CRF_MODEL):
        logging.info("Preparing to download model...")
        download(URL_TO_CRF_MODEL, "models", CRF_FILENAME)
    else:
        print(PATH_TO_CRF_MODEL)


def download_embeddings():
    if not os.path.exists(PATH_TO_EMBEDDINGS_DB):
        if not os.path.exists(PATH_TO_EMBEDDINGS_DECOMPRESS):
            if not os.path.exists(PATH_TO_EMBEDDINGS_COMPRESS):
                logging.info(
                    "Preparing to download embeddings... (this may take a while)"
                )
                download(URL_TO_EMBEDDINGS, "embeddings", EMBEDDINGS_COMPRESS)
            logging.info(
                "Preparing to decompress embeddings... (this may take a while)"
            )
            decompress_embeddings(
                PATH_TO_EMBEDDINGS_DECOMPRESS, PATH_TO_EMBEDDINGS_COMPRESS
            )
        logging.info(
            "Calling quickvec to convert embeddings to database... (this may also take a "
            "while)"
        )
        set_embeddings_with_quickvec(
            PATH_TO_EMBEDDINGS_DECOMPRESS, PATH_TO_EMBEDDINGS_DB
        )
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


if __name__ == "__main__":
    main()
