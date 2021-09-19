# -*- coding: utf-8 -*-

# @FileName: AnalysisThread.py
# @Time    : 2021-03-05 9:55
# @Author  : Dorad, cug.xia@gmail.com
# @Blog    ：https://blog.cuger.cn


from PyQt5.QtCore import QThread, pyqtSignal

from ImageTool import *


# 所有 mask, 0 均是被遮住的部分, 不要的

class AnalysisThread(QThread):
    '''
    Analysis Thread for global OTSU
    '''
    process = pyqtSignal(int)
    finish = pyqtSignal(np.ndarray)

    def __init__(self):
        QThread.__init__(self)
        self.grayImage = None
        self.labelImage = None
        self.edgeMask = None  # inner the polygon is True
        self.ROIsMaskList = None  # inner the ROI is True

    def setParameters(self, grayImage: np.array, cropPolygon: QPolygonF = None, ROIs: list = []):
        self.grayImage = grayImage
        if not cropPolygon:
            self.edgeMask = np.zeros((self.grayImage.shape[0], self.grayImage.shape[1]), dtype=bool)
        else:
            self.edgeMask = QPolygon2Mask(self.grayImage.shape[0], self.grayImage.shape[1], cropPolygon)
        self.ROIsMaskList = []
        for roi in ROIs:
            self.ROIsMaskList.append(
                np.logical_and(QPolygon2Mask(self.grayImage.shape[0], self.grayImage.shape[1], roi), self.edgeMask))

    def run(self):
        if type(self.grayImage) == np.array:
            return
        self.labelImage = OtsuWithMask2bw(self.grayImage, self.edgeMask == 0)
        self.process.emit(100)
        self.finish.emit(self.labelImage)


class ROIsToZonesAnalysisThread(AnalysisThread):
    def __init__(self):
        AnalysisThread.__init__(self)

    def run(self):
        bw = np.zeros(self.grayImage.shape, dtype=bool)
        for i, roiMask in enumerate(self.ROIsMaskList):
            self.process.emit(i / len(self.ROIsMaskList) * 100)
            bw = np.logical_or(roiMask, bw)
        self.finish.emit(bw)


class ROIsOTSUAnalysisThread(AnalysisThread):
    def __init__(self):
        AnalysisThread.__init__(self)

    def run(self):
        bw = np.zeros(self.grayImage.shape, dtype=bool)
        for i, roiMask in enumerate(self.ROIsMaskList):
            self.process.emit(i / len(self.ROIsMaskList) * 100)
            roiBw = OtsuWithMask2bw(self.grayImage, roiMask == 0)
            bw = np.logical_or(roiBw, bw)
        self.finish.emit(bw)


class RissAnalysisThread(ROIsOTSUAnalysisThread):
    def __init__(self):
        ROIsOTSUAnalysisThread.__init__(self)

    def run(self):
        roisMask = np.zeros(self.grayImage.shape, dtype=bool)
        for i, roiMask in enumerate(self.ROIsMaskList):
            roisMask = np.logical_or(roiMask, roisMask)
            self.process.emit(i / len(self.ROIsMaskList) * 100)
        # get threshold by riss method based on rois
        rissThreshold = self._getRissThresholdWithROIs(self.grayImage, roisMask)
        bw = GetBinaryImageWithThresholdWithMask(self.grayImage, self.edgeMask == 0, rissThreshold)
        self.finish.emit(bw)

    @staticmethod
    def _getRissThresholdWithROIs(image: np.array, mask: np.array):
        '''
        :param image:
        :param mask:
        :return:
        '''
        masked = np.ma.masked_array(image, mask == 0)
        # calculate the mean and std
        mu = np.mean(masked.compressed())
        sigma = np.std(masked.compressed())
        threshold = mu + 1.96 * sigma
        return threshold
