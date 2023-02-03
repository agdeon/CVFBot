from enum import Enum
import os
import time
import cv2
import shutil


class LogTypes(Enum):
    COMMON = 0  # общие логи
    DETAILED = 1    # детальные логи
    COMPLETE = 2    # полные логи


class ExtendedLog:
    enabled = True
    global_log_type = LogTypes.COMMON

    folder_name = "Logs"
    image_folder_name = "ImageLog"
    filename = 'TextLog.txt'
    img_type = '.png'

    def write(log_type, text, img=None, console=True, exceptional=False):
        if not ExtendedLog.enabled or log_type.value > ExtendedLog.global_log_type.value:
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
        with open(file_path, "a") as file:
            file.write(f"{textlog}\n")
        if console:
            print(textlog)

    # устанавливает отображение логов по степени информативности
    def set_global_type(log_type):
        ExtendedLog.global_log_type = log_type

    def clear():
        path = os.path.join(os.getcwd(), ExtendedLog.folder_name)
        if os.path.exists(path):
            shutil.rmtree(path)

    def disable():
        ExtendedLog.enabled = False

    def enable():
        ExtendedLog.enabled = True
