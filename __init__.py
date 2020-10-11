# -*- coding: utf-8 -*-

__author__ = "Paul Blottiere"
__contact__ = "blottiere.paul@gmail.com"
__copyright__ = "Copyright 2020, Paul Blottiere"
__date__ = "2020/10/10"
__email__ = "blottiere.paul@gmail.com"
__license__ = "GPLv3"

from qgis.core import QgsApplication, Qgis

from .src.core.deps import Deps


def classFactory(iface):
    return LittoDyn(iface)


class LittoDyn(object):
    def __init__(self, iface):
        self.iface = iface
        self.provider = None

        deps = Deps()
        self.fresh_install = deps.run()

    def initProcessing(self):
        if self.fresh_install:
            widget = self.iface.messageBar().createMessage("LittoDyn", "Some missing dependencies have been installed at startup. QGIS have to be restarted to use LittoDyn plugin.")
            self.iface.messageBar().pushWidget(widget, Qgis.Warning)
            return

        from .src.gui.provider.provider import LittoDynProvider
        self.provider = LittoDynProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def initGui(self):
        self.initProcessing()

    def unload(self):
        if not self.provider:
            return

        QgsApplication.processingRegistry().removeProvider(self.provider)
