# Firepower_O365_Feed_Parser (PROOF OF CONCEPT)

This is a script that parses the XML feed (https://support.content.office.net/en-us/static/O365IPAddresses.xml) that Microsoft publishes with URL, IPv4 and IPv6 addresses. These addresses are used for the infrastructure of the Microsoft cloud applications (Office 365). The script will parse the XML file into 3 separate lists and use the FMC API's to upload them to 3 Group Objects. These Group Objects can be used in a Firepower trust rule. By doing so the traffic is excluded from further inspection, to ensure low latency. 

## Getting Started with the Installation

These instructions will enable you to download the script and run it, so that the output can be used in Firepower as Group Objects. The script consists of 2 python files. The main script needs to run (indefintely) and a function is built in to rerun the script every x amount of seconds. Then, using the MD5 hash of the XML file, it is checked if changes were made to the XML file. If changes happened, the XML file is parsed and uploaded using a PUT request to FMC. Important is to use SSL verification and to test the script before running this in a production environment. Also, please be aware that a policy redeploy is needed to update the policies. Currently there is no API call built in to do a policy redeploy, since this might cause other unfinished policies or objects to be deployed (e.g. if a network administrator is working in the GUI). This can be done using the API as well, if preferred. 

###So, what do you need to get started?

* Create 3 Group Objects in FMC: "O365_XML_URL" (URL Group Object), "O365_XML_IPv4" (Network Group Object) and "O365_XML_IPv6" (Network Group Object)
* Use either the FMC API Explorer, or a Script, to do a GET request for the group objects. Write down the Object ID's (e.g. "000C2943-1B6C-0ec3-0000-035789805120"). You will need these later in the PUT requests to update the objects.
* Furthermore you need the IP address (or domain) of the FMC, the username and password. These are added to the API caller function and also for the FMC API explorer. 
* The FMC API explorer can be reached at https://<IP-address of FMC>/api/api-explorer
* Recommended is also to download a SSL certificate from FMC and put it in the same folder as the scripts. 
* You will also need the correct API path, it is in the script already, however there is a unique identifier for the domain. This can be obtained from the FMC API explorer.
* Please test this properly before implementing in a production environment. 
* The running script should be hosted in a secure environment. For example: if a malicious actor can place additional IP-addresses or URL's in the list somehow, they will be put in a Firepower trust rule, and might cause the malicious actor to bypass security.

More instructions are in script and will be elaborated on at a later point in time. Please contact me for more info...

Written by Christopher van der Made (Cisco)
