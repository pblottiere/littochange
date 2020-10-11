# -*- coding: utf-8 -*-

__author__ = "Paul Blottiere"
__contact__ = "blottiere.paul@gmail.com"
__copyright__ = "Copyright 2020, Paul Blottiere"
__date__ = "2020/10/10"
__email__ = "blottiere.paul@gmail.com"
__license__ = "GPLv3"

from .vi import LittoDynChangeDetectorVi


class LittoDynChangeDetectorNgrdi(LittoDynChangeDetectorVi):
    """
    A change with NGRDI
    * NGDRI : https://www.indexdatabase.de/db/i-single.php?id=390)
    For sea bottom
    NGRDI= (Green - Red)/(Green + Red) `
    """

    def _vi(self,img):
        """
        ngrdi of image
        """
        return (img[:,:,1]-img[:,:,2])/(img[:,:,1]+img[:,:,2])
