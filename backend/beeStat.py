# beeStatsEngine.py
#
# 2015 December 28
#
# This routine is the top-=level routine to periodically run each profile's stats and generate the corresponding output to the profile's log file.
# Input - none. This program uses the BEE_PATH argument passed to it by the calling script which specifies the directory in which to find the bee.ini profile list.
# Output - this program generates output to each profile's log file (i.e. bee_<profileName>.txt)
#
# This routine does the following:
# 1. steps through each active profile,
# 2. checks to see if the profile's (lastRunTime + frequency) is in the past and if so,
# runs generateOutput(profile) for the profile and updates the profile's lastRunTime.
# Once it steps through each profile, it then sleeps for a minute.

##########################
##########################
########## ON SECOND THOUGHT, THIS WON'T WORK BECAUSE IF WE KILL THE PROCESS,
########## THERE COULD BE A PROBLEM BECAUSE THIS PROCESS MAY BE PART-WAY THROUGH
########## WRITING THE bee.ini FILE AND THIS COULD LEAD TO CORRUPTION OF THE FILE.
########## INSTEAD, WE MIGHT BE BETTER OFF USING CRON TO PERIODICALLY EXECUTE A
########## MODIFIED VERSION OF THIS PROGRAM.
########## YET TO BE BUILT.


import sys
import json
import time
import datetime
import beeExchangeServices as es
import os
BEE_PATH = sys.argv[1] # This is passed in as input

def checkProfiles():
    # Steps through each profile.
    # For active profiles, checks to see if they should be run based on lastRunTime and frequency.
    # Requires no input.

    # Get the list of profiles
    with open(BEE_PATH + "/backend/beeProfileList.ini") as f:
        profileFileJSON = f.read()

    profileFile = json.loads(profileFileJSON)

    # Step through each profile
    for profile in profileFile:

        # skip any profile with a blank name, just in case there is one there.
        if profile["profileName"] == "":
            continue

        # skip the profile if it is not set to active.     
        if profile["active"] in ("false", "False", "no", "No"):
            continue 

        currentTime = datetime.datetime.now() # save the current time to later save into the profile's last run time
        currentTimeHR = currentTime.strftime('%Y-%m-%d %H:%M:%S') # strips milliseconds

        # check to see if we need to run the profile - based on lastRunTime + frequencyMins <= now 
        if inputTimeLTNow(profile["lastRunTime"],profile["frequencyMins"]) or (profile["lastRunTime"] == ""):
            # generate the stats
            es.generateOutput(profile["profileName"])

            # Save the current time to the profile.lastRunTime
            profile["lastRunTime"] = currentTimeHR
            es.updateProfile(json.dumps(profile))


def convertHRTimeToSeconds(inputHRTime):
    # Converts human-readable time into seconds.
    # INPUT - inputHRTime

    # Strip millisends from input HR time
    d = datetime.datetime.strptime(inputHRTime, "%Y-%m-%d %H:%M:%S")
    
    # Convert inputTime to seconds
    return time.mktime(d.timetuple())


def inputTimeLTNow(inputHRTime, inputTimeOffset):
    # Returns True if INPUT TIME + INPUT OFFSET <= NOW
    # INPUT:
    # - Human-readable time (typically taken from profile.lastRunTime
    # - Time offset in minutes (typically taken from profile.frequencyMins)

    # if inputHRTime is blank, then default to YES and return
    if inputHRTime == "":
        return True

    # Convert inputTime to seconds
    inputTimeSeconds = convertHRTimeToSeconds(inputHRTime)

    # Convert current time to seconds
    currentTime = datetime.datetime.now()
    currentTimeHR = currentTime.strftime('%Y-%m-%d %H:%M:%S') # strips milliseconds
    currentTimeSeconds = convertHRTimeToSeconds(currentTimeHR)

    # if inputTime + opffset is in the past (i.e we should run generateOutput), then return TRUE else returne FALSE
    if (inputTimeSeconds + (int(inputTimeOffset) * 60)) <= currentTimeSeconds:
        return True
    else:
        return False

    
    


## Main code loop. Leave if we dectect the 'stop' file placed in the bee folder.
while not os.path.exists(BEE_PATH + "/beeStatStop"):

    checkProfiles()  # check to log stats for each profile
    
    for i in range(1,6):  # 6 times ten second sleeps = one minute
        time.sleep (10) # sleep for ten seconds
        if os.path.exists(BEE_PATH + "/beeStatStop"):
            break

# Remove the file
os.remove(BEE_PATH + "/beeStatStop")
