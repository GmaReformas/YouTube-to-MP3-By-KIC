[app]

title = YouTube to MP3 By KIC
package.name = youtubetomp3
package.domain = com.kic
source.dir = .
source.include_exts = py,png,jpg
version = 1.0
requirements = python3,kivy,yt-dlp
orientation = portrait
fullscreen = 1
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 24
android.ndk = 25b
android.sdk = 33
android.accept_sdk_license = True
android.archs = arm64-v8a
presplash.filename = %(source.dir)s/logo.png
icon.filename = %(source.dir)s/logo.png
log_level = 2
warn_on_root = 0
