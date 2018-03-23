# Transcripts of UIS Security Podcast

This repository contains automated transcripts of the [UIS Security
Podcast](http://feeds.feedburner.com/UisSecurityPodcast) made using the Google
Cloud Speech Transcription API.

The transcriptions are
[hosted](https://rjw57.github.io/uis-security-podcast-transcripts/) via GitHub
pages.

## Rendering transcriptions

A very simple [template](transcript.in.html) is provided to render a transcript
from the raw data from Google. To render the transcriptions:

```console
$ python3 -m virtualenv venv -p $(which python3)
$ source venv/bin/activate
$ pip install -r requirements.txt
$ make
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
