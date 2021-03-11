# -*- coding: utf-8 -*-

# @FileName: ImageTool.py
# @Time    : 2021-03-08 19:59
# @Author  : Dorad, cug.xia@gmail.com
# @Blog    ：https://blog.cuger.cn


'''
this file provide some function for image transform
'''

import numpy as np
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from skimage import color, measure, morphology


def QImageToGrayByChannel(qimage: QImage, channel, isNdarray=False):
    if not channel in ['RGB', 'Gray', 'Red', 'Green', 'Blue']:
        return False
    if channel == 'RGB':
        return qimage
    imageArray = QImage2NArray(qimage)
    imageArray = NAImage2GrayByChannel(imageArray, channel)
    imageArray = np.squeeze(imageArray)
    if isNdarray:
        return imageArray
    return NArray2QImage(imageArray)


def NAImage2GrayByChannel(image, channel='Gray'):
    channel = channel.upper()
    if not channel in ['GRAY', 'RED', 'GREEN', 'BLUE']:
        return False
    if channel == 'GRAY':
        imageArray = np.mean(image, axis=2)
    elif channel == 'RED':
        imageArray = image[:, :, 0]
    elif channel == 'GREEN':
        imageArray = image[:, :, 1]
    else:
        imageArray = image[:, :, 2]
    return np.squeeze(imageArray)


def QImage2GrayNArray(qimage: QImage):
    return color.rgb2gray(QImage2NArray(qimage))


def QPolygon2Mask(width, height, polygon: QPolygonF):
    '''
    convert QPolygon to mask with the image width and height.
    :param width: image width
    :param height: image height
    :param polygon: QPolygon
    :return: binary image with the pixels in polygon marked as True
    test pass at 2021.03.08
    '''
    poa = np.empty([len(polygon), 2])
    for i, p in enumerate(polygon):
        poa[i, :] = [p.x(), p.y()]
    from skimage import draw
    mask = draw.polygon2mask((width, height), poa)
    return mask


def NArray2QImage(img: np.ndarray):
    '''
    convert ndarray to QImage
    :param img:
    :return:
    '''
    from qimage2ndarray import array2qimage
    if (len(img.shape) > 2):
        img = img.transpose((1, 0, 2))
    else:
        img = img.transpose((1, 0))
    return array2qimage(img)


def NArray2QPixmap(image: np.array):
    return QPixmap.fromImage(NArray2QImage(image))


def QImage2NArray(qimage: QImage):
    '''
    convert QImage to NArray
    :param qimage: QImage
    :return: image with the format of ndarray
    test pass at 2021.03.08
    '''
    from qimage2ndarray import rgb_view
    img = rgb_view(qimage=qimage)
    if (len(img.shape) > 2):
        img = img.transpose((1, 0, 2))
    else:
        img = img.transpose((1, 0))
    return img


def QPixmap2NArray(qpixmap: QPixmap):
    '''
    convert QPixmap to NArray
    :param qpixmap:
    :return:
    '''
    return QImage2NArray(qpixmap.toImage())


def GetBinaryImageWithThresholdWithMask(image: np.array, mask: np.array, threshold: int):
    masked = np.ma.masked_array(image, mask)
    maskedImage = masked.filled(fill_value=0)
    bw = maskedImage >= threshold
    return bw


# 分析 mask == 1 的区域的 OTSU
def OtsuWithMask2bw(image: np.array, mask: np.array):
    from skimage import filters
    masked = np.ma.masked_array(image, mask)
    otsuThreshold = filters.threshold_otsu(masked.compressed())
    bw = GetBinaryImageWithThresholdWithMask(image, mask, otsuThreshold)
    return bw


def QPolygonF2list(polygon: QPolygonF):
    data = []
    for point in polygon:
        data.append([point.x(), point.y()])
    return data


def list2QPolygonF(data):
    polygon = QPolygonF()
    for row in data:
        polygon.append(QPointF(row[0], row[1]))
    return polygon


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    # width = 500
    # height = 400
    # polygon = QPolygonF()
    # polygon.append(QPointF(50, 0))
    # polygon.append(QPointF(150, 280))
    # polygon.append(QPointF(350, 20))
    # mask = QPolygon2Mask(width, height, polygon)
    # plt.imshow(mask)
    # plt.show()
    # pass
    image = QImage("./aligned.jpg")
    ig = QImage2NArray(image)
    print(ig.shape)
    # image_new = NArray2QImage(ig)
    plt.imshow(ig)
    plt.show()
    pass
