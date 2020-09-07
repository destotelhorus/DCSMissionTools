import os
from shutil import copyfile
from MIZFile import MIZFile
import argparse

parser = argparse.ArgumentParser(description='Assorted mission tools for digital combat simulator.')
parser.add_argument('missionfile', help='mission file to work on', nargs='+')
parser.add_argument('-C', '--compress-ids', help='Compresses the unit- and groupIds in the mission as to avoid their '
                                                 'values growing too large',
                    action='store_true', required=False)
parser.add_argument('-F1', '--fix-eplrs', help='Fixes wrongful links to groups for EPLRS waypoint settings. Will only '
                                               'work if used together with -C',
                              action='store_true', required=False)

parser.add_argument('-v', '--verbose', help='Give more feedback on what is being worked on',
                    action='store_true', required=False)

args = parser.parse_args()

def printv(obj):
    if args.verbose:
        print(obj)

def compressIds(mission):
    unitids = dict()
    groupids = dict()
    unitIndex = 1
    groupIndex = 1
    print("compressing ids!")
    print("beginning analysis")
    for coalition_idx, coalition in mission["coalition"].items():
        printv("analysing coalition: {}".format(coalition_idx))
        for country_idx, country in coalition["country"].items():
            printv("analysing country: {}".format(country["name"]))
            for unittype in ["helicopter", "ship", "plane", "vehicle", "static"]:
                printv("analysing unittype: {}".format(unittype))
                if not unittype in country:
                    printv("unittype-key {} not found".format(unittype))
                    continue
                for group_idx, group in country[unittype]["group"].items():
                    unitsingroup = []

                    printv("analysing group {}".format(group["groupId"]))
                    groupids[group["groupId"]] = groupIndex
                    groupIndex += 1
                    for unit_idx, unit in group["units"].items():
                        printv("analysing unit {}".format(unit["unitId"]))
                        unitids[unit["unitId"]] = unitIndex
                        unitIndex += 1
                        unitsingroup.append(unit["unitId"])

                    for point_idx, point in group["route"]["points"].items():
                        if not "task" in point:
                            continue
                        for task_idx, task in point["task"]["params"]["tasks"].items():
                            if task["id"] == 'WrappedAction':
                                if "params" in task:
                                    if "action" in task["params"]:
                                        if task["params"]["action"]["id"] == 'ActivateICLS':
                                            if not task["params"]["action"]["params"]["unitId"] in unitsingroup:
                                                print("group {0} has ActivateICLS task for unit {1} not part of group".format(group["groupId"], task["params"]["action"]["params"]["unitId"]))
                                        if task["params"]["action"]["id"] == 'ActivateBeacon':
                                            if not task["params"]["action"]["params"]["unitId"] in unitsingroup:
                                                print("group {0} has ActivateICLS task for unit {1} not part of group".format(group["groupId"], task["params"]["action"]["params"]["unitId"]))
                                        if task["params"]["action"]["id"] == 'EPLRS':
                                            if not group["groupId"] == task["params"]["action"]["params"]["groupId"]:
                                                print("group {0} has EPLRS task for group {1} which is a foreign group".format(group["groupId"], task["params"]["action"]["params"]["groupId"]))
    print("beginning changes")
    for coalition_idx, coalition in mission["coalition"].items():
        printv("applying changes to coalition: {}".format(coalition_idx))
        for country_idx, country in coalition["country"].items():
            printv("applying changes to country: {}".format(country["name"]))
            for unittype in ["helicopter", "ship", "plane", "vehicle", "static"]:
                printv("applying changes to unittype: {}".format(unittype))
                if not unittype in country:
                    printv("unittype-key {} not found".format(unittype))
                    continue
                for group_idx, group in country[unittype]["group"].items():
                    unitsingroup = []
                    printv("applying changes to group {}".format(group["groupId"]))

                    for unit_idx, unit in group["units"].items():
                        printv("applying changes to unit {}".format(unit["unitId"]))
                        unitsingroup.append(unit["unitId"])

                        if not unit["unitId"] == unitids[unit["unitId"]]:
                            print("unit with id {0} will be rewritten as {1}".format(
                                unit["unitId"],
                                unitids[unit["unitId"]]
                            ))
                            unit["unitId"] = unitids[unit["unitId"]]

                    for point_idx, point in group["route"]["points"].items():
                        if not "task" in point:
                            continue
                        for task_idx, task in point["task"]["params"]["tasks"].items():
                            if task["id"] == 'WrappedAction':
                                if not "params" in task:
                                    continue
                                if not "action" in task["params"]:
                                    continue
                                if task["params"]["action"]["id"] == 'ActivateICLS':
                                    rewriteTaskUnitId(group, task, unitids, unitsingroup)
                                if task["params"]["action"]["id"] == 'ActivateBeacon':
                                    rewriteTaskUnitId(group, task, unitids, unitsingroup)
                                if task["params"]["action"]["id"] == 'EPLRS':
                                    rewriteTaskGroupId(group, task, groupids)

                    if not group["groupId"] == groupids[group["groupId"]]:
                        print("group with id {0} will be rewritten as {1}".format(
                            group["groupId"],
                            groupids[group["groupId"]]
                        ))
                        group["groupId"] = groupids[group["groupId"]]

def rewriteTaskGroupId(group, task, groupids):
    if not group["groupId"] == task["params"]["action"]["params"]["groupId"]:
        if args.fix_eplrs:
            print("FIXING: group {1} {0} task will be pointed at this groups new id {2}".format(
                task["params"]["action"]["id"],
                group["groupId"],
                groupids[group["groupId"]]
            ))
            task["params"]["action"]["params"]["groupId"] = groupids[group["groupId"]]
        elif task["params"]["action"]["params"]["groupId"] in groupids and not task["params"]["action"]["params"]["groupId"] == groupids[task["params"]["action"]["params"]["groupId"]]:
            print("group {1} has {0} task for group {2} which is a foreign group will be pointed at new id {3}".format(
                task["params"]["action"]["id"],
                group["groupId"],
                task["params"]["action"]["params"]["groupId"],
                groupids[task["params"]["action"]["params"]["groupId"]]
            ))
            task["params"]["action"]["params"]["groupId"] = groupids[task["params"]["action"]["params"]["groupId"]]
        else:
            print("group {1} has {0} task for group {2} which is a foreign group, could not find target to redirect. "
                  "Won't change the value".format(
                task["params"]["action"]["id"],
                group["groupId"],
                task["params"]["action"]["params"]["groupId"]
            ))
    elif not task["params"]["action"]["params"]["groupId"] == groupids[task["params"]["action"]["params"]["groupId"]]:
        print("group {1} {0} task will be pointed to new group id {2} of previously connected group".format(
            task["params"]["action"]["id"],
            group["groupId"],
            groupids[group["groupId"]]
        ))
        task["params"]["action"]["params"]["groupId"] = groupids[task["params"]["action"]["params"]["groupId"]]

def rewriteTaskUnitId(group, task, unitids, unitsingroup):
    if not task["params"]["action"]["params"]["unitId"] in unitsingroup:
        if args.fix_eplrs:
            print("group {1} {0} task for unit {2} will be pointed at first unit in group".format(
                task["params"]["action"]["id"],
                group["groupId"],
                task["params"]["action"]["params"]["unitId"]
            ))
            task["params"]["action"]["params"]["unitId"] = unitids[group["units"][0]["unitId"]]
        elif task["params"]["action"]["params"]["unitId"] in unitids and not task["params"]["action"]["params"]["unitId"] == unitids[task["params"]["action"]["params"]["unitId"]]:
            print("group {1} {0} task for unit {2} will be pointed at new id {3} for that foreign unit".format(
                task["params"]["action"]["id"],
                group["groupId"],
                task["params"]["action"]["params"]["unitId"],
                unitids[task["params"]["action"]["params"]["unitId"]]
           ))
            task["params"]["action"]["params"]["unitId"] = unitids[task["params"]["action"]["params"]["unitId"]]
        else:
            print("group {1} {0} task for unit {2} could not find target to redirect. Won't change the value".format(
                task["params"]["action"]["id"],
                group["groupId"],
                task["params"]["action"]["params"]["unitId"]
            ))
    elif not task["params"]["action"]["params"]["unitId"] == unitids[task["params"]["action"]["params"]["unitId"]]:
        print("group {1} {0} task for unit {2} will be pointed to new unit id {3} of previously connected unit".format(
            task["params"]["action"]["id"],
            group["groupId"],
            task["params"]["action"]["params"]["unitId"],
            unitids[task["params"]["action"]["params"]["unitId"]]
        ))
        task["params"]["action"]["params"]["unitId"] = unitids[task["params"]["action"]["params"]["unitId"]]

if __name__ == '__main__':
    for missionfile in args.missionfile:
        MIZ = MIZFile(missionfile, False)
        print("Opening mission {}".format(missionfile))
        mission = MIZ.getMission()

        if args.compress_ids:
            compressIds(mission)

        print("Committing changes to mission {}".format(missionfile))
        MIZ.setMission(mission)
        MIZ.commit()
    print("done")