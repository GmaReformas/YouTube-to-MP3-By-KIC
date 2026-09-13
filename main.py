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

if platform != 'android':
    Window.size = (400, 700)

def get_lang():
    try:
        if platform == 'android':
            from jnius import autoclass
            lang = autoclass('java.util.Locale').getDefault().getLanguage()
            if lang.startswith('es'): return 'es'
            if lang.startswith('ro'): return 'ro'
        else:
            loc = locale.getdefaultlocale()[0]
            if loc and loc.startswith('es'): return 'es'
            if loc and loc.startswith('ro'): return 'ro'
    except:
        pass
    return 'en'

T = {
    "es": {
        "title": "YouTube to MP3 By KIC (Cornel)",
        "subtitle": "Pega enlaces y descarga en MP3",
        "placeholder": "Pega aqui los enlaces de YouTube...",
        "add": "+ Agregar",
        "clear": "Limpiar",
        "download": "Descargar todo",
        "status_ready": "Listo para descargar",
        "count": "Cola: {n} | Pendientes: {p}",
        "adding": "Agregando...",
        "downloading": "Descargando...",
        "converting": "Convirtiendo...",
        "completed": "Completado: {ok} OK, {err} errores",
        "error": "Error",
        "folder": "Descargas: {path}",
        "dedication": "PARA LUCIAN (SERPU) MI HERMANO",
    },
    "ro": {
        "title": "YouTube to MP3 By KIC (Cornel)",
        "subtitle": "Lipeste linkurile si descarca in MP3",
        "placeholder": "Lipeste linkurile YouTube aici...",
        "add": "+ Adauga",
        "clear": "Goleste",
        "download": "Descarca tot",
        "status_ready": "Gata de descarcare",
        "count": "Coada: {n} | In asteptare: {p}",
        "adding": "Se adauga...",
        "downloading": "Se descarca...",
        "converting": "Se converteste...",
        "completed": "Completat: {ok} OK, {err} erori",
        "error": "Eroare",
        "folder": "Descarcari: {path}",
        "dedication": "PARA LUCIAN (SERPU) FRATELE MEU",
    },
    "en": {
        "title": "YouTube to MP3 By KIC (Cornel)",
        "subtitle": "Paste links and download as MP3",
        "placeholder": "Paste YouTube links here...",
        "add": "+ Add",
        "clear": "Clear",
        "download": "Download all",
        "status_ready": "Ready to download",
        "count": "Queue: {n} | Pending: {p}",
        "adding": "Adding...",
        "downloading": "Downloading...",
        "converting": "Converting...",
        "completed": "Completed: {ok} OK, {err} errors",
        "error": "Error",
        "folder": "Downloads: {path}",
        "dedication": "PARA LUCIAN (SERPU) MY HERMANO",
    },
}

BG = '#0f0f0f'
CARD = '#16213e'
SURF = '#1a1a2e'
BORDER = '#2a2a4a'
TXT = '#e6e6e6'
SUB = '#a0a0a0'
RED = '#ef5350'
GREEN = '#66bb6a'
BLUE = '#4fc3f7'
YELLOW = '#fdd835'
NEON = '#00d4ff'


class YtMp3App(App):
    def build(self):
        self.lang = get_lang()
        self.t = T[self.lang]
        self.title = self.t["title"]
        self.downloading = False
        self.queue = []

        if platform == 'android':
            self.download_dir = '/storage/emulated/0/Download/MP3'
        else:
            self.download_dir = str(os.path.expanduser('~/Downloads/MP3'))
        os.makedirs(self.download_dir, exist_ok=True)

        root = BoxLayout(orientation='vertical', padding=12, spacing=8)

        title_lbl = Label(
            text=self.t["title"],
            font_size='20sp',
            bold=True,
            color=hex_to_rgba(RED),
            size_hint_y=None,
            height=40,
        )
        root.add_widget(title_lbl)

        sub_lbl = Label(
            text=self.t["subtitle"],
            font_size='12sp',
            color=hex_to_rgba(SUB),
            size_hint_y=None,
            height=24,
        )
        root.add_widget(sub_lbl)

        self.url_input = TextInput(
            hint_text=self.t["placeholder"],
            multiline=True,
            size_hint_y=None,
            height=100,
            background_color=hex_to_rgba(SURF),
            foreground_color=hex_to_rgba(TXT),
            hint_foreground_color=hex_to_rgba(SUB),
            cursor_color=hex_to_rgba(BLUE),
            font_size='13sp',
            padding=[8, 8],
        )
        root.add_widget(self.url_input)

        btn_row = BoxLayout(spacing=8, size_hint_y=None, height=44)
        self.add_btn = Button(
            text=self.t["add"],
            background_color=hex_to_rgba(BLUE),
            color=(0, 0, 0, 1),
            bold=True,
            font_size='13sp',
        )
        self.add_btn.bind(on_press=self.add_urls)
        btn_row.add_widget(self.add_btn)

        self.clear_btn = Button(
            text=self.t["clear"],
            background_color=hex_to_rgba(RED),
            color=(0, 0, 0, 1),
            bold=True,
            font_size='13sp',
        )
        self.clear_btn.bind(on_press=self.clear_queue)
        btn_row.add_widget(self.clear_btn)
        root.add_widget(btn_row)

        scroll = ScrollView()
        self.queue_box = BoxLayout(orientation='vertical', spacing=4, size_hint_y=None)
        self.queue_box.bind(minimum_height=self.queue_box.setter('height'))
        scroll.add_widget(self.queue_box)
        root.add_widget(scroll)

        self.count_lbl = Label(
            text=self.t["count"].format(n=0, p=0),
            font_size='11sp',
            color=hex_to_rgba(SUB),
            size_hint_y=None,
            height=22,
        )
        root.add_widget(self.count_lbl)

        self.progress = ProgressBar(
            max=100,
            value=0,
            size_hint_y=None,
            height=16,
        )
        root.add_widget(self.progress)

        self.status_lbl = Label(
            text=self.t["status_ready"],
            font_size='12sp',
            color=hex_to_rgba(SUB),
            size_hint_y=None,
            height=24,
        )
        root.add_widget(self.status_lbl)

        dl_row = BoxLayout(spacing=8, size_hint_y=None, height=44)
        self.dl_btn = Button(
            text=self.t["download"],
            background_color=hex_to_rgba(GREEN),
            color=(0, 0, 0, 1),
            bold=True,
            font_size='13sp',
        )
        self.dl_btn.bind(on_press=self.start_download)
        dl_row.add_widget(self.dl_btn)
        root.add_widget(dl_row)

        dedi_lbl = Label(
            text=self.t["dedication"],
            font_size='13sp',
            bold=True,
            color=hex_to_rgba(NEON),
            size_hint_y=None,
            height=28,
        )
        root.add_widget(dedi_lbl)

        return root

    def add_urls(self, *args):
        text = self.url_input.text.strip()
        if not text:
            return
        urls = [l.strip() for l in text.split('\n') if re.search(r'(youtube\.com|youtu\.be)', l.strip())]
        if not urls:
            self.status_lbl.text = "No valid links"
            self.status_lbl.color = hex_to_rgba(RED)
            return

        for url in urls:
            self.queue.append({'url': url, 'status': 'pending', 'title': ''})
            lbl = Label(
                text=url[:60] + '...' if len(url) > 60 else url,
                font_size='11sp',
                color=hex_to_rgba(TXT),
                size_hint_y=None,
                height=30,
                text_size=(None, None),
            )
            self.queue_box.add_widget(lbl)

        self.url_input.text = ''
        self.status_lbl.text = self.t["adding"]
        self.status_lbl.color = hex_to_rgba(GREEN)
        self._update_count()

    def clear_queue(self, *args):
        if self.downloading:
            return
        self.queue.clear()
        self.queue_box.clear_widgets()
        self._update_count()

    def _update_count(self):
        n = len(self.queue)
        p = sum(1 for q in self.queue if q['status'] == 'pending')
        self.count_lbl.text = self.t["count"].format(n=n, p=p)

    def start_download(self, *args):
        pending = [q for q in self.queue if q['status'] == 'pending']
        if not pending:
            self.status_lbl.text = self.t["status_ready"]
            self.status_lbl.color = hex_to_rgba(SUB)
            return

        self.downloading = True
        self.dl_btn.disabled = True
        self.add_btn.disabled = True
        self.clear_btn.disabled = True
        self.progress.value = 0

        threading.Thread(target=self._download_all, daemon=True).start()

    def _download_all(self):
        import yt_dlp

        pending = [q for q in self.queue if q['status'] == 'pending']
        total = len(pending)
        ok = 0
        err = 0

        for i, item in enumerate(pending):
            item['status'] = 'downloading'
            Clock.schedule_once(lambda dt, t=i: self._set_status(
                self.t["downloading"].format(n=t+1, total=total)), 0)

            def hook(d, idx=i):
                if d['status'] == 'downloading':
                    pct = float(re.search(r'([\d.]+)', d.get('_percent_str', '0')).group(1))
                    overall = (idx * 100 + pct) / total
                    Clock.schedule_once(lambda dt, v=overall: self._set_progress(v), 0)
                elif d['status'] == 'finished':
                    Clock.schedule_once(lambda dt: self._set_status(self.t["converting"]), 0)

            opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(self.download_dir, '%(title)s.%(ext)s'),
                'progress_hooks': [hook],
                'postprocessors': [
                    {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '0'},
                ],
                'quiet': True,
                'no_warnings': True,
            }

            if platform == 'android':
                opts['ffmpeg_location'] = '/data/data/org.kivy.python/files'

            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(item['url'], download=False)
                    item['title'] = info.get('title', 'Unknown')
                    ydl.download([item['url']])
                item['status'] = 'ok'
                ok += 1
            except Exception as e:
                item['status'] = 'error'
                err += 1

            Clock.schedule_once(lambda dt, v=(i+1)/total*100: self._set_progress(v), 0)

        Clock.schedule_once(lambda dt: self._finish(ok, err), 0)

    def _set_progress(self, val):
        self.progress.value = val

    def _set_status(self, text):
        self.status_lbl.text = text
        self.status_lbl.color = hex_to_rgba(YELLOW)

    def _finish(self, ok, err):
        self.downloading = False
        self.dl_btn.disabled = False
        self.add_btn.disabled = False
        self.clear_btn.disabled = False
        self.progress.value = 100
        self.status_lbl.text = self.t["completed"].format(ok=ok, err=err)
        self.status_lbl.color = hex_to_rgba(GREEN)
        self._update_count()


def hex_to_rgba(hex_color):
    h = hex_color.lstrip('#')
    r, g, b = int(h[0:2], 16)/255, int(h[2:4], 16)/255, int(h[4:6], 16)/255
    return (r, g, b, 1)


if __name__ == '__main__':
    YtMp3App().run()
