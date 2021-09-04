# -*- coding: utf-8 -*-

# @FileName: MainWindow.py
# @Time    : 2021-03-09 10:55
# @Author  : Dorad, cug.xia@gmail.com
# @Blog    ：https://blog.cuger.cn

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import datetime
from AnalysisThread import *
from ImageTool import *
from LabelImageDataTable import LabelDataTable
import os
import pickle5 as pickle
from ImageRegistration import ImageRegWidget


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowIcon(QIcon('res/icons/logo.ico'))
        self.setWindowTitle(
            "Shear Damage Zones Measurement Toolbox of Rock Joint (v2.0.0) By Ding Xia, cug_xia@cug.edu.cn")
        self.setMinimumSize(900, 700)

        '''
        center widget
        '''

        # main
        self.centerWidget = QSplitter(Qt.Horizontal)
        from View import PolygonView, LabelImageView
        self.originView = PolygonView()
        self.labelView = LabelImageView()
        self.centerWidget.addWidget(self.originView)
        self.centerWidget.addWidget(self.labelView)
        self.centerWidget.setStretchFactor(0, 1)
        self.centerWidget.setStretchFactor(1, 1)
        self.setCentralWidget(self.centerWidget)

        # connect originView and labelView
        self.originView.MousePosChanged.connect(self.__updateMosuePositionShownInStatusBar)
        self.originView.PolygonDrawFinishedSignal.connect(self.__updateActionsStatus)
        self.labelView.MousePosChanged.connect(self.__updateMosuePositionShownInStatusBar)
        self.originView.RealScaleChangedSignal.connect(self.__updateRealScale)

        '''
        actions
        '''

        # open('res/icons/delete-new.png')
        # File
        self.actionOpenImage = QAction(QIcon('res/icons/load-image.png'), 'Open Image', self)
        self.actionOpenImage.setShortcut(QKeySequence.Open)
        self.actionReplaceImage = QAction(QIcon('res/icons/load-image.png'), 'Replace Image', self)
        self.actionOpenProject = QAction(QIcon('res/icons/folder-open.png'), 'Open Project', self)
        self.actionSaveProject = QAction(QIcon('res/icons/save.png'), 'Save Project', self)
        self.actionSaveProject.setShortcut(QKeySequence.Save)
        self.actionSaveProjectAs = QAction(QIcon('res/icons/save.png'), 'Save Project As', self)
        self.actionSaveProjectAs.setShortcut(QKeySequence.SaveAs)
        self.actionImportProject = QAction(QIcon('res/icons/import.png'), 'Import Project', self)
        self.actionCloseProject = QAction(QIcon('res/icons/close.png'), 'Close Project', self)
        self.actionCloseProject.setShortcut(QKeySequence.Close)
        self.actionExit = QAction(QIcon('res/icons/exit.png'), 'Exit', self)

        self.actionImageRegistration = QAction(QIcon('res/icons/align-center.png'), 'Image Registration', self)
        # pretreatment
        # channel
        self.actionGroupChannel = QActionGroup(self)
        self.actionChannelRGB = QAction(QIcon('res/icons/channel-rgb.png'), 'RGB')
        self.actionChannelRGB.setCheckable(True)
        self.actionChannelRGB.setChecked(True)
        self.actionChannelGray = QAction(QIcon('res/icons/channel-gray.png'), 'Gray')
        self.actionChannelGray.setCheckable(True)
        self.actionChannelRed = QAction(QIcon('res/icons/channel-red.png'), 'Red')
        self.actionChannelRed.setCheckable(True)
        self.actionChannelGreen = QAction(QIcon('res/icons/channel-green.png'), 'Green')
        self.actionChannelGreen.setCheckable(True)
        self.actionChannelBlue = QAction(QIcon('res/icons/channel-blue.png'), 'Blue')
        self.actionChannelBlue.setCheckable(True)
        self.actionGroupChannel.addAction(self.actionChannelRGB)
        self.actionGroupChannel.addAction(self.actionChannelGray)
        self.actionGroupChannel.addAction(self.actionChannelRed)
        self.actionGroupChannel.addAction(self.actionChannelGreen)
        self.actionGroupChannel.addAction(self.actionChannelBlue)

        self.actionMedianFilter = QAction(QIcon('res/icons/median-filter.png'), 'Median Filter', self)

        self.actionSetScale = QAction(QIcon('res/icons/ruler.png'), 'Set Scale', self)
        self.actionCropImage = QAction(QIcon('res/icons/crop.png'), 'Crop Image', self)
        self.actionCreateNewROI = QAction(QIcon('res/icons/polygon.png'), 'Create New ROI', self)
        self.actionDeleteSelectedROIs = QAction(QIcon('res/icons/delete-rois.png'), 'Delete Selected ROIs', self)
        # analysis
        self.actionAnalysisOtsuBasedOnROIs = QAction(QIcon('res/icons/run.png'),
                                                     'Analysis - OTSU Threshold Method Based on ROIs',
                                                     self)
        self.actionAnalysisROIs = QAction(QIcon('res/icons/run.png'), 'Analysis - ROIs to Label Image',
                                          self)
        self.actionAnalysisOTSU = QAction(QIcon('res/icons/run.png'),
                                          'Analysis - Global Threshold Method based on OTSU',
                                          self)
        self.actionAnalysisRiss = QAction(QIcon('res/icons/run.png'),
                                          'Analysis - Global Theashold Method based on Riss',
                                          self)
        # post-processing
        self.actionFilterSmallZones = QAction(QIcon('res/icons/filter-small-zones.png'),
                                              'Filter Small Shear Damage Zones',
                                              self)
        self.actionFilterSmallHoles = QAction(QIcon('res/icons/filter-small-holes.png'),
                                              'Filter Small Holes in Shear Damage Zones',
                                              self)
        self.actionExportImageWithROIs = QAction(QIcon('res/icons/export-rois.png'),
                                                 'Export Image With ROIs',
                                                 self)
        self.actionExportImageWithShearDamageZones = QAction(QIcon('res/icons/export-label-image.png'),
                                                             'Export Image With Shear Damage Zones',
                                                             self)
        self.actionExportImageWithShearDamageZonesAsBinaryImage = QAction(QIcon('res/icons/export-label-image.png'),
                                                                          'Export Image With Shear Damage Zones as Binary Image',
                                                                          self)
        self.actionDamageZonesTable = QAction(QIcon('res/icons/table.png'), 'Table for Damage Zones', self)
        # about
        self.actionTutorials = QAction(QIcon('res/icons/tutorials.png'), 'Tutorials', self)
        self.actionInfo = QAction(QIcon('res/icons/info.png'), 'Information', self)
        self.actionAbout = QAction(QIcon('res/icons/question-circle.png'), 'About', self)

        # connect action
        self.actionOpenImage.triggered.connect(self.__openImage)
        self.actionReplaceImage.triggered.connect(self.__replaceImage)
        self.actionOpenProject.triggered.connect(self.__openProject)
        self.actionSaveProject.triggered.connect(self.__saveProject)
        self.actionSaveProjectAs.triggered.connect(self.__saveProjectAs)
        self.actionImportProject.triggered.connect(self.__importOldProject)
        self.actionCloseProject.triggered.connect(self.__closeProject)
        self.actionExit.triggered.connect(self.close)
        # # pre
        self.actionGroupChannel.triggered.connect(self.__channelChanged)
        self.actionImageRegistration.triggered.connect(self.__imageRegistration)  # 需要补充
        self.actionMedianFilter.triggered.connect(self.__medianFilter)
        self.actionSetScale.triggered.connect(self.originView.setScale)
        self.actionCropImage.triggered.connect(self.originView.startDrawCropPolygon)
        self.actionCreateNewROI.triggered.connect(self.originView.startDrawROIPolygon)
        self.actionDeleteSelectedROIs.triggered.connect(self.originView.deleteSelectedROIs)
        # # analysis, 全部需要补充
        self.actionAnalysisOtsuBasedOnROIs.triggered.connect(self.__analysisOtsuBasedOnROIs)
        self.actionAnalysisROIs.triggered.connect(self.__analysisROIs)
        self.actionAnalysisOTSU.triggered.connect(self.__analysisOTSU)
        self.actionAnalysisRiss.triggered.connect(self.__analysisRiss)
        # # post
        self.actionFilterSmallZones.triggered.connect(self.labelView.filterSmallZones)
        self.actionFilterSmallHoles.triggered.connect(self.labelView.filterSmallHoles)
        self.actionExportImageWithROIs.triggered.connect(self.__exportImageWithROIs)
        self.actionExportImageWithShearDamageZones.triggered.connect(self.__exportImageWithDamageZones)
        self.actionExportImageWithShearDamageZonesAsBinaryImage.triggered.connect(
            self.__exportImageWithDamageZonesAsBinaryImage)
        self.actionDamageZonesTable.triggered.connect(self.__damageZonesTable)  # 需要补充
        # # help
        self.actionTutorials.triggered.connect(self.__tutorials)
        self.actionInfo.triggered.connect(self.__info)
        self.actionAbout.triggered.connect(self.__about)

        '''
        menu bar
        '''

        ## set menu bar
        menuBar = self.menuBar()
        # file
        menuFile = menuBar.addMenu('File')
        menuFile.addActions([
            self.actionOpenImage,
            self.actionReplaceImage,
            self.actionImageRegistration,
            menuFile.addSeparator(),
            self.actionOpenProject,
            self.actionSaveProject,
            self.actionSaveProjectAs,
            self.actionImportProject,
            self.actionCloseProject,
            menuFile.addSeparator(),
            self.actionExit
        ])
        # pretreatment
        menuPretreatment = menuBar.addMenu('Pretreatment')
        channelMenu = menuPretreatment.addMenu('Channel')
        channelMenu.addActions([
            self.actionChannelRGB,
            self.actionChannelGray,
            self.actionChannelRed,
            self.actionChannelGreen,
            self.actionChannelBlue
        ])
        menuPretreatment.addActions([
            menuPretreatment.addSeparator(),
            self.actionMedianFilter,
            self.actionSetScale,
            self.actionCropImage,
            menuPretreatment.addSeparator(),
            self.actionCreateNewROI,
            self.actionDeleteSelectedROIs
        ])
        # analysis
        analysisMenu = menuBar.addMenu('Analysis')
        analysisMenu.addActions([
            self.actionAnalysisOtsuBasedOnROIs,
            analysisMenu.addSeparator(),
            self.actionAnalysisROIs,
            self.actionAnalysisOTSU,
            self.actionAnalysisRiss
        ])

        # postprocessing
        postprocessingMenu = menuBar.addMenu('Postprocessing')
        postprocessingMenu.addActions([
            self.actionFilterSmallZones,
            self.actionFilterSmallHoles,
            postprocessingMenu.addSeparator(),
            self.actionExportImageWithROIs,
            self.actionExportImageWithShearDamageZones,
            self.actionExportImageWithShearDamageZonesAsBinaryImage,
            postprocessingMenu.addSeparator(),
            self.actionDamageZonesTable
        ])
        # help
        helpMenu = menuBar.addMenu('Help')
        helpMenu.addActions([
            self.actionTutorials,
            self.actionInfo,
            self.actionAbout
        ])

        '''
        toolbar
        '''

        # toolbar
        toolbar = self.addToolBar('total')
        toolbar.addActions([
            self.actionOpenImage,
            self.actionImageRegistration,
            self.actionOpenProject,
            self.actionSaveProjectAs,
            toolbar.addSeparator(),
        ])
        toolbar.addActions(self.actionGroupChannel.actions())
        toolbar.addSeparator()
        toolbar.addActions([
            self.actionSetScale,
            self.actionCropImage,
            self.actionCreateNewROI,
            self.actionDeleteSelectedROIs,
            toolbar.addSeparator(),
            self.actionAnalysisOtsuBasedOnROIs,
            toolbar.addSeparator(),
            self.actionFilterSmallZones,
            self.actionFilterSmallHoles,
            self.actionDamageZonesTable,
            self.actionExportImageWithROIs,
            self.actionExportImageWithShearDamageZones,
            toolbar.addSeparator(),
            self.actionTutorials,
            self.actionAbout
        ])

        '''
        status bar
        '''
        self.labelMusePosition = QLabel()
        self.labelCopyright = QLabel('Copyright©2019-%s Dorad. All Rights Reserved. Email: cug_xia@cug.edu.cn' % (
            datetime.datetime.now().year))
        self.processBar = QProgressBar(self)
        self.processBar.setRange(0, 100)
        self.processBar.setVisible(False)
        self.statusBar().addWidget(self.labelMusePosition)
        self.statusBar().addWidget(self.processBar)
        self.statusBar().addPermanentWidget(self.labelCopyright)

        # initUi
        self.initUi()

    def initUi(self) -> None:
        '''
        parameters
        :return:
        '''

        if not (hasattr(self, 'projectWorkPath') and self.projectWorkPath):
            self.projectWorkPath = os.getcwd()
        self.projectFileName = None
        self.imageFileName = None
        self.originImage = None

        self.colorChannel = 'RGB'
        self.__setColorChannelByName(self.colorChannel)

        self.originView.clear()
        self.labelView.clear()
        self.__updateActionsStatus()

    # File

    def __openImage(self, image=np.array([]), initUi=True):
        if type(image) != np.ndarray:
            filePath, fileType = QFileDialog.getOpenFileName(self, caption='Choose the image',
                                                             directory=self.projectWorkPath,
                                                             filter='Image (*.jpg);;Image (*.png);;Image (*.tif)')
            if not filePath:
                QMessageBox.warning(self, 'No File Selected', 'No image file is selected.')
                return
            image = QImage(filePath)
            if initUi:
                self.initUi()
            self.projectWorkPath, self.imageFileName = os.path.split(filePath)
        else:
            image = NArray2QImage(image)
            # self.initUi()
        self.originImage = image
        self.originView.setImage(self.originImage)
        self.__updateActionsStatus()

    def __replaceImage(self):
        self.__openImage(image=None, initUi=False)

    def __openProject(self):
        filePath, fileType = QFileDialog.getOpenFileName(self, 'Choose the project file',
                                                         directory=self.projectWorkPath,
                                                         filter=' project (*.pro);')
        if not filePath:
            QMessageBox.warning(self, 'No Project File Selected', 'No project file is selected.')
            return
        self.initUi()
        self.projectWorkPath, self.projectFileName = os.path.split(filePath)
        try:
            with open(filePath, mode='rb') as f:
                project = pickle.load(f)
            # decode
            self.originImage = NArray2QImage(project['originImage'])
            self.__setColorChannelByName(project['colorChannel'])
            for roi in project['ROIs']:
                self.originView.addRoiPolygon(list2QPolygonF(roi))
            self.originView.realScale = project['realScale']
            self.labelView.realScale = project['realScale']
            if project['binaryImage'].max() > 0:
                self.labelView.setImage(project['binaryImage'])
            if project['cropPolygon']:
                self.originView.setCropPolygon(list2QPolygonF(project['cropPolygon']))
                self.labelView.setCropPolygon(self.originView.cropPolygon)
            self.__updateActionsStatus()
        except Exception as e:
            QMessageBox.warning(self, 'Illegal Project Document',
                                'Illegal project document, please select a legal one: %s' % e)
            return

    def __importOldProject(self):
        filePath, fileType = QFileDialog.getOpenFileName(self, 'Choose the project file',
                                                         directory=self.projectWorkPath,
                                                         filter=' project (*.pro);')
        if not filePath:
            QMessageBox.warning(self, 'No Project File Selected', 'No project file is selected.')
            return
        self.initUi()
        self.projectWorkPath, self.projectFileName = os.path.split(filePath)

        import scipy.sparse as sp
        import json
        def JsonDecoding(project):
            # crop_polygon, QPolygonF
            T = QPolygonF()
            if project['crop_polygon']:
                for p in project['crop_polygon']:
                    T.append(QPointF(p[0], p[1]))
            project['crop_polygon'] = T
            # polygon, QPolygon
            if project['polygon']:
                for polygon in project['polygon']:
                    T = QPolygonF()
                    for point in polygon['geo']:
                        T.append(QPointF(point[0], point[1]))
                    polygon['geo'] = T
            # label_image
            limage = project['label_image']
            project['offset'] = QPointF(project['offset'][0], project['offset'][1])
            if len(limage['data']):
                project['label_image'] = sp.csr_matrix((limage['data'], limage['indices'], limage['indptr']),
                                                       dtype=int).toarray()
            else:
                project['label_image'] = np.array([])
            return project

        try:
            with open(filePath, mode='rb') as f:
                project = json.load(f)
            # decode
            project = JsonDecoding(project)
            self.originImage = QImage(project['base_image'])
            self.__setColorChannelByName()
            if project['crop_polygon']:
                self.originView.setCropPolygon(project['crop_polygon'])
                self.labelView.setCropPolygon(project['crop_polygon'])
            for roi in project['polygon']:
                self.originView.addRoiPolygon(roi['geo'])
            if 'real_scale' in project:
                self.originView.realScale = project['real_scale']
                self.labelView.realScale = project['real_scale']
            if project['label_image'].max() > 0:
                self.labelView.setImage(project['label_image'].T > 0)
            self.__updateActionsStatus()
        except Exception as e:
            QMessageBox.warning(self, 'Illegal Project Document',
                                'Illegal project document, please select a legal one: %s' % e)
            return

    def __saveProject(self):
        if not self.projectFileName:
            self.__saveProjectAs()
            return
        ROIs = []
        for roi in self.originView.getROIsPolygon():
            ROIs.append(QPolygonF2list(roi))

        project = {
            'originImage': QImage2NArray(self.originImage),  # QPixmap
            'cropPolygon': QPolygonF2list(self.originView.cropPolygon),  # QPolygonF
            'colorChannel': self.colorChannel,
            'ROIs': ROIs,  # list of QPolygonF
            'realScale': self.originView.realScale,  # float
            'binaryImage': self.labelView.binaryImage  # ndarray
        }
        filePath = os.path.join(self.projectWorkPath, self.projectFileName)
        try:
            with open(filePath, mode='wb') as f:
                pickle.dump(project, f, pickle.HIGHEST_PROTOCOL)
                QMessageBox.information(self, 'Success', 'Project file has been saved successfully.')
            self.__updateActionsStatus()
        except Exception as e:
            QMessageBox.warning(self, 'Error', 'Failed to write project file. %s' % e)
            return

    def __saveProjectAs(self):
        filePath, fileType = QFileDialog.getSaveFileName(self, 'Choose the path for project',
                                                         os.path.join(self.projectWorkPath, 'project-%s.pro' % (
                                                             datetime.datetime.now().strftime('%Y%m%d%H%M%S'))),
                                                         ' project (*.pro);;')
        if not filePath:
            QMessageBox.warning(self, 'No Path Selected', 'No Path is selected.')
            return
        self.projectWorkPath, self.projectFileName = os.path.split(filePath)
        self.__saveProject()
        self.__updateActionsStatus()

    def __closeProject(self):
        reply = QMessageBox.warning(self, 'Close project', 'Close the project all clear all windows?',
                                    QMessageBox.Yes | QMessageBox.No,
                                    QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.initUi()
        self.__updateActionsStatus()

    def __setColorChannelByName(self, channel='RGB'):
        for act in self.actionGroupChannel.actions():
            if channel == act.text():
                self.colorChannel = act.text()
                act.setChecked(True)
            else:
                act.setChecked(False)
        # change the image in origin view
        if not self.originImage:
            return
        self.originView.setImage(QImageToGrayByChannel(self.originImage, self.colorChannel))
        self.__updateActionsStatus()

    # pretreatment
    def __channelChanged(self, action):
        self.__setColorChannelByName(action.text())

    def __imageRegistration(self):
        self.imageRegWidget = ImageRegWidget()
        if self.originImage is not None:
            self.imageRegWidget.loadDamageImage(QImage2NArray(self.originImage).transpose((1, 0, 2)))
        self.imageRegWidget.finish.connect(self.__updateImage)
        self.imageRegWidget.show()
        self.__updateActionsStatus()

    def __medianFilter(self):
        # ask to imput the size of disk.
        diskRadius, ok = QInputDialog.getInt(self, 'Input the radius of disk for median filter.', 'Radius(mm)', 3,
                                             3, 100, 2)
        if not ok:
            return
        grayImage = QImage2GrayNArray(self.originView.getImage())
        self.originImage = NArray2QImage(medianFilter(grayImage, diskRadius))
        self.originView.setImage(self.originImage)
        self.__updateActionsStatus()

    def __updateImage(self, image):
        self.__openImage(image, initUi=False)

    # analysis
    def __analysisOtsuBasedOnROIs(self):
        self.AT = ROIsOTSUAnalysisThread()
        self.__analysisRun()

    def __analysisROIs(self) -> None:
        '''
        generate the labelImage based on the ROIs
        :return:
        '''
        self.AT = ROIsToZonesAnalysisThread()
        self.__analysisRun()

    def __analysisOTSU(self):
        self.AT = AnalysisThread()
        self.__analysisRun()

    def __analysisRiss(self):
        self.AT = RissAnalysisThread()
        self.__analysisRun()

    def __analysisRun(self):
        if not hasattr(self, 'AT'):
            return
        progress = QProgressDialog(self)
        progress.setWindowTitle("Analyzing")
        progress.setLabelText("Analyzing...")
        progress.setCancelButtonText("cancel")
        progress.setMinimumDuration(5)
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        self.processDialog = progress
        self.processDialog.setMaximum(100)
        self.processDialog.setValue(1)
        self.processBar.setMaximum(100)
        self.__updateProcessBarValue(1)

        grayImage = QImage2GrayNArray(self.originView.getImage())
        self.labelView.setCropPolygon(self.originView.getCropPolygon())

        self.AT.setParameters(grayImage, self.originView.getCropPolygon(), self.originView.getROIsPolygon())
        self.AT.process.connect(self.__updateProcessBarValue)
        self.AT.process.connect(self.processDialog.setValue)
        self.AT.finish.connect(self.__analysisFinished)
        self.AT.start()
        self.__updateActionsStatus()

    def __analysisFinished(self, binaryImage):
        self.labelView.setImage(binaryImage)
        self.AT.process.disconnect()
        self.AT.finish.disconnect()
        self.processBar.setVisible(False)
        if hasattr(self, 'processDialog'):
            self.processDialog.close()
            delattr(self, 'processDialog')
        QMessageBox.information(self, 'Finished', 'Analysis is Finished.')
        delattr(self, 'AT')
        self.__updateActionsStatus()

    # post
    def __exportImageWithROIs(self):
        filePath, fileType = QFileDialog.getSaveFileName(self, 'Choose the path to save image with ROIs',
                                                         os.path.join(self.projectWorkPath, 'ImageWithROIs-%s.png' % (
                                                             datetime.datetime.now().strftime('%Y%m%d%H%M%S'))),
                                                         ' png (*.png);; eps (*.eps)')
        if not filePath:
            QMessageBox.warning(self, 'No Path Selected', 'No Path is selected.')
            return
        # check the file type
        if fileType == 'eps (*.eps)':
            # eps format
            # get image and cropPolygon
            image = QImage2NArray(self.originView.getImage())
            if len(image.shape) > 2:
                image = image.transpose((1, 0, 2))
            else:
                image = image.transpose((1, 0))
            from shapely.geometry import Polygon
            cropPolygon = self.originView.getCropPolygon()
            ROIs = self.originView.getROIsPolygon()
            # draw as eps
            import matplotlib.pyplot as plt
            plt.imshow(image)
            for roi in ROIs:
                roi = QPolygonF2list(roi)
                plt.plot(*Polygon(roi).exterior.xy, 'r')
            plt.plot(*Polygon(QPolygonF2list(cropPolygon)).exterior.xy, 'g')
            plt.axis('equal')
            plt.axis('off')
            plt.savefig(filePath, format='eps', transparent=True)
            pass
        else:
            image = self.originView.getRenderedImageFromScene()
            image.save(filePath)
        self.__updateActionsStatus()

    def __exportImageWithDamageZones(self):
        filePath, fileType = QFileDialog.getSaveFileName(self, 'Choose the path to save image with shear damage zones',
                                                         os.path.join(self.projectWorkPath,
                                                                      'ColoredDamageZones-%s.png' % (
                                                                          datetime.datetime.now().strftime(
                                                                              '%Y%m%d%H%M%S'))),
                                                         ' png (*.png);;')
        if not filePath:
            QMessageBox.warning(self, 'No Path Selected', 'No Path is selected.')
            return
        image = self.labelView.getRenderedImageFromScene()
        image.save(filePath)
        self.__updateActionsStatus()

    def __exportImageWithDamageZonesAsBinaryImage(self):
        filePath, fileType = QFileDialog.getSaveFileName(self, 'Choose the path to save image with shear damage zones',
                                                         os.path.join(self.projectWorkPath,
                                                                      'BinaryDamageZones-%s.png' % (
                                                                          datetime.datetime.now().strftime(
                                                                              '%Y%m%d%H%M%S'))),
                                                         ' png (*.png);;')
        if not filePath:
            QMessageBox.warning(self, 'No Path Selected', 'No Path is selected.')
            return
        image = self.labelView.getBinaryImage()
        image.save(filePath)
        self.__updateActionsStatus()

    def __damageZonesTable(self):
        self.resultTable = LabelDataTable()
        self.resultTable.setData(self.labelView.binaryImage, self.originView.realScale, self.originView.cropPolygon)
        self.resultTable.show()
        self.__updateActionsStatus()

    # help
    def __tutorials(self):
        QDesktopServices.openUrl(QUrl('https://blog.cuger.cn'))

    def __info(self):
        msgBox = QMessageBox(QMessageBox.NoIcon, 'SFRM Tool',
                             'Shear Damage Zones Measurement Toolbox of Rock Joint (the SDZM toolbox) is designed to detect shear failure region from discontinuity image which is taken after Direct Shear Test.')
        # QMessageBox.information(self, 'DSFRD Tool',
        #                         'Discontinuity Shear Failure Region Detection Tool is designed to detect shear failure region from discontinuity image which is taken after Direct Shear Test.')
        msgBox.setIconPixmap(QPixmap('./images/icons/logo.png'))
        msgBox.exec()

    def __about(self) -> None:
        QMessageBox.aboutQt(self)

    # private
    def __updateMosuePositionShownInStatusBar(self, x, y) -> None:
        self.labelMusePosition.setText('X: %.2f, Y:%.2f' % (x, y))

    # change the button status according to the parameters
    def __updateActionsStatus(self) -> None:
        image = self.originView.getImage()
        hasOriginImage = not (image is None or image is False)
        self.actionReplaceImage.setEnabled(hasOriginImage)
        self.actionSaveProject.setEnabled(hasOriginImage)
        self.actionSaveProjectAs.setEnabled(hasOriginImage)
        self.actionCloseProject.setEnabled(hasOriginImage)
        self.actionMedianFilter.setEnabled(hasOriginImage)
        self.actionSetScale.setEnabled(hasOriginImage)
        self.actionCropImage.setEnabled(hasOriginImage)
        self.actionCreateNewROI.setEnabled(hasOriginImage)
        self.actionDeleteSelectedROIs.setEnabled(hasOriginImage and len(self.originView.scene.selectedItems()))
        self.actionAnalysisOtsuBasedOnROIs.setEnabled(hasOriginImage and len(self.originView.getROIsPolygon()))
        self.actionAnalysisROIs.setEnabled(hasOriginImage and len(self.originView.getROIsPolygon()))
        self.actionAnalysisOTSU.setEnabled(hasOriginImage)
        self.actionAnalysisRiss.setEnabled(hasOriginImage and len(self.originView.getROIsPolygon()))
        self.actionFilterSmallZones.setEnabled(len(self.labelView.binaryImage.shape))
        self.actionFilterSmallHoles.setEnabled(len(self.labelView.binaryImage.shape))
        self.actionExportImageWithROIs.setEnabled(hasOriginImage)
        self.actionExportImageWithShearDamageZones.setEnabled(len(self.labelView.binaryImage.shape))
        self.actionExportImageWithShearDamageZonesAsBinaryImage.setEnabled(len(self.labelView.binaryImage.shape))
        self.actionDamageZonesTable.setEnabled(len(self.labelView.binaryImage.shape))
        pass

    def __updateRealScale(self, newScale, oldScale):
        self.labelView.realScale = newScale

    def __updateProcessBarValue(self, value: float) -> None:
        self.processBar.setValue(value)
        self.processBar.setVisible(True)

    def closeEvent(self, event: QCloseEvent) -> None:
        reply = QMessageBox.warning(self, 'Exit', 'Exit the program?',
                                    QMessageBox.Yes | QMessageBox.No,
                                    QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    # imagePath = './res/SY4.JPG'
    # mainWindow.originView.setImage(imagePath)
    # mainWindow.originView.setImageCenter()
    mainWindow.show()
    sys.exit(app.exec_())
