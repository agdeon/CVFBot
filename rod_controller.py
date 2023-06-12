import pyautogui
import time


class RodController:
    exit = False

    @staticmethod
    def bring():
        while 1:
            if RodController.exit:
                RodController.exit = False
                break
            pyautogui.press('a')
            pyautogui.press('s')
            pyautogui.press('d')
            time.sleep(0.1)

    @staticmethod
    def stop_bring():
        RodController.exit = True

    @staticmethod
    def cast():
        pass

    @staticmethod
    def switch():
        pass


if __name__ == "__main__":
    RodController.bring()