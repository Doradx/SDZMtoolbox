# -*- coding: utf-8 -*-

# @FileName: AnalysisThread.py
# @Time    : 2021-03-05 9:55
# @Author  : Dorad, cug.xia@gmail.com
# @Blog    ：https://blog.cuger.cn

from PyQt5.QtCore import *
from PyQt5.QtGui import *
import numpy as np
from ImageTool import *


# 所有 mask, 1 均是被遮住的部分, 不要的

class AnalysisThread(QThread):
    process = pyqtSignal(int)
    finish = pyqtSignal(np.ndarray)

    def __init__(self):
        QThread.__init__(self)
        self.image = None
        self.labelImage = None
        self.mask = None

    def setParamters(self, grayImage: np.array, cropPolygon: QPolygonF):
        self.image = grayImage
        self.mask = QPolygon2Mask(self.image.shape[0], self.image.shape[1], cropPolygon)

    def run(self):
        if type(self.image) == np.array:
            return
        self.labelImage = OtsuWithMask2bw(self.image, self.mask == 0)
        self.process.emit(100)
        self.finish.emit(self.labelImage)


class ROIsOTSUAnalysisThread(AnalysisThread):
    def __init__(self):
        AnalysisThread.__init__(self)
        self.ROIs = None
        self.mask = None

    def setParamters(self, image: np.array, ROIs: list, cropPolygon: QPolygonF):
        self.image = image
        self.ROIs = ROIs
        self.mask = QPolygon2Mask(self.image.shape[0], self.image.shape[1], cropPolygon)

    def run(self):
        bw = np.zeros(self.image.shape, dtype=bool)
        for roi in self.ROIs:
            roiMask = QPolygon2Mask(self.image.shape[0], self.image.shape[1], roi)
            roiBw = OtsuWithMask2bw(self.image, roiMask)
            bw = np.logical_and(roiBw, bw)
        self.finish.emit(bw)


class RissAnalysisThread(ROIsOTSUAnalysisThread):
    def __init__(self):
        ROIsOTSUAnalysisThread.__init__(self)

    def run(self):
        roisMask = np.zeros(self.image.shape, dtype=bool)
        for roi in self.ROIs:
            roiMask = QPolygon2Mask(self.image.shape, roi)
            roisMask = np.logical_or(roiMask, roisMask)
        # get threshold by riss method based on rois
        rissThreshold = self._getRissThresholdWithROIs(self.image, roisMask)
        bw = GetBinaryImageWithThresholdWithMask(self.image, self.mask == 0, rissThreshold)
        self.finish.emit(bw)

    @staticmethod
    def _getRissThresholdWithROIs(image: np.array, mask: np.array):
        '''
        需要补充
        :param image:
        :param mask:
        :return:
        '''
        from skimage import filters
        masked = np.ma.masked_array(image, mask == 0)

        otsuThreshold = filters.threshold_otsu(masked.compressed())
        maskedImage = masked.filled(fill_value=0)
        bw = maskedImage >= otsuThreshold
        return bw
