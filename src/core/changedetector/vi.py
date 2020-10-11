# -*- coding: utf-8 -*-

__author__ = "Paul Blottiere"
__contact__ = "blottiere.paul@gmail.com"
__copyright__ = "Copyright 2020, Paul Blottiere"
__date__ = "2020/10/10"
__email__ = "blottiere.paul@gmail.com"
__license__ = "GPLv3"

import numpy as np

from .base import LittoDynChangeDetector


class LittoDynChangeDetectorVi(LittoDynChangeDetector):
    """
    Generic class for vegetation index based change detectors
    Expected input images bands are
    1 : Blue
    2 : Green
    3 : Red
    4 : Infra Red
    """

    def _dodetect(self):
        """
        For vegetaion indexes we always return abs diff between the vegetation indexes of input images
        """

        vi1=self._vi(self.img1)
        vi2=self._vi(self.img2)
        dist = np.zeros((self.img1.shape[0],self.img1.shape[1]))
        self.change=np.abs(vi2-vi1)

    def _vi(self):
        """
        Vegetation index
        """
        pass
