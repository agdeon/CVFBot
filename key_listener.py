import sys
import time
from pynput import keyboard
from project_constants import *
from extended_log import ExtendedLog


class KeyListener:

    def __init__(self, name):
        self.name = name
        self.exit = False
        self.listener = None
        self.associations = []

    def start(self):
        self.listener = keyboard.Listener(on_press=self._on_any_key_press)
        self.listener.start()
        while 1:
            time.sleep(0.1)
            if self.exit:
                ExtendedLog.write(LOG_LVL_COMPLETE, f"[Listener {self.name}]: Loop exit")
                break

    def _get_func_by_key(self, key_code):
        for f, kc in self.associations:
            if str(key_code) == kc:
                return f

    def _on_any_key_press(self, key_code):
        func = self._get_func_by_key(key_code)
        if func is None:
            return
        func()
        ExtendedLog.write(LOG_LVL_COMPLETE, f"[Listener {self.name}]: Function \"{func.__name__}\" execution")

    def stop(self):
        if self.listener is not None:
            self.listener.stop()
        self.exit = True

    def assign(self, func, key_const):
        self.associations.append((func, key_const))
        ExtendedLog.write(LOG_LVL_COMPLETE,
                          f"[Listener {self.name}]: Function \"{func.__name__}\" have been assigned to key with code: {key_const}")


# для прямых тестов модуля
if __name__ == "__main__":
    listener1 = KeyListener('Test')
    listener1.start()