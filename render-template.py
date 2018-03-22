#!/usr/bin/env python3
"""
Render transcript using jinja2.

Usage:
    render-transcript.py (-h | --help)
    render-transcript.py [--output=FILE] <template> [<transcript>]

Options:
    -h, --help                  Show a brief usage summary.

    -o, --output=FILE           Write output to a specific file. Use "-" to indicate standard
                                output [default: -]

    <template>                  Template for rendered output.

    <transcript>                Transcript to render or "-" for standard input. [default: -]

"""
import sys

import docopt
import durations
import jinja2
import json


def main():
    # Parse command line options
    opts = docopt.docopt(__doc__)

    # Load Jinja2 context
    with open_from_opt(opts['<transcript>'] or '-', 'rb') as fobj:
        context = json.load(fobj)

    # Create the Jinja2 environment and load the transcript
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader('.'), trim_blocks=True
    )
    env.filters['durationformat'] = durationformat
    template = env.get_template(opts['<template>'])

    with open_from_opt(opts['--output'], 'w') as fobj:
        fobj.write(template.render(context))


def durationformat(value):
    duration = durations.Duration(value)
    seconds = int(duration.to_seconds())
    hours = seconds // (60*60)
    seconds -= 60*60*hours
    minutes = seconds // 60
    seconds -= 60*minutes
    return '{hours:d}h{minutes:02d}m{seconds:02d}s'.format(
        hours=hours, minutes=minutes, seconds=seconds)


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
