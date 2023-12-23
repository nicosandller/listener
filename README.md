
# Listener - An Audio Monitoring System

Listener is a Python-based audio monitoring system that detects loud noises and sends an email alert with an attached audio clip of the detected noise. The application is designed to run in the background, monitoring the surrounding environment continuously.

## Features

- Real-time audio monitoring
- RMS computation for noise detection
- Email alerts with attached audio file when a loud noise is detected
- Regular status updates via email

## Config file

Create a config file `config.py` on the same directory as `listener.py`

```python
# This will be the detection threshold at which point you will get a notification
THRESHOLD = 2000  # Modify this as needed
# How many seconds to record
RECORD_SECONDS = 5
# Number of audio samples you read at a time for each chunk
CHUNK_SIZE = 4096
# Number of audio samples per second.
RATE = 22050 
WAVE_OUTPUT_FILENAME = "output.wav"
EMAIL_ADDRESSES_TO = ["email1@email.com", "email2@email.com"]
# Sender account credentials
EMAIL_PASSWORD = "SOME PASSWORD"
EMAIL_ADDRESS_FROM = "sender_email@gmail.com"
# Minimum time between notifications
MIN_EMAIL_DELAY = 3600  # Minimum delay of 1 hour
```


## Audio sampling logic explained

#### CHUNK_SIZE

- This is the number of audio samples you read at a time for each chunk. By increasing the chunk size, your script will read in larger amounts of data at once, which could help prevent the buffer from overflowing
- recommended min: 1024 max:8000

#### RATE
-  This is the sample rate, or the number of audio samples per second.
-  recommended min: 22050 max:44100 

#### RATE / CHUNK_SIZE 
- is giving you the number of chunks per second
- when you multiply this by RECORD_SECONDS, you get the total number of chunks needed for the recording.


## Sender account
You can use gmail to send the email notifications. To do so got to https://myaccount.google.com/apppasswords and create an app password for the account you want to use


## Cron job

You can use[`crontab`](https://man7.org/linux/man-pages/man5/crontab.5.html) + [`screen`](https://linux.die.net/man/1/screen) to set the script to run on every device reboot on a `screen` shell:

- On a shell: `crontab -e`
- Add the following on a line in the crontab file: `@reboot /usr/bin/screen -dmS listener /usr/bin/python3 /full/path/to/listener.py`

## Screen

To look at the screen shell:
```
 screen -ls
.....
screen -r [session name]
.....
To close the session without closing it, inside the screen session, press Ctrl + A.
Then, press D.
```

## Sound card (for linux devices)

This script works directly on a a macbook computer but if you want to run it in a linux based single board computer you'll need some extra configuration.

You might need to configure the audio input device that will be used by `pyaudio`. If using linux you need to install alsa:

- On a linux shell: `apt-get install alsa-utils`
- Then find your audio input with: `arecord --list-devices` 

And configure your device (need to add more details here)


## TODO:
- add requirements.txt
- finish soundcard config README for linux devices