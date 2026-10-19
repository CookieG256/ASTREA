# Building ASTREA

Install Python 3.11 and run `python -m pip install -r requirements-build.txt`,
then run `python build_game.py` on the target operating system.

The script produces a versioned macOS `.app` archive, a Windows `.exe`, or a
Linux executable archive. Native builds are required: PyInstaller does not
cross-compile between operating systems. If an `assets/` directory exists, its
contents are bundled automatically.

The GitHub Actions workflow builds all three platforms when manually started or
when a `v*` tag is pushed. Pushing a version tag (for example, `v1.1.0`) builds
all platforms and publishes the installers as downloadable assets on a GitHub
Release. Manual workflow runs provide the platform packages under the run's
**Artifacts** section.

To publish a release, push the project to a GitHub repository with Actions
enabled, then create and push the version tag:

```bash
git tag v1.1.0
git push origin v1.1.0
```
