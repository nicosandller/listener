# Standard library imports
import os
import queue
import smtplib
import threading
import time
import traceback
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging

# Setup logging
logging.basicConfig(filename='listener.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Related third-party imports
import audioop
import pyaudio
import wave

# Local application/library-specific imports
from config import (
    CHUNK_SIZE,
    EMAIL_ADDRESS_FROM,
    EMAIL_ADDRESSES_TO,
    EMAIL_PASSWORD,
    MIN_EMAIL_DELAY,
    RATE,
    RECORD_SECONDS,
    THRESHOLD,
    WAVE_OUTPUT_PATH,
    LOG_EMAIL_INTERVAL
)


log = []
max_rms = 0

FORMAT = pyaudio.paInt16

def log_exception(message):
    exception = traceback.format_exc()
    log_message = f"{message}: {exception}"
    log.append(log_message)
    logger.error(log_message)  # log the error message to the log file
    print("\n" + log_message)

def setup_server():
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(EMAIL_ADDRESS_FROM, EMAIL_PASSWORD)
    return server

def send_email(subject, body, attachment_path=None):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS_FROM
    msg['To'] = ", ".join(EMAIL_ADDRESSES_TO)
    msg['Subject'] = f"Listener: {subject}"
    msg.attach(MIMEText(body, 'plain'))
    
    if attachment_path:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(attachment_path, 'rb').read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment_path))
        msg.attach(part)
    
    try:
        server = setup_server()
        print("\nsending email...")
        server.sendmail(EMAIL_ADDRESS_FROM, EMAIL_ADDRESSES_TO, msg.as_string())
        server.quit()
    except Exception:
        log_exception("Failed to send an email")

# Startup email
def send_startup_email():
    time.sleep(20)  # Send 20 seconds after startup
    print("\nSending program start email")
    send_email("Program started", 'The sound detection program has started and is currently active.')

threading.Thread(target=send_startup_email, daemon=True).start()

# Log email
def email_logs():
    while True:
        time.sleep(LOG_EMAIL_INTERVAL)  # Send every hour
        print("\nSending logs email")
        logs_to_send = log.copy()
        log.clear()
        send_email("exception log", '\n'.join(logs_to_send))

threading.Thread(target=email_logs, daemon=True).start()

# Create a queue to hold the audio data
audio_queue = queue.Queue()

# Store the timestamp of the last email sent
last_email_sent_time = 0

def write_and_send_email():
    while True:
        frames = audio_queue.get()
        print("\nwriting audio file...")

        output_filename = f"output_{datetime.now().strftime('%Y%m%d%H%M%S')}.wav"
        output_filepath = os.path.join(WAVE_OUTPUT_PATH, output_filename)
        
        try:
            with wave.open(output_filepath, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(p.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))
        except Exception:
            log_exception("Failed to write to the .wav file")

        send_email("Loud noise detected", "", output_filepath)

        try:
            os.remove(output_filepath)
        except Exception:
            log_exception("Failed to delete the .wav file")

        audio_queue.task_done()

# Start the write_and_send_email function in a separate thread
threading.Thread(target=write_and_send_email, daemon=True).start()

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK_SIZE)

rms_values = []
last_print_time = time.time()
last_log_time = time.time()

try:
    print("* listening")
    log.append("*Listening started")
    while True:
        current_time = time.time()

        if not stream.is_active():
            try:
                stream = p.open(format=FORMAT, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK_SIZE)

            except Exception as e:
                log_exception("Audio stream was inactive, trying to reopen...")
            
        try:
            data = stream.read(CHUNK_SIZE)
            rms = audioop.rms(data, 2)

        except Exception as e:
            log_exception("Exception during listening and processing")

        rms_values.append(rms)
        max_rms = max(max_rms, rms)

        # every 3 seconds print to terminal
        if current_time - last_print_time > 3:  # Check if 3 seconds have passed
            average_rms = round(sum(rms_values) / len(rms_values), 2)
            print("\rAverage RMS: " + str(average_rms), end="")
            rms_values = []  # Reset the list
            last_print_time = current_time  # Reset the timer

        # every log email interval: log the max
        if (current_time - last_log_time) > LOG_EMAIL_INTERVAL:  
            log.append(f"Max RMS: {max_rms}")
            print("\Max RMS for last hour: " + str(average_rms), end="")
            max_rms = 0  # Reset the max RMS
            last_log_time = current_time # Reset the timer

        # if sound is too loud
        if rms >= THRESHOLD:
            print("\n> Loud noise detected, RMS: ", rms)
            frames = [stream.read(CHUNK_SIZE) for _ in range(int(RATE / CHUNK_SIZE * RECORD_SECONDS))]

            # If time since last email is more than min delay: send an email
            if time.time() - last_email_sent_time >= MIN_EMAIL_DELAY:  
                audio_queue.put(frames)
                last_email_sent_time = time.time()

except KeyboardInterrupt:
    pass

print("* done recording")
log.append("*Recording stopped")
audio_queue.join()
stream.stop_stream()
stream.close()
p.terminate()



