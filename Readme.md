# Auto fishing toll for World Of Warcraft

## Getting started

Here is some dependencies you need to install:

- pyaudio
- opencv-python
- pyautogui
- mss

All of them can be installed with `pip` except `pyaudio`.

You will need to install `portaudio` mannually.

I tested it on Manjaro with Python verison 3.7.4.

You need a picture of the `Fishing Float` which you can use `PrintScreen` hotkey to get.

Notice that due to the fishing float recognition is implemented by template maching, so when you switch to another place you will need a new picture of fishing float.

This issue might be able to resolve by using neural networks instead template match.

It will be better if you turn off all other sound effects other than the game sound.

If someone else is fishing beside you, their sound effects might lead some bugs.

## Disclaimer

Pleas don't abuse this, I built this for basic Machine Learning demostrating and fun, DO NOT ABUSE IT!
