# MODULE FOR SUPPORTING FUNCTIONS FOR O365WebServiceParser

# Copyright (c) 2018 Cisco and/or its affiliates.
# This software is licensed to you under the terms of the Cisco Sample
# Code License, Version 1.0 (the "License"). You may obtain a copy of the
# License at
#                https://developer.cisco.com/docs/licenses
# All use of the material herein must be in accordance with the terms of
# the License. All rights not expressly granted by the License are
# reserved. Unless required by applicable law or agreed to separately in
# writing, software distributed under the License is distributed on an "AS
# IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied.

# import libraries
import datetime
import sys
import time

# NOTE migrated this function to other main file (O365WebServiceParser), this python file redundant 

# Function that can be used to schedule the O365WebServiceParser to refresh at intervals. Caution: this creates an infinite loop.
# Takes the O365WebServiceParser function and the interval as parameters. 
def intervalScheduler(function, interval):

    # user feedback
    sys.stdout.write("\n")
    sys.stdout.write("O365 Web Service Parser will be refreshed every %d seconds. Please use ctrl-C to exit.\n" %interval)
    sys.stdout.write("\n")

    # interval loop, unless keyboard interrupt
    try:
        while True:
            function()
            # get current time, for user feedback
            date_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            sys.stdout.write("\n")
            sys.stdout.write("[%s] O365 Web Service Parser executed by IntervalScheduler, current interval is %d seconds. Please use ctrl-C to exit.\n" % (date_time, interval))
            sys.stdout.write("\n")
            # sleep for X amount of seconds and then run again. Caution: this creates an infinite loop to check the Web Service Feed for changes
            time.sleep(interval)

    # handle keyboard interrupt
    except (KeyboardInterrupt, SystemExit):
        sys.stdout.write("\n")
        sys.stdout.write("\n")
        sys.stdout.write("Exiting... O365 Web Service Parser will not be automatically refreshed anymore.\n")
        sys.stdout.write("\n")
        sys.stdout.flush()
        pass

# end of script
