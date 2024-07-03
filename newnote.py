#!/usr/bin/env python
import logging, util, os, re, signal, shutil, code
from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path

this_script_path     = Path(__file__).resolve()
this_script_dir      = this_script_path.parent.resolve()
this_script_filename = this_script_path.name
notes_dir_path       = Path("/Users/wtk/notes/").resolve()

def sigint_handler(signum, frame):
    logger = logging.getLogger(name=this_script_filename)
    logger.critical("Received SIGINT. Exiting")
    exit()
signal.signal(signal.SIGINT, sigint_handler)

def parse_args():
    desc_str = ("Creates a new numbered directory under /notes/ with the given name, containing a simple notes.txt file.\n\n")
    parser = ArgumentParser(formatter_class=RawTextHelpFormatter, description=desc_str)
    parser.add_argument("dirname", type=str, help="The name of the directory to create")
    parser.add_argument("--debug", action="store_true", help="If specified, log messages at DEBUG level and higher will be printed to the console")
    return parser.parse_args()

if (__name__ == "__main__"):
    args = parse_args()
    util.init_logging(console_level=(logging.DEBUG if args.debug else logging.INFO))
    logger = logging.getLogger(name=this_script_filename)

    # Get a list of the existing files and directories in /notes/
    try:
        notes_contents = os.listdir(path=notes_dir_path)
    except Exception as err:
        logger.error("A %s exception was raised while trying to list the contents of directory %s" % (type(err).__name__, notes_dir_path))
        exit(1)
    logger.debug("Contents of notes%s:\n %s" % (os.sep, str(notes_contents)))

    # Iterate through the list of notes_contents to find the highest numbered directory
    pattern = re.compile("^([0-9]+)_") # One or more digits at the start of a string followed by an underscore
    last_dir_num = -1
    for obj in notes_contents:
        matched = pattern.match(obj)

        # matched[1] corresponds to the first capture group
        if matched is not None and matched[1] is not None and int(matched[1]) > last_dir_num:
            last_dir_num = int(matched[1])

    if (last_dir_num == -1):
        logger.error("Failed to determine the last problem number. Exiting")
        exit(1)

    new_dir_name = "%d_%s" % (last_dir_num + 1, args.dirname)
    logger.info("Last problem number was %d. Creating new directory notes%s%s" % (last_dir_num, os.sep, new_dir_name))

    # Create the new directory
    new_dir_path = os.path.join(notes_dir_path, new_dir_name)
    try:
        os.mkdir(new_dir_path)
    except Exception as err:
        logger.error("A %s exception was raised while trying to create new directory %s" % (type(err).__name__, new_dir_path))
        exit(1)
    logger.debug("Created new directory %s" % new_dir_path)

    # Copy sample notes.txt file to new directory
    try:
        shutil.copyfile(os.path.join(this_script_dir, "notes.txt"), os.path.join(new_dir_path, "notes.txt"))
    except Exception as err:
        logger.error("A %s exception was raised while trying to copy notes.txt to new directory %s" % (type(err).__name__, new_dir_path))
        exit(1)
    logger.info("Copied notes.txt to new problem directory")

    if args.debug:
        code.interact(banner="\n", local=locals()) # Enter interactive Python interpreter
