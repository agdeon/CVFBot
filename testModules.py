import pyautogui
import cv2
import numpy as np
import math
import functools

from moduletester import MTest
import projectconstants as pc
from extendedlog import ExtendedLog


# Вспомогательные функции
def show_img(img):
    scale = 0.8
    resized = cv2.resize(img, (round(img.shape[1]*scale), round(img.shape[0]*scale)), interpolation = cv2.INTER_AREA)
    cv2.imshow('show_image', resized)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def get_distance(start_point, end_point):
    return math.sqrt(abs(start_point[0] - end_point[0])**2 + abs(start_point[1] - end_point[1])**2)


# проверяет каждый эл. массива на равность
# определенному значению с допустимым отклонением
def is_all_approx_equal(array, etalon, deviation):
    for i in array:
        if abs(i - etalon) > deviation:
            return False
    return True

# Функции для привязки
def take_screenshot(inter_res):
    img = pyautogui.screenshot()
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    ExtendedLog.write(pc.LOG_LVL_DETAILED, 'Скриншот сохранен', img)
    return img


def load_img(inter_res):
    img_name = 'test.jpg'
    inter_res = cv2.imread(img_name)
    ExtendedLog.write(pc.LOG_LVL_DETAILED, f'{img_name} загружено')
    return inter_res


def threshold_show(inter_res):
    imgray = cv2.cvtColor(inter_res, cv2.COLOR_RGB2GRAY)
    imgray = cv2.medianBlur(imgray, 3)
    adp_thresh = cv2.adaptiveThreshold(imgray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
    ExtendedLog.write(pc.LOG_LVL_DETAILED, f'adaptive thresh gaussian')
    show_img(adp_thresh)
    return inter_res


# Возвращает контуры найденных квадратов
def find_squares(inter_res):
    imgray = cv2.cvtColor(inter_res, cv2.COLOR_RGB2GRAY)
    imgray = cv2.medianBlur(imgray, 5)
    adp_thresh = cv2.adaptiveThreshold(imgray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
    cnts, hierarchy = cv2.findContours(adp_thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    all_cnt_img = cv2.cvtColor(adp_thresh, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(all_cnt_img, cnts, -1, (0, 255, 0), 3)
    ExtendedLog.write(pc.LOG_LVL_DETAILED, f'Все контуры найдены {len(cnts)}шт. ', all_cnt_img)
    show_img(all_cnt_img)

    # отсеиваем по приблизительной длинне слота
    cnts_sifted_by_length = []
    for cnt in cnts:
        perim = cv2.arcLength(cnt, True)
        if perim > 150 and perim < 520:
            cnts_sifted_by_length.append(cnt)
        else:
            ExtendedLog.write(pc.LOG_LVL_COMPLETE, f'Отсеян контур с perim {perim}')
    ExtendedLog.write(pc.LOG_LVL_COMPLETE, f'Подходят по длинне дуги {len(cnts_sifted_by_length)}шт. ')

    # ищем только квадраты
    sq_contours = []
    for cnt in cnts_sifted_by_length:
        perim = cv2.arcLength(cnt, True)
        # апроксимируем кривые, обход квадрата в апроксиме идет начиная
        # с top left точки: down -> right -> up -> left
        approx = cv2.approxPolyDP(cnt, 3, True)
        if len(approx) != 4:
            ExtendedLog.write(pc.LOG_LVL_COMPLETE, f'Апроксим должно быть 4!')
            continue

        # проверка на равность близл. сторон
        deviation = 3
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
            ExtendedLog.write(pc.LOG_LVL_COMPLETE, f'Стороны не равны! {max(dist_list)}, {min(dist_list)}')
            continue

        # проверка на прямые углы
        deviation = 3   # допустимое отклонение в пикселях
        perpendicular_cnt = 0   # должно быть 4
        prev_curve = approx[3]
        for curve in approx:
            if abs(prev_curve[0][0] - curve[0][0]) <= deviation and abs(prev_curve[0][1] - curve[0][1]) > deviation:
                perpendicular_cnt += 1
            elif abs(prev_curve[0][0] - curve[0][0]) > deviation and abs(prev_curve[0][1] - curve[0][1]) <= deviation:
                perpendicular_cnt += 1
            prev_curve = curve
        if perpendicular_cnt != 4:
            ExtendedLog.write(pc.LOG_LVL_COMPLETE, f'Прямых углов меньше чем 4')
            continue
        sq_contours.append(cnt)

    restored = cv2.cvtColor(adp_thresh, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(restored, sq_contours, -1, (0, 255, 0), 3)
    ExtendedLog.write(pc.LOG_LVL_DETAILED, f'Контуры квадратов найдены {len(sq_contours)}шт. ', restored)
    show_img(restored)
    return sq_contours


# Отсеиваем мелкие квадраты
def filter_found_squares(sq_contours):
    # Устранение возможных случаев "контур в контуре"
    print(sq_contours)


# Готовые сценарии тестов
def screenshot_test():
    ExtendedLog.clear()
    ExtendedLog.set_level(pc.LOG_LVL_DETAILED)
    screnshot_test = MTest('screenshot_test')
    screnshot_test.bind(take_screenshot, pc.KEY_NUM1)
    screnshot_test.start()


def contours_test():
    test = MTest('all_contours_test')
    test.bind(take_screenshot, pc.KEY_NUM1)
    test.bind(load_img, pc.KEY_NUM2)
    test.bind(find_squares, pc.KEY_NUM3)
    test.bind(filter_found_squares, pc.KEY_NUM4)
    test.start()


# Клиентский код
ExtendedLog.clear()
ExtendedLog.set_level(pc.LOG_LVL_COMPLETE)
contours_test()
