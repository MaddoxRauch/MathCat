#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
   MultiExpressionButton extends the Kivy Button object and adds three different events; on_single_press,
   on_double_press, and on_double_press. DOUBLE_PRESS_TIME determines how long it will wait for the second press before
   concluding it is a single press and LONG_PRESS_TIME determines how long the button must be held down to be considered
   a long press.
"""
from kivy.uix.button import Button
from kivy.clock import Clock
import timeit

__author__ = "Mark Rauch Richards"

DOUBLE_TAP_TIME = 0.2   # Change time in seconds
LONG_PRESSED_TIME = 0.3  # Change time in seconds


class MultiExpressionButton(Button):

    def __init__(self, **kwargs):
        super(MultiExpressionButton, self).__init__(**kwargs)
        self.start = 0
        self.single_hit = 0
        self.press_state = False
        self.register_event_type('on_single_press')
        self.register_event_type('on_double_press')
        self.register_event_type('on_long_press')

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.start = timeit.default_timer()
            if touch.is_double_tap:
                self.press_state = True
                self.single_hit.cancel()
                self.dispatch('on_double_press')
        else:
            return super(MultiExpressionButton, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.press_state is False:
            if self.collide_point(touch.x, touch.y):
                stop = timeit.default_timer()
                awaited = stop - self.start

                def not_double(time):
                    nonlocal awaited
                    if awaited > LONG_PRESSED_TIME:
                        self.dispatch('on_long_press')
                    else:
                        self.dispatch('on_single_press')

                self.single_hit = Clock.schedule_once(not_double, DOUBLE_TAP_TIME)
            else:
                return super(MultiExpressionButton, self).on_touch_down(touch)
        else:
            self.press_state = False

    def on_single_press(self):
        pass

    def on_double_press(self):
        pass

    def on_long_press(self):
        pass
