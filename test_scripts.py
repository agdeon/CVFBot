import pyautogui
import cv2
import numpy as np
import math
import time

from constants import *
from func_tester import *
from extended_log import *
from img_debug import *


# Переменные в ходе работы
class Runtime:
    image = None
    inventory_area_img = None
    inventory_coords = None
    thresholded_inv_img = None
    contours = None
    hierarchy = None
    square_contours = None
    square_rects = None


# Финальные значения
class Finals:
    inv_rects_with_collisions = None
    relative_inventory_rects = None


# Computing Functions
class CFunc:
    @staticmethod
    def get_distance(start_point, end_point):
        return math.sqrt(abs(start_point[0] - end_point[0]) ** 2 + abs(start_point[1] - end_point[1]) ** 2)

    @staticmethod
    def is_contour_in_area(contour, area):
        for vector in contour:
            for point in vector:
                in_area = area[0][0] < point[0] < area[1][0] and area[0][1] < point[1] < area[1][1]
                if not in_area:
                    return False
        return True

    @staticmethod
    def get_contour_rect(contour):
        x, y, w, h = cv2.boundingRect(contour)
        return [x, y, x + w, y + h]

    @staticmethod
    def has_same_rects(array_of_rects, chk_rect):
        max_deviation = 5
        for cur_rect in array_of_rects:
            if abs(cur_rect[0] - chk_rect[0]) <= max_deviation \
                    and abs(cur_rect[1] - chk_rect[1]) <= max_deviation \
                    and abs(cur_rect[2] - chk_rect[2]) <= max_deviation \
                    and abs(cur_rect[3] - chk_rect[3]) <= max_deviation:
                return True
        return False

    @staticmethod
    def is_contour_square(contour):
        # 4 аппроксимы
        approx = cv2.approxPolyDP(contour, 5, True)
        if len(approx) != 4:
            return False

        # Проверка на равность близл. сторон
        max_deviation = 3
        curve1_start_point = approx[0][0]
        curve2_start_point = approx[1][0]
        curve3_start_point = approx[2][0]
        curve4_start_point = approx[3][0]
        dist_1_to_2 = CFunc.get_distance(curve1_start_point, curve2_start_point)
        dist_2_to_3 = CFunc.get_distance(curve2_start_point, curve3_start_point)
        dist_3_to_4 = CFunc.get_distance(curve3_start_point, curve4_start_point)
        dist_4_to_1 = CFunc.get_distance(curve4_start_point, curve1_start_point)
        dist_list = [dist_1_to_2, dist_2_to_3, dist_3_to_4, dist_4_to_1]
        if max(dist_list) - min(dist_list) > max_deviation:
            return False
        ExtendedLog.write(LOG_LVL_COMPLETE, f'Стороны РАВНЫ: {max(dist_list)}, {min(dist_list)}')

        # Проверка на прямые углы
        max_deviation = 3
        ppdicular_cnt = 0
        prev_curve = approx[3]
        for curve in approx:
            along_axis_movement = \
                abs(prev_curve[0][0] - curve[0][0]) <= max_deviation < abs(prev_curve[0][1] - curve[0][1]) \
                or abs(prev_curve[0][0] - curve[0][0]) > max_deviation >= abs(prev_curve[0][1] - curve[0][1])
            if along_axis_movement:
                ppdicular_cnt += 1
            prev_curve = curve
        if ppdicular_cnt != 4:
            return False

        return True


# Main Functions
class MFunc:
    @staticmethod
    def load_test_img():
        Runtime.image = cv2.imread('day.png')

    @staticmethod
    def take_screenshot():
        img = pyautogui.screenshot()
        Runtime.image = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        ExtendedLog.write(LOG_LVL_DETAILED, 'Скриншот сохранен', Runtime.image)

    @staticmethod
    def select_inventory_area_img():
        h, w, c = Runtime.image.shape
        x0 = w / 2 - w / 6
        y0 = h / 2
        x1 = w / 2 + w / 6.5
        y1 = h
        sub_image = Runtime.image[round(y0):round(y1), round(x0):round(x1)]
        Runtime.inventory_area_img = sub_image
        Runtime.inventory_coords = [x0, y0, x1, y1]

        ExtendedLog.write(LOG_LVL_DETAILED, 'Рабочая область изображения вычислена', sub_image)
        ImgDebug.display(sub_image)

    @staticmethod
    def threshold_inventory_area_img(blur, thresh):
        imgray = cv2.cvtColor(Runtime.inventory_area_img, cv2.COLOR_RGB2GRAY)
        blured = cv2.medianBlur(imgray, blur)
        adp_thresh = cv2.adaptiveThreshold(blured, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, thresh, 2)
        Runtime.thresholded_inv_img = adp_thresh

        ExtendedLog.write(LOG_LVL_COMPLETE, f'Thresholding test', adp_thresh)
        ImgDebug.display(adp_thresh)

    @staticmethod
    def find_all_contours():
        Runtime.contours, Runtime.hierarchy = \
            cv2.findContours(Runtime.thresholded_inv_img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        all_cnt_img = cv2.cvtColor(Runtime.thresholded_inv_img, cv2.COLOR_GRAY2BGR)
        cv2.drawContours(all_cnt_img, Runtime.contours, -1, (0, 255, 0), 1)
        ExtendedLog.write(LOG_LVL_COMPLETE, f'All contours found', all_cnt_img)
        ImgDebug.display(all_cnt_img)

    @staticmethod
    def find_inventory_squares_only():
        # Отсев по длинне дуги
        cnts_sifted_by_length = []
        for cnt in Runtime.contours:
            perim = cv2.arcLength(cnt, True)
            if 250 < perim < 500:
                cnts_sifted_by_length.append(cnt)
        ExtendedLog.write(LOG_LVL_COMPLETE, f'Подходят по длинне дуги: {len(cnts_sifted_by_length)} шт. ')

        sq_contours = []
        for cnt in cnts_sifted_by_length:
            if CFunc.is_contour_square(cnt):
                sq_contours.append(cnt)

        Runtime.square_contours = sq_contours
        Runtime.square_rects = map(CFunc.get_contour_rect, sq_contours)

        squares_img = Runtime.inventory_area_img.copy()
        cv2.drawContours(squares_img, sq_contours, -1, (0, 255, 0), 1)
        ExtendedLog.write(LOG_LVL_COMPLETE, f'Squares contours found', squares_img)
        ImgDebug.display(squares_img)

    @staticmethod
    def draw_relative_inventory_rects():
        img = Runtime.inventory_area_img.copy()
        for x0, y0, x1, y1 in Finals.relative_inventory_rects:
            cv2.rectangle(img, (x0, y0), (x1, y1), (0, 255, 0), 1)
        ImgDebug.display(img)

    @staticmethod
    def group_collisions():
        grouped = []
        collisions = Finals.inv_rects_with_collisions.copy()

        while len(collisions):
            comp = collisions.pop(0)
            grouped.append([comp])
            i = 0
            while i < len(collisions):
                if CFunc.has_same_rects([comp], collisions[i]):
                    grouped[len(grouped) - 1].append(collisions.pop(i))
                else:
                    i += 1

        Finals.grouped_collisions = grouped
        ExtendedLog.write(LOG_LVL_DETAILED, f"Коллизии сгрупированы: {Finals.grouped_collisions}")

    @staticmethod
    def replace_collisions_by_smaller():
        grouped_colls = Finals.grouped_collisions
        smaller_rects = []
        for cur_coll in grouped_colls:
            smaller_rect = None
            for rect in cur_coll:
                if smaller_rect is None:
                    smaller_rect = rect
                if rect[0] >= smaller_rect[0] and rect[1] >= smaller_rect[1] \
                        and rect[2] <= smaller_rect[2] and rect[3] <= smaller_rect[3]:
                    smaller_rect = rect
            smaller_rects.append(smaller_rect)
        Finals.relative_inventory_rects = smaller_rects

# Scripts
def find_slots():
    ImgDebug.disable()

    MFunc.load_test_img()
    MFunc.select_inventory_area_img()

    Finals.inv_rects_with_collisions = []
    for blur in range(3, 151, 2):
        for thresh in range(3, 21, 2):
            MFunc.threshold_inventory_area_img(blur, thresh)
            MFunc.find_all_contours()
            MFunc.find_inventory_squares_only()
            for rect in Runtime.square_rects:
                Finals.inv_rects_with_collisions.append(rect)

    MFunc.group_collisions()
    MFunc.replace_collisions_by_smaller()

    ImgDebug.enable()
    MFunc.draw_relative_inventory_rects()
    ExtendedLog.write(LOG_LVL_DETAILED, f'Found {len(Finals.relative_inventory_rects)} squares at all.')


# Run
ExtendedLog.enable()
ExtendedLog.clear()
ExtendedLog.set_level(LOG_LVL_DETAILED)
ImgDebug.enable()

test = FTest('test1')
test.assign(find_slots, KEY_NUM1)
test.start()
