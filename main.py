import os, re, locale, threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import platform

IS_ANDROID = (platform == 'android')

if not IS_ANDROID:
    Window.size = (400, 700)


def get_lang():
    try:
        if IS_ANDROID:
            from jnius import autoclass
            loc = autoclass('java.util.Locale').getDefault().getLanguage()
            if loc.startswith('es'):
                return 'es'
            if loc.startswith('ro'):
                return 'ro'
        else:
            loc = locale.getdefaultlocale()
            if loc and loc[0]:
                if loc[0].startswith('es'):
                    return 'es'
                if loc[0].startswith('ro'):
                    return 'ro'
    except Exception:
        pass
    return 'en'


T = {
    "es": {
        "title": "YouTube to MP3 By KIC",
        "sub": "Pega enlaces y descarga en MP3",
        "ph": "Pega aqui los enlaces de YouTube...",
        "add": "+ Agregar",
        "clear": "Limpiar",
        "dl": "Descargar todo",
        "ready": "Listo",
        "cnt": "Cola: {n} | Pendientes: {p}",
        "doing": "Descargando...",
        "conv": "Convirtiendo...",
        "done": "Completado: {ok} OK, {err} errores",
        "dedi": "PARA LUCIAN (SERPU) MI HERMANO",
    },
    "ro": {
        "title": "YouTube to MP3 By KIC",
        "sub": "Lipeste linkurile si descarca in MP3",
        "ph": "Lipeste linkurile YouTube aici...",
        "add": "+ Adauga",
        "clear": "Goleste",
        "dl": "Descarca tot",
        "ready": "Gata",
        "cnt": "Coada: {n} | In asteptare: {p}",
        "doing": "Se descarca...",
        "conv": "Se converteste...",
        "done": "Completat: {ok} OK, {err} erori",
        "dedi": "PARA LUCIAN (SERPU) FRATELE MEU",
    },
    "en": {
        "title": "YouTube to MP3 By KIC",
        "sub": "Paste links and download as MP3",
        "ph": "Paste YouTube links here...",
        "add": "+ Add",
        "clear": "Clear",
        "dl": "Download all",
        "ready": "Ready",
        "cnt": "Queue: {n} | Pending: {p}",
        "doing": "Downloading...",
        "conv": "Converting...",
        "done": "Completed: {ok} OK, {err} errors",
        "dedi": "PARA LUCIAN (SERPU) MY HERMANO",
    },
}

TXT = '#e6e6e6'
SUB = '#a0a0a0'
RED = '#ef5350'
GRN = '#66bb6a'
BLU = '#4fc3f7'
YLW = '#fdd835'
NEO = '#00d4ff'
SURF = '#1a1a2e'


def rgba(h):
    h = h.lstrip('#')
    return (int(h[0:2], 16) / 255.0,
            int(h[2:4], 16) / 255.0,
            int(h[4:6], 16) / 255.0, 1)


class YtMp3App(App):
    def build(self):
        self.t = T[get_lang()]
        self.title = self.t["title"]
        self.downloading = False
        self.queue = []
        self.dl_dir = self._dir()

        r = BoxLayout(orientation='vertical', padding=12, spacing=8)

        r.add_widget(Label(text=self.t["title"], font_size='20sp',
                           bold=True, color=rgba(RED),
                           size_hint_y=None, height=40))
        r.add_widget(Label(text=self.t["sub"], font_size='12sp',
                           color=rgba(SUB), size_hint_y=None, height=24))

        self.inp = TextInput(
            hint_text=self.t["ph"], multiline=True,
            size_hint_y=None, height=100,
            background_color=rgba(SURF), foreground_color=rgba(TXT),
            hint_foreground_color=rgba(SUB), cursor_color=rgba(BLU),
            font_size='13sp', padding=[8, 8])
        r.add_widget(self.inp)

        br = BoxLayout(spacing=8, size_hint_y=None, height=44)
        self.b_add = Button(text=self.t["add"], background_color=rgba(BLU),
                            color=(0, 0, 0, 1), bold=True, font_size='13sp')
        self.b_add.bind(on_press=self._add)
        br.add_widget(self.b_add)
        self.b_clr = Button(text=self.t["clear"], background_color=rgba(RED),
                            color=(0, 0, 0, 1), bold=True, font_size='13sp')
        self.b_clr.bind(on_press=self._clr)
        br.add_widget(self.b_clr)
        r.add_widget(br)

        sv = ScrollView()
        self.qbox = BoxLayout(orientation='vertical', spacing=4,
                              size_hint_y=None)
        self.qbox.bind(minimum_height=self.qbox.setter('height'))
        sv.add_widget(self.qbox)
        r.add_widget(sv)

        self.cnt = Label(text=self.t["cnt"].format(n=0, p=0),
                         font_size='11sp', color=rgba(SUB),
                         size_hint_y=None, height=22)
        r.add_widget(self.cnt)

        self.prog = ProgressBar(max=100, value=0,
                                size_hint_y=None, height=16)
        r.add_widget(self.prog)

        self.stat = Label(text=self.t["ready"], font_size='12sp',
                          color=rgba(SUB), size_hint_y=None, height=24)
        r.add_widget(self.stat)

        dr = BoxLayout(spacing=8, size_hint_y=None, height=44)
        self.b_dl = Button(text=self.t["dl"], background_color=rgba(GRN),
                           color=(0, 0, 0, 1), bold=True, font_size='13sp')
        self.b_dl.bind(on_press=self._go)
        dr.add_widget(self.b_dl)
        r.add_widget(dr)

        r.add_widget(Label(text=self.t["dedi"], font_size='13sp',
                           bold=True, color=rgba(NEO),
                           size_hint_y=None, height=28))
        return r

    def _dir(self):
        if not IS_ANDROID:
            d = os.path.expanduser('~/Downloads/MP3')
            try:
                os.makedirs(d, exist_ok=True)
            except Exception:
                d = os.path.expanduser('~/Downloads')
            return d

        for d in ['/storage/emulated/0/Download/MP3',
                  '/sdcard/Download/MP3']:
            try:
                os.makedirs(d, exist_ok=True)
                return d
            except Exception:
                continue

        try:
            from jnius import autoclass
            ctx = autoclass(
                'org.kivy.android.PythonActivity').mActivity
            d = os.path.join(str(ctx.getFilesDir()), 'MP3')
            os.makedirs(d, exist_ok=True)
            return d
        except Exception:
            pass

        return os.getcwd()

    def _add(self, *args):
        text = self.inp.text.strip()
        if not text:
            return
        urls = [l.strip() for l in text.split('\n')
                if re.search(r'(youtube\.com|youtu\.be)', l.strip())]
        if not urls:
            self.stat.text = "No valid links"
            self.stat.color = rgba(RED)
            return
        for u in urls:
            self.queue.append({'url': u, 'st': 'pending'})
            self.qbox.add_widget(Label(
                text=u[:60] + ('...' if len(u) > 60 else ''),
                font_size='11sp', color=rgba(TXT),
                size_hint_y=None, height=30))
        self.inp.text = ''
        self._upd()

    def _clr(self, *args):
        if self.downloading:
            return
        self.queue.clear()
        self.qbox.clear_widgets()
        self._upd()

    def _upd(self):
        n = len(self.queue)
        p = sum(1 for q in self.queue if q['st'] == 'pending')
        self.cnt.text = self.t["cnt"].format(n=n, p=p)

    def _go(self, *args):
        if self.downloading or not any(
                q['st'] == 'pending' for q in self.queue):
            return
        self.downloading = True
        self.b_dl.disabled = True
        self.b_add.disabled = True
        self.b_clr.disabled = True
        self.prog.value = 0
        threading.Thread(target=self._dl, daemon=True).start()

    def _dl(self):
        try:
            import yt_dlp
        except Exception:
            Clock.schedule_once(lambda dt: self._end(0, len(self.queue)), 0)
            return

        pending = [q for q in self.queue if q['st'] == 'pending']
        total = len(pending)
        ok = err = 0

        for i, item in enumerate(pending):
            item['st'] = 'doing'
            Clock.schedule_once(
                lambda dt: self._sts(self.t["doing"]), 0)

            def hook(d, idx=i):
                if d['status'] == 'downloading':
                    m = re.search(r'([\d.]+)',
                                  d.get('_percent_str', '0'))
                    pct = float(m.group(1)) if m else 0
                    Clock.schedule_once(
                        lambda dt, v=(idx * 100 + pct) / total:
                            self._prg(v), 0)
                elif d['status'] == 'finished':
                    Clock.schedule_once(
                        lambda dt: self._sts(self.t["conv"]), 0)

            opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(
                    self.dl_dir, '%(title)s.%(ext)s'),
                'progress_hooks': [hook],
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '0'}],
                'quiet': True,
                'no_warnings': True,
            }

            if IS_ANDROID:
                priv = os.environ.get('ANDROID_PRIVATE', '')
                for p in [priv,
                          '/data/data/com.kic.youtubetomp3/files']:
                    if p and os.path.exists(
                            os.path.join(p, 'ffmpeg')):
                        opts['ffmpeg_location'] = p
                        break

            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(
                        item['url'], download=False)
                    item['title'] = info.get('title', '?')
                    ydl.download([item['url']])
                item['st'] = 'ok'
                ok += 1
            except Exception:
                item['st'] = 'error'
                err += 1

            Clock.schedule_once(
                lambda dt, v=(i + 1) / total * 100: self._prg(v), 0)

        Clock.schedule_once(lambda dt: self._end(ok, err), 0)

    def _prg(self, v):
        self.prog.value = v

    def _sts(self, t):
        self.stat.text = t
        self.stat.color = rgba(YLW)

    def _end(self, ok, err):
        self.downloading = False
        self.b_dl.disabled = False
        self.b_add.disabled = False
        self.b_clr.disabled = False
        self.prog.value = 100
        self.stat.text = self.t["done"].format(ok=ok, err=err)
        self.stat.color = rgba(GRN)
        self._upd()


if __name__ == '__main__':
    YtMp3App().run()
