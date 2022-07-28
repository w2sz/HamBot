# HamBot

Voice transcription for radio traffic.

The code in this repository is solely for the purpose of prototyping and concept verification.

## Tested Environment

Less powerful machine has no guarantee in good performance.

### Hardware

- Processor: AMD Ryzen 7 3800X 8-Core Processor 3.90GHz
- Installed RAM: 32 GB
- Software-Defined Radio: RSP1 connected via USB

### Software

- Python 3.9.12
- VOSK 0.3.42
- PyAudio 0.2.11
- Mastodon.py 1.5.1
- SDRuno 1.41.1
- Windows specifications
  - Edition: Windows 10 Home
  - Version: 2004

## FMBot.py

This program transcribe what it hears to text, and optionally post the content to Mastodon sites.

You need to [download](https://alphacephei.com/vosk/models) and unzip VOSK speech models to the project base directory first.

To run: get a list of available audio devices by

```bash
python FMBot.py -l
```

Then specify the index of device you would like to monitor on (e.g. 1):

```bash
python FMBot.py -d 1
```

To enable network feature, run with

```bash
python FMBot.py -d 1 --apibaseurl MASTODON_SERVER_URL
```

Remember to replace the ACCESS_TOKEN in the script with your own value.

## playground.ipynb

This notebook contains some chucks of code we used for performance analysis.
