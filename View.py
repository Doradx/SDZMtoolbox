# -*- coding: utf-8 -*-

# @FileName: View.py
# @Time    : 2021-02-25 10:30
# @Author  : Dorad, cug.xia@gmail.com
# @Blog    ：https://blog.cuger.cn

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from enum import Enum
import numpy as np
from ImageTool import *


class ImageGateType(Enum):
    RGB = 1
    RED = 2
    GREEN = 3
    BLUE = 4
    GRAY = 5


class DrawType(Enum):
    NONE = 0
    CROPPOLYGON = 1
    ROIPOLYGON = 2
    SCALELINE = 3


class View(QGraphicsView):
    MousePosChanged = pyqtSignal([float, float], name='position of mouse has changed.')

    def __init__(self):
        super(QGraphicsView, self).__init__()

        self.initUi()

        # button
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.scene.setBackgroundBrush(Qt.gray)

        # add button and signal
        zoomInButton = QPushButton(QIcon('./res/icons/zoom-in.png'), '')
        zoomInButton.clicked.connect(self.zoomIn)
        zoomOutButton = QPushButton(QIcon('./res/icons/zoom-out.png'), '')
        zoomOutButton.clicked.connect(self.zoomOut)
        centerButton = QPushButton(QIcon('./res/icons/expand.png'), '')
        centerButton.clicked.connect(self.center)

        self.hBox = QHBoxLayout(self)
        toolBox = QVBoxLayout(self)
        toolBox.addWidget(zoomInButton)
        toolBox.addWidget(zoomOutButton)
        toolBox.addWidget(centerButton)
        toolBox.addStretch(1)
        self.hBox.addLayout(toolBox)
        self.hBox.addStretch(1)

    def initUi(self):
        self.baseScale = 1.2  # 基础缩放倍数
        self.currentScale = 1  # 比例尺
        self.maxScaleTimes = 10  # 最大缩放次数
        self.mouseLeftButtonDown = False
        self.mousePos = None

        self.imageItem = None
        self.originImage = None
        self.imageGateType = ImageGateType.RGB

        self.setMouseTracking(True)
        # self.setDragMode(self.ScrollHandDrag)
        self.setMinimumWidth(400)
        self.setMinimumHeight(400)

    '''
    视图缩放
    '''

    def __scale(self, scale):
        if scale > 0:
            scale = self.baseScale
        elif scale < 0:
            scale = 1 / self.baseScale
        else:
            scale = 1 / self.currentScale
        if abs(self.currentScale * scale) > self.maxScaleTimes or abs(
                self.currentScale * scale) < 1 / self.maxScaleTimes:
            return
        self.currentScale *= scale
        self.scale(scale, scale)

    def zoomIn(self):
        self.__scale(1)

    def zoomOut(self):
        self.__scale(-1)

    def center(self):
        self.__scale(0)

    def wheelEvent(self, event: QWheelEvent) -> None:
        angle = event.angleDelta().y()
        if (angle > 0):
            self.zoomIn()
        else:
            self.zoomOut()

    def setImage(self, image: QImage):
        """
        set the image
        :param imagePath:
        """
        if self.imageItem:
            self.scene.removeItem(self.imageItem)
            self.imageItem = None
        self.originImage = QPixmap.fromImage(image)
        self.imageItem = self.scene.addPixmap(self.originImage)
        self.imageItem.setZValue(0)
        self.centerOn(self.imageItem)

    def getImage(self):
        if not self.imageItem:
            return False
        return self.imageItem.pixmap().toImage()

    def getRenderedImageFromScene(self, cropped=True):
        originImage = self.getImage()
        area = QRect(QPoint(0, 0), QPoint(originImage.width(), originImage.height()))
        image = QImage(area.size(), QImage.Format_ARGB32_Premultiplied)
        image.fill(Qt.transparent)
        painter = QPainter(image)
        if self.cropPolygon and cropped:
            path = QPainterPath()
            path.addPolygon(self.cropPolygon)
            painter.setClipPath(path)
        self.scene.render(painter, QRectF(image.rect()), QRectF(area))
        painter.end()
        return image

    def clear(self):
        self.scene.clear()
        self.initUi()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.pos())
        self.MousePosChanged.emit(pos.x(), pos.y())


class PolygonView(View):
    PolygonDrawFinishedSignal = pyqtSignal([DrawType, QPolygonF], name='Polygon drawing finished')
    RealScaleChangedSignal = pyqtSignal([float, float], name='new real scale and old real scale')

    def __init__(self):
        View.__init__(self)
        self.initUi()

    def initUi(self):
        View.initUi(self)
        self.isDrawing = False  # 是否正在绘制多边形
        self.pointsCache = []
        self.cropPolygon = QPolygonF()
        # self.cropPolygonItem = None
        self.ROIPolygonsItems = []
        self.realScale = None

        # draw type
        from enum import Enum
        self.DrawType = DrawType.NONE
        scale = 6
        # 颜色配置
        self.tmpRoiPolygonPen = QPen(Qt.red, scale)
        self.tmpRoiPolygonPen.setDashOffset(10)
        dashScale = 2
        self.tmpRoiPolygonPen.setDashPattern({0.0, 2.0 * dashScale, 1.0 * dashScale, 2.0 * dashScale})
        self.tmpCropPolygonPen = QPen(Qt.green, scale)
        self.tmpCropPolygonPen.setDashOffset(10)
        self.tmpCropPolygonPen.setDashPattern({0.0, 2.0 * dashScale, 1.0 * dashScale, 2.0 * dashScale})
        self.tmpScaleLinePolygonPen = QPen(Qt.green, scale)
        # self.cropPolygonPen = QPen(Qt.green, 10)
        self.penCropPolygon = QPen(Qt.green, scale)
        self.penROIsPolygon = QPen(Qt.red, scale)
        self.penROIsPolygonFillColor = QColor(200, 0, 0, 35)

    # ACTION
    def startDrawCropPolygon(self):
        self.DrawType = DrawType.CROPPOLYGON
        self.__startDraw()

    def startDrawROIPolygon(self):
        self.DrawType = DrawType.ROIPOLYGON
        self.__startDraw()

    def setScale(self):
        self.DrawType = DrawType.SCALELINE
        self.__startDraw()

    def setImage(self, image: QImage):
        View.setImage(self, image)
        if len(self.cropPolygon) > 2:
            self.setCropPolygon(self.cropPolygon)
        else:
            self.setCropPolygon()

    # PROPERTY
    def getCropPolygon(self):
        if len(self.cropPolygon):
            return self.cropPolygon
        image = self.getImage()
        return QPolygonF(image.rect())

    def getROIsPolygon(self):
        ROIsPolygon = []
        for item in self.ROIPolygonsItems:
            ROIsPolygon.append(item.polygon())
        return ROIsPolygon

    def addRoiPolygon(self, polygon: QPolygonF):
        item = self.scene.addPolygon(polygon, self.penROIsPolygon, self.penROIsPolygonFillColor)
        item.setFlag(QGraphicsItem.ItemIsSelectable, True)
        item.setZValue(100)
        self.ROIPolygonsItems.append(item)

    def deleteSelectedROIs(self):
        for item in self.scene.selectedItems():
            self.scene.removeItem(item)
            self.ROIPolygonsItems.remove(item)

    def clear(self):
        View.clear(self)
        # clear the params
        self.initUi()

    def __startDraw(self):
        self.isDrawing = True
        # self.setMouseTracking(True)

    def __stopDraw(self, save=True):
        self.isDrawing = False
        # self.setMouseTracking(False)
        if len(self.pointsCache) < 2 or not save:
            # 未满足条件
            self.pointsCache = []
            return
        elif self.DrawType == DrawType.SCALELINE:
            # show the dialog to input the scale.
            drawnScaleLine = QLineF(self.pointsCache[0], self.pointsCache[1])
            inputLineLength, ok = QInputDialog.getDouble(self, 'Input the length of line', 'Length of line(mm)', 10, 0,
                                                         999999999, 4)
            if not ok:
                return
            if not (inputLineLength and drawnScaleLine.length()):
                QMessageBox.warning('Length of line must be positive number.')
                return
            newScale = inputLineLength / drawnScaleLine.length()
            if not self.realScale:
                oldScale = -1
            else:
                oldScale = self.realScale
            self.RealScaleChangedSignal.emit(newScale, oldScale)
            self.realScale = newScale
        else:
            # 满足条件
            polygon = QPolygonF()
            for point in self.pointsCache:
                polygon.append(point)
            # 判断 polygon 类型
            if self.DrawType == DrawType.CROPPOLYGON:
                self.setCropPolygon(polygon)
            else:
                self.addRoiPolygon(polygon)
            self.PolygonDrawFinishedSignal.emit(self.DrawType, polygon)

        self.pointsCache = []
        self.setCursor(Qt.ArrowCursor)
        self.__tmpPolygonRender()

    def setCropPolygon(self, cropPolygon=None):
        if not cropPolygon or not len(cropPolygon):
            self.cropPolygon = QPolygonF(QRectF(self.getImage().rect()))
        else:
            self.cropPolygon = cropPolygon
        if not self.imageItem:
            return
        originImage = self.imageItem.pixmap()
        newImage = QPixmap(originImage.size())
        newImage.fill(Qt.transparent)
        path = QPainterPath()
        path.addPolygon(self.cropPolygon)
        painter = QPainter(newImage)
        painter.setClipPath(path)
        painter.drawPixmap(QPointF(), originImage)
        painter.end()
        self.imageItem.setPixmap(newImage)
        self.imageItem.update()

    def __tmpPolygonRender(self):
        if hasattr(self, 'tempPolygonItem') and self.tempPolygonItem is not None:
            self.scene.removeItem(self.tempPolygonItem)
            self.tempPolygonItem = None
        if len(self.pointsCache) and self.isDrawing:
            polygon = QPolygonF()
            for point in self.pointsCache:
                polygon.append(point)
            if self.mousePos:
                polygon.append(QPointF(self.mapToScene(self.mousePos)))
            pen = self.tmpCropPolygonPen
            if self.DrawType == DrawType.SCALELINE:
                pen = self.tmpScaleLinePolygonPen
            elif self.DrawType == DrawType.CROPPOLYGON:
                pen = self.tmpCropPolygonPen
            elif self.DrawType == DrawType.ROIPOLYGON:
                pen = self.tmpRoiPolygonPen
            self.tempPolygonItem = self.scene.addPolygon(polygon, pen)

        self.update()
        self.viewport().update()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        View.mousePressEvent(self, event)
        if event.button() == Qt.LeftButton and self.isDrawing:
            # point = QPoint(event.pos().x(), event.pos().y())
            point = self.mapToScene(event.pos())
            self.pointsCache.append(point)
            print('添加坐标点: %f, %f' % (point.x(), point.y()))
        if self.isDrawing and self.DrawType == DrawType.SCALELINE and len(self.pointsCache) == 2:
            self.__stopDraw()
        if event.button() == Qt.RightButton and self.isDrawing:
            self.__stopDraw()
        self.__tmpPolygonRender()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        View.mouseMoveEvent(self, event)
        self.mousePos = event.pos()
        if self.isDrawing:
            self.setCursor(Qt.CrossCursor)
            self.__tmpPolygonRender()
        else:
            self.setCursor(Qt.ArrowCursor)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        # 正在绘制 polygon
        if self.isDrawing:
            if event.key() == Qt.Key_Delete:
                self.pointsCache.pop()
            elif event.key() == Qt.Key_Escape:
                self.__stopDraw(False)
        elif (event.key() == Qt.Key_Delete):
            # 删除选中的 ROIPOLYGON
            self.deleteSelectedROIs()
        self.__tmpPolygonRender()


# 展示结果, 根据 label image 上色

class LabelImageView(View):
    def __init__(self):
        View.__init__(self)
        # 显示模式: 二值化模式, RGB模式
        # 设置 color bar
        self.colorBar = ColorCircle(45)
        colorBarLayout = QVBoxLayout()
        colorBarLayout.addWidget(self.colorBar)
        colorBarLayout.addStretch(1)
        self.hBox.insertLayout(1, colorBarLayout)
        self.initUi()

    def initUi(self):
        View.initUi(self)
        self.cropPolygon = QPolygonF()
        self.binaryImage = np.zeros([], dtype=bool)
        self.realScale = None

    def setCropPolygon(self, cropPolygon: np.ndarray):
        self.cropPolygon = cropPolygon
        self.__updateDrawnItems()

    # 重载, 设置标签图像, 用于展示结果
    def setImage(self, binaryImage: np.array):
        self.binaryImage = binaryImage
        self.__updateDrawnItems()

    def filterSmallZones(self):
        if not self.realScale:
            QMessageBox.warning(self, 'Error', 'The scale should be set before.')
            return
        # get the setting
        minBlockSizeVlue, ok = QInputDialog.getDouble(self, 'Input the filter value(mm^2)',
                                                      'Miniumn size of block(mm^2)', 0.5, 0, 100, 4)
        if not ok:
            return
        # filter the small blocks
        from skimage import morphology
        self.binaryImage = morphology.remove_small_objects(self.binaryImage,
                                                           minBlockSizeVlue / self.realScale / self.realScale,
                                                           connectivity=2)
        self.__updateDrawnItems()

    def filterSmallHoles(self):
        if not self.realScale:
            QMessageBox.warning(self, 'Error', 'The scale should be set before.')
            return
        # get the setting
        minHoleValue, ok = QInputDialog.getDouble(self, 'Input the filter value(mm^2)',
                                                  'Miniumn size of hole in block(mm^2)', 0.5, 0, 100, 4)
        if not ok:
            return
        self.binaryImage = morphology.remove_small_holes(self.binaryImage,
                                                         minHoleValue / self.realScale / self.realScale,
                                                         connectivity=2)
        self.__updateDrawnItems()

    def __updateDrawnItems(self):
        if np.sum(self.binaryImage) <= 0:
            return
        if self.imageItem:
            self.scene.removeItem(self.imageItem)
        from skimage import measure
        labelImage = measure.label(self.binaryImage)
        # 分析 property, 计算角度
        renderImage = QImage(labelImage.shape[0], labelImage.shape[1], QImage.Format_ARGB32)
        renderImage.fill(Qt.white)
        painter = QPainter(renderImage)
        from skimage import measure
        data = measure.regionprops(labelImage)
        for labelData in data:
            # generate the color for each label according to the orientation and axis_length
            orientation = labelData.orientation
            if not labelData.major_axis_length or not labelData.minor_axis_length:
                ratioOfMainAxisAndSecondaryAxis = 0
            else:
                ratioOfMainAxisAndSecondaryAxis = 1 - labelData.minor_axis_length / labelData.major_axis_length / 5
            labelColor = self.colorBar.getColorByAngleAndRP(orientation,
                                                            ratioOfMainAxisAndSecondaryAxis)
            painter.setPen(labelColor)
            points = QPolygon()
            for point in labelData.coords:
                points.append(QPoint(point[0], point[1]))
            painter.drawPoints(points)
        painter.end()
        cropPixmap = QPixmap(renderImage.size())
        cropPixmap.fill(Qt.transparent)
        cropPixmapPainter = QPainter(cropPixmap)
        if len(self.cropPolygon) > 2:
            path = QPainterPath()
            path.addPolygon(self.cropPolygon)
            cropPixmapPainter.setClipPath(path)
        cropPixmapPainter.drawPixmap(QPoint(), QPixmap.fromImage(renderImage))
        cropPixmapPainter.end()
        # renderImage = QPixmap.fromImage(renderImage)
        self.imageItem = self.scene.addPixmap(cropPixmap)
        self.centerOn(self.imageItem)

    def clear(self):
        View.clear(self)
        self.initUi()


from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import numpy as np


class ColorCircle(QWidget):
    def __init__(self, radius=100.0):
        QWidget.__init__(self)
        self.radius = radius
        self.setFixedSize(radius * 2, radius * 2)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def paintEvent(self, ev):
        QWidget.paintEvent(self, ev)
        p = QPainter(self)
        for i in range(self.width()):
            for j in range(self.height()):
                angle = np.arctan2(j - self.radius, i - self.radius)
                r = np.sqrt(np.power(i - self.radius, 2) + np.power(j - self.radius, 2))
                color = self.getColorByAngleAndRP(angle, r / self.radius)
                p.setPen(color)
                p.drawPoint(i, j)

    def getColorByAngleAndRP(self, angle, radiusPercentage):
        color = QColor(255, 255, 255, 0)
        angle = np.mod(angle + 2 * np.pi, 2 * np.pi)
        h = angle / (2. * np.pi)
        v = radiusPercentage
        s = 1.0
        if v <= 1.0:
            color.setHsvF(h, s, v, 1.0)
        return color


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    hLayout = QSplitter(Qt.Horizontal)
    view = PolygonView()
    view.setImage('./SY7.JPG')
    # view.startDrawCropPolygon()
    hLayout.addWidget(view)
    rView = LabelImageView()
    # rView.setImage('./SY7.JPG')
    hLayout.addWidget(rView)
    hLayout.setStretchFactor(0, 1)
    hLayout.setStretchFactor(1, 1)
    mask = np.zeros([1000, 1000], dtype=int)
    mask[100:200, 200:400] = 1
    # rView.setImage(mask)

    width = 500
    height = 400
    polygon = QPolygonF()
    polygon.append(QPointF(0, 0))
    polygon.append(QPointF(10, 150))
    polygon.append(QPointF(100, 250))
    # polygon.append(QPointF(0, 100))
    # polygon.append(QPointF(0, 50))
    # polygon.append(QPointF(150, 50))
    mask = QPolygon2Mask(width, height, polygon)
    rView.setImage(mask)
    image = rView.getRenderedImageFromScene()
    image.save('output.png')
    # cropPolygon = QPolygonF()
    # cropPolygon.append(QPointF(0, 0))
    # cropPolygon.append(QPointF(0, 300))
    # cropPolygon.append(QPointF(200, 300))
    # cropPolygon.append(QPointF(200, 0))
    # rView.setCropPolygon(cropPolygon)
    hLayout.show()
    # view.show()
    sys.exit(app.exec_())
