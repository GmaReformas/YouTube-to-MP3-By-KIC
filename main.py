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
SUB = [0.63, 0.63, 0.63, 1]
BLU = [0.31, 0.76, 0.97, 1]
GRN = [0.4, 0.73, 0.42, 1]
RED = [0.94, 0.33, 0.31, 1]
YLW = [0.99, 0.85, 0.21, 1]


class YtMp3App(App):
    def build(self):
        self.queue = []
        self.downloading = False

        r = BoxLayout(orientation='vertical', padding=10, spacing=6)

        r.add_widget(Label(text='YT to MP3 By KIC',
                           font_size='22sp', color=RED,
                           size_hint_y=None, height=50))
        r.add_widget(Label(text='Paste links and download MP3',
                           font_size='12sp', color=SUB,
                           size_hint_y=None, height=24))

        self.inp = TextInput(hint_text='Paste YouTube links here...',
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
        b2 = Button(text='Download all', background_color=GRN,
                    color=[0, 0, 0, 1], font_size='13sp')
        b2.bind(on_press=self._go)
        br.add_widget(b2)
        r.add_widget(br)

        self.cnt = Label(text='Queue: 0', font_size='11sp',
                         color=SUB, size_hint_y=None, height=24)
        r.add_widget(self.cnt)

        self.stat = Label(text='Ready', font_size='13sp',
                          color=SUB, size_hint_y=None, height=30)
        r.add_widget(self.stat)

        r.add_widget(Label(text='PARA LUCIAN (SERPU)',
                           font_size='13sp', bold=True,
                           color=[0, 0.83, 1, 1],
                           size_hint_y=None, height=30))

        return r

    def _add(self, *a):
        t = self.inp.text.strip()
        if not t:
            return
        urls = [l.strip() for l in t.split('\n')
                if re.search(r'(youtube\.com|youtu\.be)', l.strip())]
        if not urls:
            self.stat.text = 'No valid YouTube links'
            self.stat.color = RED
            return
        for u in urls:
            self.queue.append({'url': u, 'st': 'pending'})
        self.inp.text = ''
        self._upd()
        self.stat.text = 'Added %d link(s)' % len(urls)
        self.stat.color = TXT

    def _upd(self):
        n = len(self.queue)
        p = sum(1 for q in self.queue if q['st'] == 'pending')
        self.cnt.text = 'Queue: %d | Pending: %d' % (n, p)

    def _go(self, *a):
        if self.downloading or not any(
                q['st'] == 'pending' for q in self.queue):
            return
        self.downloading = True
        self.stat.text = 'Downloading...'
        self.stat.color = YLW
        threading.Thread(target=self._dl, daemon=True).start()

    def _dl(self):
        try:
            import yt_dlp
        except Exception:
            Clock.schedule_once(
                lambda dt: self._end(0, len(self.queue)), 0)
            return

        pending = [q for q in self.queue if q['st'] == 'pending']
        total = len(pending)
        ok = err = 0
        dl_dir = os.path.join(os.path.expanduser('~'), 'Downloads')

        for i, item in enumerate(pending):
            item['st'] = 'doing'
            Clock.schedule_once(lambda dt: self._sts('Downloading...'), 0)

            opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(dl_dir, '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '0'}],
                'quiet': True,
                'no_warnings': True,
            }

            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    ydl.download([item['url']])
                item['st'] = 'ok'
                ok += 1
            except Exception:
                item['st'] = 'error'
                err += 1

            pct = (i + 1) / total * 100
            Clock.schedule_once(
                lambda dt, v=pct: setattr(self.stat, 'text',
                                          'Progress: %d%%' % int(v)), 0)

        Clock.schedule_once(lambda dt: self._end(ok, err), 0)

    def _sts(self, t):
        self.stat.text = t
        self.stat.color = YLW

    def _end(self, ok, err):
        self.downloading = False
        self.stat.text = 'Done: %d OK, %d errors' % (ok, err)
        self.stat.color = GRN
        self._upd()


if __name__ == '__main__':
    YtMp3App().run()
