import pyaudio
import audioop
import time
import wave
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import threading
import queue

from config import (
    THRESHOLD, 
    CHUNK_SIZE, 
    RATE, 
    RECORD_SECONDS , 
    WAVE_OUTPUT_FILENAME, 
    EMAIL_ADDRESS_FROM, 
    EMAIL_ADDRESSES_TO, 
    EMAIL_PASSWORD, 
    MIN_EMAIL_DELAY
)

FORMAT = pyaudio.paInt16

# function to send an email
def send_email(file_path):

    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS_FROM
    msg['To'] = ", ".join(EMAIL_ADDRESSES_TO)
    msg['Subject'] = "Loud noise detected"

    part = MIMEBase('application', 'octet-stream')
    part.set_payload(open(file_path, 'rb').read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file_path))
    msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(EMAIL_ADDRESS_FROM, EMAIL_PASSWORD)
    text = msg.as_string()
    server.sendmail(EMAIL_ADDRESS_FROM, EMAIL_ADDRESSES_TO, text)
    server.quit()

# Create a queue to hold the audio data
audio_queue = queue.Queue()

# Store the timestamp of the last email sent
last_email_sent_time = 0

def write_and_send_email():
    while True:
        # Get the frames from the queue
        frames, output_filename = audio_queue.get()

        # Write the frames to a .wav file
        wf = wave.open(output_filename, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

        # send email
        send_email(output_filename)
        
        # Mark the task as done
        audio_queue.task_done()

# Start the write_and_send_email function in a separate thread
threading.Thread(target=write_and_send_email, daemon=True).start()

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK_SIZE)

rms_values = []
last_print_time = time.time()

try:
    print("* listening")
    while True:
        data = stream.read(CHUNK_SIZE)
        rms = audioop.rms(data, 2)  # here's where you calculate the volume

        # print RMS
        rms_values.append(rms)
        current_time = time.time()
        if current_time - last_print_time > 3:  # Check if 3 seconds have passed
            average_rms = sum(rms_values) / len(rms_values)
            print("\rAverage RMS: " + str(average_rms), end="")
            rms_values = []  # Reset the list
            last_print_time = current_time  # Reset the timer

        if rms >= THRESHOLD:
            print("\n> Noise detected, RMS: ", rms)
            print("Recording...")
            frames = []
            for _ in range(0, int(RATE / CHUNK_SIZE * RECORD_SECONDS)):
                data = stream.read(CHUNK_SIZE)
                frames.append(data)

            print("Recording finished, preparing to send an email...")
            
            # Check if an hour has passed since the last email
            if time.time() - last_email_sent_time >= MIN_EMAIL_DELAY:  # 3600 seconds = 1 hour
                # If so, add the frames to the queue to be processed by the other thread
                audio_queue.put((frames, WAVE_OUTPUT_FILENAME))
                last_email_sent_time = time.time()

            else:
                print("aborting email, already sent one in the last hour.")

            

        # time.sleep(0.1)

except KeyboardInterrupt:
    pass

print("* done recording")

# Wait for all the audio data to be written and emailed before closing the stream
audio_queue.join()

stream.stop_stream()
stream.close()
p.terminate()
