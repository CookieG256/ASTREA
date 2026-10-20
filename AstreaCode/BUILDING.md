# Building ASTREA

Install Python 3.11 and run `python -m pip install -r requirements-build.txt`,
then run `python build_game.py` on the target operating system.

The script produces a versioned macOS `.app` archive, a Windows `.exe`, or a
Linux executable archive. Native builds are required: PyInstaller does not
cross-compile between operating systems. If an `assets/` directory exists, its
contents are bundled automatically.

## Android APK

The unified game code detects Android through `plataforma.IS_MOBILE`. Virtual
touch controls are drawn and handled only while playing on Android; desktop
input and the desktop builds are unchanged.

The Android build uses Buildozer and python-for-android's SDL2 `pygame` recipe.
That recipe builds classic `pygame` (currently 2.1.0), not `pygame-ce`. The game
uses the shared `pygame` API, but the Android package is not a pygame-ce build.
The desktop dependency remains the one declared in `requirements.txt`. If the
game starts depending on pygame-ce-only APIs, those features must be replaced or
an Android recipe for pygame-ce must be validated before publishing.

For a local Android build, use Linux (or a Linux VM/WSL environment) with Java
17, the Android SDK/NDK, and Buildozer installed. From the project directory:

```bash
python -m pip install "buildozer==1.5.0" "Cython==0.29.36"
buildozer android debug
```

The generated APK is written to `bin/`. The first build downloads Android
toolchains and can take a while. The GitHub Actions workflow runs this Linux
build automatically and uploads the APK as the `ASTREA-Android` artifact.

The workflow builds Windows, macOS, Linux, and Android when manually started
or when a `v*` tag is pushed. Pushing a version tag (for example, `v1.2.0`) builds
all platforms and publishes the installers and APK as downloadable assets on a
GitHub Release. Manual workflow runs provide the packages under the run's
**Artifacts** section.

To publish a release, push the project to a GitHub repository with Actions
enabled, then create and push the version tag:

```bash
git tag v1.2.0
git push origin v1.2.0
```
