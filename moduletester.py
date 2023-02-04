import sys
import time
import projectconstants as pc
from pynput import keyboard
from extendedlog import ExtendedLog

# Bounded func must have 1 required arg - intermediate result interm_res
# which allows to have common variable to all bounded functions
# to stop current Test
class MTest:
    def __init__(self, text):
        self.name = text
        self.exit = False
        self.numpad_listener = None
        self.associations = []
        self.interm_res = None   # промежуточный результат для всех тестируемых функций

        self.bind(self._stop, pc.KEY_NUM0)

    def bind(self, func, key_const):
        self.associations.append((func, key_const))
        ExtendedLog.write(pc.LOG_LVL_COMPLETE, f"[{self.name}]: Функция {func.__name__} привязана к клавише {key_const}")

    def start(self, loop=True):
        ExtendedLog.write(pc.LOG_LVL_COMPLETE, f"[{self.name}]: Test запущен с loop={loop}")
        self.numpad_listener = keyboard.Listener(on_press=self._numpad_on_press)
        self.numpad_listener.start()
        if not loop:
            return
        while 1:
            time.sleep(0.2)
            if self.exit:
                ExtendedLog.write(pc.LOG_LVL_COMPLETE, f"[{self.name}]: Test завершен")
                sys.exit()

    def _numpad_on_press(self, key_code):
        func = self._get_func_by_key(key_code)
        if func is None:
            return
        self.interm_res = func(self.interm_res)

    def _get_func_by_key(self, key_code):
        for f, kc in self.associations:
            if str(key_code) == kc:
                return f

    def _stop(self, interm_res):
        if self.numpad_listener is not None:
            self.numpad_listener.stop()
        self.exit = True


# для прямых тестов модуля
# if __name__ == '__main__':
#     test1 = MTest('exit_script test')
#     test1.start(loop=True)
