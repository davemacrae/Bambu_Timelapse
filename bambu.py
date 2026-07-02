#!/usr/bin/env python
"""
Module: bambu
Description: This module gathers image files for printing a specific 3D Model
             and generates a timelapse video script. It then runs ffmpeg to create the video.

    DONE: Compress and remove original images after processing.
    TODO: add checking of supplied codec against available codecs in ffmpeg
          to avoid errors.

"""

from datetime import datetime
import subprocess
import shlex
from pathlib import Path
import argparse
from os import remove

# the directory containing the snapshots to process
# this can (and probably should) be overriden by the --base option
BASE = "/backup/homeassistant/media/snapshots/bambu/"

# The default output directory, can be overriden by the --out option.
OUTPUT = "/home/dave/Videos/Timelapse"

# The defualt resolution of the output video
RESOLUTION = "1280"


def arg_parser() -> argparse.Namespace:
    """
    Process the command line arguments
        :return: Parsed arguments namespace
    """

    parser = argparse.ArgumentParser(description="Bambu Timelapse video generator")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    parser.add_argument(
        "--base", type=str, help="Base directory for timelapse images", default=BASE
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output directory for timelapse videos",
        default=OUTPUT,
    )
    parser.add_argument(
        "--resolution",
        type=str,
        help="Resolution of timelapse videos",
        default=RESOLUTION,
    )
    parser.add_argument(
        "--codec",
        type=str,
        help="Video codec to use (e.g., x265, x264)",
        default="x265",
    )
    parser.add_argument(
        "--duration", type=float, help="Time snapshot is shown", default=0.25
    )
    parser.add_argument(
        "--keep", action="store_true", help="Keep original image files after processing"
    )

    args = parser.parse_args()
    if args.debug:
        print(f"Arguments: {args}")
    return args


def gather_files() -> list:
    """
    Gather files from the specified directory for timelapse processing.
    :return: List of file paths to include in the timelapse
    """
    # Calculate the time of Dusk and Dawn for date_time

    file_list = []

    dir_path = args.base
    f = Path(dir_path)
    glob_path = "*.jpg"
    glob = f.glob(glob_path)

    # make sure we are not including any empty files.
    for i in glob:
        if i.stat().st_size > 0:
            file_list.append(f"{i.parent}/{i.name}")

    return sorted(file_list)


def gen_video(file_list: list, duration: float) -> None:
    """
    Generate a script to process the gathered files into a timelapse
    video and then use ffmpeg to create the video.
        :param file_list: List of file paths to include in the timelapse
        :param duration: Duration in seconds for each image in the timelapse
        :return: None
    """

    out = Path(args.base).name
    output_dir = args.output + "/" + out
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    date_time = datetime.now()
    timestamp = date_time.strftime("%Y-%m-%d %H-%M")

    """
      As the output is based on the model name, ensure that we timestamp the
      output to allow for tracking of multiple prints.
    """
    out_file = output_dir + "/" + timestamp + "-" + out + f"-{args.codec}.mp4"

    """
      Create the script that will be used by ffmpeg to create the timelapse
      video.
    """
    script_name = f"{out}.script"
    with open(script_name, "w") as script_file:
        for file in file_list:
            script_file.write(f"file '{file}'\n")
            script_file.write(f"duration {duration}\n")

    script = f"ffmpeg -hide_banner -loglevel error -y \
                      -f concat -safe 0 \
                      -i \"{script_name}\" \
                      -fps_mode vfr \
                      -c:v lib{args.codec} \
                      -pix_fmt yuv420p \
                      -{args.codec}-params log-level=quiet \
                      -vf \"scale='min({args.resolution}, iw)':-1\" \
                      '{out_file}'"
    if args.debug:
        print(script)
    ffmpeg = shlex.split(script)
    try:
        p = subprocess.Popen(ffmpeg, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        p.wait()
    except Exception as e:
        print(f"Error executing command: {e}")
        remove(script_name) if script_name and Path(script_name).exists() else None
        remove(out_file) if Path(out_file).exists() else None
        return
    if p.returncode != 0:
        print(f"Command {p.args} exited with {p.returncode} code, output: \n{p.stdout}")
        remove(script_name) if script_name and Path(script_name).exists() else None
        remove(out_file) if Path(out_file).exists() else None
        return

    # Tidy up script file
    script_file.close()
    remove(script_name)
    if not args.keep:
        delete_files(file_list)


def delete_files(file_list: list) -> None:
    """
    Delete the original image files after processing to save space.
    :param file_list: List of file paths to delete
    :return: None
    """
    for file in file_list:
        try:
            remove(file)
        except Exception as e:
            print(f"Error deleting file {file}: {e}")

    try:
        Path(args.base).rmdir()
    except Exception as e:
        print(f"Error removing directory {Path(args.base)}: {e}")


def main() -> None:
    """Main function to gather files and generate timelapse videos."""

    files = gather_files()
    if files:
        gen_video(files, args.duration)
    else:
        if args.debug:
            print("No files found.")


if __name__ == "__main__":

    script_name = ""  # need this to be global so we can zap it on error
    args = arg_parser()
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
        remove(script_name) if script_name and Path(script_name).exists() else None
