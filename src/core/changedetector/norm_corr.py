# -*- coding: utf-8 -*-

__author__ = "Paul Blottiere"
__contact__ = "blottiere.paul@gmail.com"
__copyright__ = "Copyright 2020, Paul Blottiere"
__date__ = "2020/10/10"
__email__ = "blottiere.paul@gmail.com"
__license__ = "GPLv3"

import numpy as np
from scipy.spatial import distance

from .base import LittoDynChangeDetector


class LittoDynChangeDetectorNormCorr(LittoDynChangeDetector):
    """
    A change with only correlation distance
    """

    def _dodetect(self):
        dist = np.zeros((self.img1.shape[0],self.img1.shape[1]))
        for i in range(self.img1.shape[0]):
            for j in range(self.img1.shape[1]):
                dist[i,j] = distance.correlation(self.img1[i,j,:], self.img2[i,j,:])
        self.change=dist
