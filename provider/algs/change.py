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
from qgis.core import (QgsProject,
                       QgsMapLayer,
                       QgsMessageLog,
                       QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterDefinition,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink)

from processing.gui.wrappers import WidgetWrapper


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

            if name == 'INFO_DATE':
                w_date = mw.wrappers[name]

            if name == 'INPUT_RASTER_1':
                w_raster_1 = mw.wrappers[name]

            if name == 'INPUT_RASTER_2':
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

    def __init__(self, name='', description='', options=[], default=None, isSource=False,
                 multiple=False, optional=False):

        QgsProcessingParameterDefinition.__init__(self, name, description, default, optional)

        self.setMetadata({
            'widget_wrapper': {
                'class': LittoDynRasterComboBoxWrapper}})


class LittoDynValueWrapper(WidgetWrapper):

    def __init__(self, param, dialog, row=0, col=0, **kwargs):
        super().__init__(param, dialog, row, col, **kwargs)

    def createWidget(self):
        self.widget = QLineEdit()
        self.widget.setReadOnly(True)
        return self.widget

    def setValue(self, val):
        self.widget.setText(val)


class LittoDynDateParameter(QgsProcessingParameterDefinition):

    def __init__(self, name='', description='', options=[], default=None, isSource=False,
                 multiple=False, optional=False):

        QgsProcessingParameterDefinition.__init__(self, name, description, default, optional)

        self.setMetadata({
            'widget_wrapper': {
                'class': LittoDynValueWrapper}})


class ChangeDetectionAlgorithm(QgsProcessingAlgorithm):
    INPUT_EXTENT = 'INPUT_EXTENT'
    INPUT_RASTER_1 = 'INPUT_RASTER_1'
    INPUT_RASTER_2 = 'INPUT_RASTER_2'
    INFO_DATE = 'INFO_DATE'
    OUTPUT = 'OUTPUT'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ChangeDetectionAlgorithm()

    def name(self):
        return 'changedetection'

    def displayName(self):
        return self.tr('Change Detection')

    def shortHelpString(self):
        return self.tr("Change Detection")

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_EXTENT,
                self.tr('Extent'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        self.addParameter(
            LittoDynRasterParameter(
                self.INPUT_RASTER_1,
                self.tr('Raster 1')
            )
        )

        self.addParameter(
            LittoDynRasterParameter(
                self.INPUT_RASTER_2,
                self.tr('Raster 2')
            )
        )

        self.addParameter(
            LittoDynDateParameter(
                self.INFO_DATE,
                self.tr('Days between rasters')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        extent = self.parameterAsSource(
            parameters,
            self.INPUT_EXTENT,
            context
        )

        raster_1_id = self.parameterAsString(
            parameters,
            self.INPUT_RASTER_1,
            context
        )
        raster_1 = QgsProject.instance().mapLayer(raster_1_id)

        raster_2_id = self.parameterAsString(
            parameters,
            self.INPUT_RASTER_2,
            context
        )
        raster_2 = QgsProject.instance().mapLayer(raster_2_id)

        name = "{}_{}".format(raster_1.name(), raster_2.name())
        root = QgsProject.instance().layerTreeRoot()
        group = root.addGroup(name)

        return {}

        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.
        source = self.parameterAsSource(
            parameters,
            self.INPUT,
            context
        )

        # If source was not found, throw an exception to indicate that the algorithm
        # encountered a fatal error. The exception text can be any string, but in this
        # case we use the pre-built invalidSourceError method to return a standard
        # helper text for when a source cannot be evaluated
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            source.fields(),
            source.wkbType(),
            source.sourceCrs()
        )

        # Send some information to the user
        feedback.pushInfo('CRS is {}'.format(source.sourceCrs().authid()))

        # If sink was not created, throw an exception to indicate that the algorithm
        # encountered a fatal error. The exception text can be any string, but in this
        # case we use the pre-built invalidSinkError method to return a standard
        # helper text for when a sink cannot be evaluated
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        # Compute the number of steps to display within the progress bar and
        # get features from source
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        features = source.getFeatures()

        for current, feature in enumerate(features):
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                break

            # Add a feature in the sink
            sink.addFeature(feature, QgsFeatureSink.FastInsert)

            # Update the progress bar
            feedback.setProgress(int(current * total))

        # To run another Processing algorithm as part of this algorithm, you can use
        # processing.run(...). Make sure you pass the current context and feedback
        # to processing.run to ensure that all temporary layer outputs are available
        # to the executed algorithm, and that the executed algorithm can send feedback
        # reports to the user (and correctly handle cancellation and progress reports!)
        if False:
            buffered_layer = processing.run("native:buffer", {
                'INPUT': dest_id,
                'DISTANCE': 1.5,
                'SEGMENTS': 5,
                'END_CAP_STYLE': 0,
                'JOIN_STYLE': 0,
                'MITER_LIMIT': 2,
                'DISSOLVE': False,
                'OUTPUT': 'memory:'
            }, context=context, feedback=feedback)['OUTPUT']

        # Return the results of the algorithm. In this case our only result is
        # the feature sink which contains the processed features, but some
        # algorithms may return multiple feature sinks, calculated numeric
        # statistics, etc. These should all be included in the returned
        # dictionary, with keys matching the feature corresponding parameter
        # or output names.
        return {self.OUTPUT: dest_id}
