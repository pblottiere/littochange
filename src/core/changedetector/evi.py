# -*- coding: utf-8 -*-

__author__ = "Paul Blottiere"
__contact__ = "blottiere.paul@gmail.com"
__copyright__ = "Copyright 2020, Paul Blottiere"
__date__ = "2020/10/10"
__email__ = "blottiere.paul@gmail.com"
__license__ = "GPLv3"

from .vi import LittoDynChangeDetectorVi


class LittoDynChangeDetectorEvi(LittoDynChangeDetectorVi):
    """
    A change with evi
    * EVI : enhanced vegetation index (https://www.indexdatabase.de/db/i-single.php?id=16)
    More robuste to atmo effects
    EVI = 2.5 * ((NIR - R) / (NIR + 6 * R â 7.5 * B + 1))
    """

    def _vi(self,img):
        """
        evi of image
        """
        return 2.5*((img[:,:,3]-img[:,:,2])/(img[:,:,3]+6*img[:,:,2]-7.5*img[:,:,0]+1))
