import os
import pathlib
from typing import List, Tuple, Dict
from collections import defaultdict

import attr

if os.name == "nt":
    temp = pathlib.PosixPath
    pathlib.PosixPath = pathlib.WindowsPath

@attr.s
class Token(object):
    """
    The object that models a token (a string of chars between two spaces/punct).

    Attributes:
            text (str): string representation of the Token
            label (str): labeled assigned (BIO)
            position (int): position of the token within the sentence/context
            probability (float): score/prob assigned by the tagger to the label
    """
    text = attr.ib(type=str)
    label = attr.ib(type=str)
    position = attr.ib(type=int)
    probability = attr.ib(type=float, default=None, eq=False, repr=False)

    @property
    def lang_label(self):
        return self.label.split("-")[1]

    @property
    def bio_label(self):
        return self.label.split("-")[0]

    def is_outside_label(self) -> bool:
        return self.bio_label == "O"

    def is_begin_label(self) -> bool:
        return self.bio_label == "B"

    def is_inside_label(self) -> bool:
        return self.bio_label == "I"



    def to_tuple(self) -> Tuple[str, str, float]:
        """

        Returns:
            The token formatted as a tuple of shape (text, label, probability)


        """

        return (self.text, self.label, self.probability)


    def to_dict(self) -> Dict:
        """

        Returns:
            The token formatted as a dict

        """

        return {"text": self.text, "label": self.label, "probability": self.probability}
