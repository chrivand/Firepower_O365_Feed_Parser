# NOTE: this is a proof of concept script, please test before using in production!

# import objects
import xml.etree.ElementTree as ET
import requests
import sys
import hashlib
import json
import time
# import additional functions from extra file
from XMLParserFunctions import APIcaller, intervalScheduler, md5

# define global variables
CurrentMD5 = ""
XML_URL = 'https://support.content.office.net/en-us/static/O365IPAddresses.xml'


# function to pare the XML feed, so that it can be called iteratively (e.g by the scheduler)
def XMLFeedParser():
    # download file from Microsoft and open it for read
    r = requests.get(XML_URL, auth=('user', 'pass'))
    with open('O365IPAddresses.xml', 'wb') as XML_File:
        XML_File.write(r.content)

    XML_File = open('O365IPAddresses.xml', 'r')
    
    if XML_File:
        # user feed back
        sys.stdout.write("\n")
        sys.stdout.write("XML file successfully downloaded!\n") 
        sys.stdout.write("\n")

    #calculate MD5
    global CurrentMD5
    NewMD5 = md5(XML_File.name)
    
    # if MD5 changed, parse XML file and make API calls
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

        
        # API call for URL list
        object_id_url = "000C2943-1B9D-0ed3-0000-025769805102"
        objectgroup_name_url = "O365_XML_URL"
        object_type_url = "Url"
        objectgroup_type_url = "urlgroup"
        put_list_url = URL_List
        object_field_url = "url"
        APIcaller(object_id_url, objectgroup_name_url, object_type_url, objectgroup_type_url, put_list_url, object_field_url)

        # API call for IPv4 list
        object_id_IPv4 = "000C2943-1B9D-0ed3-0000-025769804555"
        objectgroup_name_IPv4 = "O365_XML_IPv4"
        object_type_IPv4 = "Network"
        objectgroup_type_IPv4 = "networkgroup"
        put_list_IPv4 = IPv4_List
        object_field_ipv4 = "value"
        APIcaller(object_id_IPv4, objectgroup_name_IPv4, object_type_IPv4, objectgroup_type_IPv4, put_list_IPv4, object_field_ipv4)

        # API call for IPv6 list
        object_id_ipv6 = "000C2943-1B9D-0ed3-0000-025769805120"
        objectgroup_name_ipv6 = "O365_XML_IPv6"
        object_type_ipv6 = "Network"
        objectgroup_type_ipv6 = "networkgroup"
        put_list_ipv6 = IPv6_List
        object_field_ipv6 = "value"
        APIcaller(object_id_ipv6, objectgroup_name_ipv6, object_type_ipv6, objectgroup_type_ipv6, put_list_ipv6, object_field_ipv6)
        
    
    if(CurrentMD5 == NewMD5):
        # user feed back
        sys.stdout.write("\n")
        sys.stdout.write("XML feed has not been updated, no API calls needed!\n") 
        sys.stdout.write("\n")

    # close file after API calls
    XML_File.close

##############END FUNCTION##############START EXECUTION SCRIPT##############

try:
    # uncomment for executing just once
    #XMLFeedParser()

    # uncomment when using the intervalScheduler for automatic refreshing (pass function and seconds)
    intervalScheduler(XMLFeedParser, 15) 

except (KeyboardInterrupt, SystemExit):
    sys.stdout.write("\n")
    sys.stdout.write("\n")
    sys.stdout.write("Exiting...\n")
    sys.stdout.write("\n")
    sys.stdout.flush()
    pass

# end of script