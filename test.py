from project_constants import *
from key_listener import KeyListener
from extended_log import ExtendedLog
from rod_controller import RodController

ExtendedLog.clear()
ExtendedLog.enable()
ExtendedLog.set_level(LOG_LVL_COMPLETE)


listener1 = KeyListener('Test')
listener1.assign(listener1.stop, KEY_NUM0)
listener1.assign(RodController.cast, KEY_NUM1)
listener1.assign(RodController.bring, KEY_NUM2)
listener1.assign(RodController.stop_bring, KEY_NUM3)
listener1.start()
