# -*- coding: utf-8 -*-

__author__ = "Paul Blottiere"
__contact__ = "blottiere.paul@gmail.com"
__copyright__ = "Copyright 2020, Paul Blottiere"
__date__ = "2020/10/10"
__email__ = "blottiere.paul@gmail.com"
__license__ = "GPLv3"

import os
import tempfile
from qgis.PyQt.QtGui import QIcon

from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtWidgets import QComboBox, QLineEdit

from qgis import processing
from qgis.core import (
    Qgis,
    QgsFields,
    QgsProject,
    QgsWkbTypes,
    QgsMapLayer,
    QgsGeometry,
    QgsMessageLog,
    QgsProcessing,
    QgsFeatureSink,
    QgsRasterLayer,
    QgsVectorLayer,
    QgsProcessingUtils,
    QgsVectorFileWriter,
    QgsProcessingContext,
    QgsProcessingException,
    QgsProcessingAlgorithm,
    QgsProcessingParameterEnum,
    QgsProcessingParameterDefinition,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterRasterDestination,
)

from processing.gui.wrappers import WidgetWrapper
from processing.core.ProcessingConfig import ProcessingConfig

from littodyn.src.core.changedetector.evi import LittoDynChangeDetectorEvi
from littodyn.src.core.changedetector.pca import LittoDynChangeDetectorPca
from littodyn.src.core.changedetector.ndvi import LittoDynChangeDetectorNdvi
from littodyn.src.core.changedetector.ngrdi import LittoDynChangeDetectorNgrdi
from littodyn.src.core.changedetector.norm_cos import LittoDynChangeDetectorNormCos
from littodyn.src.core.changedetector.norm_corr import LittoDynChangeDetectorNormCorr
from littodyn.src.core.changedetector.norm_euclid import (
    LittoDynChangeDetectorNormEuclid,
)


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
    INPUT_ALG_NAME = "INPUT_ALG_NAME"
    INFO_DATE = "INFO_DATE"
    OUTPUT_BUFFER = "OUTPUT_BUFFER"
    OUTPUT_CHANGES = "OUTPUT_CHANGES"

    def tr(self, string):
        return QCoreApplication.translate("Processing", string)

    def icon(self):
        cwd = os.path.dirname(os.path.realpath(__file__))
        return QIcon(os.path.join(cwd, "icon.png"))

    def createInstance(self):
        return LittoDynChangeDetectorAlgorithm()

    def name(self):
        return "changedetection"

    def displayName(self):
        return self.tr("Change Detection")

    def shortHelpString(self):
        return self.tr("Change Detection")

    def initAlgorithm(self, config=None):
        self.options = [
            "PCA",
            "EVI",
            "NDVI",
            "NGRDI",
            "Euclidean Norm",
            "Correlation Norm",
            "Cosine Norm",
        ]
        self.addParameter(
            QgsProcessingParameterEnum(
                self.INPUT_ALG_NAME,
                self.tr("Algorithm"),
                options=self.options,
                defaultValue=0,
            )
        )

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

        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT_CHANGES, self.tr("Changes")
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        # extract input parameters
        alg = self.parameterAsEnum(parameters, self.INPUT_ALG_NAME, context)

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

        outputFile = self.parameterAsRasterLayer(
            parameters, self.OUTPUT_CHANGES, context
        )

        # create a temporary vector layer
        tmp = tempfile.mkdtemp()
        path_roi = os.path.join(tmp, "roi.shp")
        writer = QgsVectorFileWriter(
            path_roi,
            "UTF-8",
            QgsFields(),
            QgsWkbTypes.Polygon,
            extent.sourceCrs(),
            "ESRI Shapefile",
        )

        # create buffered extent and update temporary shp for detector
        for feature in extent.getFeatures():
            geom = feature.geometry()
            buffer = geom.buffer(
                10, 100, QgsGeometry.CapFlat, QgsGeometry.JoinStyleMiter, 100
            )
            feature.setGeometry(buffer)
            feature.setFields(QgsFields())
            sink.addFeature(feature)
            writer.addFeature(feature)
        del writer

        # run change detector
        path1 = raster_1.source()
        path2 = raster_2.source()
        detector = LittoDynChangeDetectorPca(path1, path2, path_roi)
        if alg == 1:
            detector = LittoDynChangeDetectorEvi(path1, path2, path_roi)
        elif alg == 2:
            detector = LittoDynChangeDetectorNdvi(path1, path2, path_roi)
        elif alg == 3:
            detector = LittoDynChangeDetectorNgrdi(path1, path2, path_roi)
        elif alg == 4:
            detector = LittoDynChangeDetectorNormEuclid(path1, path2, path_roi)
        elif alg == 5:
            detector = LittoDynChangeDetectorNormCorr(path1, path2, path_roi)
        elif alg == 6:
            detector = LittoDynChangeDetectorNormCos(path1, path2, path_roi)
        detector.detect()

        # store output layers in group
        if Qgis.QGIS_VERSION_INT >= 31500:
            alg_name = self.options[alg].lower().replace(" ", "_")
            name = "{}_{}_{}".format(raster_1.name(), raster_2.name(), alg_name)
            ProcessingConfig.setSettingValue(ProcessingConfig.RESULTS_GROUP_NAME, name)

        # save result in temporary file
        tmp = tempfile.mkdtemp()
        path_changes = os.path.join(tmp, "changes.tif")
        detector.save(path_changes)

        rl = QgsRasterLayer(path_changes, "changes", "gdal")
        context.temporaryLayerStore().addMapLayer(rl)
        context.addLayerToLoadOnCompletion(
            rl.id(),
            QgsProcessingContext.LayerDetails(
                "Changes", context.project(), self.OUTPUT_CHANGES
            ),
        )

        return {
            self.OUTPUT_CHANGES: rl.id(),
            self.OUTPUT_BUFFER: self.dest_id,
            self.OUTPUT_CHANGES: rl.id(),
        }
