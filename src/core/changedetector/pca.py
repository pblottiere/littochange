# -*- coding: utf-8 -*-

__author__ = "Paul Blottiere"
__contact__ = "blottiere.paul@gmail.com"
__copyright__ = "Copyright 2020, Paul Blottiere"
__date__ = "2020/10/10"
__email__ = "blottiere.paul@gmail.com"
__license__ = "GPLv3"

import numpy as np
from collections import Counter
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

from .base import LittoDynChangeDetector


class LittoDynChangeDetectorPCA(LittoDynChangeDetector):
    """
    A change detector with PCA + kmeans
    """

    def _find_vector_set(self, diff_image):
        vector_set = np.reshape(
            diff_image, [diff_image.shape[0] * diff_image.shape[1], diff_image.shape[2]]
        )
        mean_vec = np.mean(vector_set, axis=0)
        vector_set -= mean_vec

        return vector_set, mean_vec

    def _find_FVS(self, EVS, diff_image, mean_vec):

        feature_vector_set = np.reshape(
            diff_image, [diff_image.shape[0] * diff_image.shape[1], diff_image.shape[2]]
        )
        FVS = np.dot(feature_vector_set, EVS)
        FVS = FVS - mean_vec
        return FVS

    def _clustering(self, FVS, components, new):

        kmeans = KMeans(components, verbose=0)
        kmeans.fit(FVS)
        output = kmeans.predict(FVS)
        count = Counter(output)

        least_index = min(count, key=count.get)
        change_map = np.reshape(output, new)

        return least_index, change_map

    def _dodetect(self):

        diff_image = abs(self.img1 - self.img2)

        vector_set, mean_vec = self._find_vector_set(diff_image)

        pca = PCA()
        pca.fit(vector_set)
        EVS = pca.components_

        FVS = self._find_FVS(EVS, diff_image, mean_vec)

        components = 3
        least_index, change_map = self._clustering(
            FVS, components, [diff_image.shape[0], diff_image.shape[1]]
        )

        change_map[change_map == least_index] = 255
        change_map[change_map != 255] = 0

        self.change = change_map.astype(np.float32)
