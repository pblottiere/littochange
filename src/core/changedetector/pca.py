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


class LittoDynChangeDetectorPca(LittoDynChangeDetector):
    """
    A change detector with PCA + kmeans
    """

    def _find_vector_set(self, diff_image):
        self.isdata=np.where(self.roi_mask)
        vector_set=np.zeros([len(self.isdata[0]),diff_image.shape[2]],dtype=np.float)
        for i in range(len(self.isdata[0])):
            vector_set[i,:]=diff_image[self.isdata[0][i], self.isdata[1][i],:]
        mean_vec = np.mean(vector_set, axis=0)
        vector_set -= mean_vec

        return vector_set, mean_vec

    def _find_FVS(self, EVS, diff_image, mean_vec):
        feature_vector_set=np.zeros([len(self.isdata[0]),diff_image.shape[2]],dtype=np.float)
        for i in range(len(self.isdata[0])):
            feature_vector_set[i,:]=diff_image[self.isdata[0][i], self.isdata[1][i],:]

        FVS = np.dot(feature_vector_set, EVS)
        FVS = FVS - mean_vec
        return FVS

    def _clustering(self, FVS, components, new):

        kmeans = KMeans(components, verbose=0)
        kmeans.fit(FVS)
        output = kmeans.predict(FVS)
        count = Counter(output)

        max_index = max(count, key = count.get)
        change_map=np.zeros(new)+np.nan
        for i in range(len(self.isdata[0])):
           change_map[self.isdata[0][i], self.isdata[1][i]]=output[i]

        return max_index, change_map

    def _dodetect(self):

        diff_image = np.abs(self.img1 - self.img2)

        vector_set, mean_vec = self._find_vector_set(diff_image)

        pca = PCA()
        pca.fit(vector_set)
        EVS = pca.components_

        FVS = self._find_FVS(EVS, diff_image, mean_vec)

        components = 3
        max_index, self.change = self._clustering(FVS, components, [diff_image.shape[0],diff_image.shape[1]])
