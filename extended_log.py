import os
import time
import cv2
import shutil

import constants


class ExtendedLog:
    enabled = True
    level = constants.LOG_LVL_COMMON

    folder_name = "Logs"
    image_folder_name = "ImageLog"
    filename = 'TextLog.txt'
    img_type = '.png'

    def write(level, text, img=None, console=True, exceptional=False):
        if not ExtendedLog.enabled or level > ExtendedLog.level:
            return
        parent_directory = os.getcwd()
        log_dir = os.path.join(parent_directory, ExtendedLog.folder_name)
        if not os.path.exists(log_dir):
            os.mkdir(log_dir)
        image_log_dir = os.path.join(log_dir, ExtendedLog.image_folder_name)
        if not os.path.exists(image_log_dir):
            os.mkdir(image_log_dir)
        if img is not None:
            img_name = str(round(time.time()*1000)) + ExtendedLog.img_type
            textlog = f'{text} -> Image: {img_name}'
            cv2.imwrite(os.path.join(image_log_dir, img_name), img)
        else:
            textlog = text
        file_path = os.path.join(log_dir, ExtendedLog.filename)
        with open(file_path, "a", encoding="utf-8") as file:
            file.write(f"{textlog}\n")
        if console:
            print(textlog)

    # устанавливает отображение логов по степени информативности
    def set_level(level):
        ExtendedLog.level = level

    def clear():
        path = os.path.join(os.getcwd(), ExtendedLog.folder_name)
        if os.path.exists(path):
            shutil.rmtree(path)

    def disable():
        ExtendedLog.enabled = False

    def enable():
        ExtendedLog.enabled = True


# для прямых тестов модуля
# if __name__ == '__main__':
#     ExtendedLog.clear()
#     ExtendedLog.set_level(cnst.LOG_LVL_COMMON)
#     ExtendedLog.write(cnst.LOG_LVL_COMMON, 'Just a random text...')

