# -*- coding: utf-8 -*-

__author__ = "Paul Blottiere"
__contact__ = "blottiere.paul@gmail.com"
__copyright__ = "Copyright 2020, Paul Blottiere"
__date__ = "2020/10/10"
__email__ = "blottiere.paul@gmail.com"
__license__ = "GPLv3"

import numpy as np
from osgeo import gdal, ogr


class LittoDynChangeDetector(object):
    """
    Generic class for change detector
    Implement common methods (read, write, ROI...) to all detectors
    """

    def __init__(self, path_img1, path_img2, path_roi):
        self.path_img1 = path_img1
        self.path_img2 = path_img2
        self.path_roi = path_roi
        self._load_inputs()

    def _load_inputs(self):
        ds = gdal.Open(self.path_img1, gdal.GA_ReadOnly)
        self.geo = ds.GetGeoTransform()
        self.proj = ds.GetProjection()
        self.cols = ds.RasterXSize
        self.rows = ds.RasterYSize
        self.bands = ds.RasterCount
        self.img1 = np.zeros([self.rows, self.cols, self.bands], dtype=np.float)
        for i in range(self.bands):
            self.img1[:, :, i] = ds.GetRasterBand(i + 1).ReadAsArray()
        self.img2 = np.zeros([self.rows, self.cols, self.bands], dtype=np.float)
        ds = gdal.Open(self.path_img2, gdal.GA_ReadOnly)
        for i in range(self.bands):
            self.img2[:, :, i] = ds.GetRasterBand(i + 1).ReadAsArray()
        self._init_mask()

    def _init_mask(self):
        """
        Rasterize roi on dataset area
        """
        driver = ogr.GetDriverByName("ESRI Shapefile")
        dataSource = driver.Open(self.path_roi, 1)
        layer = dataSource.GetLayer()
        # Memory dataset for rasterized roi
        target_ds = gdal.GetDriverByName("MEM").Create(
            "", self.cols, self.rows, 1, gdal.GDT_Byte
        )
        target_ds.SetGeoTransform(self.geo)
        target_ds.SetProjection(self.proj)
        datainit = np.zeros([self.rows, self.cols], dtype=np.int8)
        myband = target_ds.GetRasterBand(1)
        myband.WriteArray(datainit)
        gdal.RasterizeLayer(target_ds, (1,), layer, burn_values=(1,))
        self.roi_mask = target_ds.GetRasterBand(1).ReadAsArray()

    def detect(self):
        self._dodetect()
        self._apply_roi()

    def _dodetect(self):
        # Generic case here, return 0
        self.change = np.zeros([self.rows, self.cols], dtype=np.float)

    def _apply_roi(self):
        self.change[np.where(self.roi_mask == 0)] = np.nan

    def save(self, path_out):
        driver = gdal.GetDriverByName("GTiff")
        self.ds = driver.Create(path_out, self.cols, self.rows, 1, gdal.GDT_Float32)
        self.ds.SetProjection(self.proj)
        self.ds.SetGeoTransform(self.geo)
        self.ds.GetRasterBand(1).WriteArray(self.change)
