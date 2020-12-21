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

from macos_speech import Synthesizer

speaker = Synthesizer(voice='Alex', device='Built-in')

num_blocks, list_tasks, list_completed = (0, '', [])


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


class PomodoroTitle(Screen):

    def update_val(self):
        global num_blocks
        global list_tasks
        num_blocks = self.ids['bl2'].text
        list_tasks = self.ids['text1'].text
    pass


class PomodoroTask(Screen):
    full_time = 3
    min_elapsed, sec_elapsed = divmod(full_time, 60)
    init = StringProperty(f"{min_elapsed:02d}:{sec_elapsed:02d} remaining.")

    def time_elapsed(self, dt):
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
            self.manager.current = 'taskstart'
            return False

    def task(self):
        event = Clock.create_trigger(
            self.time_elapsed, timeout=1, interval=True)
        event()


class PomodoroTaskStart(Screen):
    def next_label(self):
        # global list_tasks
        # global list_completed

        # list_tasks=list_tasks.split()

        # for task in list_tasks:
        #     self.add_widget(C)

        event_3 = Clock.create_trigger(
            self.speaker_end, timeout=1, interval=False)
        event_3()

    def speaker_end(self, dt):
        formatted_text = "Good job! Did you complete a task?"
        speaker.say(formatted_text)


class PomodoroTaskEnd(Screen):
    brk_time = 30
    min_elapsed, sec_elapsed = divmod(brk_time, 60)
    init_break_time = StringProperty(
        f"{min_elapsed:02d}:{sec_elapsed:02d} remaining.")

    def break_time(self):
        global num_blocks
        event = Clock.create_trigger(
            self.time_elapsed, timeout=1, interval=True)
        event()

    def time_elapsed(self, dt):
        lab_text = self.ids['break_timer_label']
        self.brk_time = self.brk_time - 1
        min_elapsed, sec_elapsed = divmod(self.brk_time, 60)
        formatted_text = f"{min_elapsed:02d}:{sec_elapsed:02d} remaining."
        lab_text.text = formatted_text
        if self.brk_time == 0:
            formatted_text = "Good job getting a pomodoro! You've earned a few minutes to spend however you like!"
            speaker.say(formatted_text)
            return False


class PomodoroApp(App):
    def build(self):
        self.title = u"\U0001F345"+'Pomodoro App'
        sm = ScreenManager()
        sm.add_widget(PomodoroTitle(name='titlemain'))
        sm.add_widget(PomodoroTask(name='taskmain'))
        sm.add_widget(PomodoroTaskStart(name='taskstart'))
        sm.add_widget(PomodoroTaskEnd(name='taskend'))
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
