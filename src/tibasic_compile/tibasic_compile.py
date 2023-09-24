#!/usr/bin/env python3


import argparse
import subprocess
import logging
import re
import sys
from tivars.types import TIProgram


# TODO: test that using θ as a program name actually works (like it gets pushed to the calc properly and runs)
def parse_args():
    parser = argparse.ArgumentParser(description="compile and upload things")
    parser.add_argument(
        "-v",
        "--verbose",
        required=False,
        action="store_true",
        help="verbosity",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # To handle some shared args
    def add_infile_arg(parser):
        parser.add_argument(
            "infile_contents",
            metavar="infile",
            type=infile,
            help="Input file containing TI-Basic source code",
        )

    def add_outfile_arg(parser):
        parser.add_argument(
            "outfile_path",
            metavar="outfile",
            type=outfile,
            help="8xp binary file that'll be uploaded to the calculator",
        )

    def add_program_name_arg(parser):
        parser.add_argument(
            "program_name",
            type=ti_program_name,
            help=(
                "Name of the program in the calculator menu. 1-8 chars long, valid chars: A-Z, 0-9, θ. First"
                " char can't be a number"
            ),
        )

    def add_processing_bool_arg(parser):
        parser.add_argument(
            "-s",
            "--skip-processing",
            required=False,
            action="store_false",
            dest="should_process",
            help="Skip pre-processing of file that strips out comments",
        )

    parser_build = subparsers.add_parser("build", help="create 8xp file from given source code")
    add_infile_arg(parser_build)
    add_outfile_arg(parser_build)
    add_program_name_arg(parser_build)
    add_processing_bool_arg(parser_build)

    parser_upload = subparsers.add_parser("upload", help="upload 8xp file to calculator")
    add_outfile_arg(parser_upload)

    # same args as build
    parser_install = subparsers.add_parser("install", help="builds and uploads the program")
    add_infile_arg(parser_install)
    add_outfile_arg(parser_install)
    add_program_name_arg(parser_install)
    add_processing_bool_arg(parser_install)

    args = parser.parse_args()

    return args


def infile(file_path: str):
    # TODO: I think this is enough error handling but look it over again once im less tired
    try:
        file_string = None
        with open(file_path, "r") as file:
            file_string = file.read()
        return file_string
    except OSError as e:
        raise argparse.ArgumentTypeError(str(e)) from e


def outfile(file_path: str):
    try:
        # TODO: add some minimal arg validation just to make sure the path is possibly valid
        #       since TIProgram.save() handles the file opening, writing, and closing
        # file = open(file_path, 'a')
        # file.close()
        return file_path
    except OSError as e:
        raise argparse.ArgumentTypeError(str(e)) from e


# TODO: rename `string` to `name` or something better
def ti_program_name(string: str):
    if len(string) == 0 or len(string) > 8:
        msg = f"program name must be 1-8 characters long, '{string}' is {len(string)} characters long"
    elif not string.replace("θ", "").isupper():  # Checks if the string is capitalized (ignoring θ)
        msg = "program name must be fully capitalized"
    elif string[0].isnumeric():
        msg = "first character of program name cannot be a number"
    elif not re.match(
        "[A-Zθ][A-Z0-9θ]*$", string
    ):  # Using * rather than {0, 7} because the length check was already done
        msg = "program name can only contain A-Z, 0-9, and θ"
    else:
        # If we make it this far, that means all conditions passed (string is valid)
        return string
    raise argparse.ArgumentTypeError(msg)


# TODO: delete line if it's just whitespace (0 or more spaces, + newline)
# preprocesses our input
# - strips out comments
# - (TODO) reports potential syntax errors
def preprocess(input_file_contents) -> str:
    logger.info("Pre-processing source code")

    # Script contents as big list of chars
    processed = list(input_file_contents)

    # Iterate over list (1 char at a time) and remove comments
    in_string = False
    i = -1
    while i < len(processed) - 1:
        i += 1
        char = processed[i]

        if char == "\n":
            # Strings close themselves at the end of lines in TI-Basic
            in_string = False
            continue

        if in_string and char == '"':
            in_string = False
            continue

        if not in_string:
            if char == '"':
                in_string = True
            elif char == "#":
                # Keep skipping comment text until we hit end of the line
                while processed[i] != "\n":
                    del processed[i]
                i -= 1  # Go back to the char before newline, so the loop doesn't skip it

    # Multiline string containing source code (with comments stripped out)
    processed = "".join(processed)

    # It would be better for performance to do this in the above loop but idrc tbh
    temp = ""
    for line in processed.splitlines():
        if not line or line.isspace():
            continue  # Don't add line if it's empty or just whitespace
        temp += line + "\n"
    processed = temp

    # Strip trailing newline
    processed = processed.rstrip("\n")

    logger.info("Processing complete")
    return processed


# text file -> 8xp program
def build(input_file_contents, output_file_path, program_name) -> None:
    logger.info("Compiling program: %s", program_name)

    program = TIProgram(name=program_name)
    program.load_string(input_file_contents)
    program.save(output_file_path)

    logger.info("Program written at %s", output_file_path)


# Use `tilp` to upload program to calculator
def upload(output_file_path) -> None:
    logger.info("Uploading %s", output_file_path)

    model = "ti84+ce"
    cable_type = "directlink"
    proc = subprocess.run(
        ["tilp", "--no-gui", "--silent", model, cable_type, output_file_path],
        check=False,
        capture_output=True,
        timeout=5,
        encoding="utf-8",
    )

    tilp_stdout = proc.stdout
    tilp_stderr = proc.stderr

    # Clean up stderr because it's in an annoying format
    if tilp_stderr != "":
        tilp_stderr = re.sub(
            r"\n+", "\n", tilp_stderr  # Turn >1 consecutive newlines into 1
        ).rstrip()  # then strip trailing

    # Handle errors
    if tilp_stderr != "":
        logger.critical("Failed to upload file: %s", tilp_stderr)
        sys.exit(1)
    elif "placeholder that will never match" in tilp_stdout:
        # TODO: figure out what error messages can be present and check if stdout contains them
        logger.critical("Failed to upload file: %s", "I have no clue what happened tbh")
        sys.exit(1)
    elif proc.returncode != 0:
        logger.critical("'%s' exited with exit status %s", " ".join(proc.args), proc.returncode)
        sys.exit(1)
    else:
        logger.info("Upload completed")


# dummy main() to call in setup.py (or in the future, pyproject.toml)
def main():
    # Set up logging
    global logger
    logger = logging.getLogger("tibasic_compiler")
    # FORMAT_STR = "%(name)s (%(levelname)s): %(message)s"
    FORMAT_STR = "%(levelname)s: %(message)s"
    logging.basicConfig(format=FORMAT_STR)

    args = parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    should_build = False
    should_upload = False
    match args.command:
        case "build":
            should_build = True
        case "upload":
            should_upload = True
        case "install":
            should_build = True
            should_upload = True
        case _:
            logger.error("how did you even do this??")
            sys.exit(5)

    if args.should_process:
        input_file_contents = preprocess(args.infile_contents)
    else:
        input_file_contents = args.infile_contents

    if should_build:
        build(input_file_contents, args.outfile_path, args.program_name)
    if should_upload:
        upload(args.outfile_path)

    logger.info("Done!")

    # DEBUGGING
    logger.debug("---original script---")
    logger.debug(args.infile_contents)
    logger.debug("---------")

    logger.debug("---processed script---")
    logger.debug(input_file_contents)
    logger.debug("---------")

    logger.debug(f"outfile name: {args.outfile_path}")
    logger.debug(f"program name: {args.program_name}")


if __name__ == "__main__":
    main()
