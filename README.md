# DCS-MissionTools

## Setup
`python3 -m venv ./venv`  
`source ./venv/bin/activate`  
`pip install -r requirements.txt`

## Run
`python DCSMissionTools.py --help`

## Help
```
usage: DCSMissionTools.py [-h] [-D [DUMP_MISSION]] [-C] [-F1] [-v]
                          missionfile [missionfile ...]

Assorted mission tools for digital combat simulator.

positional arguments:
  missionfile           mission file to work on

optional arguments:
  -h, --help            show this help message and exit
  -D [DUMP_MISSION], --dump-mission [DUMP_MISSION]
                        Dumps the mission LUA of the first missionfile out to
                        the specified file, or use "-" for STDOUT. This will
                        prevent any other action from being taken!
  -C, --compress-ids    Compresses the unit- and groupIds in the mission as to
                        avoid their values growing too large
  -F1, --fix-eplrs      Fixes incorrect links to groups for EPLRS waypoint
                        settings. Will only work if used together with -C
  -v, --verbose         Give more feedback on what is being worked on

```

## What can it do
This toolbox can currently compress ids inside a mission. Meaning unit and group its will be put into as low regions as possible as to avoid certain problems and crashes with DCS.
However scripts that reference groups or units by ID will not be automatically rewritten!

If wished for, wrong EPLRS pointers can also be corrected again. **(Warning: This seems highly experimental and not necessary or actually useful!)**

The tool can also easily dump a mission as LUA file from inside the MIZ, savind just a few seconds of doing it manually.