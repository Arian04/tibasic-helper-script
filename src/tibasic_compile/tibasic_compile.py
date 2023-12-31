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

    def add_upload_method_arg(parser):
        parser.add_argument(
            "-m",
            "--upload-method",
            required=True,  # I know an option (-f, --foo) shouldn't be required but it looks ugly otherwise
            dest="upload_method",
            choices=["tilp", "cemu"],
            help="Method used to upload the program",
        )

    parser_build = subparsers.add_parser("build", help="create 8xp file from given source code")
    add_infile_arg(parser_build)
    add_outfile_arg(parser_build)
    add_program_name_arg(parser_build)
    add_processing_bool_arg(parser_build)

    parser_upload = subparsers.add_parser("upload", help="upload 8xp file to calculator")
    add_outfile_arg(parser_upload)
    add_upload_method_arg(parser_upload)

    # same args as build
    parser_install = subparsers.add_parser("install", help="builds and uploads the program")
    add_infile_arg(parser_install)
    add_outfile_arg(parser_install)
    add_program_name_arg(parser_install)
    add_upload_method_arg(parser_install)
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
# - strips out any leading whitespace
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
                i -= 1  # Go back to the char before newline, so the next iteration doesn't skip it

    # Multiline string containing source code (with comments stripped out)
    processed = "".join(processed)

    # Strip leading whitespace on each line + remove line if it's only whitespace
    # It would be better for performance to do this in the above loop but idrc tbh
    temp = ""
    for line in processed.splitlines():
        if not line or line.isspace():
            continue  # Don't add line if it's empty or just whitespace
        temp += line.lstrip() + "\n"  # append l-strip'd line
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
def upload(output_file_path, method) -> None:
    logger.info("Uploading %s", output_file_path)

    stdout = None
    stderr = None
    args = None
    return_code = None
    if method == "tilp":
        model = "ti84+ce"
        cable_type = "directlink"
        proc = subprocess.run(
            ["tilp", "--no-gui", "--silent", model, cable_type, output_file_path],
            check=False,
            capture_output=True,
            timeout=5,
            encoding="utf-8",
        )
        stdout = proc.stdout
        stderr = proc.stderr
        args = proc.args
        return_code = proc.returncode

        # Clean up stderr because it's in an annoying format
        if stderr != "":
            # Trim some empty space
            stderr = re.sub(
                r"\n+", "\n", stderr  # Turn >1 consecutive newlines into 1
            ).strip()  # then strip leading and trailing whitespace

            # Logs look like, for example: (tilp:244637): ticables-WARNING **: 02:40:00.344:  no devices found!
            # TODO: try to trim out that extra garbage before the actual error

            # Remove consecutive duplicate lines (because it prints errors multiple times for some reason)
            temp = ""
            previous_line = None
            for current_line in stderr.splitlines():
                if current_line != previous_line:
                    temp += current_line + "\n"

                previous_line = current_line
            temp = temp[:-1]  # trim extra newline added on final iteration
            stderr = temp

    elif method == "cemu":
        proc = subprocess.run(
            ["CEmu", "--no-reset", "--send", output_file_path],
            check=False,
            capture_output=True,
            timeout=5,
            encoding="utf-8",
        )
        stdout = proc.stdout
        stderr = proc.stderr
        args = proc.args
        return_code = proc.returncode

    logger.debug("upload process stdout: %s", stdout)

    # Handle errors
    if stderr != "":
        logger.critical("Failed to upload file: %s", stderr)
        sys.exit(1)
    elif return_code != 0:
        if args is None:
            logger.critical("Failed to access process arguments")
            logger.critical("'%s' exited with exit status %s", method, return_code)
        else:
            logger.critical("'%s' exited with exit status %s", " ".join(args), return_code)
        sys.exit(1)

    logger.info("Upload completed")


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

    input_file_contents = None
    if should_build:
        if args.should_process:
            input_file_contents = preprocess(args.infile_contents)
        else:
            input_file_contents = args.infile_contents

        build(input_file_contents, args.outfile_path, args.program_name)
    if should_upload:
        upload(args.outfile_path, args.upload_method)

    logger.info("Done!")

    # DEBUGGING
    if should_build:
        logger.debug("---original script---")
        logger.debug("\n" + args.infile_contents)
        logger.debug("---------")

        if input_file_contents is not None:
            logger.debug("---processed script---")
            logger.debug("\n" + input_file_contents)
            logger.debug("---------")

        logger.debug(f"program name: {args.program_name}")

    logger.debug(f"outfile name: {args.outfile_path}")


if __name__ == "__main__":
    main()
