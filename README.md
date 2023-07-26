# Listener
Listen to loud noises and send out a notification


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

## Sound card

You might need to configure the audio input device that will be used by `pyaudio`. If using linux you need to install alsa:

- On a linux shell: `apt-get install alsa-utils`
- Then find your audio input with: `arecord --list-devices` 

And configure your device (need to add more details here)