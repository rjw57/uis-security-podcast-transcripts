# Transcripts of UIS Security Podcast

This repository contains automated transcripts of the [UIS Security
Podcast](http://feeds.feedburner.com/UisSecurityPodcast) made using the Google
Cloud Speech Transcription API.

The transcriptions are
[hosted](https://rjw57.github.io/uis-security-podcast-transcripts/) via GitHub
pages.

## Installation

This software uses some Python bindings to ffmpeg's various ``libav...``
libraries. Make sure to [install
dependencies](http://mikeboers.github.io/PyAV/installation.html#dependencies)
for those first. On later Ubuntu-likes:

```console
$ sudo apt-get install -y \
	libavformat-dev libavcodec-dev libavdevice-dev \
	libavutil-dev libswscale-dev libavresample-dev libavfilter-dev
```

One can then install the package proper:

```console
$ python3 -m virtualenv venv -p $(which python3)
$ source venv/bin/activate
$ pip install -r requirements.txt
```

## Rendering transcriptions

A very simple [template](transcript.in.html) is provided to render a transcript
from the raw data from Google. To render the transcriptions:

```console
$ make html
```

## Rendering video

As an experiment, you can render a video for a podcast episode by downloading
the MP3 and using the ``render-video.py`` script in combination with ``ffmpeg``:

```console
$ ./render-video.py data/${EPISODE}.json temp.mp4 && \
	ffmpeg -y -i temp.mp4 -i ${EPISODE}.mp3 -acodec copy -vcodec copy ${EPISODE}.mp4
```

## Transcribing an episode

Transcription follows closely the procedure outlined in [Google's
documentation](https://cloud.google.com/speech/docs/async-recognize). Each
episode is converted to a FLAC file via ffmpeg and uploaded to a bucket.
Transcription is performed via:

```console
$ gcloud ml speech recognize-long-running \
    gs://${BUCKET_NAME}/${EPISODE}.flac \
    --language-code='en-GB' --include-word-time-offsets --async
```

This will write a JSON document with an operation ID to standard output. This
can be waited for and piped into a data file via:

```console
$ gcloud ml speech operations wait ${OPERATION_ID} >${EPISODE}.json
```
