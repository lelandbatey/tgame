#!/usr/bin/env python3
'''
tgame is a super simple game of one button and one text field.
'''
from pprint import pformat
import random
import time

import tkinter as tk

# These are the 'states' that our little application can be in.
INITIAL = 'INITIAL'
WAITING = 'WAITING'
TIMER_RUNNING = 'TIMER_RUNNING'
TIMER_STOPPED = 'TIMER_STOPPED'
FINISHED = 'FINISHED'

TIME_PASSED = 'TIME_PASSED'
BUTTON_DOWN = 'BUTTON_DOWN'
BUTTON_RELS = 'BUTTON_RELS'


def partialize(func, stuff):
    def inner(thing=None):
        return func(stuff, thing)

    return inner


class State:
    def __init__(self, root, frame, timer_display, button):
        self.root = root
        self.frame = frame
        self.timer_display = timer_display
        self.button = button

        self.start_running_time = 20
        self.cease_running_time = 20

        self.statename = INITIAL

        self.seconds_user_holding_button = 0
        self.user_currently_pressing_button = False

        self.moment_start_last_frame = 0
        self.moment_start_current_frame = 0

    def __repr__(self):
        yeskeys = [
            'statename',
            'seconds_user_holding_button',
            'user_currently_pressing_button',
            'moment_start_last_frame',
            'moment_start_current_frame',
            'start_running_time',
            'cease_running_time',
        ]
        d = {k: v for k, v in self.__dict__.items() if k in yeskeys}
        return pformat(d)


def generateStartStopTimes():
    # ├────────┬─────────┬───────────┬────────────┤
    #        Now        Next       Next
    #                   start      stop
    #
    # - Time between now and start and start and stop is meant to vary in order to
    #   keep the player on their toes
    now = time.time()
    next_start = now + random.randint(4, 9)
    next_stop = next_start + random.randint(1, 6)
    return next_start, next_stop


def setButtonColor(button, fg, bg):
    button['fg'] = fg
    button['bg'] = bg
    button['activeforeground'] = fg
    button['activebackground'] = bg


def frameUpdate(state: State, event=None):
    if event is None:
        event = TIME_PASSED

    state.moment_start_last_frame = state.moment_start_current_frame
    state.moment_start_current_frame = time.time()

    # Re-enable editing by setting the state back to normal (which allows us to
    # edit and insert the contents), then we edit the contents (by deleting and
    # re-inputting what we want), then we set back to disabled so the user
    # can't type anything.
    state.timer_display.config(state=tk.NORMAL)

    if event == BUTTON_DOWN:
        state.user_currently_pressing_button = True
    elif event == BUTTON_RELS:
        state.user_currently_pressing_button = False

    if state.statename == INITIAL:
        # state.button['text'] = 'CLICK TO START'
        if event is BUTTON_RELS:
            state.statename = WAITING
            strt, stop = generateStartStopTimes()
            state.start_running_time = strt
            state.cease_running_time = stop

    elif state.statename == WAITING:
        state.button['text'] = "Don't click till the timer starts..."
        if state.moment_start_current_frame > state.start_running_time:
            state.statename = TIMER_RUNNING

    elif state.statename == TIMER_RUNNING:
        frame_delta = state.moment_start_current_frame - state.moment_start_last_frame
        if state.moment_start_current_frame < state.cease_running_time:
            state.timer_display.delete('1.0', tk.END)
            time_passed_string = "{:0>8.3f}".format(time.time() - state.start_running_time)
            state.timer_display.insert(tk.END, time_passed_string)
            state.button['text'] = "CLICK AND HOLD!"
            if state.user_currently_pressing_button:
                state.seconds_user_holding_button += frame_delta
                setButtonColor(state.button, 'white', 'green')
            else:
                setButtonColor(state.button, 'white', 'red')
        else:
            if state.user_currently_pressing_button:
                state.seconds_user_holding_button -= frame_delta
                state.button['text'] = "You need to release!"
                setButtonColor(state.button, 'white', 'red')
            else:
                state.statename = TIMER_STOPPED
                setButtonColor(state.button, 'SystemButtonText', 'SystemButtonFace')

    elif state.statename == TIMER_STOPPED:
        max_possible_seconds = state.cease_running_time - state.start_running_time
        total_seconds = state.seconds_user_holding_button
        click_time_ratio = total_seconds / (max_possible_seconds)
        percent = click_time_ratio * 100

        msg = 'clicked for {:0>5.2f} seconds out of {:0>5.2f} seconds\nmissed: {:0>5.2f} seconds\n{:0>4.1f}% of the timer'.format(
            total_seconds,
            max_possible_seconds,
            max_possible_seconds - total_seconds,
            percent,
        )
        state.timer_display.delete('1.0', tk.END)
        state.timer_display.insert(tk.END, msg)
        state.button['text'] = "click to play again"
        if event == BUTTON_RELS:
            state.statename = INITIAL
            state.seconds_user_holding_button = 0
            state.timer_display.delete('1.0', tk.END)
            state.button['text'] = "Click to start playing"

    state.timer_display.config(state=tk.DISABLED)

    if event == TIME_PASSED:
        nextFrameFunc = partialize(frameUpdate, state)
        state.root.after(5, nextFrameFunc)


def buttonPress(state, event):
    frameUpdate(state, event=BUTTON_DOWN)


def buttonRelease(state, event):
    frameUpdate(state, event=BUTTON_RELS)


def main():
    root = tk.Tk()
    frame = tk.Frame(root)
    font = ('TkTextFont', '18')
    timer_display = tk.Text(frame, font=font, height=1, width=20)
    btn = tk.Button(frame, text="Click to start playing")

    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    frame.grid(row=0, column=0, sticky="news")
    frame.columnconfigure(0, weight=1)
    frame.columnconfigure(1, weight=1)
    frame.rowconfigure(0, weight=1)
    timer_display.grid(row=0, column=0, sticky="news")
    btn.grid(row=0, column=1, sticky='news')
    root.geometry('800x640')

    state = State(root, frame, timer_display, btn)
    state.statename = INITIAL

    btn.bind('<ButtonPress-1>', partialize(buttonPress, state))
    btn.bind('<ButtonRelease-1>', partialize(buttonRelease, state))

    nextFrameFunc = partialize(frameUpdate, state)
    state.root.after(5, nextFrameFunc)
    state.root.mainloop()


if __name__ == '__main__':
    main()
