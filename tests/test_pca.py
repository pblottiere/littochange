# -*- coding: utf-8 -*-

__author__ = "Paul Blottiere"
__contact__ = "blottiere.paul@gmail.com"
__copyright__ = "Copyright 2020, Paul Blottiere"
__date__ = "2020/10/10"
__email__ = "blottiere.paul@gmail.com"
__license__ = "GPLv3"

import os
from src.core.changedetector.pca import LittoDynChangeDetectorPCA

cwd = os.path.dirname(os.path.realpath(__file__))
img1 = os.path.join(cwd, "20170706_102911_0f43_AnalyticMS_SR.tif")
img2 = os.path.join(cwd, "20180723_104602_103c_AnalyticMS_SR.tif")
roi = os.path.join(cwd, "roi.shp")
result = os.path.join(cwd, "pca.tif")

detector = LittoDynChangeDetectorPCA(img1,
                               img2,
                               roi
                               )
detector.detect()
detector.save(result)
