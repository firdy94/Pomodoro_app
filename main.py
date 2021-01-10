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
task_time, breaktime, big_breaktime = 3, 4, 5
check_ref_box, whole_box = [], None


def on_checkbox_active(dic):
    global list_tasks
    global list_completed
    for idx, wgt in dic.items():
        check_obj = wgt[0]
        task_name = wgt[1]
        if check_obj.active:
            list_completed.append(task_name)
            list_tasks.remove(task_name)
            print(f"{wgt[1]} has been completed")
    return None


class TitleLayout(GridLayout):
    background_image = ObjectProperty(
        Image(source='/Users/mac/Documents/GitHub/Pomodoro_app/background_GIFS/swirl_square.gif', anim_delay=.07))


class TaskLayout(BoxLayout):
    background_image = ObjectProperty(
        Image(source='/Users/mac/Documents/GitHub/Pomodoro_app/background_GIFS/swirl_square.gif', anim_delay=.07))


class TaskStartLayout(BoxLayout):
    background_image = ObjectProperty(
        Image(source='/Users/mac/Documents/GitHub/Pomodoro_app/background_GIFS/tomato1.gif', anim_delay=.07))


class TaskEndLayout(BoxLayout):
    background_image = ObjectProperty(
        Image(source='/Users/mac/Documents/GitHub/Pomodoro_app/background_GIFS/break_square.gif', anim_delay=.07))


class FourTasksEndLayout(BoxLayout):
    background_image = ObjectProperty(
        Image(source='/Users/mac/Documents/GitHub/Pomodoro_app/background_GIFS/break_square.gif', anim_delay=.07))


class AppEndLayout(BoxLayout):
    background_image = ObjectProperty(
        Image(source='/Users/mac/Documents/GitHub/Pomodoro_app/background_GIFS/tomato-slice.gif', anim_delay=.07))


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
    init = StringProperty(f"{min_elapsed:02d}:{sec_elapsed:02d} remaining.")

    def time_elapsed(self, dt):
        print(self.full_time)
        global num_blocks_done
        global num_blocks_left
        global task_time
        lab_text = self.ids['time_lab']
        pb_text = self.ids['pb']
        self.full_time = self.full_time - 1
        min_elapsed, sec_elapsed = divmod(self.full_time, 60)
        formatted_text = f"{min_elapsed:02d}:{sec_elapsed:02d} remaining."
        lab_text.text = formatted_text
        pb_text.value = self.full_time
        pb_text.canvas.clear()
        with pb_text.canvas:
            # Draw no-progress circle
            Color(0.46, 0.46, 0.46, .7)
            Ellipse(pos=pb_text.pos, size=pb_text.size)
            # Draw progress circle, small hack if there is no progress (angle_end = 0 results in full progress)
            Color(1, 0, 0, .5)
            Ellipse(pos=pb_text.pos, size=pb_text.size,
                    angle_end=(0.001 if pb_text.value_normalized == 0 else pb_text.value_normalized*360))
            # Draw the inner circle (colour should be equal to the background)
            Color(0, 0, 0, .8)
            Ellipse(pos=(pb_text.pos[0] + pb_text.thickness / 2, pb_text.pos[1] + pb_text.thickness / 2),
                    size=(pb_text.size[0] - pb_text.thickness, pb_text.size[1] - pb_text.thickness))

        if self.full_time == 0:
            num_blocks_left -= 1
            num_blocks_done += 1
            self.manager.current = 'taskstart'
            self.full_time = task_time
            min_elapsed, sec_elapsed = divmod(self.full_time, 60)
            lab_text.text = (f"{min_elapsed:02d}:{sec_elapsed:02d} remaining.")
            pb_text.value = self.full_time
            pb_text.max = self.full_time

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

        lay = BoxLayout(orientation='vertical', size=self.size, size_hint=(1, .2), pos_hint={
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
                Label(text=task, color=(0, 0, 0, 1)))
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
        f"{min_elapsed:02d}:{sec_elapsed:02d} remaining.")

    def break_time(self):
        self.speaker_4_end()
        event = Clock.create_trigger(
            self.time_elapsed, timeout=1, interval=True)
        event()

    def time_elapsed(self, dt):
        global num_blocks_done
        global num_blocks_left

        lab_text = self.ids['big_break_timer_label']
        self.brk_time = self.brk_time - 1
        min_elapsed, sec_elapsed = divmod(self.brk_time, 60)
        formatted_text = f"{min_elapsed:02d}:{sec_elapsed:02d} remaining."
        lab_text.text = formatted_text
        if self.brk_time == 0:

            if num_blocks_left > 0:
                self.manager.current = 'taskmain'
            else:
                self.manager.current = 'append'

            self.brk_time = big_breaktime

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
        f"{min_elapsed:02d}:{sec_elapsed:02d} remaining.")

    def break_time(self):
        self.speaker_end()
        event = Clock.create_trigger(
            self.time_elapsed, timeout=1, interval=True)
        event()

    def time_elapsed(self, dt):
        global num_blocks_done
        global num_blocks_left

        lab_text = self.ids['break_timer_label']
        self.brk_time = self.brk_time - 1
        min_elapsed, sec_elapsed = divmod(self.brk_time, 60)
        formatted_text = f"{min_elapsed:02d}:{sec_elapsed:02d} remaining."
        lab_text.text = formatted_text
        if self.brk_time == 0:
            if num_blocks_left > 0:
                self.manager.current = 'taskmain'
            else:
                self.manager.current = 'append'
            self.brk_time = breaktime
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


# num_completed = 0
# task_completed = 0
# for num in range(num_cycles):
#     task_status = pomodoro_task()
#     num_completed += 1
#     if task_status == 'y':
#         task_completed += 1
#     if (num_completed % 4) == 0:
#         pomodoro_big_break()
#     else:
#         pomodoro_mini_break()
# print(
#     f"Well done completing {num_completed} blocks of work! How you were very productive and lets do this more often!")

# tomato = u"\U0001F345"
