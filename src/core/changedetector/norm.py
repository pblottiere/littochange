# -*- coding: utf-8 -*-

__author__ = "Paul Blottiere"
__contact__ = "blottiere.paul@gmail.com"
__copyright__ = "Copyright 2020, Paul Blottiere"
__date__ = "2020/10/10"
__email__ = "blottiere.paul@gmail.com"
__license__ = "GPLv3"

import numpy as np

from .base import LittoDynChangeDetector


class LittoDynChangeDetectorNormEuclid(LittoDynChangeDetector):
    """
    A change with only euclidian distance
    """

    def _dodetect(self):
        self.change = np.sqrt(np.sum((self.img1 - self.img2) ** 2, axis=2))
