[app]

title = ASTREA
package.name = astrea
package.domain = org.astrea
source.dir = .
source.include_exts = py,png,jpg,jpeg,bmp,gif,ogg,wav,mp3,ttf,otf,json,txt
source.exclude_dirs = .git,.venv,.buildozer,__pycache__,build,dist,bin,tests
source.exclude_patterns = save_roguelike.json,saves/*
version = 1.2.0
requirements = python3,pygame
orientation = landscape
fullscreen = 1

android.api = 33
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True
android.allow_backup = False

p4a.branch = v2023.09.16
p4a.commit = e155baf9f94ef6ef0589541210e9cdb20f960d52
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1
