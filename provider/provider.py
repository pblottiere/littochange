# -*- coding: utf-8 -*-

__author__ = "Paul Blottiere"
__contact__ = "blottiere.paul@gmail.com"
__copyright__ = "Copyright 2020, Paul Blottiere"
__date__ = "2020/10/10"
__email__ = "blottiere.paul@gmail.com"
__license__ = "GPLv3"


from qgis.core import QgsProcessingProvider

from .algs.change import ChangeDetectionAlgorithm


class LittoDynProvider(QgsProcessingProvider):

    def loadAlgorithms(self, *args, **kwargs):
        self.addAlgorithm(ChangeDetectionAlgorithm())

    def id(self, *args, **kwargs):
        return 'littodyn'

    def name(self, *args, **kwargs):
        return self.tr('LittoDyn')

    def icon(self):
        return QgsProcessingProvider.icon(self)
