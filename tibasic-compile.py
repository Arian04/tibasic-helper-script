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
        "infile_contents",
        metavar="infile",
        type=infile,
        help="Input file containing TI-Basic source code",
    )
    parser.add_argument(
        "outfile_path",
        metavar="outfile",
        type=outfile,
        help="8xp binary file that'll be uploaded to the calculator",
    )
    parser.add_argument(
        "program_name",
        type=ti_program_name,
        help=(
            "Name of the program in the calculator menu. 1-8 chars long, valid chars: A-Z, 0-9, θ. First char"
            " can't be a number"
        ),
    )
    parser.add_argument(
        "-v",
        "--verbose",
        required=False,
        action="store_true",
        help="verbosity",
    )
    # pylint: disable=redefined-outer-name
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

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


# text -> 8xp program
def build(input_file_contents, output_file_path, program_name):
    logger.info("Compiling program: {}", program_name)

    program = TIProgram(name=program_name)
    program.load_string(input_file_contents)
    program.save(output_file_path)

    logger.info("Program written at {}", output_file_path)


def upload(output_file_path):
    logger.info("Uploading {}", output_file_path)

    # Use `tilp` to upload program to calculator
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
            r"\n+", "\n", tilp_stderr  # Turn >1 newlines into 1
        ).rstrip()  # then strip trailing

    # Handle errors
    if tilp_stderr != "":
        logger.critical("Failed to upload file: {}", tilp_stderr)
        sys.exit(1)
    elif "placeholder that will never match" in tilp_stdout:
        # TODO: figure out what error messages can be present and check if stdout contains them
        logger.critical("Failed to upload file: {}", "I have no clue what happened tbh")
        sys.exit(1)
    elif proc.returncode != 0:
        logger.critical("'{}' exited with exit status {}", " ".join(proc.args), proc.returncode)
        sys.exit(1)
    else:
        logger.info("Upload completed")


if __name__ == "__main__":
    # Set up logging
    logger = logging.getLogger("tibasic_compiler")
    # FORMAT_STR = "%(name)s (%(levelname)s): %(message)s"
    FORMAT_STR = "%(levelname)s: %(message)s"
    logging.basicConfig(format=FORMAT_STR)

    args = parse_args()

    build(args.infile_contents, args.outfile_path, args.program_name)

    upload(args.outfile_path)

    logger.info("Done!")

    # DEBUGGING
    print("---script start---")
    print(args.infile_contents)
    print("---script end---")
    print(f"outfile name: {args.outfile_path}")
    print(f"program name: {args.program_name}")
