# Firepower_O365_Feed_Parser (PROOF OF CONCEPT, NO PRODUCTION SCRIPT)

This is a script that parses the XML feed (https://support.content.office.net/en-us/static/O365IPAddresses.xml) that Microsoft publishes with URL, IPv4 and IPv6 addresses. These addresses are used for the infrastructure of the Microsoft cloud applications (Office 365). The script will parse the XML file into 3 separate lists and use the FMC API's to upload them to 3 Group Objects. These Group Objects can be used in a Firepower trust rule. By doing so the traffic is excluded from further inspection, to ensure low latency.

## Getting Started with the Installation

These instructions will enable you to download the script and run it, so that the output can be used in Firepower as Group Objects. The script consists of 2 python files. The main script needs to run (indefintely) and a function is built in to rerun the script every x amount of seconds. Then, using the MD5 hash of the XML file, it is checked if changes were made to the XML file. If changes happened, the XML file is parsed and uploaded using a PUT request to FMC. Important is to use SSL verification and to test the script before running this in a production environment. Also, please be aware that a policy redeploy is needed to update the policies. Currently there is no API call built in to do a policy redeploy, since this might cause other unfinished policies or objects to be deployed (e.g. if a network administrator is working in the GUI). This can be done using the API as well, if preferred. 

More instructions to be written, please contact me for more info...

Written by Christopher van der Made (Cisco)
