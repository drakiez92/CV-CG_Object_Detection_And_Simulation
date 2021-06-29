import io
import numpy as np
import cv2 as cv


def detect_color(img):
    img_hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    lower_green = (20, 30, 150)
    upper_green = (40, 80, 250)
    mask = cv.inRange(img_hsv, lower_green, upper_green)
    result = cv.bitwise_and(img_hsv, img_hsv, mask=mask)
    return result


def detect_corner(img, blockSize=3, ksize=3, k=0.04, threshold=0.01):
    gray = img
    dst = cv.cornerHarris(gray, blockSize, ksize, k)
    # result is dilated for marking the corners, not important
    dst = cv.dilate(dst, None)
    img = img*0
    # Threshold for an optimal value, it may vary depending on the image.
    img[dst > threshold*dst.max()] = 255

    return img


def box_board(img):
    w, h = img.shape
    corner = []
    distance = []
    min_x1, min_x2, min_x3, min_x4 = 9999999, 9999999, 9999999, 9999999
    x1, x2, x3, x4 = 0, 0, 0, 0
    for i in range(w):
        for j in range(h):
            if img[i, j] == 255:
                corner.append([i, j])
                if (i**2 + j**2 < min_x1):
                    min_x1 = i**2 + j**2
                    x1 = (j, i)
                if (i**2 + (h-j)**2 < min_x2):
                    min_x2 = i**2 + (h-j)**2
                    x2 = (j, i)
                if ((w-i)**2 + j**2 < min_x3):
                    min_x3 = (w-i)**2 + j**2
                    x3 = (j, i)
                if ((w-i)**2 + (h-j)**2 < min_x4):
                    min_x4 = (w-i)**2 + (h-j)**2
                    x4 = (j, i)
    return x1, x2, x3, x4


def detect_board(img):

    img_color = detect_color(img)
    img_color = cv.cvtColor(cv.cvtColor(
        img_color, cv.COLOR_HSV2BGR), cv.COLOR_BGR2GRAY)
    img_corner = detect_corner(img_color)
    x1, x2, x3, x4 = box_board(img_corner)
    return x1, x2, x3, x4


def find_pos(x, y, w, h):
    pos_x = int(x / w * 8) + 1
    pos_y = int(y / h * 8) + 1
    return pos_x, pos_y


def huy(img):
    return detect_board(img)


def perspective_point(xmin, ymin, xmax, ymax):
    x = (xmax + xmin) // 2
    y = ymin + (ymax - ymin) // 8 
    return (x, y)


def get_position(img, detected):
    board_corner = huy(img)
    positions = []
    pts1 = np.array(board_corner, dtype=np.float32)
    pts2 = np.float32([[0, 0], [400, 0], [0, 400], [400, 400]])

    matrix = cv.getPerspectiveTransform(pts1, pts2)
    for obj in detected:
        xmin = obj['xmin']
        xmax = obj['xmax']
        ymin = obj['ymin']
        ymax = obj['ymax']
        # result = cv.warpPerspective(img, matrix, (400, 400))

        x, y = perspective_point(xmin, ymin, xmax, ymax)

        print(x, y)
        topleft = cv.perspectiveTransform(np.array([[[x, y]]], dtype=np.float32), matrix)
        x, y = topleft[0, 0]
        print(x, y)

        x, y = find_pos(x, y, 400, 400)

        positions.append(dict({'name': obj['name'], 'x': x, 'y': y}))

    return positions


def find_chessboard(img, detected):

    return dict({'isDetected': 'ok', 'positions': get_position(img, detected)})
