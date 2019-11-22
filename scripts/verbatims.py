#!/usr/bin/env python3

import json
import sys

import click


@click.group()
def cli():
    """Manage the verbatims in verbatims.json.

    With our verbatims now being in a JSON file, we have long blocks of text as
    single strings, which is a bit of a pain.  This provides tools for dumping
    verbatims from, and loading them to, the verbatims.json file in a plain
    text form.
    """
    pass


@click.command()
@click.option("--verbatim-id")
@click.option("--src-file", default="src/verbatims.json")
@click.option("--out-file", default=None)
def dump(verbatim_id, src_file, out_file):
    """Dump the content of a verbatim.

    If no outfile is specified, print to STDOUT.
    """
    with open(src_file) as src:
        data = json.load(src)
        for verbatim in data:
            if verbatim["id"] == verbatim_id:
                if out_file:
                    with open(out_file, "w") as output:
                        output.write(verbatim["text"])
                else:
                    print(verbatim["text"])


@click.command()
@click.option("--verbatim-id")
@click.option("--src-file", default="src/verbatims.json")
@click.option("--in-file", default=None)
@click.option("--out-file", default=None)
@click.option("--replace/--no-replace", default=False)
def add(verbatim_id, src_file, in_file, out_file, replace):
    """Add or optionally replace a verbatim.

    By default, this will act as a standard Unix filter by reading from
    STDIN and printing to STDOUT.  If you use an output file, it is strongly
    encouraged that you not output directly back to your verbatims.json --
    it would technically work, but an error in processing could end up with
    you having an empty file.

    This method will not overwrite an existing verbatim, if one exists with
    the same id, unless the --replace option is specified.
    """
    with open(src_file) as src:
        verbatims = json.load(src)

    text_file = open(in_file) if in_file else sys.stdin
    try:
        text = text_file.read()
    finally:
        text_file.close()

    new_record = {"id": verbatim_id, "text": text}

    foundit = False
    for (index, item) in enumerate(verbatims):
        if item["id"] == verbatim_id:
            foundit = True
            if replace:
                verbatims[index] = new_record
            else:
                print(
                    f"Verbatim '{verbatim_id}' already exists.  "
                    "If you mean it, use --replace."
                )
                sys.exit(1)

    if not foundit:
        verbatims.append(new_record)

    if out_file:
        dest = open(out_file, "w")
    else:
        dest = sys.stdout

    try:
        json.dump(verbatims, dest, indent=4)
    finally:
        dest.close()


cli.add_command(dump)
cli.add_command(add)

if __name__ == "__main__":
    cli()
