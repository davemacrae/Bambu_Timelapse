# Bambu_Timelapse

Python scripts to create a timelapse video from a set of images captured 
during printing

## Requirements

* Python 3.6.*
* ffmpeg (<https://github.com/FFmpeg/FFmpeg>)

## Install

```bash
Clone the repo
```

## Usage
```bash
usage: bambu.py [-h] [--debug] [--base BASE] [--output OUTPUT]
                [--resolution RESOLUTION] [--codec CODEC]

Bambu Timelapse video generator

options:
  -h, --help            show this help message and exit
  --debug               Enable debug output
  --base BASE           Base directory for timelapse images
  --output OUTPUT       Output directory for timelapse videos
  --duration DURATION   Time snapshot is shown
  --resolution RESOLUTION
                        Resolution of timelapse videos
  --codec CODEC         Video codec to use (e.g., x265, x264)
```

## Home Assistant

This suite relies on you setting up Home Assistant to generate the snapshot files that will be included in the Timelapse video. It __does not__ use the native timelapse function of the printer.

The printer is integrated into HA via the [ha-bambulab](https://github.com/greghesp/ha-bambulab) HACS integration.

I use the [Advanced Snapshot](https://github.com/Phil7989/advanced_snapshot) HACS integration to generate the snapshots but it should be possible to just use the generic camera.snapshot facility.

The snapshots are stored in a directory on my NAS that is accessible both from HA and my server where I run the actual script. The directory is named after the model being printed. At the end of the print job, when the printer state shifts to "idle", the automation calls a shell command to use ssh to invoke the script.

I have included a sample snippet from automations.yaml and shell_command.yaml.
