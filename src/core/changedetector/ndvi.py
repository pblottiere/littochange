# -*- coding: utf-8 -*-

__author__ = "Paul Blottiere"
__contact__ = "blottiere.paul@gmail.com"
__copyright__ = "Copyright 2020, Paul Blottiere"
__date__ = "2020/10/10"
__email__ = "blottiere.paul@gmail.com"
__license__ = "GPLv3"

from .vi import LittoDynChangeDetectorVi


class LittoDynChangeDetectorNdvi(LittoDynChangeDetectorVi):
    """
    A change with ndvi
    Normalized vegetation index (https://www.indexdatabase.de/db/i-single.php?id=58)
    Simple
    NDVI = (NIR-R)/(NIR+R)
    """

    def _vi(self, img):
        """
        ndvi of image
        """
        return (img[:, :, 3] - img[:, :, 2]) / (img[:, :, 3] + img[:, :, 2])
