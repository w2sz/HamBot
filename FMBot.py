#!/usr/bin/env python3

'''
FMBot.py
Author: Hisen (Zhemin) Zhang KD2TAI

This program transcribe what it hears to text, and optionally post the content to 
Mastodon sites.

The main body of code was adapted from the example below:
https://github.com/alphacep/vosk-api/blob/master/python/example/test_microphone.py

'''

import json
import argparse
import os
import queue
import sounddevice as sd
import vosk
import sys

import datetime
from mastodon import Mastodon

ACCESS_TOKEN = 'YOUR_ACCESS_TOKEN'

q = queue.Queue()


def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text


def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        '-l', '--list-devices', action='store_true',
        help='show list of audio devices and exit')
    args, remaining = parser.parse_known_args()
    if args.list_devices:
        print(sd.query_devices())
        parser.exit(0)
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[parser])
    parser.add_argument(
        '-f', '--filename', type=str, metavar='FILENAME',
        help='audio file to store recording to')
    parser.add_argument(
        '-d', '--device', type=int_or_str,
        help='input device (numeric ID or substring)')
    parser.add_argument(
        '-r', '--samplerate', type=int, help='sampling rate')
    parser.add_argument(
        '--apibaseurl', type=str,
        help='optionally push transcribed text to the specified URL')

    args = parser.parse_args(remaining)

    try:
        if args.samplerate is None:
            device_info = sd.query_devices(args.device, 'input')
            # soundfile expects an int, sounddevice provides a float:
            args.samplerate = int(device_info['default_samplerate'])

        model = vosk.Model(
            model_path='vosk-model-en-us-0.22')

        if args.filename:
            dump_fn = open(args.filename, "wb")
        else:
            dump_fn = None

        mastodon = None
        if args.apibaseurl:
            mastodon = Mastodon(
                access_token=ACCESS_TOKEN,
                api_base_url=args.apibaseurl,
                ratelimit_method='pace'
            )
            print(
                "WARNING: Network feature enabled. Transcribed text may be publicly available.")

        with sd.RawInputStream(samplerate=args.samplerate, blocksize=4000, device=args.device, dtype='int16',
                               channels=1, callback=callback):
            print('#' * 80)
            print('Press Ctrl+C to stop the recording')
            print('#' * 80)

            rec = vosk.KaldiRecognizer(model, args.samplerate)
            while True:
                data = q.get()
                if rec.AcceptWaveform(data):
                    recognized_text = json.loads(rec.Result())['text']
                    recognized_time = datetime.datetime.now().strftime("%H:%M:%S")

                    # Some simple filtering below...
                    # Empty string
                    if recognized_text == '':
                        continue
                    # One word phrase
                    if recognized_text.count(' ') == 0:
                        continue

                    msg = f'[{recognized_time}] {recognized_text}'
                    print(msg)
                    if mastodon:
                        # if network feature enabled
                        mastodon.toot(msg)

                if dump_fn is not None:
                    dump_fn.write(data)

    except KeyboardInterrupt:
        print('\nDone')
        parser.exit(0)
    except Exception as e:
        parser.exit(type(e).__name__ + ': ' + str(e))


if __name__ == '__main__':
    main()
