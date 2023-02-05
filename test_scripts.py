import pyautogui
import cv2
import numpy as np
import math
import time

import constants
from func_tester import FTest
from extended_log import ExtendedLog
from img_debug import ImgDebug


# Common variables
class CVar:
    inventory_coords = []
    image = cv2.imread('night.png')


################################
# Вспомогательные функции
################################
def get_distance(start_point, end_point):
    return math.sqrt(abs(start_point[0] - end_point[0]) ** 2 + abs(start_point[1] - end_point[1]) ** 2)


def is_all_approx_equal(array, etalon, max_deviation):
    for i in array:
        if abs(i - etalon) > max_deviation:
            return False

    return True


def is_contour_in_area(contour, area):
    for vector in contour:
        for point in vector:
            in_area = area[0][0] < point[0] < area[1][0] and area[0][1] < point[1] < area[1][1]
            if not in_area:
                return False
    return True


def get_contour_coords(contour):
    x, y, w, h = cv2.boundingRect(contour)
    return [x, y, x + w, y + h]


def array_has_double_coords(array, chk_coord, max_deviation):
    for cur_coord in array:
        if abs(cur_coord[0] - chk_coord[0]) <= max_deviation \
                and abs(cur_coord[1] - chk_coord[1]) <= max_deviation \
                and abs(cur_coord[2] - chk_coord[2]) <= max_deviation \
                and abs(cur_coord[3] - chk_coord[3]) <= max_deviation:
            return True
    return False


##########################
# Функции для привязки
##########################
def take_screenshot():
    img = pyautogui.screenshot()
    CVar.image = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    ExtendedLog.write(constants.LOG_LVL_DETAILED, 'Скриншот сохранен', CVar.image)


def threshold_show():
    imgray = cv2.cvtColor(CVar.image, cv2.COLOR_RGB2GRAY)
    imgray = cv2.medianBlur(imgray, 3)
    adp_thresh = cv2.adaptiveThreshold(imgray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    ExtendedLog.write(constants.LOG_LVL_DETAILED, f'Adaptive thresh gaussian', adp_thresh)
    ImgDebug.display(adp_thresh)


def find_squares(img):
    imgray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    imgray = cv2.medianBlur(imgray, 5)
    adp_thresh = cv2.adaptiveThreshold(imgray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    all_contours, hierarchy = cv2.findContours(adp_thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    bgr_img = cv2.cvtColor(adp_thresh, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(bgr_img, all_contours, -1, (0, 255, 0), 3)
    ExtendedLog.write(constants.LOG_LVL_COMPLETE, f'Все контуры найдены {len(all_contours)}шт. ', bgr_img)
    ImgDebug.display(bgr_img)

    # Отсев по длинне дуги
    cnts_sifted_by_length = []
    for cnt in all_contours:
        perim = cv2.arcLength(cnt, True)
        if 230 < perim < 450:
            cnts_sifted_by_length.append(cnt)
    ExtendedLog.write(constants.LOG_LVL_COMPLETE, f'Подходят по длинне дуги: {len(cnts_sifted_by_length)} шт. ')

    # Ищем только квадраты
    square_contours = []
    for cnt in cnts_sifted_by_length:
        perim = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 10, True)
        if len(approx) != 4:
            ExtendedLog.write(constants.LOG_LVL_COMPLETE, f'Апроксим должно быть 4!')
            continue

        # Проверка на равность близл. сторон
        max_deviation = 15
        curve1_start_point = approx[0][0]
        curve2_start_point = approx[1][0]
        curve3_start_point = approx[2][0]
        curve4_start_point = approx[3][0]
        dist_1_to_2 = get_distance(curve1_start_point, curve2_start_point)
        dist_2_to_3 = get_distance(curve2_start_point, curve3_start_point)
        dist_3_to_4 = get_distance(curve3_start_point, curve4_start_point)
        dist_4_to_1 = get_distance(curve4_start_point, curve1_start_point)
        dist_list = [dist_1_to_2, dist_2_to_3, dist_3_to_4, dist_4_to_1]
        if max(dist_list) - min(dist_list) > max_deviation:
            ExtendedLog.write(constants.LOG_LVL_COMPLETE, f'Стороны не равны! {max(dist_list)}, {min(dist_list)}')
            continue
        ExtendedLog.write(constants.LOG_LVL_COMPLETE, f'Стороны РАВНЫ: {max(dist_list)}, {min(dist_list)}')

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
            ExtendedLog.write(constants.LOG_LVL_COMPLETE, f'Прямых углов меньше чем 4')
            continue

        # Найден квадрат
        square_contours.append(cnt)

    bgr_img = cv2.cvtColor(adp_thresh, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(bgr_img, square_contours, -1, (0, 255, 0), 3)
    ImgDebug.display(bgr_img)
    ExtendedLog.write(constants.LOG_LVL_DETAILED, f'Контуры квадратов: найдено {len(square_contours)} шт. ', bgr_img)

    h, w, ch = img.shape
    search_area = [
        [w / 2 - w / 6, h / 2],  # top left
        [w / 2 + w / 6, h]  # bottom right
    ]
    sifted_by_area_cnts = []
    for cnt in square_contours:
        if is_contour_in_area(cnt, search_area):
            sifted_by_area_cnts.append(cnt)

    # Выбор слотов инвентаря
    inventory_contours = []
    for cnt in sifted_by_area_cnts:
        if abs(cv2.arcLength(cnt, True) - cv2.arcLength(sifted_by_area_cnts[0], True)) < 5:
            inventory_contours.append(cnt)
    bgr_img = cv2.cvtColor(adp_thresh, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(bgr_img, inventory_contours, -1, (0, 255, 255), 3)
    ImgDebug.display(bgr_img)
    ExtendedLog.write(constants.LOG_LVL_DETAILED, f'Контуры инвентаря найдены: {inventory_contours}', bgr_img)

    # Создаем массив координат квадратов [[x0, y0, x1, y1],...] на основе найденных контуров
    inv_squares_coords = []
    for cnt in inventory_contours:
        inv_squares_coords.append(get_contour_coords(cnt))

    return inv_squares_coords


def find_all_inventory_coords():
    cur_coords = find_squares(CVar.image)
    for coord in cur_coords:
        if not array_has_double_coords(CVar.inventory_coords, coord, 3):
            CVar.inventory_coords.append(coord)
    ExtendedLog.write(constants.LOG_LVL_DETAILED, f'Найдено слотов инвентаря: {len(CVar.inventory_coords)}')


def draw_inventory_coords():
    img = CVar.image.copy()
    for x0, y0, x1, y1 in CVar.inventory_coords:
        cv2.rectangle(img, (x0, y0), (x1, y1), (0, 255, 0), 3)
    ImgDebug.display(img)


##########################
# Запуск теста
#######################
ExtendedLog.enable()
ExtendedLog.clear()
ExtendedLog.set_level(constants.LOG_LVL_COMPLETE)
ImgDebug.enable()

test = FTest('test1')
test.bind(take_screenshot, constants.KEY_NUM1)
test.bind(find_all_inventory_coords, constants.KEY_NUM2)
test.bind(draw_inventory_coords, constants.KEY_NUM3)
test.start()
