from tracemalloc import stop
import speech_recognition as sr
# import pyaudio
import pyttsx3
from gtts import gTTS
from playsound import playsound
import os
import argparse
import time
import subprocess
import re

AUDIO_FILES_BASE_PATH=r'./audio_files/'

NO_CONNECTION_ERR_TEXT = "Failed to generate audio file. Please check your internet connection."
NO_CONNECTION_ERR_AUDIO = "no_connection.mp3"

WELCOME_TEXT = "Welcome Rishabh!"
WELCOME_AUDIO = "welcome.mp3"

SAY_SOMETHING_TEXT = "What can I do for you."
SAY_SOMETHING_AUDIO = "say_something.mp3"

SETUP_COMPLETED_TEXT = "Setup is complete. Thank you!"
SETUP_COMPLETED_AUDIO = "setup_completed.mp3"

SETUP_FIRST_TEXT = "Please setup the application before use."
SETUP_FIRST_AUDIO = "setup_first.mp3"

OUTPUT_AUDIO = "output.mp3"

MALE_VOICE = True

STOP = False

VPN_EXEC = r'C:\Users\LENOVO\Desktop\connector.cmd'
# voice_engine = pyttsx3.init()


def setup():
    success = True
    if not os.path.exists(AUDIO_FILES_BASE_PATH):
        try:
            os.mkdir(AUDIO_FILES_BASE_PATH)
        except:
            print("Failed to create audio file directory.")
            success = False
    try:
        generate_audio_file(WELCOME_TEXT, filename=WELCOME_AUDIO)
    except:
        print("Failed to generate audio file for welcome text.")
        success = False
    try:
        generate_audio_file(NO_CONNECTION_ERR_TEXT, filename=NO_CONNECTION_ERR_AUDIO)
    except:
        print("Failed to generate audio file for connection error.")
        success = False
    try:
        generate_audio_file(SAY_SOMETHING_TEXT, filename=SAY_SOMETHING_AUDIO)
    except:
        print("Failed to generate audio file for say something audio.")
        success = False
    try:
        generate_audio_file(SETUP_COMPLETED_TEXT, filename=SETUP_COMPLETED_AUDIO)
    except:
        print("Failed to generate audio file for setup complete audio.")
        success = False
    try:
        generate_audio_file(SETUP_FIRST_TEXT, filename=SETUP_FIRST_AUDIO)
    except Exception as ex:
        print(f"Failed to generate audio file for setup first audio. {ex}")
        success = False
    if not success:
        exit(1)
    play_audio(SETUP_COMPLETED_AUDIO)


def is_setup_complete():
    if not (os.path.exists(AUDIO_FILES_BASE_PATH) and \
            os.path.exists(AUDIO_FILES_BASE_PATH + WELCOME_AUDIO) and \
            os.path.exists(AUDIO_FILES_BASE_PATH + NO_CONNECTION_ERR_AUDIO) and \
            os.path.exists(AUDIO_FILES_BASE_PATH + SAY_SOMETHING_AUDIO) and \
            os.path.exists(AUDIO_FILES_BASE_PATH + SETUP_COMPLETED_AUDIO) and \
            os.path.exists(AUDIO_FILES_BASE_PATH + SETUP_FIRST_AUDIO)):
        return False
    else:
        return True


def generate_audio_file(text, filename=None, input_audio=False):
    audio_file = AUDIO_FILES_BASE_PATH + "input_audio.mp3"
    if not input_audio:
        audio_file = AUDIO_FILES_BASE_PATH + OUTPUT_AUDIO
    # If file name is specified use that.
    if filename:
        audio_file = f"{AUDIO_FILES_BASE_PATH}{filename}"
    # Add mp3 extension to audio files.
    if audio_file.split(".")[-1] != "mp3":
            audio_file = f"{audio_file}.mp3"
    # Remove the audio file if previously present
    if os.path.exists(audio_file):
            os.remove(audio_file)
    try:
        myobj = gTTS(text=text, lang="en", tld='co.in', slow=False)
        myobj.save(audio_file)
    except:
        if os.path.exists(audio_file):
            play_audio(NO_CONNECTION_ERR_AUDIO)
        else:
            print("Failed to generate audio file. Please check your internet connection.")


def play_audio(audio_file_name=None):
    """
    Play audio.
    :param: audio_file_name: Name of the audio file.
    :return: returns False if failed to play the audio.
    """
    if not audio_file_name:
        print("Audio file name must be provided.")
        return False

    audio_file = AUDIO_FILES_BASE_PATH + audio_file_name
    if os.path.exists(audio_file):
        try:
            playsound(audio_file)
        except:
            print(f"Failed to play audio file: {audio_file}")
            return False

def connect_vpn():
    try:
        subprocess.check_output(VPN_EXEC)
    except Exception as ex:
        print(f"Failed to connect vpn {ex}")

def voice_parser(recognizer, audio):
    global STOP
    import re
    try:
        out = recognizer.recognize_google(audio)
        # print(f"Voice recognized by google: {out}")
        if out:
            print(out)
            generate_audio_file(out)
            play_audio(OUTPUT_AUDIO)
            out = out.casefold()
            if re.match('^exit', out):
                STOP = True
            if re.match("connect.*vpn", out):
                connect_vpn()
        else:
            print("Please speak I could not understand what you said.")
    except Exception as ex:
        if re.match("recognition connection failed", f"{ex}".casefold()):
            play_audio(NO_CONNECTION_ERR_AUDIO)
        print(f"Failed recognizing the audio using google recognizer as error: {ex}")
    

parser = argparse.ArgumentParser()
parser.add_argument("--setup", help="First time setup", action="store_true")
parser.add_argument("--start", help="Start the voice recognition system", action="store_true")
args = parser.parse_args()

if args.setup:
    setup()
elif args.start:
    # start
    if not is_setup_complete():
        print("Please complete the setup first.")
        exit(1)
    play_audio(WELCOME_AUDIO)
    r = sr.Recognizer()
    m = sr.Microphone()
    with m as source:
        r.adjust_for_ambient_noise(source)
        print("Say something!")
        play_audio(SAY_SOMETHING_AUDIO)
        # audio = r.listen(source)
    stop_listening = r.listen_in_background(m, voice_parser, phrase_time_limit=5)
    # for _ in range(50): time.sleep(0.1)
    # stop_listening(wait_for_stop=False)
    while True: 
        time.sleep(0.1)
        if STOP:
            stop_listening(wait_for_stop=True)
            exit(0)
else:
    parser.print_help()
