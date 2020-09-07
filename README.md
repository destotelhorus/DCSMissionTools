# DCS-MissionTools

## Setup
`python3 -m venv ./venv`  
`source ./venv/bin/activate`  
`pip install -r requirements.txt`

## Run
`python DCSMissionTools.py --help`

## Help
```
usage: DCSMissionTools.py [-h] [-C] [-F1] [-v] missionfile [missionfile ...]

Assorted mission tools for digital combat simulator.

positional arguments:
  missionfile         mission file to work on

optional arguments:
  -h, --help          show this help message and exit
  -C, --compress-ids  Compresses the unit- and groupIds in the mission as to
                      avoid theirvalues growing too large
  -F1, --fix-eplrs    Fixes wrongful links to groups for EPLRS waypoint
                      settings. Will onlywork if used together with -C
  -v, --verbose       Give more feedback on what is being worked on
```

## What can it do
This toolbox can currently compress ids inside a mission. Meaning unit and group its will be put into as low regions as possible as to avoid certain problems and crashes with DCS.
However scripts that reference groups or units by ID will not be automatically rewritten!

If wished for, wrong EPLRS pointers can also be corrected again.