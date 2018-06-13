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

# import libraries
import xml.etree.ElementTree as ET
import requests
import sys
import hashlib
import json
import time
# import supporting functions from additional file
from XMLParserFunctions import APIcaller, intervalScheduler, md5

# define global variables, CurrentMD5 will be updated every time script refreshes, please manually input MD5 if intervalScheduler is not used
CurrentMD5 = "NONE"
XML_URL = 'https://support.content.office.net/en-us/static/O365IPAddresses.xml'


# function to parse the XML feed, so that it can be called iteratively (e.g by the scheduler function)
def XMLFeedParser():
    # download file from Microsoft and open it for reading
    r = requests.get(XML_URL, auth=('user', 'pass'))
    with open('O365IPAddresses.xml', 'wb') as XML_File:
        XML_File.write(r.content)

    XML_File = open('O365IPAddresses.xml', 'r')
    
    if XML_File:
        # user feed back
        sys.stdout.write("\n")
        sys.stdout.write("XML file successfully downloaded!\n") 
        sys.stdout.write("\n")

    # calculate MD5 to check if XML file was updated
    global CurrentMD5
    NewMD5 = md5(XML_File.name)
    
    # if MD5 changed, the XML file was updated, so it will be parsed and API calls will be done to update FMC Group Objects
    if(CurrentMD5 != NewMD5):   
        # user feed back
        sys.stdout.write("\n")
        sys.stdout.write("XML feed has been updated (Old MD5: %s, new MD5: %s)!\n" % (CurrentMD5, NewMD5)) 
        sys.stdout.write("\n")

        # update global MD5 variable
        CurrentMD5 = NewMD5

        # parse XML file
        tree = ET.parse(XML_File)
        root = tree.getroot()

        # user feed back
        sys.stdout.write("\n")
        sys.stdout.write("XML file successfully parsed!\n") 
        sys.stdout.write("\n")

        # initiate lists to be filled with addresses
        URL_List = []
        IPv4_List = []
        IPv6_List = []

        #loop through XML file and add addresses to the correct lists
        for addresslist in root.iter('addresslist'):
            if(addresslist.get('type') == "URL"):
                for address in addresslist.findall('address'):
                    URL_List.append(address.text)
            if(addresslist.get('type') == "IPv4"):
                for address in addresslist.findall('address'):
                    IPv4_List.append(address.text)
            if(addresslist.get('type') == "IPv6"):
                for address in addresslist.findall('address'):
                    IPv6_List.append(address.text)

        
        # API call for URL list (user feedback is provided from the APIcaller function)
        object_id_url = "O365_XML_URL OBJECT ID HERE"   # INPUT REQUIRED
        objectgroup_name_url = "O365_XML_URL"
        object_type_url = "Url"
        objectgroup_type_url = "urlgroup"
        put_list_url = URL_List
        object_field_url = "url"
        APIcaller(object_id_url, objectgroup_name_url, object_type_url, objectgroup_type_url, put_list_url, object_field_url)

        # API call for IPv4 list
        object_id_IPv4 = "O365_XML_IPv4 OBJECT ID HERE"   # INPUT REQUIRED
        objectgroup_name_IPv4 = "O365_XML_IPv4"
        object_type_IPv4 = "Network"
        objectgroup_type_IPv4 = "networkgroup"
        put_list_IPv4 = IPv4_List
        object_field_ipv4 = "value"
        APIcaller(object_id_IPv4, objectgroup_name_IPv4, object_type_IPv4, objectgroup_type_IPv4, put_list_IPv4, object_field_ipv4)

        # API call for IPv6 list
        object_id_ipv6 = "O365_XML_IPv6 OBJECT ID HERE"   # INPUT REQUIRED
        objectgroup_name_ipv6 = "O365_XML_IPv6"
        object_type_ipv6 = "Network"
        objectgroup_type_ipv6 = "networkgroup"
        put_list_ipv6 = IPv6_List
        object_field_ipv6 = "value"
        APIcaller(object_id_ipv6, objectgroup_name_ipv6, object_type_ipv6, objectgroup_type_ipv6, put_list_ipv6, object_field_ipv6)
        
    # if the MD5 did not change, the XML file was not updated. 
    if(CurrentMD5 == NewMD5):
        # user feed back
        sys.stdout.write("\n")
        sys.stdout.write("XML feed has NOT been updated, no API calls needed!\n") 
        sys.stdout.write("\n")

    # close file after API calls
    XML_File.close

##############END PARSE FUNCTION##############START EXECUTION SCRIPT##############

try:
    # uncomment for executing XMLFeedParser just once, please copy paste MD5 hash that is outputted in terminal
    #XMLFeedParser()

    # calls the intervalScheduler for automatic refreshing (pass XMLFeedParser function and interval in seconds (1 hour = 3600 seconds))
    intervalScheduler(XMLFeedParser, 300) #set to 5 minutes

except (KeyboardInterrupt, SystemExit):
    sys.stdout.write("\n")
    sys.stdout.write("\n")
    sys.stdout.write("Exiting...\n")
    sys.stdout.write("\n")
    sys.stdout.flush()
    pass

# end of script