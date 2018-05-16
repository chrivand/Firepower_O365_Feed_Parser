# NOTE: this is a proof of concept script, please test before using in production!

# import objects
import xml.etree.ElementTree as ET
import requests
import sys

# thishis is an EXAMPLE function that can be used to schedule the Parser to refresh at intervals. Takes the XMLFeedParser function and the interval as parameters.
def intervalScheduler(function, interval):
    # configure interval to refresh the AdBlocker (in seconds, 3600s = 1h, 86400s = 1d)
    setInterval = interval
    XMLFeedParser = function

    # user feedback
    sys.stdout.write("\n")
    sys.stdout.write("XML Feed Parser will be refreshed every %d seconds. Please use ctrl-C to exit.\n" %interval)
    sys.stdout.write("\n")

    # interval loop, unless keyboard interrupt
    try:
        while True:
            XMLFeedParser()
            sys.stdout.write("\n")
            sys.stdout.write("XML Feed updated!\n")
            sys.stdout.write("\n")
            time.sleep(setInterval)
    # handle keyboard interrupt
    except (KeyboardInterrupt, SystemExit):
        sys.stdout.write("\n")
        sys.stdout.write("\n")
        sys.stdout.write("Exiting... XML Feed Parser will not be automatically refreshed anymore.\n")
        sys.stdout.write("\n")
        sys.stdout.flush()
        pass

# function to pare the XML feed, so that it can be called iteratively (e.g by the scheduler)
def XMLFeedParser():
    # download file from Microsoft and open it for read
    XML_URL = 'https://support.content.office.net/en-us/static/O365IPAddresses.xml'
    r = requests.get(XML_URL, allow_redirects=True)
    XML_File = open('O365IPAddresses.xml', 'r')

    # user feed back
    sys.stdout.write("\n")
    sys.stdout.write("XML file successfully downloaded!\n") 
    sys.stdout.write("\n")

    # overwrite old files with files or create new the first time 
    Parsed_File_URL = open('/Users/christophervandermade/Documents/GitHub/Firepower_O365_Feed_Parser/Parsed_File_URL.txt', 'w+')
    Parsed_File_IPv4 = open('/Users/christophervandermade/Documents/GitHub/Firepower_O365_Feed_Parser/Parsed_File_IPv4.txt', 'w+')
    Parsed_File_IPv6 = open('/Users/christophervandermade/Documents/GitHub/Firepower_O365_Feed_Parser/Parsed_File_IPv6.txt', 'w+')

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

    #create .txt files to use in firepower
    for URL in URL_List:
    	Parsed_File_URL.write("%s\n" % URL)
        
    # user feed back
    sys.stdout.write("\n")
    sys.stdout.write("URL .txt file successfully created!\n") 
    sys.stdout.write("\n")

    for IPv4 in IPv4_List:
    	Parsed_File_IPv4.write("%s\n" % IPv4)

    # user feed back
    sys.stdout.write("\n")
    sys.stdout.write("IPv4 .txt file successfully created!\n") 
    sys.stdout.write("\n")

    for IPv6 in IPv6_List:
    	Parsed_File_IPv6.write("%s\n" % IPv6)

    # user feed back
    sys.stdout.write("\n")
    sys.stdout.write("IPv6 .txt file successfully created!\n") 
    sys.stdout.write("\n")

    # TO DO: upload TXT files to Firepower as objects (either through API, or by hosting online them and use them as Network Object Feed)

    # https://<management_center_IP_or_name>:<https_port>/<object_URL>/object_UUIDoptions
    # /api/fmc_config/v1/domain/{domain_UUID}/object/networks/{object_UUID}


    #close the opened files
    XML_File.close
    Parsed_File_URL.close
    Parsed_File_IPv4.close
    Parsed_File_IPv6.close

# run the function (interval can also be used)
# call the AdBlocker function so that it gets executed in this file, 
try:
    # comment out if using the intervalScheduler for automatic refreshing
    XMLFeedParser()
    
    # uncomment when using the intervalScheduler for automatic refreshing
    #intervalScheduler(XMLFeedParser, 86400)
except (KeyboardInterrupt, SystemExit):
    sys.stdout.write("\n")
    sys.stdout.write("\n")
    sys.stdout.write("Exiting...\n")
    sys.stdout.write("\n")
    sys.stdout.flush()
    pass

# end of script