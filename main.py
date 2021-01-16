import time
import kivy

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.clock import Clock
from kivy.graphics.instructions import Canvas, CanvasBase
from kivy.uix.checkbox import CheckBox

from macos_speech import Synthesizer

speaker = Synthesizer(voice='Alex')

num_blocks_left, num_blocks_done, list_tasks, list_completed = (0, 0, '', [])
task_time, breaktime, big_breaktime = 1, 1, 1
check_ref_box, whole_box = [], None


def on_checkbox_active(dic):
    global list_tasks
    global list_completed
    for idx, wgt in dic.items():
        check_obj = wgt[0]
        task_name = wgt[1]
        if check_obj.active and task_name not in list_completed:
            list_completed.append(task_name)
            list_tasks.remove(task_name)
            print(f"{wgt[1]} has been completed")
    return None


class TitleLayout(GridLayout):
    background_image = ObjectProperty(
        Image(source='/Users/mac/Documents/GitHub/Pomodoro_app/background_GIFS/abstract_red.gif', anim_delay=.05))


class TaskLayout(BoxLayout):
    background_image = ObjectProperty(
        Image(source='/Users/mac/Documents/GitHub/Pomodoro_app/background_GIFS/typing_red.gif', anim_delay=.02))


class TaskStartLayout(BoxLayout):
    background_image = ObjectProperty(
        Image(source='/Users/mac/Documents/GitHub/Pomodoro_app/background_GIFS/celebration_red.gif', anim_delay=.05))


class TaskEndLayout(BoxLayout):
    background_image = ObjectProperty(
        Image(source='/Users/mac/Documents/GitHub/Pomodoro_app/background_GIFS/cloud_red.gif', anim_delay=.05))


class FourTasksEndLayout(BoxLayout):
    background_image = ObjectProperty(
        Image(source='/Users/mac/Documents/GitHub/Pomodoro_app/background_GIFS/cloud_red.gif', anim_delay=.05))


class AppEndLayout(BoxLayout):
    background_image = ObjectProperty(
        Image(source='/Users/mac/Documents/GitHub/Pomodoro_app/background_GIFS/abstract_red.gif', anim_delay=.07))


class PomodoroTitle(Screen):

    def update_val(self):
        global num_blocks_left
        global list_tasks
        num_blocks_left = int(self.ids['bl2'].text)
        list_tasks = self.ids['text1'].text.split(sep='\n')
    pass


class PomodoroTask(Screen):
    global task_time
    full_time = task_time
    min_elapsed, sec_elapsed = divmod(full_time, 60)
    init = StringProperty(f"{min_elapsed:02d}:{sec_elapsed:02d} remaining")

    def time_elapsed(self, dt):
        print(self.full_time)
        global num_blocks_done
        global num_blocks_left
        global task_time
        lab_text = self.ids['time_lab']
        self.full_time = self.full_time - 1
        min_elapsed, sec_elapsed = divmod(self.full_time, 60)
        formatted_text = f"{min_elapsed:02d}:{sec_elapsed:02d} remaining"
        lab_text.text = formatted_text
        if self.full_time == 0:
            num_blocks_left -= 1
            num_blocks_done += 1
            self.manager.current = 'taskstart'
            self.full_time = task_time
            min_elapsed, sec_elapsed = divmod(self.full_time, 60)
            lab_text.text = (f"{min_elapsed:02d}:{sec_elapsed:02d} remaining")
            return False

    def task(self):
        event = Clock.create_trigger(
            self.time_elapsed, timeout=1, interval=True)
        event()


class PomodoroTaskStart(Screen):
    check_ref = {}

    def next_label(self):
        global list_tasks
        global list_completed
        global check_ref_box
        global whole_box

        lay = BoxLayout(orientation='vertical', size=self.size, size_hint=(1, .4), pos_hint={
                        'center_x': .4, 'center_y': .5})
        lay.clear_widgets()
        for i, task in enumerate(list_tasks):
            layout = BoxLayout(orientation="horizontal", size_hint=(.5, 1), pos_hint={
                               'center_x': .5, 'center_y': .5})
            check_ref_box.append(layout)
            check = CheckBox()
            self.check_ref[f'checkbox_{i}'] = [check, task]
            check.bind(
                active=lambda checkid, checkval: on_checkbox_active(self.check_ref))
            layout.add_widget(check)
            layout.add_widget(
                Label(text=task, color=(1, 1, 1, 1)))
            lay.add_widget(layout)
        self.add_widget(lay)
        event_3 = Clock.create_trigger(
            self.speaker_end, timeout=1, interval=False)
        event_3()
        whole_box = lay

    def speaker_end(self, dt):
        formatted_text = "Good job! Did you complete a task?"
        speaker.say(formatted_text)

    def clear_widgets(self):
        global whole_box
        self.remove_widget(whole_box)

    def break_type(self):
        global num_blocks_done
        global num_blocks_left
        global check_ref_box
        check_ref_box.clear()
        if num_blocks_done % 4 != 0:
            self.manager.current = 'taskend'
        else:
            self.manager.current = '4tasksend'


class Pomodoro4TasksEnd(Screen):
    global big_breaktime
    brk_time = big_breaktime
    min_elapsed, sec_elapsed = divmod(big_breaktime, 60)
    init_break_time = StringProperty(
        f"{min_elapsed:02d}:{sec_elapsed:02d} remaining")

    def break_time(self):
        self.speaker_4_end()
        event = Clock.create_trigger(
            self.time_elapsed, timeout=1, interval=True)
        event()

    def time_elapsed(self, dt):
        global num_blocks_done
        global num_blocks_left
        global big_breaktime

        lab_text = self.ids['big_break_timer_label']
        self.brk_time = self.brk_time - 1
        min_elapsed, sec_elapsed = divmod(self.brk_time, 60)
        formatted_text = f"{min_elapsed:02d}:{sec_elapsed:02d} remaining"
        lab_text.text = formatted_text
        if self.brk_time == 0:
            if num_blocks_left > 0:
                self.manager.current = 'taskmain'
            else:
                self.manager.current = 'append'
            self.brk_time = big_breaktime
            min_elapsed, sec_elapsed = divmod(self.brk_time, 60)
            formatted_text = f"{min_elapsed:02d}:{sec_elapsed:02d} remaining"
            lab_text.text = formatted_text
            return False
        elif num_blocks_done % 4 == 0:
            self.manager.current = '4tasksend'

    def speaker_4_end(self):
        formatted_text = "Good job getting a big pomodoro! You've earned a long break to rest and re-energize!"
        speaker.say(formatted_text)


class PomodoroTaskEnd(Screen):
    global breaktime
    brk_time = breaktime
    min_elapsed, sec_elapsed = divmod(breaktime, 60)
    init_break_time = StringProperty(
        f"{min_elapsed:02d}:{sec_elapsed:02d} remaining")

    def break_time(self):
        self.speaker_end()
        event = Clock.create_trigger(
            self.time_elapsed, timeout=1, interval=True)
        event()

    def time_elapsed(self, dt):
        global num_blocks_done
        global num_blocks_left
        global breaktime

        lab_text = self.ids['break_timer_label']
        self.brk_time = self.brk_time - 1
        min_elapsed, sec_elapsed = divmod(self.brk_time, 60)
        formatted_text = f"{min_elapsed:02d}:{sec_elapsed:02d} remaining"
        lab_text.text = formatted_text
        if self.brk_time == 0:
            if num_blocks_left > 0:
                self.manager.current = 'taskmain'
            else:
                self.manager.current = 'append'
            self.brk_time = breaktime
            min_elapsed, sec_elapsed = divmod(self.brk_time, 60)
            formatted_text = f"{min_elapsed:02d}:{sec_elapsed:02d} remaining"
            lab_text.text = formatted_text

            return False

    def speaker_end(self):
        formatted_text = "Good job getting a pomodoro! You've earned a few minutes to spend however you like!"
        speaker.say(formatted_text)


class PomodoroAppEnd(Screen):
    pass


class PomodoroApp(App):
    def build(self):
        self.title = u"\U0001F345"+'Pomodoro App'
        sm = ScreenManager()
        sm.add_widget(PomodoroTitle(name='titlemain'))
        sm.add_widget(PomodoroTask(name='taskmain'))
        sm.add_widget(PomodoroTaskStart(name='taskstart'))
        sm.add_widget(PomodoroTaskEnd(name='taskend'))
        sm.add_widget(Pomodoro4TasksEnd(name='4tasksend'))
        sm.add_widget(PomodoroAppEnd(name='append'))
        return sm


if __name__ == '__main__':
    PomodoroApp().run()
