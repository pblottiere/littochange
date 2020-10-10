# -*- coding: utf-8 -*-

__author__ = "Paul Blottiere"
__contact__ = "blottiere.paul@gmail.com"
__copyright__ = "Copyright 2020, Paul Blottiere"
__date__ = "2020/10/10"
__email__ = "blottiere.paul@gmail.com"
__license__ = "GPLv3"

from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtWidgets import QComboBox, QLineEdit

from qgis import processing
from qgis.core import (
    QgsProject,
    QgsMapLayer,
    QgsGeometry,
    QgsFields,
    QgsMessageLog,
    QgsVectorLayer,
    QgsProcessing,
    QgsFeatureSink,
    QgsProcessingContext,
    QgsProcessingUtils,
    QgsProcessingException,
    QgsProcessingAlgorithm,
    QgsProcessingParameterDefinition,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterFeatureSink,
)

from processing.gui.wrappers import WidgetWrapper
from processing.core.ProcessingConfig import ProcessingConfig


class LittoDynRasterComboBoxWrapper(WidgetWrapper):
    def __init__(self, param, dialog, row=0, col=0, **kwargs):
        super().__init__(param, dialog, row, col, **kwargs)

    def createWidget(self):
        widget = QComboBox()
        widget.addItem("")
        widget.currentIndexChanged.connect(self.event)

        project = QgsProject.instance()
        for id, layer in project.mapLayers().items():
            if layer.type() != QgsMapLayer.RasterLayer:
                continue

            if not layer.temporalProperties().isActive():
                continue

            widget.addItem(id)

        return widget

    def value(self):
        return self.widget.currentText()

    def layer(self):
        return QgsProject.instance().mapLayer(self.widget.currentText())

    def event(self):
        w_raster_1 = None
        w_raster_2 = None
        w_date = None

        mw = self.dialog.mainWidget()
        if not mw:
            return

        for parameter in self.dialog.algorithm().parameterDefinitions():
            name = parameter.name()

            if name == "INFO_DATE":
                w_date = mw.wrappers[name]

            if name == "INPUT_RASTER_1":
                w_raster_1 = mw.wrappers[name]

            if name == "INPUT_RASTER_2":
                w_raster_2 = mw.wrappers[name]

        if w_raster_1 and w_raster_2 and w_date:
            raster_1_layer = w_raster_1.layer()
            raster_2_layer = w_raster_2.layer()

            if not raster_1_layer or not raster_2_layer:
                return

            raster_1_prop = raster_1_layer.temporalProperties()
            raster_2_prop = raster_2_layer.temporalProperties()

            begin_1 = raster_1_prop.fixedTemporalRange().begin()
            begin_2 = raster_2_prop.fixedTemporalRange().begin()

            days = begin_1.daysTo(begin_2)
            w_date.setValue(str(days))


class LittoDynRasterParameter(QgsProcessingParameterDefinition):
    def __init__(
        self,
        name="",
        description="",
        options=[],
        default=None,
        isSource=False,
        multiple=False,
        optional=False,
    ):

        QgsProcessingParameterDefinition.__init__(
            self, name, description, default, optional
        )

        self.setMetadata({"widget_wrapper": {"class": LittoDynRasterComboBoxWrapper}})


class LittoDynValueWrapper(WidgetWrapper):
    def __init__(self, param, dialog, row=0, col=0, **kwargs):
        super().__init__(param, dialog, row, col, **kwargs)

    def createWidget(self):
        self.widget = QLineEdit()
        self.widget.setReadOnly(True)
        return self.widget

    def setValue(self, val):
        self.widget.setText(val)

    def value(self):
        return 0


class LittoDynDateParameter(QgsProcessingParameterDefinition):
    def __init__(
        self,
        name="",
        description="",
        options=[],
        default=None,
        isSource=False,
        multiple=False,
        optional=False,
    ):

        QgsProcessingParameterDefinition.__init__(
            self, name, description, default, optional
        )

        self.setMetadata({"widget_wrapper": {"class": LittoDynValueWrapper}})


class LittoDynChangeDetectorAlgorithm(QgsProcessingAlgorithm):
    INPUT_EXTENT = "INPUT_EXTENT"
    INPUT_RASTER_1 = "INPUT_RASTER_1"
    INPUT_RASTER_2 = "INPUT_RASTER_2"
    INFO_DATE = "INFO_DATE"
    OUTPUT_BUFFER = "OUTPUT_BUFFER"

    def tr(self, string):
        return QCoreApplication.translate("Processing", string)

    def createInstance(self):
        return LittoDynChangeDetectorAlgorithm()

    def name(self):
        return "changedetection"

    def displayName(self):
        return self.tr("Change Detection")

    def shortHelpString(self):
        return self.tr("Change Detection")

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_EXTENT, self.tr("Extent"), [QgsProcessing.TypeVectorPolygon]
            )
        )

        self.addParameter(
            LittoDynRasterParameter(self.INPUT_RASTER_1, self.tr("Raster 1"))
        )

        self.addParameter(
            LittoDynRasterParameter(self.INPUT_RASTER_2, self.tr("Raster 2"))
        )

        self.addParameter(
            LittoDynDateParameter(self.INFO_DATE, self.tr("Days between rasters"))
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT_BUFFER, self.tr("Buffered extent")
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        extent = self.parameterAsVectorLayer(parameters, self.INPUT_EXTENT, context)

        raster_1_id = self.parameterAsString(parameters, self.INPUT_RASTER_1, context)
        raster_1 = QgsProject.instance().mapLayer(raster_1_id)

        raster_2_id = self.parameterAsString(parameters, self.INPUT_RASTER_2, context)
        raster_2 = QgsProject.instance().mapLayer(raster_2_id)

        (sink, self.dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT_BUFFER,
            context,
            QgsFields(),
            extent.wkbType(),
            extent.sourceCrs(),
        )

        name = "{}_{}".format(raster_1.name(), raster_2.name())
        ProcessingConfig.setSettingValue(ProcessingConfig.RESULTS_GROUP_NAME, name)

        for feature in extent.getFeatures():
            geom = feature.geometry()
            buffer = geom.buffer(
                0.001, 4, QgsGeometry.CapFlat, QgsGeometry.JoinStyleMiter, 100
            )
            feature.setGeometry(buffer)
            feature.setFields(QgsFields())
            sink.addFeature(feature)

        return {self.OUTPUT_BUFFER: self.dest_id}
