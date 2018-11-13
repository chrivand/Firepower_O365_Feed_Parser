# NOTE: this is a Proof of Concept script, please test before using in production!

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

import getpass
import json
import os
import requests
import sys
import time
import uuid
# import supporting functions from additional file
from Firepower import Firepower
from O365WebServiceFunctions import intervalScheduler

# Config Paramters
CONFIG_FILE     = "config.json"
CONFIG_DATA     = None

# Object Prefix
OBJECT_PREFIX = ""

# A function to load CONFIG_DATA from file
def loadConfig():

    global CONFIG_DATA

    sys.stdout.write("\n")
    sys.stdout.write("Loading config data...")
    sys.stdout.write("\n")

    # If we have a stored config file, then use it, otherwise create an empty one
    if os.path.isfile(CONFIG_FILE):

        # Open the CONFIG_FILE and load it
        with open(CONFIG_FILE, 'r') as config_file:
            CONFIG_DATA = json.loads(config_file.read())

        sys.stdout.write("Config loading complete.")
        sys.stdout.write("\n")
        sys.stdout.write("\n")

    else:

        sys.stdout.write("Config file not found, loading empty defaults...")
        sys.stdout.write("\n")
        sys.stdout.write("\n")

        # Set the CONFIG_DATA defaults
        CONFIG_DATA = {
            "FMC_IP": "",
            "FMC_USER": "",
            "FMC_PASS": "",
            "IP_UUID": "",
            "URL_UUID": "",
            "SERVICE":  False,
            "SSL_VERIFY": False,
            "SSL_CERT": "/path/to/certificate",
            "AUTO_DEPLOY": False,
            "VERSION":  0,
        }

# A function to store CONFIG_DATA to file
def saveConfig():

    sys.stdout.write("Saving config data...")
    sys.stdout.write("\n")

    with open(CONFIG_FILE, 'w') as output_file:
        json.dump(CONFIG_DATA, output_file, indent=4)

# A function to deploy pending policy pushes
def DeployPolicies(fmc):

    # Get pending deployments
    pending_deployments = fmc.getPendingDeployments()

    # Setup a dict to hold our deployments
    deployments = {}

    # See if there are pending deployments
    if pending_deployments['paging']['count'] > 0:

        # Iterate through pending deployments
        for item in pending_deployments['items']:

            # Only get ones that can be deployed
            if item['canBeDeployed']:

                # Only get ones that don't cause traffic interruption
                if item['trafficInterruption'] == "NO":

                    # If there are multiple devices, append them
                    if item['version'] in deployments:
                        device_list = deployments[item['version']]
                        device_list.append(item['device']['id'])
                        deployments[item['version']] = device_list
                    else:
                        deployments[item['version']] = [item['device']['id']]

        # Build JSON for each of our deployments
        for version, devices in deployments.items():

            deployment_json = {
                "type": "DeploymentRequest",
                "version": version,
                "forceDeploy": False,
                "ignoreWarning": True,
                "deviceList": devices,
            }

            fmc.postDeployments(deployment_json)

        sys.stdout.write("All pending deployments have been requested.\n")
    
    else:

        sys.stdout.write("There were zero pending deployments.\n")

# function to parse the Web Service, so that it can be called iteratively (e.g by the scheduler function)
def WebServiceParser():

    # Instantiate a Firepower object
    fmc = Firepower(CONFIG_DATA)

    # If there's no defined Network Object, make one, then store the UUID - else, get the current object
    if CONFIG_DATA['IP_UUID'] is '':

        # Create the JSON to submit
        object_json = {
            'name': OBJECT_PREFIX + 'O365_Web_Service_IPs',
            'type': 'NetworkGroup',
            'overridable': True,
        }

        # Create the Network Group object in the FMC
        ip_group_object = fmc.createObject('networkgroups', object_json)

        # Save the UUID of the object
        CONFIG_DATA['IP_UUID'] = ip_group_object['id']
        saveConfig()
    else:
        # Get the Network Group object of the specified UUID
        ip_group_object = fmc.getObject('networkgroups', CONFIG_DATA['IP_UUID'])

    # If there's no defined URL Object, make one, then store the UUID
    if CONFIG_DATA['URL_UUID'] is '':

        # Create the JSON to submit
        object_json = {
            'name': OBJECT_PREFIX + 'O365_Web_Service_URLs',
            'type': 'UrlGroup',
            'overridable': True,
        }

        # Create the URL Group object in the FMC
        url_group_object = fmc.createObject('urlgroups', object_json)

        # Save the UUID of the object
        CONFIG_DATA['URL_UUID'] = url_group_object['id']
        saveConfig()
    else:
        # Get the URL Group object of the specified UUID
        url_group_object = fmc.getObject('urlgroups', CONFIG_DATA['URL_UUID'])

    # Get the latest version of the loaded feed
    latestVersion = CONFIG_DATA['VERSION']

    # create GUID for GET requests
    clientRequestId = str(uuid.uuid4())

    # URL needed to check latest version
    webServiceVersionURL = "https://endpoints.office.com/version?clientrequestid="

    # assemble URL for get request for version 
    getURLVersion = webServiceVersionURL + clientRequestId

    # do GET request 
    reqVersion = requests.get(getURLVersion)

    # grab output in JSON format
    version = reqVersion.json()

    # loop through version list and grab Wordwide list version
    for element in version:
        if(element['instance'] == 'Worldwide'):
            newVersion = int(element['latest'])

    # if the version did not change, the Web Service feed was not updated. 
    if(newVersion == latestVersion):

        # user feed back
        sys.stdout.write("\n")
        sys.stdout.write("Web Service List has NOT been updated since the last load, no update needed!\n") 
        sys.stdout.write("\n")

    # check if there is a newer version 
    if(newVersion > latestVersion):

        # update version and save the config
        CONFIG_DATA['VERSION'] = newVersion

        # user feedback
        sys.stdout.write("\n")
        sys.stdout.write("New version of Office 365 worldwide commercial service instance endpoints detected: %(version)s" % {'version': CONFIG_DATA['VERSION']})
        sys.stdout.write("\n")

        ### PARSE JSON FEED ###

        # URL needed for the worldwide web service feed
        webServiceURL = "https://endpoints.office.com/endpoints/worldwide?clientrequestid="

        # assemble URL for get request
        getURL = webServiceURL + clientRequestId

        # do GET request 
        req = requests.get(getURL)  

        # initiate lists to be filled with addresses
        URL_List = []
        IP_List = []

        # error handling if true then the request was HTTP 200, so successful 
        if(req.status_code == 200):

            # grab output in JSON format
            output = req.json()

            # iterate through each 'item' in the JSON data
            for item in output:

                # make sure URLs exist in the item
                if 'urls' in item:
                    
                    # iterate through all URLs in each item
                    for url in item['urls']:

                        # remove asterisks to put URLs into Firepower format 
                        #   (https://www.cisco.com/c/en/us/support/docs/security/firesight-management-center/118852-technote-firesight-00.html#anc14)
                        url = url.replace('*','')

                        # if the URL hasn't already been appended, then append it
                        if url not in URL_List:
                            URL_List.append(url)

                # make sure IPs exist in the item
                if 'ips' in item:

                    # iterate through all IPs in each item
                    for ip in item['ips']:

                        # if the IP hasn't already been appended, then append it
                        if ip not in IP_List:
                            IP_List.append(ip)

        # Reset the fetched Network Group object to clear the 'literals'
        ip_group_object['literals'] = []
        ip_group_object.pop('links', None)

        # Add all the fetched IPs to the 'literals'of the Network Group object
        for ip_address in IP_List:
            ip_group_object['literals'].append({'type': 'Network', 'value': ip_address})

        # Update the NetworkGroup object
        fmc.updateObject('networkgroups', CONFIG_DATA['IP_UUID'], ip_group_object)

        # Reset the fetched URL Group object to clear the 'literals'
        url_group_object['literals'] = []
        url_group_object.pop('links', None)

        # Add all the fetched URLs to the 'literals' of the URL Group object
        for url in URL_List:
            url_group_object['literals'].append({'type': 'Url', 'url': url})

        # Update the UrlGroup object
        fmc.updateObject('urlgroups', CONFIG_DATA['URL_UUID'], url_group_object)

        # user feed back
        sys.stdout.write("\n")
        sys.stdout.write("Web Service List has been successfully updated!\n") 
        sys.stdout.write("\n")

        saveConfig()

        # If the user wants us to deploy policies, then do it
        if CONFIG_DATA['AUTO_DEPLOY']:
            DeployPolicies(fmc)

##############END PARSE FUNCTION##############START EXECUTION SCRIPT##############

if __name__ == "__main__":

    # Load config data from file
    loadConfig()

    # If not hard coded, get the FMC IP, Username, and Password
    if CONFIG_DATA['FMC_IP'] is '':
        CONFIG_DATA['FMC_IP'] = input("FMC IP Address: ")
    if CONFIG_DATA['FMC_USER'] is '':
        CONFIG_DATA['FMC_USER'] = input("FMC Username: ")
    if CONFIG_DATA['FMC_PASS'] is '':
        CONFIG_DATA['FMC_PASS'] = getpass.getpass("FMC Password: ")

    # Save the FMC data
    saveConfig()

    try:
        if CONFIG_DATA['SERVICE']:
            # Calls the intervalScheduler for automatic refreshing (pass O365WebServiceParser function and interval in seconds (1 hour = 3600 seconds))
            intervalScheduler(WebServiceParser, 3600) #set to 1 hour
        else:
            # Execute O365WebServiceParser just once
            WebServiceParser()

    except (KeyboardInterrupt, SystemExit):
        sys.stdout.write("\n")
        sys.stdout.write("\n")
        sys.stdout.write("Exiting...\n")
        sys.stdout.write("\n")
        sys.stdout.flush()
        pass

# end of script
