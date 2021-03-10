# -*- coding: utf-8 -*-

# @FileName: ImageRegistration.py
# @Time    : 2021-03-10 15:07
# @Author  : Dorad, cug.xia@gmail.com
# @Blog    ：https://blog.cuger.cn

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import datetime, os

import matplotlib

matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from skimage import io, color
import numpy as np


class ImageRegWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.leftLayout = QVBoxLayout()
        self.tabWidget = QTabWidget()

        self.preImageCanvas = Canvas()
        self.damageImageCanvas = Canvas()
        self.featureMatchsCanvas = Canvas()
        self.resultCanvas = Canvas()

        self.tabWidget.addTab(self.preImageCanvas, 'Pre Image')
        self.tabWidget.addTab(self.damageImageCanvas, 'Damage Image')
        self.tabWidget.addTab(self.featureMatchsCanvas, 'Feature Matching')
        self.tabWidget.addTab(self.resultCanvas, 'Result')

        self.buttonLoadPreImage = QPushButton('Load Pre Image')
        self.buttonLoadPreImage.clicked.connect(self.__loadPreImage)
        self.buttonLoadDamageImage = QPushButton('Load Damage Image')
        self.buttonLoadDamageImage.clicked.connect(self.__loadDamageImage)
        self.selectFeatureBox = QComboBox()
        self.selectFeatureBox.addItems([
            'SIFT',
            'ORB',
        ])
        self.lineEditMaxFeaturePoints = QLineEdit('500')
        self.lineEditMaxFeaturePoints.setValidator(QIntValidator(20, 5000))
        self.buttonAnalysis = QPushButton('Analysis')
        self.buttonAnalysis.clicked.connect(self.__analysis)

        groupBoxImageReg = QGroupBox('Image Registration')
        groupBoxImageReg.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        vBox = QVBoxLayout()
        vBox.addWidget(self.buttonLoadPreImage)
        vBox.addWidget(self.buttonLoadDamageImage)
        formBox = QFormLayout()
        formBox.addRow('Feature', self.selectFeatureBox)
        formBox.addRow('MaxFeatures', self.lineEditMaxFeaturePoints)
        vBox.addLayout(formBox)
        vBox.addWidget(self.buttonAnalysis)
        groupBoxImageReg.setLayout(vBox)

        groupBoxExport = QGroupBox('Export')
        self.selectSubType = QComboBox()
        self.selectSubType.addItems([
            'Pre-Damage',
            'Damage-Pre',
            'Both'
        ])
        self.buttonLoadImageToSDZM = QPushButton('Load to SDZM toolbox')
        self.buttonExportAsPng = QPushButton('Export as *.png')
        exportFormBox = QFormLayout()
        exportFormBox.addRow('Sub Type', self.selectSubType)
        exportVBox = QVBoxLayout()
        exportVBox.addLayout(exportFormBox)
        exportVBox.addWidget(self.buttonLoadImageToSDZM)
        exportVBox.addWidget(self.buttonExportAsPng)
        groupBoxExport.setLayout(exportVBox)

        self.leftLayout.addWidget(groupBoxImageReg)
        self.leftLayout.addStretch()
        self.leftLayout.addWidget(groupBoxExport)

        hBox = QHBoxLayout()
        hBox.addLayout(self.leftLayout)
        hBox.addWidget(self.tabWidget)
        self.setLayout(hBox)

        self.setMinimumSize(800, 600)
        self.initUi()

    def initUi(self):
        if not (hasattr(self, 'projectWorkPath') and self.projectWorkPath):
            self.projectWorkPath = os.getcwd()
        self.preImage = None
        self.damageImage = None
        self.alignedImage = None

    def __loadPreImage(self):
        filePath, fileType = QFileDialog.getOpenFileName(self, caption='Choose the image',
                                                         directory=self.projectWorkPath,
                                                         filter='Image (*.jpg);;Image (*.png);;Image (*.tif)')
        if not filePath:
            QMessageBox.warning(self, 'No File Selected', 'No image file is selected.')
            return
        self.initUi()
        self.projectWorkPath, _ = os.path.split(filePath)
        self.__setPreImage(io.imread(filePath))

    def __loadDamageImage(self):
        filePath, fileType = QFileDialog.getOpenFileName(self, caption='Choose the image',
                                                         directory=self.projectWorkPath,
                                                         filter='Image (*.jpg);;Image (*.png);;Image (*.tif)')
        if not filePath:
            QMessageBox.warning(self, 'No File Selected', 'No image file is selected.')
            return
        self.projectWorkPath, _ = os.path.split(filePath)
        self.__setDamageImage(io.imread(filePath))

    def __analysis(self):
        IT = ImageRegThread()
        IT.setParameters(self.preImage, self.damageImage, self.selectFeatureBox.currentText())
        IT.error.connect(self.__errorHandle)
        IT.finish.connect(self.__analysisFinished)
        IT.run()

    def __setPreImage(self, image):
        # plt.close(1)
        self.preImage = image
        self.preImageCanvas.imshow(self.preImage, 'Image of Undamaged Specimen')
        self.tabWidget.setCurrentWidget(self.preImageCanvas)

    def __setDamageImage(self, image):
        # plt.close(1)
        self.damageImage = image
        self.damageImageCanvas.imshow(self.damageImage, 'Image of Damaged Specimen')
        self.tabWidget.setCurrentWidget(self.damageImageCanvas)

    def __setMatchesImage(self, image):
        self.featureMatchsCanvas.imshow(image, 'Match Result of Features')
        self.tabWidget.setCurrentWidget(self.featureMatchsCanvas)

    def __setAlignedImage(self, image):
        self.alignedImage = image
        self.resultCanvas.imshow(self.alignedImage, 'Aligned Image of Damaged Specimen')
        self.tabWidget.setCurrentWidget(self.resultCanvas)

    def __errorHandle(self, error):
        QMessageBox.warning(self, 'Error', error)

    def __analysisFinished(self, imageAligned, matchesImage):
        self.__setMatchesImage(matchesImage)
        self.__setAlignedImage(imageAligned)


# matplotlib 绘图

class Canvas(FigureCanvas):
    def __init__(self, dpi=200):
        self.fig = Figure(dpi=dpi)
        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def imshow(self, image, title=None, mod='111'):
        axes = self.fig.add_subplot(mod)
        axes.imshow(image)
        if not title:
            axes.set_title(title)
        self.draw()


# 图像对齐

class ImageRegThread(QThread):
    finish = pyqtSignal([np.ndarray, np.ndarray], name='analysis finished')
    error = pyqtSignal([int], name='error')

    def __init__(self):
        QThread.__init__(self)

    def setParameters(self, imageRef, image, algorithm='ORB', maxFeatures=1000):
        self.imageRef = imageRef
        self.image = image
        self.algorithm = algorithm
        self.maxFeatures = maxFeatures

    def run(self):
        import cv2 as cv2
        self.algorithm = self.algorithm.upper()
        if self.algorithm not in ['ORB', 'SIFT']:
            self.error.emit('The algorithm not exist.')
            return
        # select detector
        if self.algorithm == 'SIFT':
            descExtractor = cv2.SIFT_create()
        elif self.algorithm == 'ORB':
            descExtractor = cv2.ORB_create(self.maxFeatures)
        # find keypoints with detector
        kpRef, desRef = descExtractor.detectAndCompute(self.imageRef, None)
        kp, des = descExtractor.detectAndCompute(self.image, None)
        # match features
        bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)
        matches = bf.match(desRef, des)
        matches = sorted(matches, key=lambda x: x.distance)
        matches = matches[0:100]
        MIN_MATCH_COUNT = 10
        # ransac
        if len(matches) > MIN_MATCH_COUNT:
            dst_pts = np.float32([kpRef[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
            src_pts = np.float32([kp[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
            M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
            matchesMask = mask.ravel().tolist()
        else:
            self.error.emit("Not enough matches are found - {}/{}".format(len(matches), MIN_MATCH_COUNT))
            matchesMask = None
            return
        draw_params = dict(matchColor=(0, 255, 0),  # draw matches in green color
                           singlePointColor=None,
                           matchesMask=matchesMask,  # draw only inliers
                           flags=2)
        matchesImage = cv2.drawMatches(self.imageRef, kpRef, self.image, kp, matches, None, **draw_params)
        imageWarped = cv2.warpPerspective(self.image, M, (self.imageRef.shape[1], self.imageRef.shape[0]))
        self.finish.emit(imageWarped, matchesImage)


import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = ImageRegWidget()
    mainWindow.show()
    sys.exit(app.exec_())
    # open('./data/MJ1-1/shear-down.jpg')
    # imageRef = io.imread('./data/MJ1-1/origin-down.jpg')
    # image = io.imread('./data/MJ1-1/shear-down.jpg')
    # IT = ImageRegThread()
    # IT.setParameters(imageRef, image)
    #
    #
    # def finish(image, matches):
    #     fig = plt.figure()
    #     ax0 = fig.add_subplot(211)
    #     ax0.imshow(image)
    #     ax1 = fig.add_subplot(212)
    #     ax1.imshow(matches)
    #     plt.show()
    #
    #
    # IT.finish.connect(finish)
