# Testing Guide

This guide walks through complete testing for the `girlfriend` CLI project, from quick local checks to installation testing and Debian package verification.

## What You Are Testing

You want to verify that:

- the Python package imports correctly
- the CLI starts without crashing
- all core commands work
- config and streak files are created correctly
- interactive AI chat configuration works
- Gemini fallback uses the saved config key correctly
- complex prompts fall through to Gemini automatically
- AI failures are shown clearly
- optional Linux integrations behave properly
- the package installs with `pip`
- the package can be built and installed as a `.deb`

## Test Environment

Recommended environment:

- Linux machine or VM
- Python 3.9 or newer
- `pip`
- optional: `espeak`
- optional: `notify-send` from `libnotify-bin`
- optional for AI chat setup: Gemini API key from `https://aistudio.google.com/app/apikey`
- optional for Debian packaging: `debhelper`, `dh-python`, `python3-all`, `python3-setuptools`, `python3-rich`

Check your environment:

```bash
python3 --version
pip3 --version
uname -a
```

## Project Root

Run all commands from the project root:

```bash
cd /home/ben/Desktop/girlfriend-release/girlfriend
```

## 1. Quick Smoke Test

This confirms the app starts and the CLI parser works.

```bash
python3 -m girlfriend.cli --help
python3 -m girlfriend.cli --version
python3 -m girlfriend.cli --no-typing
python3 -m girlfriend.cli chat --help
```

Expected result:

- help text prints
- version prints
- the startup banner appears
- a romantic message appears
- no traceback is shown

## 2. Automated Unit Tests

Run the built-in test suite:

```bash
python3 -m unittest discover -s tests -v
```

Expected result:

- all tests should show `ok`
- final output should end with `OK`

If a test fails:

- read the traceback carefully
- confirm you are in the project root
- re-run the single failing test after fixing the issue

Example single test run:

```bash
python3 -m unittest tests.test_basic -v
```

## 3. Manual Feature Testing

### Default message

```bash
python3 -m girlfriend.cli --no-typing
```

Check:

- banner renders correctly
- colorful output appears
- one random message is shown
- streak line prints at the bottom

### Mood system

Test each mood:

```bash
python3 -m girlfriend.cli --mood caring --no-typing
python3 -m girlfriend.cli --mood jealous --no-typing
python3 -m girlfriend.cli --mood hacker --no-typing
python3 -m girlfriend.cli --mood clingy --no-typing
python3 -m girlfriend.cli --mood sleepy --no-typing
python3 -m girlfriend.cli --mood gamer --no-typing
python3 -m girlfriend.cli --mood motivational --no-typing
```

Check:

- mood label changes in the header
- output color changes
- message tone feels different for each mood

### ASCII mode

Check:

- mood art appears inside the main header block
- the small art matches the active mood
- layout does not break in your terminal

### Quotes

```bash
python3 -m girlfriend.cli --quote --no-typing
```

Check:

- a quote appears
- no parser error occurs

### Compliment mode

```bash
python3 -m girlfriend.cli compliment
```

Check:

- compliment appears
- message is nerdy and playful

### Roast mode

```bash
python3 -m girlfriend.cli roast
```

Check:

- roast appears
- content is funny and harmless

### Streak and stats

```bash
python3 -m girlfriend.cli streak
python3 -m girlfriend.cli stats
```

Check:

- current streak is shown
- total interactions increase after repeated runs
- stats command prints the config path

### System monitor

```bash
python3 -m girlfriend.cli monitor
```

Check:

- CPU percent is shown
- RAM percent is shown
- disk percent is shown
- battery is shown or `not detected`
- a funny reaction appears

### Offline chat mode

```bash
python3 -m girlfriend.cli chat
```

Try these sample inputs:

- `hello`
- `I found a bug`
- `I am tired`
- `I love you`
- `help`
- `quit`

Check:

- replies are context-aware
- `quit` exits cleanly
- no crash on normal chat flow

### Interactive AI chat config

```bash
python3 -m girlfriend.cli chat --config
```

Walk through these settings:

- save the API key
- choose a chat mood
- choose a chat theme
- choose a response style

Check:

- Rich prompts and tables render correctly
- settings are saved to `~/.girlfriend/config.json`
- no manual JSON editing is required
- there are no yes or no AI prompts

### Gemini key priority and failure handling

Test missing key behavior:

```bash
GIRLFRIEND_HOME=/tmp/girlfriend-ai-missing python3 -m girlfriend.cli chat
```

Then ask a complex prompt such as:

- `Explain Linux namespaces and cgroups in simple terms`

Check:

- local/simple prompts still work
- complex prompts fall through to AI handling
- missing key error tells you to use `girlfriend chat --config`
- Gemini fallback can answer complex prompts when the saved key is valid
- failures are specific for invalid key, quota, offline mode, or API issues

### Config command

View config:

```bash
python3 -m girlfriend.cli config
```

Change config:

```bash
python3 -m girlfriend.cli config --set-name ben
python3 -m girlfriend.cli config --set-mood hacker
python3 -m girlfriend.cli config --set-theme gamer
python3 -m girlfriend.cli config --enable-voice
python3 -m girlfriend.cli config
```

Check:

- config updates are displayed
- later runs reflect the changed mood or theme
- existing config command still works alongside `chat --config`

Disable voice again if you want:

```bash
python3 -m girlfriend.cli config --disable-voice
```

## 4. Data File Testing

By default the app stores user data in:

```text
~/.girlfriend/
```

Inspect the files:

```bash
ls -la ~/.girlfriend
cat ~/.girlfriend/config.json
cat ~/.girlfriend/streak.json
```

Check:

- `config.json` exists
- `streak.json` exists
- JSON content is valid
- new chat keys such as `gemini_api_key`, `chat_mood`, `chat_theme`, and `chat_response_style` are present after chat setup

If your environment is locked down and home is not writable, the app may fall back to a temporary directory. You can force a custom data directory for testing:

```bash
mkdir -p /tmp/girlfriend-test
GIRLFRIEND_HOME=/tmp/girlfriend-test python3 -m girlfriend.cli --no-typing
ls -la /tmp/girlfriend-test
cat /tmp/girlfriend-test/config.json
cat /tmp/girlfriend-test/streak.json
```

This is useful for clean repeatable testing.

## 5. Notification Testing

Install notification support if needed:

```bash
sudo apt update
sudo apt install -y libnotify-bin
```

Test notification support:

```bash
python3 -m girlfriend.cli notify-test
python3 -m girlfriend.cli --notify --no-typing
```

Check:

- desktop notification appears
- no crash if notifications are unavailable

Expected fallback:

- if `notify-send` is not installed, the app should print a warning and continue

## 6. Voice Testing

Install `espeak` if needed:

```bash
sudo apt update
sudo apt install -y espeak
```

Test voice:

```bash
python3 -m girlfriend.cli speak
```

Test softer feminine presets:

```bash
python3 -m girlfriend.cli config --set-voice-profile cute --set-voice-rate 145 --set-voice-pitch 72
python3 -m girlfriend.cli speak
python3 -m girlfriend.cli config --set-voice-profile soft
python3 -m girlfriend.cli speak
python3 -m girlfriend.cli config --set-voice-profile anime
python3 -m girlfriend.cli speak
```

Enable voice in config and test default command:

```bash
python3 -m girlfriend.cli config --enable-voice
python3 -m girlfriend.cli --no-typing
python3 -m girlfriend.cli config --disable-voice
```

Check:

- audio plays
- command does not crash if `espeak` is missing
- app prints a helpful warning if voice is unavailable

## 7. Pip Installation Testing

### Install in a virtual environment

This is the safest way to test packaging.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install .
girlfriend --help
girlfriend chat --help
girlfriend --no-typing
girlfriend monitor
deactivate
```

Check:

- installation succeeds
- `girlfriend` command is available
- command works outside `python -m`

### Global install test

If you want to test system-wide installation:

```bash
sudo pip3 install .
girlfriend --help
girlfriend --no-typing
```

Note:

- many Linux distributions prefer virtual environments or distro packages over `sudo pip`
- use this only if you intentionally want a system-wide command test

## 8. Build Artifact Testing

Build source and wheel packages:

```bash
python3 -m pip install build
python3 -m build
ls -la dist
```

Check:

- a source tarball exists
- a wheel file exists

Optional install-from-wheel test:

```bash
python3 -m venv /tmp/girlfriend-wheel-test
source /tmp/girlfriend-wheel-test/bin/activate
pip install dist/*.whl
girlfriend --help
deactivate
```

## 9. Debian Package Testing

### Install packaging dependencies

```bash
sudo apt update
sudo apt install -y build-essential devscripts debhelper-compat dh-python python3-all python3-setuptools pybuild-plugin-pyproject python3-rich lintian
```

### Build the `.deb`

From the project root:

```bash
dpkg-buildpackage -us -uc -b
```

Expected result:

- build completes successfully
- a `.deb` file appears in the parent directory

Check the package:

```bash
ls -la ..
```

You should see something like:

```text
../girlfriend_3.0.0-1_all.deb
```

### Install the `.deb`

```bash
sudo dpkg -i ../girlfriend_3.0.0-1_all.deb
sudo apt -f install
```

### Test the installed package

```bash
girlfriend --help
girlfriend --no-typing
girlfriend compliment
girlfriend monitor
girlfriend chat --help
```

Check:

- command is available globally
- no import errors happen after install

### Remove the package

```bash
sudo dpkg -r girlfriend
```

## 10. Regression Testing Checklist

Before release, test this full checklist:

- `python3 -m unittest discover -s tests -v`
- `python3 -m girlfriend.cli --help`
- `python3 -m girlfriend.cli --version`
- `python3 -m girlfriend.cli --no-typing`
- `python3 -m girlfriend.cli --quote --no-typing`
- `python3 -m girlfriend.cli compliment`
- `python3 -m girlfriend.cli roast`
- `python3 -m girlfriend.cli streak`
- `python3 -m girlfriend.cli stats`
- `python3 -m girlfriend.cli monitor`
- `python3 -m girlfriend.cli chat --help`
- `python3 -m girlfriend.cli chat`
- `python3 -m girlfriend.cli chat --config`
- `python3 -m girlfriend.cli config`
- `python3 -m girlfriend.cli notify-test`
- `python3 -m girlfriend.cli speak`
- `pip install .`
- `girlfriend --help`
- `dpkg-buildpackage -us -uc -b`

## 11. Common Problems

### `ModuleNotFoundError`

Cause:

- package not installed correctly
- command run from the wrong directory

Fix:

```bash
cd /home/ben/Desktop/girlfriend-release/girlfriend
pip install .
```

### `girlfriend: command not found`

Cause:

- package not installed
- virtual environment not activated

Fix:

```bash
pip install .
source .venv/bin/activate
girlfriend --help
```

### `notify-send` not found

Fix:

```bash
sudo apt install -y libnotify-bin
```

### `espeak` not found

Fix:

```bash
sudo apt install -y espeak
```

### `.deb` build fails

Cause:

- missing build dependencies
- Debian packaging tools not installed

Fix:

```bash
sudo apt install -y build-essential devscripts debhelper-compat dh-python python3-all python3-setuptools pybuild-plugin-pyproject python3-rich lintian
```

## 12. Recommended Full Test Flow

If you only want one complete sequence, use this order:

```bash
cd /home/ben/Desktop/girlfriend-release/girlfriend
python3 -m unittest discover -s tests -v
python3 -m girlfriend.cli --help
python3 -m girlfriend.cli --version
python3 -m girlfriend.cli --no-typing
python3 -m girlfriend.cli --quote --no-typing
python3 -m girlfriend.cli compliment
python3 -m girlfriend.cli roast
python3 -m girlfriend.cli monitor
python3 -m girlfriend.cli chat --help
python3 -m girlfriend.cli chat --config
python3 -m girlfriend.cli chat
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install .
girlfriend --help
girlfriend chat --help
girlfriend --no-typing
deactivate
dpkg-buildpackage -us -uc -b
sudo dpkg -i ../girlfriend_3.0.0-1_all.deb
girlfriend --help
girlfriend monitor
```

## 13. Release Readiness

The project is ready for release when:

- unit tests pass
- manual CLI checks pass
- optional integrations fail gracefully when missing
- AI setup and Gemini fallback behavior are verified
- `pip install .` works
- `.deb` builds successfully
- the installed `girlfriend` command works globally

At that point, you have tested the app like a real open-source package.
