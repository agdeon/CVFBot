import pyautogui
import cv2
import numpy as np
import math

from func_tester import FTest
import constants
from extended_log import ExtendedLog


##########################
# Вспомогательные функции
##########################
def show_img(img):
    scale = 0.8
    resized = cv2.resize(img, (round(img.shape[1]*scale), round(img.shape[0]*scale)), interpolation = cv2.INTER_AREA)
    cv2.imshow('show_image', resized)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def get_distance(start_point, end_point):
    return math.sqrt(abs(start_point[0] - end_point[0])**2 + abs(start_point[1] - end_point[1])**2)


def is_all_approx_equal(array, etalon, deviation):
    for i in array:
        if abs(i - etalon) > deviation:
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
    img_name = 'test.jpg'
    inter_res = cv2.imread(img_name)
    ExtendedLog.write(constants.LOG_LVL_DETAILED, f'{img_name} загружено')

    return inter_res


def threshold_show(inter_res):
    imgray = cv2.cvtColor(inter_res, cv2.COLOR_RGB2GRAY)
    imgray = cv2.medianBlur(imgray, 3)
    adp_thresh = cv2.adaptiveThreshold(imgray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
    ExtendedLog.write(constants.LOG_LVL_DETAILED, f'Adaptive thresh gaussian', adp_thresh)
    show_img(adp_thresh)

    return inter_res


def find_squares(inter_res):
    imgray = cv2.cvtColor(inter_res, cv2.COLOR_RGB2GRAY)
    imgray = cv2.medianBlur(imgray, 5)
    adp_thresh = cv2.adaptiveThreshold(imgray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
    all_contours, hierarchy = cv2.findContours(adp_thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    bgr_img = cv2.cvtColor(adp_thresh, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(bgr_img, all_contours, -1, (0, 255, 0), 3)
    ExtendedLog.write(constants.LOG_LVL_DETAILED, f'Все контуры найдены {len(all_contours)}шт. ', bgr_img)
    show_img(bgr_img)

    # Отсев по длинне дуги
    cnts_sifted_by_length = []
    for cnt in all_contours:
        perim = cv2.arcLength(cnt, True)
        if 150 < perim < 500:
            cnts_sifted_by_length.append(cnt)
        else:
            ExtendedLog.write(constants.LOG_LVL_COMPLETE, f'Отсеян контур с perim {perim}')
    ExtendedLog.write(constants.LOG_LVL_COMPLETE, f'Подходят по длинне дуги {len(cnts_sifted_by_length)}шт. ')

    # Ищем только квадраты
    sq_contours = []
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
        
        sq_contours.append(cnt)

    bgr_img = cv2.cvtColor(adp_thresh, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(bgr_img, sq_contours, -1, (0, 255, 0), 3)
    ExtendedLog.write(constants.LOG_LVL_DETAILED, f'Контуры квадратов найдены {len(sq_contours)}шт. ', bgr_img)
    show_img(bgr_img)
    return sq_contours


def filter_found_squares(sq_contours):
    # Устранение возможных случаев "контур в контуре"
    print(sq_contours)


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
    test.bind(filter_found_squares, constants.KEY_NUM4)
    test.start()


##########################
# Клиентский код
##########################
ExtendedLog.clear()
ExtendedLog.set_level(constants.LOG_LVL_COMPLETE)
contours_test()
