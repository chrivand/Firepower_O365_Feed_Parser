# NOTE: this is a Proof of Concept script, please test before using in production!

# Copyright (c) 2019 Cisco and/or its affiliates.
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
import datetime
import time
import uuid
import webexteamssdk

# import supporting functions from additional file
from Firepower import Firepower

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
            "IP_BYPASS_UUID": "",
            "IP_DEFAULT_UUID": "",
            "URL_BYPASS_UUID": "",
            "URL_DEFAULT_UUID": "",
            "SERVICE_AREAS": "",
            "O365_PLAN": "",
            "SERVICE":  False,
            "SSL_VERIFY": False,
            "SSL_CERT": "/path/to/certificate",
            "AUTO_DEPLOY": False,
            "VERSION":  0,
            "WEBEX_ACCESS_TOKEN": "",
            "WEBEX_ROOM_ID": "",
            "PROXY": "",
            "PROXY_USER": "",
            "PROXY_PASSWD": "",
            "PROXY_HOST": "",
            "PROXY_PORT": "",
        }

# A function to store CONFIG_DATA to file
def saveConfig():

    sys.stdout.write("Saving config data...")
    sys.stdout.write("\n")

    with open(CONFIG_FILE, 'w') as output_file:
        json.dump(CONFIG_DATA, output_file, indent=4)

# A funtion to build the proxy config
def build_proxy():

    # If authentication required format with username and password. If not, start from host.
    if CONFIG_DATA['PROXY_USER'] != "":
        proxyHttp = 'http://' + CONFIG_DATA['PROXY_USER'] + ':' + CONFIG_DATA['PROXY_PASSWD'] + '@' + CONFIG_DATA['PROXY_HOST'] + ':' + CONFIG_DATA['PROXY_PORT']
        proxyHttps = 'https://' + CONFIG_DATA['PROXY_USER'] + ':' + CONFIG_DATA['PROXY_PASSWD'] + '@' + CONFIG_DATA['PROXY_HOST'] + ':' + CONFIG_DATA['PROXY_PORT']
    else:
        proxyHttp = 'http://' + CONFIG_DATA['PROXY_HOST'] + ':' + CONFIG_DATA['PROXY_PORT']
        proxyHttps = 'https://' + CONFIG_DATA['PROXY_HOST'] + ':' + CONFIG_DATA['PROXY_PORT']

    # Proxy setting to use in requests
    build_proxy.proxy = {
        proxyHttp,
        proxyHttps
    }

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

# Function that can be used to schedule the O365WebServiceParser to refresh at intervals. Caution: this creates an infinite loop.
# Takes the O365WebServiceParser function and the interval as parameters. 
def intervalScheduler(function, interval):

    # user feedback
    sys.stdout.write("\n")
    sys.stdout.write(f"O365 Web Service Parser will be refreshed every {interval} seconds. Please use ctrl-C to exit.\n")
    sys.stdout.write("\n")

    # interval loop, unless keyboard interrupt
    try:
        while True:
            function()
            # get current time, for user feedback
            date_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            sys.stdout.write("\n")
            sys.stdout.write(f"{date_time} O365 Web Service Parser executed by IntervalScheduler, current interval is {interval} seconds. Please use ctrl-C to exit.\n")
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

def check_for_new_version(clientRequestId):

    # Get the latest version of the loaded feed
    latestVersion = CONFIG_DATA['VERSION']

    # URL needed to check latest version
    webServiceVersionURL = "https://endpoints.office.com/version?clientrequestid="

    # assemble URL for get request for version 
    getURLVersion = webServiceVersionURL + clientRequestId

    # do GET request, using proxy if proxy is set
    if CONFIG_DATA['PROXY'] == True:
        reqVersion = requests.get(getURLVersion, proxies=build_proxy.proxy)
    else:
        reqVersion = requests.get(getURLVersion)

    # grab output in JSON format
    version = reqVersion.json()

    # loop through version list and grab Wordwide list version
    for element in version:
        if(element['instance'] == CONFIG_DATA['O365_PLAN']):
            newVersion = int(element['latest'])

    if latestVersion == 0:
        # user feedback
        sys.stdout.write(f"\nFirst time script runs, version of Office 365 {CONFIG_DATA['O365_PLAN']} commercial service instance endpoints detected: {newVersion}\n")
        # update version and save the config
        CONFIG_DATA['VERSION'] = newVersion
        saveConfig()
        return True
    else:
        # if the version did not change, the Web Service feed was not updated. 
        if(newVersion == latestVersion):

            # user feed back
            sys.stdout.write("\nWeb Service List has NOT been updated since the last load, no update needed!\n\n") 
            
            return False

        # check if there is a newer version 
        if(newVersion > latestVersion):

            # update version and save the config
            CONFIG_DATA['VERSION'] = newVersion
            saveConfig()

            # user feedback
            sys.stdout.write(f"\nNew version of Office 365 {CONFIG_DATA['O365_PLAN']} commercial service instance endpoints detected: {newVersion}\n")
            return True
    
# function to parse the Web Service, so that it can be called iteratively (e.g by the scheduler function)
def WebServiceParser():
    
    # create GUID for GET requests
    clientRequestId = str(uuid.uuid4())

    #check latest version
    bool_new_version = check_for_new_version(clientRequestId)

    if bool_new_version == True:
        # Instantiate a Firepower object
        fmc = Firepower(CONFIG_DATA)

        # If there's no defined Network Object, make one, then store the UUID - else, get the current object
        if CONFIG_DATA['IP_BYPASS_UUID'] == '':

            # Create the JSON to submit
            object_json = {
                'name': OBJECT_PREFIX + "O365_IPs_BYPASS_" + CONFIG_DATA['O365_PLAN'] + "_" + CONFIG_DATA['SERVICE_AREAS'].replace(',','_'),
                'type': 'NetworkGroup',
                'overridable': True,
            }

            print(object_json)

            # Create the Network Group object in the FMC
            ip_group_object = fmc.createObject('networkgroups', object_json)

            # Save the UUID of the object
            CONFIG_DATA['IP_BYPASS_UUID'] = ip_group_object['id']
            saveConfig()
        else:
            # Get the Network Group object of the specified UUID
            ip_group_object = fmc.getObject('networkgroups', CONFIG_DATA['IP_BYPASS_UUID'])

        # If there's no defined Default Network Object, make one, then store the UUID - else, get the current object
        if CONFIG_DATA["IP_DEFAULT_UUID"] == '':
            # Create the JSON to submit
            object_json = {
                'name': OBJECT_PREFIX + "O365_IPs_DEFAULT_" + CONFIG_DATA['O365_PLAN'] + "_" + CONFIG_DATA['SERVICE_AREAS'].replace(',','_'),
                'type': 'NetworkGroup',
                'overridable': True,
            }

            # Create the Network Group object in the FMC
            ip_default_group_object = fmc.createObject('networkgroups', object_json)

            # Save the UUID of the object
            CONFIG_DATA['IP_DEFAULT_UUID'] = ip_default_group_object['id']
            saveConfig()
        else:
            # Get the Network Group object of the specified UUID
            ip_default_group_object = fmc.getObject('networkgroups', CONFIG_DATA['IP_DEFAULT_UUID'])

        # If there's no defined URL Object, make one, then store the UUID
        if CONFIG_DATA['URL_BYPASS_UUID'] == '':

            # Create the JSON to submit
            object_json = {
                'name': OBJECT_PREFIX + "O365_URLs_BYPASS_" + CONFIG_DATA['O365_PLAN'] + "_" + CONFIG_DATA['SERVICE_AREAS'].replace(',','_'),
                'type': 'UrlGroup',
                'overridable': True,
            }

            # Create the URL Group object in the FMC
            url_group_object = fmc.createObject('urlgroups', object_json)

            # Save the UUID of the object
            CONFIG_DATA['URL_BYPASS_UUID'] = url_group_object['id']
            saveConfig()
        else:
            # Get the URL Group object of the specified UUID
            url_group_object = fmc.getObject('urlgroups', CONFIG_DATA['URL_BYPASS_UUID'])

        # If there's no defined Default URL Object, make one, then store the UUID
        if CONFIG_DATA['URL_DEFAULT_UUID'] == '':

            # Create the JSON to submit
            object_json = {
                'name': OBJECT_PREFIX + "O365_URLs_DEFAULT_" + CONFIG_DATA['O365_PLAN'] + "_" + CONFIG_DATA['SERVICE_AREAS'].replace(',','_'),
                'type': 'UrlGroup',
                'overridable': True,
            }

            # Create the URL Group object in the FMC
            url_default_group_object = fmc.createObject('urlgroups', object_json)

            # Save the UUID of the object
            CONFIG_DATA['URL_DEFAULT_UUID'] = url_default_group_object['id']
            saveConfig()
        else:
            # Get the URL Group object of the specified UUID
            url_default_group_object = fmc.getObject('urlgroups', CONFIG_DATA['URL_DEFAULT_UUID'])

        ### PARSE JSON FEED ###

        # create URL for requesting IP's and URL's
        if CONFIG_DATA['SERVICE_AREAS'] == 'All':
            web_service_url = f"https://endpoints.office.com/endpoints/{CONFIG_DATA['O365_PLAN']}?clientrequestid="
        else:
            web_service_url = f"https://endpoints.office.com/endpoints/{CONFIG_DATA['O365_PLAN']}?ServiceAreas={CONFIG_DATA['SERVICE_AREAS']}&clientrequestid="
            
        # assemble URL for get request
        getURL = web_service_url + clientRequestId

        # do GET request, using proxy if proxy is set
        if CONFIG_DATA['PROXY'] == True:
            req = requests.get(getURL, proxies=build_proxy.proxy)
        else:
            req = requests.get(getURL)

        # initiate lists to be filled with addresses
        URL_List = []
        URL_default_list = []
        IP_List = []
        IP_default_list = []

        # error handling if true then the request was HTTP 200, so successful 
        if(req.status_code == 200):

            # grab output in JSON format
            output = req.json()

            # iterate through each 'item' in the JSON data
            for item in output:

                # make sure URLs exist in the item
                if 'urls' in item and item['category'] != 'Default':
                    
                    # iterate through all URLs in each item
                    for url in item['urls']:

                        # remove asterisks to put URLs into Firepower format 
                        #   (https://www.cisco.com/c/en/us/support/docs/security/firesight-management-center/118852-technote-firesight-00.html#anc14)
                        url = url.replace('*','')

                        # if the URL hasn't already been appended, then append it
                        if url not in URL_List:
                            URL_List.append(url)
                # make sure URLs exist in the item
                elif 'urls' in item and item['category'] == 'Default':
                    
                    # iterate through all URLs in each item
                    for url in item['urls']:

                        url = url.replace('*','')

                        # if the URL hasn't already been appended, then append it
                        if url not in URL_List:
                            URL_default_list.append(url)


                # make sure IPs exist in the item
                if 'ips' in item and item['category'] != 'Default':

                    # iterate through all IPs in each item
                    for ip in item['ips']:

                        # if the IP hasn't already been appended, then append it
                        if ip not in IP_List:
                            IP_List.append(ip)
                # make sure IPs exist in the item
                elif 'ips' in item and item['category'] == 'Default':

                    # iterate through all IPs in each item
                    for ip in item['ips']:

                        # if the IP hasn't already been appended, then append it
                        if ip not in IP_List:
                            IP_default_list.append(ip)

        # Reset the fetched Network Group object to clear the 'literals'
        ip_group_object['literals'] = []
        ip_group_object.pop('links', None)

        # check whether list not empty (microsoft sometimes doesn't return IP's for default IP addresses for example)
        if not IP_List:
            IP_List.append("240.0.0.0/4")
            # user feed back
            sys.stdout.write("\n")
            sys.stdout.write("IP_BYPASS list returned no IP's, empty list with dummy IP range (240.0.0.0/4) created (to avoid policy deploy failure)...\n")
        
        # Add all the fetched IPs to the 'literals'of the Network Group object
        for ip_address in IP_List:
            ip_group_object['literals'].append({'type': 'Network', 'value': ip_address})

        # Update the NetworkGroup object
        fmc.updateObject('networkgroups', CONFIG_DATA['IP_BYPASS_UUID'], ip_group_object)



        # Reset the fetched DEFAULT Network Group object to clear the 'literals'
        ip_default_group_object['literals'] = []
        ip_default_group_object.pop('links', None)

        # check whether list not empty (microsoft sometimes doesn't return IP's for default IP addresses for example)
        if not IP_default_list:
            IP_default_list.append("240.0.0.0/4")
            # user feed back
            sys.stdout.write("\n")
            sys.stdout.write("IP_DEFAULT list returned no IP's, empty list with dummy IP range (240.0.0.0/4) created (to avoid policy deploy failure)...\n")
        
        # Add all the fetched IPs to the 'literals'of the Network Group object
        for ip_address in IP_default_list:
            ip_default_group_object['literals'].append({'type': 'Network', 'value': ip_address})

        # Update the NetworkGroup object
        fmc.updateObject('networkgroups', CONFIG_DATA['IP_DEFAULT_UUID'], ip_default_group_object)



        # Reset the fetched URL Group object to clear the 'literals'
        url_group_object['literals'] = []
        url_group_object.pop('links', None)

        # check whether list not empty
        if not URL_List:
            URL_List.append("example.com")
            # user feed back
            sys.stdout.write("\n")
            sys.stdout.write("URL_BYPASS list returned no URL's, empty list with dummy URL (example.com) created (to avoid policy deploy failure)...\n")
        
        # Add all the fetched URLs to the 'literals' of the URL Group object
        for url in URL_List:
            url_group_object['literals'].append({'type': 'Url', 'url': url})

        # Update the UrlGroup object
        fmc.updateObject('urlgroups', CONFIG_DATA['URL_BYPASS_UUID'], url_group_object)


        # Reset the fetched URL Group object to clear the 'literals'
        url_default_group_object['literals'] = []
        url_default_group_object.pop('links', None)

        
        # check whether list not empty
        if not URL_List:
            URL_List.append("example.com")
            # user feed back
            sys.stdout.write("\n")
            sys.stdout.write("URL_DEFAULT list returned no URL's, empty list with dummy URL (example.com) created (to avoid policy deploy failure)...\n")

        # Add all the fetched URLs to the 'literals' of the URL Group object
        for url in URL_default_list:
            url_default_group_object['literals'].append({'type': 'Url', 'url': url})

        # Update the UrlGroup object
        fmc.updateObject('urlgroups', CONFIG_DATA['URL_DEFAULT_UUID'], url_default_group_object)



        # user feed back
        sys.stdout.write("\n")
        sys.stdout.write(f"Web Service List has been successfully updated for the {CONFIG_DATA['O365_PLAN']} plan and {CONFIG_DATA['SERVICE_AREAS']} apps!\n")
        sys.stdout.write("\n")

        saveConfig()

        # If the user wants us to deploy policies, then do it
        if CONFIG_DATA['AUTO_DEPLOY']:
            DeployPolicies(fmc)
        
        # if Webex Teams tokens set, then send message to Webex room
        if CONFIG_DATA['WEBEX_ACCESS_TOKEN'] == '' or CONFIG_DATA['WEBEX_ROOM_ID'] == '':

            # user feed back
            sys.stdout.write("Webex Teams not set.\n")
            sys.stdout.write("\n")
        else:

            # adjust the Webex message based on the config
            if CONFIG_DATA['AUTO_DEPLOY']:
                message_text = f"Microsoft Office 365 objects have been successfully updated for the {CONFIG_DATA['O365_PLAN']} plan and {CONFIG_DATA['SERVICE_AREAS']} apps! Firepower policy deployment was initiated..."
            else:
                message_text = f"Microsoft Office 365 objects have been successfully updated for the {CONFIG_DATA['O365_PLAN']} plan and {CONFIG_DATA['SERVICE_AREAS']} apps! Firepower policy deployment is required."

            # instantiate the Webex handler with the access token
            #webex = ciscosparkapi.CiscoSparkAPI(CONFIG_DATA['WEBEX_ACCESS_TOKEN'])
            teams = webexteamssdk.WebexTeamsAPI(CONFIG_DATA['WEBEX_ACCESS_TOKEN'])

            # post a message to the specified Webex room
            message = teams.messages.create(CONFIG_DATA['WEBEX_ROOM_ID'], text=message_text)

    elif bool_new_version == False:
        # no new version, do nothing
        pass

##############END PARSE FUNCTION##############START EXECUTION SCRIPT##############

if __name__ == "__main__":

    # Load config data from file
    loadConfig()

    # If not hard coded, get the FMC IP, Username, and Password
    if CONFIG_DATA['FMC_IP'] == '':
        CONFIG_DATA['FMC_IP'] = input("FMC IP Address: ")
    if CONFIG_DATA['FMC_USER'] == '':
        CONFIG_DATA['FMC_USER'] = input("\nFMC Username: ")
    if CONFIG_DATA['FMC_PASS'] == '':
        CONFIG_DATA['FMC_PASS'] = getpass.getpass("\nFMC Password (NOTE: stored in plain text in config.json): ")
    # check with user which O365 service areas they are using
    if CONFIG_DATA['SERVICE_AREAS'] == '':  
        answer_input = (input("\nDo you use all O365 Service Areas / Applications (Exchange,SharePoint,Skype) [y/n]: ")).lower()
        if answer_input == "y":
            CONFIG_DATA['SERVICE_AREAS'] = 'All'
        elif answer_input == "n":
            service_areas = []
            if (input("\nDo you use Exchange Online [y/n]: ")).lower() == "y":
                service_areas.append("Exchange")
            if (input("\nDo you use SharePoint Online and OneDrive for Business [y/n]: ")).lower() == "y":
                service_areas.append("SharePoint")
            if (input("\nDo you use Skype for Business Online and Microsoft Teams [y/n]: ")).lower() == "y":
                service_areas.append("Skype")
            if (input("\nDo you use Microsoft 365 Common and Office Online [y/n]: ")).lower() == "y":
                service_areas.append("Common")
            CONFIG_DATA['SERVICE_AREAS'] = ",".join(service_areas)
    # check with user which O365 Plan they are using
    if CONFIG_DATA['O365_PLAN'] == '':
        if input("\nDo you use the default Worldwide O365 Plan (and not: Germany,USGovDoD,USGovGCCHigh,China) [y/n]: ") == "y":
            CONFIG_DATA['O365_PLAN'] = "Worldwide"
        else:
            if (input("\nDo you use the Germany O365 Plan [y/n]: ")).lower() == "y":
                CONFIG_DATA['O365_PLAN'] = "Germany"
            elif (input("\nDo you use the USGovDoD O365 Plan [y/n]: ")).lower() == "y":
                CONFIG_DATA['O365_PLAN'] = "USGovDoD"
            elif (input("\nDo you use the USGovGCCHigh O365 Plan [y/n]: ")).lower() == "y":
                CONFIG_DATA['O365_PLAN'] = "USGovGCCHigh"
            elif (input("\nDo you use the China O365 Plan [y/n]: ")).lower() == "y":
                CONFIG_DATA['O365_PLAN'] = "China"    
    # check with user if proxy is needed
    if CONFIG_DATA['PROXY'] == '':
        if input("\nDo you need to use a HTTP/HTTPS proxy to get to the internet [y/n]: ") == "y":
            CONFIG_DATA['PROXY'] = "true"
            if input("\nDoes the proxy require authentication [y/n]: ") == "y":
                CONFIG_DATA['PROXY_USER'] = input("\nProxy Username: ")
                CONFIG_DATA['PROXY_PASSWD'] = getpass.getpass("\nProxy password (NOTE: stored in plain text in config.json): ")
            CONFIG_DATA['PROXY_HOST'] = input("\nHostname or IP address of the proxy: ")
            CONFIG_DATA['PROXY_PORT'] = input("\nProxy server port number: ")
            # build the proxy dict used by requests
            build_proxy()
        else:
            CONFIG_DATA['PROXY'] = "false"

    sys.stdout.write(f"\nChosen O365 plan: {CONFIG_DATA['O365_PLAN']}, chosen applications: {CONFIG_DATA['SERVICE_AREAS']}\n")
    
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
        sys.stdout.write("\n\nExiting...\n\n")
        sys.stdout.flush()
        pass

# end of script
