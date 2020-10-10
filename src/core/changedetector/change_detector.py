#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import os
from osgeo import osr, gdal, ogr
import sys
import argparse

# import pylab
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from collections import Counter


class Change_detector(object):
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


class Change_detector_norm_euclid(Change_detector):
    """
    A change with only euclidian distance
    """

    def _dodetect(self):
        self.change = np.sqrt(np.sum((self.img1 - self.img2) ** 2, axis=2))


class Change_detector_PCA(Change_detector):
    """
    A change detector with PCA + kmeans
    """

    def _find_vector_set(self, diff_image):
        vector_set = np.reshape(
            diff_image, [diff_image.shape[0] * diff_image.shape[1], diff_image.shape[2]]
        )
        mean_vec = np.mean(vector_set, axis=0)
        vector_set -= mean_vec

        return vector_set, mean_vec

    def _find_FVS(self, EVS, diff_image, mean_vec):

        feature_vector_set = np.reshape(
            diff_image, [diff_image.shape[0] * diff_image.shape[1], diff_image.shape[2]]
        )
        FVS = np.dot(feature_vector_set, EVS)
        FVS = FVS - mean_vec
        return FVS

    def _clustering(self, FVS, components, new):

        kmeans = KMeans(components, verbose=0)
        kmeans.fit(FVS)
        output = kmeans.predict(FVS)
        count = Counter(output)

        least_index = min(count, key=count.get)
        change_map = np.reshape(output, new)

        return least_index, change_map

    def _dodetect(self):

        diff_image = abs(self.img1 - self.img2)

        vector_set, mean_vec = self._find_vector_set(diff_image)

        pca = PCA()
        pca.fit(vector_set)
        EVS = pca.components_

        FVS = self._find_FVS(EVS, diff_image, mean_vec)

        components = 3
        least_index, change_map = self._clustering(
            FVS, components, [diff_image.shape[0], diff_image.shape[1]]
        )

        change_map[change_map == least_index] = 255
        change_map[change_map != 255] = 0

        self.change = change_map.astype(np.float32)


if __name__ == "__main__":

    # Command line parser
    parser = argparse.ArgumentParser(
        description="Compute change between images. Example : python change_detector.py ./test_data/20170706_102911_0f43_AnalyticMS_SR.tif ./test_data/20180723_104602_103c_AnalyticMS_SR.tif ./test_data/roi.shp ./test_data/change.tif"
    )
    parser.add_argument(
        "path_img1",
        type=str,
        help="Path of input images 1",
    )
    parser.add_argument(
        "path_img2",
        type=str,
        help="Path of input images 2",
    )
    parser.add_argument(
        "path_roi",
        type=str,
        help="Path of input ROI shapefile",
    )
    parser.add_argument("path_out", type=str, help="Path of output change image")

    args = parser.parse_args()

    myobj = Change_detector_PCA(
        args.path_img1,
        args.path_img2,
        args.path_roi,
    )
    myobj.detect()
    myobj.save(args.path_out)
