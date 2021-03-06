# -*- coding: utf-8 -*-

# @FileName: ImageRegistration.py
# @Time    : 2021-03-10 15:07
# @Author  : Dorad, cug.xia@gmail.com
# @Blog    ：https://blog.cuger.cn

import datetime
import os

import matplotlib
from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QPushButton, QComboBox, QGroupBox, QSpinBox, QSizePolicy, \
    QFormLayout, QHBoxLayout, QFileDialog, QMessageBox, QApplication

matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from skimage import io
from ImageTool import *
import cv2 as cv2


class ImageRegWidget(QWidget):
    finish = pyqtSignal([np.ndarray], name='sub image')

    def __init__(self):
        QWidget.__init__(self)

        self.setWindowTitle('Image Registration for Rock Joint')
        self.setWindowIcon(QIcon('res/icons/logo.ico'))

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
        self.buttonLoadPreImage.clicked.connect(self.loadPreImage)
        self.buttonLoadDamageImage = QPushButton('Load Damage Image')
        self.buttonLoadDamageImage.clicked.connect(self.loadDamageImage)
        self.selectFeatureBox = QComboBox()
        self.selectFeatureBox.addItems([
            'ORB',
            'SIFT',
        ])
        self.diskRadiusOfMedianFilterBox = QSpinBox(self)
        self.diskRadiusOfMedianFilterBox.setRange(3, 20)
        self.diskRadiusOfMedianFilterBox.setValue(3)
        self.diskRadiusOfMedianFilterBox.setSingleStep(2)
        self.buttonAnalysis = QPushButton('Analysis')
        self.buttonAnalysis.clicked.connect(self.__analysis)

        groupBoxImageReg = QGroupBox('Image Registration')
        groupBoxImageReg.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        vBox = QVBoxLayout()
        vBox.addWidget(self.buttonLoadDamageImage)
        vBox.addWidget(self.buttonLoadPreImage)
        formBox = QFormLayout()
        formBox.addRow('Feature Detection Algorithm', self.selectFeatureBox)
        formBox.addRow('Disk Radius of Median Filter', self.diskRadiusOfMedianFilterBox)
        vBox.addLayout(formBox)
        vBox.addWidget(self.buttonAnalysis)
        groupBoxImageReg.setLayout(vBox)

        groupBoxExport = QGroupBox('Export')
        self.selectSubType = QComboBox()
        self.selectSubType.addItems([
            'Damage-Pre',
            'Pre-Damage',
            'Both',
        ])
        self.selectSubType.currentTextChanged.connect(self.__updateSubImage)
        self.channelType = QComboBox()
        self.channelType.addItems([
            'Gray',
            'Red',
            'Green',
            'Blue'
        ])
        self.channelType.currentTextChanged.connect(self.__updateSubImage)

        # export button
        self.buttonLoadImageToSDZM = QPushButton('Load subimage to SDZM toolbox')
        self.buttonLoadImageToSDZM.clicked.connect(self.__exportToDZMTtoolbox)
        self.buttonExportAsPng = QPushButton('Export subimage as *.png')
        self.buttonExportAsPng.clicked.connect(self.__exportAsPng)
        self.buttonExportAlignedImageAspng = QPushButton('Export aligned image as *.png')
        self.buttonExportAlignedImageAspng.clicked.connect(self.__exportAlignedImage)
        exportFormBox = QFormLayout()
        exportFormBox.addRow('Sub Type', self.selectSubType)
        exportFormBox.addRow('Channel', self.channelType)
        exportVBox = QVBoxLayout()
        exportVBox.addLayout(exportFormBox)
        exportVBox.addWidget(self.buttonExportAsPng)
        exportVBox.addWidget(self.buttonLoadImageToSDZM)
        exportVBox.addWidget(self.buttonExportAlignedImageAspng)
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
        self.subImage = None
        self.cropPolygon = None  # polygon as list type
        self.__updateActionsStatus()

    def loadPreImage(self, image=False):
        if image is False:
            filePath, fileType = QFileDialog.getOpenFileName(self, caption='Choose the image',
                                                             directory=self.projectWorkPath,
                                                             filter='Image (*.jpg);;Image (*.png);;Image (*.tif)')
            if not filePath:
                QMessageBox.warning(self, 'No File Selected', 'No image file is selected.')
                return
            self.projectWorkPath, _ = os.path.split(filePath)
            image = io.imread(filePath)
        self.__setPreImage(image)
        self.__updateActionsStatus()

    def loadDamageImage(self, image=None):
        if image is False:
            filePath, fileType = QFileDialog.getOpenFileName(self, caption='Choose the image',
                                                             directory=self.projectWorkPath,
                                                             filter='Image (*.jpg);;Image (*.png);;Image (*.tif)')
            if not filePath:
                QMessageBox.warning(self, 'No File Selected', 'No image file is selected.')
                return
            self.projectWorkPath, _ = os.path.split(filePath)
            image = io.imread(filePath)
        self.__setDamageImage(image)
        self.__updateActionsStatus()

    def __analysis(self):
        IT = ImageRegThread()
        IT.setParameters(self.preImage, self.damageImage, self.selectFeatureBox.currentText())
        IT.error.connect(self.__errorHandle)
        IT.finish.connect(self.__analysisFinished)
        IT.start()
        self.IT = IT
        self.__updateActionsStatus()

    def __setPreImage(self, image):
        # plt.close(1)
        self.preImage = image
        self.preImageCanvas.imshow(self.preImage, 'Image of Undamaged Specimen')
        self.tabWidget.setCurrentWidget(self.preImageCanvas)
        self.__updateActionsStatus()

    def __setDamageImage(self, image):
        # plt.close(1)
        self.damageImage = image
        self.damageImageCanvas.imshow(self.damageImage, 'Image of Damaged Specimen')
        self.tabWidget.setCurrentWidget(self.damageImageCanvas)
        self.__updateActionsStatus()

    def __setMatchesImage(self, image):
        self.featureMatchsCanvas.imshow(image, 'Match Result of Features')
        self.tabWidget.setCurrentWidget(self.featureMatchsCanvas)
        self.__updateActionsStatus()

    def __setAlignedImage(self, alignImage):
        self.alignedImage = alignImage
        self.resultCanvas.imshow(self.preImage, 'Image of Undamaged Specimen', '221')
        self.resultCanvas.imshow(self.damageImage, 'Image of Damage Speciimen', '222')
        self.resultCanvas.imshow(self.alignedImage, 'Aligned Image of Undamaged Specimen', '223')
        self.tabWidget.setCurrentWidget(self.resultCanvas)
        self.__updateActionsStatus()

    def __updateSubImage(self):
        cType = self.selectSubType.currentText()
        channel = self.channelType.currentText()
        if cType not in [
            'Pre-Damage',
            'Damage-Pre',
            'Both'
        ]:
            return
        damageImage = NAImage2GrayByChannel(self.damageImage, channel)
        alignedImage = NAImage2GrayByChannel(self.alignedImage, channel)
        alignedImage = medianFilter(alignedImage.astype(np.uint8), self.diskRadiusOfMedianFilterBox.value())
        alignedImage = alignedImage.astype(np.float32)
        # generate the sub image
        alignedImage = alignedImage - np.mean(alignedImage)
        damageImage = damageImage - np.mean(damageImage)
        alignedImage[alignedImage < 0] = 0
        damageImage[damageImage < 0] = 0
        # align - damage
        subImage = alignedImage.astype(np.float) - damageImage.astype(np.float)
        if cType == 'Pre-Damage':
            subImage[subImage < 0] = 0
        elif cType == 'Damage-Pre':
            subImage[subImage > 0] = 0
        # else:
        subImage = np.abs(subImage)
        subImage = np.power(subImage, 2) / 40
        subImage[subImage > 255] = 255
        # self.subImage = imAdjust(subImage, 0, 1, 1)
        self.subImage = subImage.astype(np.uint8)
        self.subImage = cv2.equalizeHist(self.subImage)
        self.resultCanvas.imshow(self.subImage, 'Sub Image', '224', 'gray')
        self.__updateActionsStatus()

    def __exportAlignedImage(self):
        # select path
        filePath, fileType = QFileDialog.getSaveFileName(self, 'Choose the path to save the image',
                                                         os.path.join(self.projectWorkPath, 'ImageOutput-%s.png' % (
                                                             datetime.datetime.now().strftime('%Y%m%d%H%M%S'))),
                                                         ' png (*.png);;')
        if not filePath:
            QMessageBox.warning(self, 'No Path Selected', 'No Path is selected.')
            return
        io.imsave(filePath, self.alignedImage)
        self.__updateActionsStatus()

    def __exportAsPng(self):
        # select path
        filePath, fileType = QFileDialog.getSaveFileName(self, 'Choose the path to save the image',
                                                         os.path.join(self.projectWorkPath, 'ImageOutput-%s.png' % (
                                                             datetime.datetime.now().strftime('%Y%m%d%H%M%S'))),
                                                         ' png (*.png);;')
        if not filePath:
            QMessageBox.warning(self, 'No Path Selected', 'No Path is selected.')
            return
        io.imsave(filePath, self.subImage)
        self.__updateActionsStatus()

    def __exportToDZMTtoolbox(self):
        self.finish.emit(self.subImage.transpose((1, 0)))
        self.__updateActionsStatus()
        self.close()

    def __errorHandle(self, error):
        QMessageBox.warning(self, 'Error', error)

    def __analysisFinished(self, imageAligned, matchesImage):
        self.__setMatchesImage(matchesImage)
        self.__setAlignedImage(imageAligned)
        self.__updateSubImage()

    def __updateActionsStatus(self):
        self.buttonLoadPreImage.setEnabled(type(self.damageImage) == np.ndarray)
        # self.buttonLoadDamageImage.setEnabled(type(self.preImage) == np.ndarray)
        self.buttonAnalysis.setEnabled(type(self.preImage) == np.ndarray and type(self.damageImage) == np.ndarray)
        self.buttonLoadImageToSDZM.setEnabled(type(self.subImage) == np.ndarray)
        self.buttonExportAsPng.setEnabled(type(self.subImage) == np.ndarray)
        self.buttonExportAlignedImageAspng.setEnabled(type(self.subImage) == np.ndarray)


# matplotlib 绘图
class Canvas(FigureCanvas):
    def __init__(self, dpi=200):
        self.fig = Figure(dpi=dpi)
        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self.fontDict = {
            'fontsize': 8
        }

    def imshow(self, image, title='', mod='111', cmap='viridis'):
        axes = self.fig.add_subplot(mod)
        axes.imshow(image, cmap)
        if len(title):
            axes.set_title(title, self.fontDict)
        axes.axis('off')
        self.draw()


# 图像对齐
class ImageRegThread(QThread):
    finish = pyqtSignal([np.ndarray, np.ndarray], name='analysis finished')
    error = pyqtSignal([int], name='error')

    def __init__(self):
        QThread.__init__(self)

    def setParameters(self, image, imageRef, algorithm='ORB', maxFeatures=1000):
        self.imageRef = imageRef
        self.image = image
        self.algorithm = algorithm
        self.maxFeatures = maxFeatures

    def run(self):
        self.algorithm = self.algorithm.upper()
        if self.algorithm not in ['ORB', 'SIFT']:
            self.error.emit('The algorithm not exist.')
            return
        # select detector
        if self.algorithm == 'SIFT':
            descExtractor = cv2.SIFT_create()
        elif self.algorithm == 'ORB':
            descExtractor = cv2.ORB_create(self.maxFeatures)
        # check the cropPolygon and
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
            # M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
            # M, mask = cv2.estimateRigidTransform(src_pts, dst_pts, False)
            M, mask = cv2.estimateAffine2D(src_pts, dst_pts, cv2.RANSAC)
            matchesMask = mask.ravel().tolist()
        else:
            self.error.emit("Not enough matches are found - {}/{}".format(len(matches), MIN_MATCH_COUNT))
            return
        draw_params = dict(matchColor=(0, 255, 0),  # draw matches in green color
                           singlePointColor=None,
                           matchesMask=matchesMask,  # draw only inliers
                           flags=2)
        matchesImage = cv2.drawMatches(self.imageRef, kpRef, self.image, kp, matches, None, **draw_params)
        # imageWarped = cv2.warpPerspective(self.image, M, (self.imageRef.shape[1], self.imageRef.shape[0]))
        imageWarped = cv2.warpAffine(self.image, M, (self.imageRef.shape[1], self.imageRef.shape[0]))
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
