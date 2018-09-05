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

import json
import os
import requests
import uuid
import time
import sys
# import supporting functions from additional file
from O365WebServiceFunctions import APIcaller, intervalScheduler



# function to parse the Web Service, so that it can be called iteratively (e.g by the scheduler function)
def WebServiceParser():     

    ### CHECK FOR LATEST VERSION ###
    # open txt file with latest version and set variable to last version (if no file exists, initiate latestVersion to zero)
    # if you want to force an update delete the latestVersion.txt from the same directory as Pyhton file is in
    try:
        # open file and read in previous latest version
        with open('latestVersion.txt', 'r') as latestVersion_File:
            latestVersion_File_Content = latestVersion_File.readlines()
            latestVersion = int(latestVersion_File_Content[0])
            
        # user feedback
        sys.stdout.write("\n")
        sys.stdout.write("Latest version is: %(version)s" % {'version': latestVersion})
        sys.stdout.write("\n")

    # error handling if file not found
    except FileNotFoundError:
        # initiate latestVersion to 0
        latestVersion = 0
        
        # user feedback
        sys.stdout.write("\n")
        sys.stdout.write("No file found with previous latest version, initiating to zero...")
        sys.stdout.write("\n")        

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

    # if the MD5 did not change, the Web Service feed was not updated. 
    if(newVersion == latestVersion):
        # user feed back
        sys.stdout.write("\n")
        sys.stdout.write("Web Service List has NOT been updated, no API calls needed!\n") 
        sys.stdout.write("\n")

    # check if there is a newer version 
    if(newVersion > latestVersion):

        # update version and write to txt file
        latestVersion = newVersion
        with open('latestVersion.txt', 'w') as latestVersion_File:
            latestVersion_File.write(str(latestVersion))

        # user feedback
        sys.stdout.write("\n")
        sys.stdout.write("New version of Office 365 worldwide commercial service instance endpoints detected: %(version)s" % {'version': latestVersion})
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
        URL_List_Flat = []
        IP_List_Flat = []

        # error handling if true then the request was HTTP 200, so successful 
        if(req.status_code == 200):
            # grab output in JSON format
            output = req.json()

            # loop through JSON and put all URLs in list
            for URL in output:
                urls = URL['urls'] if 'urls' in URL else []
                URL_List.append(urls)
            
            # loop through JSON and put all IPs in list
            for IP in output:
                ips = IP['ips'] if 'ips' in IP else []
                IP_List.append(ips)

        # take out sub lists to upload to have list in right format to send to FMC
        for sublist in URL_List:
            for item in sublist:
                URL_List_Flat.append(item)

        for sublist in IP_List:
            for item in sublist:
                IP_List_Flat.append(item)

        # API call for URL list (user feedback is provided from the APIcaller function)
        object_id_url = "<INPUT O365_Web_Service_URLs ID HERE>"   ### INPUT REQUIRED ###
        objectgroup_name_url = "O365_Web_Service_URLs"
        object_type_url = "Url"
        objectgroup_type_url = "urlgroup"
        put_list_url = URL_List_Flat
        object_field_url = "url"
        APIcaller(object_id_url, objectgroup_name_url, object_type_url, objectgroup_type_url, put_list_url, object_field_url)

        # API call for IP list
        object_id_IP = "<INPUT O365_Web_Service_IPs ID HERE>"   ### INPUT REQUIRED ###
        objectgroup_name_IP = "O365_Web_Service_IPs"
        object_type_IP = "Network"
        objectgroup_type_IP = "networkgroup"
        put_list_IP = IP_List_Flat
        object_field_ip = "value"
        APIcaller(object_id_IP, objectgroup_name_IP, object_type_IP, objectgroup_type_IP, put_list_IP, object_field_ip)

        # user feed back
        sys.stdout.write("\n")
        sys.stdout.write("Web Service List has been successfully updated!\n") 
        sys.stdout.write("\n")

##############END PARSE FUNCTION##############START EXECUTION SCRIPT##############

try:
    # uncomment for executing O365WebServiceParser just once, please copy-paste MD5 hash that is outputted in terminal
    WebServiceParser()

    # calls the intervalScheduler for automatic refreshing (pass O365WebServiceParser function and interval in seconds (1 hour = 3600 seconds))
    #intervalScheduler(WebServiceParser, 300) #set to 5 minutes

except (KeyboardInterrupt, SystemExit):
    sys.stdout.write("\n")
    sys.stdout.write("\n")
    sys.stdout.write("Exiting...\n")
    sys.stdout.write("\n")
    sys.stdout.flush()
    pass

# end of script
