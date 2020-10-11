# -*- coding: utf-8 -*-

__author__ = "Paul Blottiere"
__contact__ = "blottiere.paul@gmail.com"
__copyright__ = "Copyright 2020, Paul Blottiere"
__date__ = "2020/10/10"
__email__ = "blottiere.paul@gmail.com"
__license__ = "GPLv3"

import subprocess
from qgis.core import QgsApplication

from .src.gui.provider.provider import LittoDynProvider


def classFactory(iface):
    return LittoDyn(iface)


class LittoDyn(object):
    def __init__(self, iface):
        self.iface = iface
        self.provider = None
        self.install_deps()

    def initProcessing(self):
        self.provider = LittoDynProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def initGui(self):
        self.initProcessing()

    def unload(self):
        QgsApplication.processingRegistry().removeProvider(self.provider)

    def install_deps(self):
        deps = ["numpy", "scipy", "gdal", "scikit-learn"]
        for dep in deps:
            cmd = ["python3", "-m", "pip", "install", dep, "--user"]
            output = subprocess.check_output(cmd)
