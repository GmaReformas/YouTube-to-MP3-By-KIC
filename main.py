import os
import re
import threading

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock

BG = [0.06, 0.06, 0.06, 1]
TXT = [0.9, 0.9, 0.9, 1]
BLU = [0.31, 0.76, 0.97, 1]
GRN = [0.4, 0.73, 0.42, 1]
RED = [0.94, 0.33, 0.31, 1]


class YtMp3App(App):
    def build(self):
        self.queue = []
        self.downloading = False

        r = BoxLayout(orientation='vertical', padding=10, spacing=6)

        r.add_widget(Label(text='YT to MP3 By KIC',
                           font_size='22sp', color=TXT,
                           size_hint_y=None, height=50))

        self.inp = TextInput(hint_text='Paste YouTube links...',
                             multiline=True, font_size='13sp',
                             size_hint_y=None, height=100,
                             foreground_color=TXT,
                             cursor_color=BLU,
                             background_color=[0.1, 0.1, 0.15, 1])
        r.add_widget(self.inp)

        br = BoxLayout(size_hint_y=None, height=50, spacing=8)
        b1 = Button(text='Add', background_color=BLU,
                    color=[0, 0, 0, 1], font_size='13sp')
        b1.bind(on_press=self._add)
        br.add_widget(b1)
        b2 = Button(text='Download', background_color=GRN,
                    color=[0, 0, 0, 1], font_size='13sp')
        b2.bind(on_press=self._go)
        br.add_widget(b2)
        r.add_widget(br)

        self.stat = Label(text='Ready', font_size='14sp',
                          color=TXT, size_hint_y=None, height=40)
        r.add_widget(self.stat)

        return r

    def _add(self, *a):
        t = self.inp.text.strip()
        if t:
            self.queue.append(t)
            self.stat.text = 'Added: ' + t[:50]
            self.inp.text = ''

    def _go(self, *a):
        if not self.queue:
            self.stat.text = 'No links'
            return
        self.stat.text = 'Downloading...'
        threading.Thread(target=self._dl, daemon=True).start()

    def _dl(self):
        url = self.queue.pop(0)
        try:
            import yt_dlp
            opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(
                    os.path.expanduser('~'), 'Downloads',
                    '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '0'}],
                'quiet': True,
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            Clock.schedule_once(
                lambda dt: self._ok(), 0)
        except Exception as e:
            Clock.schedule_once(
                lambda dt, err=str(e): self._fail(err), 0)

    def _ok(self):
        self.stat.text = 'Downloaded!'

    def _fail(self, e):
        self.stat.text = 'Error: ' + e[:60]


if __name__ == '__main__':
    YtMp3App().run()
