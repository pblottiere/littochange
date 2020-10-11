# -*- coding: utf-8 -*-

__author__ = "Paul Blottiere"
__contact__ = "blottiere.paul@gmail.com"
__copyright__ = "Copyright 2020, Paul Blottiere"
__date__ = "2020/10/10"
__email__ = "blottiere.paul@gmail.com"
__license__ = "GPLv3"

import os
from src.core.changedetector.evi import LittoDynChangeDetectorEvi
from src.core.changedetector.pca import LittoDynChangeDetectorPca
from src.core.changedetector.ndvi import LittoDynChangeDetectorNdvi
from src.core.changedetector.ngrdi import LittoDynChangeDetectorNgrdi
from src.core.changedetector.norm_cos import LittoDynChangeDetectorNormCos
from src.core.changedetector.norm_corr import LittoDynChangeDetectorNormCorr
from src.core.changedetector.norm_euclid import LittoDynChangeDetectorNormEuclid

cwd = os.path.dirname(os.path.realpath(__file__))
img1 = os.path.join(cwd, "20170706_102911_0f43_AnalyticMS_SR.tif")
img2 = os.path.join(cwd, "20180723_104602_103c_AnalyticMS_SR.tif")
roi = os.path.join(cwd, "roi.shp")
result = os.path.join(cwd, "pca.tif")

#detector = LittoDynChangeDetectorPCA(img1,
#                               img2,
#                               roi
#                               )
#detector.detect()
#detector.save(result)

dict_algos={"PCA":LittoDynChangeDetectorPca,
               "EUCL":LittoDynChangeDetectorNormEuclid,
               "CORR":LittoDynChangeDetectorNormCorr,
               "COS":LittoDynChangeDetectorNormCos,
               "NDVI":LittoDynChangeDetectorNdvi,
               "EVI":LittoDynChangeDetectorEvi,
               "NGRDI":LittoDynChangeDetectorNgrdi}


for mykey in dict_algos.keys():
    myobj=dict_algos[mykey](img1,
                            img2,
                            roi,
    )
    myobj.detect()

    res = os.path.join(cwd, "{}.tif".format(mykey))
    myobj.save(res)
