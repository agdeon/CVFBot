import sys
import time
from pynput import keyboard

import project_constants
from extended_log import ExtendedLog


# Bounded func must have 1 required arg - intermediate result interm_resulst
# which allows to have common variable to all bounded functions
class FTest:
    def __init__(self, text):
        self.name = text
        self.exit = False
        self.numpad_listener = None
        self.associations = []
        self.interm_resulst = None
        self.assign(self._stop, project_constants.KEY_NUM0)

    def assign(self, func, key_const):
        self.associations.append((func, key_const))
        ExtendedLog.write(project_constants.LOG_LVL_COMPLETE, f"[{self.name}]: Функция {func.__name__} привязана к клавише {key_const}")

    def start(self, loop=True):
        ExtendedLog.write(project_constants.LOG_LVL_COMPLETE, f"[{self.name}]: Test запущен с loop={loop}")
        self.numpad_listener = keyboard.Listener(on_press=self._numpad_on_press)
        self.numpad_listener.start()
        if not loop:
            return
        while 1:
            time.sleep(0.2)
            if self.exit:
                ExtendedLog.write(project_constants.LOG_LVL_COMPLETE, f"[{self.name}]: Test завершен")
                break

    def _numpad_on_press(self, key_code):
        func = self._get_func_by_key(key_code)
        if func is None:
            return
        func()

    def _get_func_by_key(self, key_code):
        for f, kc in self.associations:
            if str(key_code) == kc:
                return f

    def _stop(self):
        if self.numpad_listener is not None:
            self.numpad_listener.stop()
        self.exit = True


# для прямых тестов модуля
# if __name__ == '__main__':
#     test1 = FTest('exit_script test')
#     test1.start(loop=True)
