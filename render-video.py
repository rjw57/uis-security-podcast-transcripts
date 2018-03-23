#!/usr/bin/env python3
"""
Generate video from transcription

Usage:
    render-video.py (-h|--help)
    render-video.py <data> <output>

Options:

    -h,--help               Show a brief usage summary.
"""
import collections
import json
import sys

import av
import docopt
import PIL.Image as Image
import PIL.ImageDraw as ImageDraw
import PIL.ImageFont as ImageFont
import tqdm

FRAME_SIZE = (1920, 1080)
FPS = 10


Word = collections.namedtuple('Word', 'word start_time end_time')


def main():
    opts = docopt.docopt(__doc__)
    with open_from_opt(opts['<data>']) as fobj:
        transcript = json.load(fobj)
    render(transcript, opts['<output>'], fps=FPS, frame_size=FRAME_SIZE)


def render(transcript, output_filename, fps, frame_size):
    # Convert words list to a more efficient deque
    words = collections.deque(extract_words(transcript))

    max_time = words[-1].end_time

    n_frames = int(max_time * FPS)

    container = av.open(output_filename, mode='w')
    stream = container.add_stream('mpeg4', rate=fps)
    stream.width, stream.height = frame_size
    stream.pix_fmt = 'yuv420p'

    safe_frame_size = (
        int(0.8 * frame_size[0]),
        int(0.8 * frame_size[1]),
    )

    next_word, next_word_font = None, None

    for frame_idx in tqdm.tqdm(range(n_frames)):
        t = float(frame_idx) / float(fps)
        if t > max_time:
            break

        if next_word and next_word.end_time < t:
            next_word = None

        while next_word is None and len(words) > 0:
            candidate = words.popleft()
            if candidate.end_time >= t:
                next_word = candidate
                next_word_font = font_for_word(next_word.word, safe_frame_size)

        frame_im = Image.new('RGB', frame_size, color=(0, 0, 0))

        if next_word and max(next_word.start_time-0.1, next_word.end_time-0.4) <= t:
            draw = ImageDraw.Draw(frame_im)
            word_w, word_h = next_word_font.getsize(next_word.word)
            x = int(0.5 * (frame_size[0] - word_w))
            y = int(0.5 * (frame_size[1] - word_h))
            draw.text((x, y), next_word.word, font=next_word_font, fill=(255, 255, 255))
            del draw

        frame = av.VideoFrame.from_image(frame_im)
        for packet in stream.encode(frame):
            container.mux(packet)

    # Flush stream
    for packet in stream.encode():
        container.mux(packet)

    # Close the file
    container.close()


FONTS = [
    ImageFont.truetype('FreeMono.ttf', size=size)
    for size in range(500, 10, -1)
]


def font_for_word(word, max_size):
    max_w, max_h = max_size
    for font in FONTS:
        w, h = font.getsize(word)
        if w < max_w and h < max_h:
            return font
    return font


def extract_words(transcript):
    # Get list of word objects
    words = []
    for result in transcript['results']:
        for word in result['alternatives'][0]['words']:
            words.append(Word(
                word=word['word'],
                start_time=parse_time(word['startTime']),
                end_time=parse_time(word['endTime'])
            ))

    # Sort by ascending end time
    words.sort(key=lambda w: w.end_time)

    return words


def parse_time(timestr):
    assert timestr.endswith('s')
    return float(timestr.strip(' s'))


def open_from_opt(path, mode='r'):
    """
    Return an open file based on a pathname in an option. Understands "-" to mean standard
    {in,out}put and respects the 'b' flag in the mode for said.

    """
    # If not std{out,in}, return open file
    if path != '-':
        return open(path, mode)

    # Otherwise, return appropriate built in file object
    if 'w' in mode:
        return sys.stdout if 'b' not in mode else sys.stdout.buffer
    else:
        return sys.stdin if 'b' not in mode else sys.stdin.buffer


if __name__ == '__main__':
    main()
