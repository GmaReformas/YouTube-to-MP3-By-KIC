[app]

title = YouTube to MP3 By KIC
package.name = youtubetomp3
package.domain = com.kic
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy,yt-dlp
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE
android.allow_backup = True
android.api = 33
android.minapi = 24
android.ndk = 25b
android.sdk = 33
android.accept_sdk_license = True
android.arch = arm64-v8a
android.release_artifact = aab
presplash.filename = %(source.dir)s/logo.png
icon.filename = %(source.dir)s/logo.png
log_level = 2
warn_on_root = 0
