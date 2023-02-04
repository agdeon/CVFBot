import time
import prconsts as pc
from pynput import keyboard
import sys
from extLog import ExtendedLog


class MTest:
    def __init__(self, text):
        self.name = text
        self.exit = False
        self.numpad_listener = None
        self.associations = []

        ExtendedLog.clear()
        ExtendedLog.set_level(pc.LOG_LVL_COMPLETE)

    def bind(self, func, key_const):
        self.associations.append((func, key_const))
        ExtendedLog.write(pc.LOG_LVL_COMPLETE, f"{self.name}: Функция {func.__name__} привязана к клавише {key_const}")

    def start(self, loop=False):
        ExtendedLog.write(pc.LOG_LVL_COMPLETE, f"{self.name}: Test запущен с loop={loop}")
        self.numpad_listener = keyboard.Listener(on_press=self._numpad_on_press)
        self.numpad_listener.start()
        if not loop:
            return
        while 1:
            time.sleep(0.3)
            if self.exit:
                ExtendedLog.write(pc.LOG_LVL_COMPLETE, f"{self.name}: Test завершен")
                sys.exit()

    def _numpad_on_press(self, key_code):
        func = self._get_func_by_key(key_code)
        if func is None:
            return
        func()

    def _get_func_by_key(self, key_code):
        for f, kc in self.associations:
            if str(key_code) == kc:
                return f

    def exit_script(self):
        self.exit = True


# для прямых тестов модуля
# if __name__ == '__main__':
#     test1 = MTest('exit_script test')
#     test1.bind(test1.exit_script, pc.KEY_NUM0)
#     test1.start(loop=True)
