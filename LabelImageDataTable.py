#!/usr/bin/python3
# -*-coding:utf-8 -*-

# Reference: **********************************************
# @Project   : code
# @File  : LabelImageDataTable.py
# @Time  : 2020/6/25 20:59
# @License   : LGPL
# @Author  : Dorad
# @Email   : cug.xia@gmail.com
# @Blog      : https://blog.cuger.cn

import csv

import numpy as np
from PyQt5.QtCore import QPointF, Qt, pyqtSignal, QRectF
from PyQt5.QtGui import QIcon, QColor, QPolygonF
from PyQt5.QtWidgets import QWidget, QToolBar, QAction, QTableWidget, QAbstractItemView, QVBoxLayout, QHBoxLayout, \
    QTableWidgetItem, \
    QFileDialog, QMessageBox, QApplication, QGroupBox, QLabel, QLineEdit, QSpacerItem, QSizePolicy


class LabelDataTable(QWidget):
    labelSelectedSignal = pyqtSignal([object], name='Table selected label changed')

    def __init__(self):
        super(LabelDataTable, self).__init__()
        self.selectedRows = np.array([], dtype=int)
        self.realScale = None
        self.polygon = None

    def initUi(self):
        self.tableHeaders = [
            'Center X(px)', 'Center Y(px)', 'Area(mm^2)', 'Perimeter(mm)', 'Area(px^2)', 'Perimeter(px)'
        ]
        self.tableData = np.array([])

        # add action
        self.toolbarHBox = QHBoxLayout()
        self.toolbar = QToolBar()

        # cancel section action
        self.showAllAction = QAction(QIcon('./res/icons/show.png'), 'Show all regions')
        self.showAllAction.triggered.connect(self.showAllRegion)

        # save action
        self.saveAction = QAction(QIcon('./res/icons/CSV.png'), 'Export table as csv')
        self.saveAction.triggered.connect(self.saveAsCsv)

        self.toolbar.addAction(self.showAllAction)
        self.toolbar.addAction(self.saveAction)
        self.toolbarHBox.addSpacerItem(QSpacerItem(20, 5, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.toolbarHBox.addWidget(self.toolbar)

        # add a status of total information, area, perimeter
        shearPerimeterHBox = QHBoxLayout()
        shearPerimeterLabel = QLabel('Perimeter: ')
        shearPerimeterValue = QLineEdit()
        shearPerimeterValue.setText('0')
        # shearPerimeterValue.setDisabled(True)
        shearPerimeterHBox.addWidget(shearPerimeterLabel)
        shearPerimeterHBox.addWidget(shearPerimeterValue)
        self.shearPerimeterValue = shearPerimeterValue

        shearAreaHBox = QHBoxLayout()
        shearAreaLabel = QLabel('Area: ')
        shearAreaValue = QLineEdit()
        shearAreaValue.setText('0')
        # shearAreaValue.setDisabled(True)
        # shearAreaHBox.addWidget(shearAreaLabel)
        # shearAreaHBox.addWidget(shearAreaValue)
        shearPerimeterHBox.addWidget(shearAreaLabel)
        shearPerimeterHBox.addWidget(shearAreaValue)
        self.shearAreaValue = shearAreaValue

        totalShearFailureRegionAreaHBox = QHBoxLayout()
        totalShearFailureRegionAreaLabel = QLabel('Total Area of Shear Failure Damage Zone:')
        totalShearFailureRegionAreaValue = QLineEdit()
        totalShearFailureRegionAreaValue.setText('0')
        # totalShearFailureRegionAreaValue.setDisabled(True)
        totalShearFailureRegionAreaHBox.addWidget(totalShearFailureRegionAreaLabel)
        totalShearFailureRegionAreaHBox.addWidget(totalShearFailureRegionAreaValue)
        # totalShearFailureRegionAreaHBox.addSpacerItem(QSpacerItem(20, 5, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.totalShearFailureRegionAreaValue = totalShearFailureRegionAreaValue

        group = QGroupBox()
        group.setTitle('Summary')
        vBox = QVBoxLayout(group)
        vBox.addLayout(shearPerimeterHBox)
        vBox.addLayout(shearAreaHBox)
        vBox.addLayout(totalShearFailureRegionAreaHBox)
        group.setLayout(vBox)

        self.table = QTableWidget(0, 6)  # id,area(mm^2), perimeter(mm), area(px^2), perimeter(px),cx(px),cy(px)
        self.table.setHorizontalHeaderLabels(self.tableHeaders)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        # set triggers for select
        # selectionModel = self.table.selectionModel()
        self.table.selectionModel().selectionChanged.connect(self.itemClickedAction)

        self.setWindowTitle('Detail Information of Shear Damage Zones')
        self.setWindowIcon(QIcon('./res/icons/table-white.png'))
        self.table.verticalHeader().setVisible(True)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(group)
        self.mainLayout.addWidget(self.table)
        self.mainLayout.addLayout(self.toolbarHBox)
        self.setLayout(self.mainLayout)
        self.labelData = []
        self.resize(self.table.size().width(), self.size().height())

    def setData(self, binaryImage, realScale, cropPolygon: QPolygonF = None):
        self.initUi()
        self.realScale = realScale
        if not cropPolygon:
            cropPolygon = QPolygonF(QRectF(0, 0, binaryImage.shape[0], binaryImage.shape[1]))
        from skimage import measure
        labelImage = measure.label(binaryImage)
        self.labelData = measure.regionprops(labelImage)
        self.tableData = np.zeros([len(self.labelData), 6])
        for i, row in enumerate(self.labelData):
            self.tableData[i, 0:6] = [
                row.centroid[0],
                row.centroid[1],
                row.area * realScale * realScale if realScale else 0,
                row.perimeter * realScale if realScale else 0,
                row.area,
                row.perimeter
            ]
        # shapely
        from shapely.geometry import Polygon
        data = []
        for point in cropPolygon:
            data.append([point.x(), point.y()])
        self.polygon = Polygon(data)
        if not realScale:
            self.shearPerimeterValue.setText(
                '%.2f px' % (self.polygon.length))
            self.shearAreaValue.setText('%.2f px^2' % (self.polygon.area))
            self.totalShearFailureRegionAreaValue.setText(
                '%.2f px^2' % (np.sum(self.tableData[:, 4])))
        else:
            self.shearPerimeterValue.setText(
                '%.2f px / %.2f mm' % (self.polygon.length, self.polygon.length * self.realScale))
            self.shearAreaValue.setText(
                '%.2f px^2 / %.2f mm^2' % (self.polygon.area, self.polygon.area * self.realScale * self.realScale))
            self.totalShearFailureRegionAreaValue.setText(
                '%.2f px^2 / %.2f mm^2' % (np.sum(self.tableData[:, 4]), np.sum(self.tableData[:, 2])))
        self.updateTable()

    def updateTable(self):
        self.table.setRowCount(len(self.labelData) + 1)
        for r in range(self.tableData.shape[0]):
            for c in range(self.tableData.shape[1]):
                item = QTableWidgetItem('%.2f' % self.tableData[r, c])
                item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.table.setItem(r, c, item)
        totalRow = len(self.tableData)
        item = QTableWidgetItem('Total')
        item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        item.setBackground(QColor(240, 240, 240))
        self.table.setItem(totalRow, 0, item)
        self.table.setSpan(totalRow, 0, 1, 2)
        for i in range(2, 6):
            item = QTableWidgetItem('%.2f' % np.sum(self.tableData[:, i]))
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            item.setBackground(QColor(240, 240, 240))
            self.table.setItem(totalRow, i, item)
        self.update()

    def showAllRegion(self):
        self.table.clearSelection()

    def saveAsCsv(self):
        import datetime
        filePath, fileType = QFileDialog.getSaveFileName(self, 'Save File',
                                                         './ShearFailureRegion-%s.csv' % (
                                                             datetime.datetime.now().strftime('%Y%m%d%H%M%S')),
                                                         'CSV(*.csv)')
        if not filePath:
            QMessageBox.warning(self, 'No Path Selected', 'No Path is selected.')
        else:
            with open(filePath, 'w') as stream:
                writer = csv.writer(stream, lineterminator='\n')
                writer.writerow([
                    'Rock Joint Shear Failure Region Detail Information'
                ])
                if not self.realScale:
                    writer.writerow([
                        'Shear Perimeter',
                        '%.2f px' % (self.polygon.length),
                        'Shear Area',
                        '%.2f px^2' % (self.polygon.area)
                    ])
                else:
                    writer.writerow([
                        'Shear Perimeter',
                        '%.2f px / %.2f mm' % (self.polygon.length, self.polygon.length * self.realScale),
                        'Shear Area',
                        '%.2f px^2 / %.2f mm^2' % (
                            self.polygon.area, self.polygon.area * self.realScale * self.realScale),
                        'Real Scale',
                        self.realScale
                    ])
                writer.writerow(self.tableHeaders)
                writer.writerows(list(self.tableData))
                writer.writerow([
                    'Total',
                    '',
                    self.table.item(self.table.rowCount() - 1, 2).text(),
                    self.table.item(self.table.rowCount() - 1, 3).text(),
                    self.table.item(self.table.rowCount() - 1, 4).text(),
                    self.table.item(self.table.rowCount() - 1, 5).text(),
                ])

    def itemClickedAction(self, selected, deselected):
        selectedRows = np.unique(np.array(list(map(lambda x: x.row() + 1, selected.indexes()))))
        deselectedRows = np.unique(np.array(list(map(lambda x: x.row() + 1, deselected.indexes()))))
        print("selected add: %s; deselected: %s" % (selectedRows, deselectedRows))
        self.selectedRows = np.unique(np.append(self.selectedRows, selectedRows)).astype(np.int)
        self.selectedRows = np.setdiff1d(self.selectedRows, deselectedRows).astype(np.int)
        selectedRows = self.selectedRows
        if not len(self.selectedRows):
            selectedRows = np.arange(1, self.table.rowCount())
        print("selected: %s" % selectedRows)
        self.labelSelectedSignal.emit(selectedRows)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    demo = LabelDataTable()
    labelMask = np.zeros([100, 100], int)
    labelMask[20:30, 10:30] = 1
    labelMask[50:60, 45:60] = 2
    labelMask[70:80, 35:80] = 3
    labelMask[10:15, 23:30] = 4
    labelMask[20:30, 50:70] = 5
    demo.setData(labelMask, None, QPolygonF([
        QPointF(0, 0),
        QPointF(0, 10),
        QPointF(10, 10),
        QPointF(10, 0),
    ]))
    demo.show()
    sys.exit(app.exec_())
