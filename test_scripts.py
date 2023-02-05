import pyautogui
import cv2
import numpy as np
import math

import constants
from func_tester import FTest
from extended_log import ExtendedLog
from img_debug import ImgDebug


################################
# Вспомогательные функции
################################
def get_distance(start_point, end_point):
    return math.sqrt(abs(start_point[0] - end_point[0])**2 + abs(start_point[1] - end_point[1])**2)


def is_all_approx_equal(array, etalon, deviation):
    for i in array:
        if abs(i - etalon) > deviation:
            return False

    return True


def is_contour_in_area(contour, area):
    for vector in contour:
        for point in vector:
            in_area = area[0][0] < point[0] < area[1][0] and area[0][1] < point[1] < area[1][1]
            if not in_area:
                return False
    return True



##########################
# Функции для привязки
##########################
def take_screenshot(inter_res):
    img = pyautogui.screenshot()
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    ExtendedLog.write(constants.LOG_LVL_DETAILED, 'Скриншот сохранен', img)

    return img


def load_img(inter_res):
    img_name = 'day.png'
    inter_res = cv2.imread(img_name)
    ExtendedLog.write(constants.LOG_LVL_DETAILED, f'{img_name} загружено')

    return inter_res


def threshold_show(inter_res):
    imgray = cv2.cvtColor(inter_res, cv2.COLOR_RGB2GRAY)
    imgray = cv2.medianBlur(imgray, 3)
    adp_thresh = cv2.adaptiveThreshold(imgray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
    ExtendedLog.write(constants.LOG_LVL_DETAILED, f'Adaptive thresh gaussian', adp_thresh)
    ImgDebug.display(adp_thresh)

    return inter_res


def find_squares(img):
    imgray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    imgray = cv2.medianBlur(imgray, 5)
    adp_thresh = cv2.adaptiveThreshold(imgray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
    all_contours, hierarchy = cv2.findContours(adp_thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    bgr_img = cv2.cvtColor(adp_thresh, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(bgr_img, all_contours, -1, (0, 255, 0), 3)
    ExtendedLog.write(constants.LOG_LVL_COMPLETE, f'Все контуры найдены {len(all_contours)}шт. ', bgr_img)
    ImgDebug.display(bgr_img)

    # Отсев по длинне дуги
    cnts_sifted_by_length = []
    for cnt in all_contours:
        perim = cv2.arcLength(cnt, True)
        if 250 < perim < 450:
            cnts_sifted_by_length.append(cnt)
        # else:
        #     ExtendedLog.write(constants.LOG_LVL_COMPLETE, f'Отсеян контур с perim {perim}')
    ExtendedLog.write(constants.LOG_LVL_COMPLETE, f'Подходят по длинне дуги: {len(cnts_sifted_by_length)} шт. ')

    # Ищем только квадраты
    square_contours = []
    for cnt in cnts_sifted_by_length:
        perim = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 3, True)
        if len(approx) != 4:
            ExtendedLog.write(constants.LOG_LVL_COMPLETE, f'Апроксим должно быть 4!')
            continue

        # Проверка на равность близл. сторон
        deviation = 5
        curve1_start_point = approx[0][0]
        curve2_start_point = approx[1][0]
        curve3_start_point = approx[2][0]
        curve4_start_point = approx[3][0]
        dist_1_to_2 = get_distance(curve1_start_point, curve2_start_point)
        dist_2_to_3 = get_distance(curve2_start_point, curve3_start_point)
        dist_3_to_4 = get_distance(curve3_start_point, curve4_start_point)
        dist_4_to_1 = get_distance(curve4_start_point, curve1_start_point)
        dist_list = [dist_1_to_2, dist_2_to_3, dist_3_to_4, dist_4_to_1]
        if max(dist_list) - min(dist_list) > deviation:
            ExtendedLog.write(constants.LOG_LVL_COMPLETE, f'Стороны не равны! {max(dist_list)}, {min(dist_list)}')
            continue
        ExtendedLog.write(constants.LOG_LVL_COMPLETE, f'Стороны РАВНЫ: {max(dist_list)}, {min(dist_list)}')

        # Проверка на прямые углы
        deviation = 3
        ppdicular_cnt = 0
        prev_curve = approx[3]
        for curve in approx:
            along_axis_movement = \
                abs(prev_curve[0][0] - curve[0][0]) <= deviation < abs(prev_curve[0][1] - curve[0][1]) \
                or abs(prev_curve[0][0] - curve[0][0]) > deviation >= abs(prev_curve[0][1] - curve[0][1])
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
    slot_sample_ctr = None
    search_area = [
        [w/2 - w/6, h/2], # top left
        [w/2 + w/6, h]  # bottom right
    ]
    for cnt in square_contours:
        if is_contour_in_area(cnt, search_area):
            bgr_img = cv2.cvtColor(adp_thresh, cv2.COLOR_GRAY2BGR)
            cv2.drawContours(bgr_img, cnt, -1, (0, 255, 255), 3)
            ImgDebug.display(bgr_img)
            ExtendedLog.write(constants.LOG_LVL_DETAILED, f'Образец найден: {cnt}', bgr_img)

            slot_sample_ctr = cnt
            break

    # Выбор слотов инвентаря
    inventory_contours = []
    for cnt in square_contours:
        if abs(cv2.arcLength(cnt, True) - cv2.arcLength(slot_sample_ctr, True)) < 5:
            inventory_contours.append(cnt)
    bgr_img = cv2.cvtColor(adp_thresh, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(bgr_img, inventory_contours, -1, (0, 255, 255), 3)
    ImgDebug.display(bgr_img)
    ExtendedLog.write(constants.LOG_LVL_DETAILED, f'Слоты инвентаря найдены: {inventory_contours}', bgr_img)

    return inventory_contours


##########################
# Готовые сценарии
##########################
def screenshot_test():
    ExtendedLog.clear()
    ExtendedLog.set_level(constants.LOG_LVL_DETAILED)
    screnshot_test = FTest('screenshot_test')
    screnshot_test.bind(take_screenshot, constants.KEY_NUM1)
    screnshot_test.start()


def contours_test():
    test = FTest('all_contours_test')
    test.bind(take_screenshot, constants.KEY_NUM1)
    test.bind(load_img, constants.KEY_NUM2)
    test.bind(find_squares, constants.KEY_NUM3)
    test.start()


ExtendedLog.enable()
ExtendedLog.clear()
ExtendedLog.set_level(constants.LOG_LVL_COMPLETE)
ImgDebug.enable()
contours_test()
