# Firepower O365 Feed Parser

_This is a Sample Script that can parse the O365 XML file and upload it to Firepower Management Center as Group Objects._

---

This is a script that parses the XML feed (https://support.content.office.net/en-us/static/O365IPAddresses.xml) that Microsoft publishes with URL, IPv4 and IPv6 addresses. These addresses are used for the infrastructure of the Microsoft cloud applications (Office 365). The script will parse the XML file into 3 separate lists and use the FMC API's to upload them to 3 Group Objects. These Group Objects can be used in a Firepower trust/prefilter rule. By doing so the traffic is excluded from further inspection, to ensure low latency. 

## Features

* Parsing O365 XML File;
* Checking if O365 file was updated, using MD5 hashes;
* Checking for updates with a specified interval (in seconds, 3600s = 1h);
* Creating right JSON format for FMC API PUT requests;
* Uploading this JSON to FMC, overwriting the previous object.

### Potential next steps

* Email / Webex Teams alert when changes were made to Objects;
* Automatic policy deploy using API when changes were made to Objects.


## Solution Components

The script consists of 2 python files. The main script needs to run (indefintely) and a function is built in to rerun the script every x amount of seconds. Then, using the MD5 hash of the XML file, it is checked if changes were made to the XML file. If changes happened, the XML file is parsed and uploaded using a PUT request to FMC. Important is to use SSL verification and to test the script before running this in a production environment. Also, please be aware that a policy redeploy is needed to update the Group Objects in the used Policies. Currently there is no API call built in to do a policy redeploy, since this might cause other unfinished policies or objects to be deployed (e.g. if a network administrator is working on a Policy in the GUI). This can be done using the API as well, if preferred. 

### Cisco Products / Services

* Cisco Firepower Management Center
* Cisco Firepower Threat Defense 


## Usage

* Please test this properly before implementing in a production environment. This is a sample script.
* The running script should be hosted in a secure environment! For example: if a malicious actor can place additional IP-addresses or URL's in the list somehow, they will be put in a Firepower trust rule, and might cause the malicious actor to bypass security.


## Installation

These instructions will enable you to download the script and run it, so that the output can be used in Firepower as Group Objects. So, what do you need to get started? Please find a list below:

1. Create 3 Group Objects in FMC: *"O365_XML_URL"* (URL Group Object), *"O365_XML_IPv4"* (Network Group Object) and *"O365_XML_IPv6"* (Network Group Object). At first you will have to put in a random URL/Network, to enable the objects. 

2. Use either the FMC API Explorer, or a Script, to do a GET request for the group objects. Write down the Object ID's (e.g. *"000XXXX-YYYY-ZZZZ-0000-01234567890"*). You will need these later in the PUT requests to update the objects. The FMC API explorer can be reached at https://IP-addressOfFMC/api/api-explorer

3. Furthermore you need the IP address (or domain) of the FMC, the username and password. These are added to the API caller function and obviously also needed for the FMC API explorer. It is recommended to create a separate FMC login account for the API usage, otherwise the admin will be logged out during the API calls. 

4. It is also recommended to download a SSL certificate from FMC and put it in the same folder as the scripts. This will be used to securely connect to FMC. In the APIcaller function, there is an option to enable SSL verification.

5. You will also need the correct API path, it is in the script already, however there is a unique identifier for the domain. This can also be obtained from the FMC API explorer.


## Okay, I have the Group Objects, now what?

More instructions are in comments in the 2 sample scripts. Please find screenshots below on what the end result will look like:

Screenshots of the 3 Group Objects, after the API call:

![Networkobjects](https://github.com/chrivand/Firepower_O365_Feed_Parser/blob/master/screenshots_FMC_O365/urlgroupobject.png)

![Networkobjects](https://github.com/chrivand/Firepower_O365_Feed_Parser/blob/master/screenshots_FMC_O365/networkgroupobjects.png)

These objects can be used in either Prefilter Policy Fastpath-rule (for the Network Objects), or in an Access Control Policy Trust-rule (for the URL Object). This is how to configure the Prefilter Policy rule in FMC:

![Networkobjects](https://github.com/chrivand/Firepower_O365_Feed_Parser/blob/master/screenshots_FMC_O365/prefilterpolicyrule.png)
![Networkobjects](https://github.com/chrivand/Firepower_O365_Feed_Parser/blob/master/screenshots_FMC_O365/prefilterpolicy.png)

Likewise, this can be done in the Access Control Policy for the URL Group Object:

![Networkobjects](https://github.com/chrivand/Firepower_O365_Feed_Parser/blob/master/screenshots_FMC_O365/ACPtrustrule.png)

For better understanding of the packet flow in Firepower Threat Defense, and how the Fastpath action in the Prefilter Policy works, please review the following flow diagram:

![Networkobjects](https://github.com/chrivand/Firepower_O365_Feed_Parser/blob/master/screenshots_FMC_O365/packetflowftd.png)

Please take caution on the following notes:

* Please test this properly before implementing in a production environment. This is a sample script.

* The running script should be hosted in a secure environment! For example: if a malicious actor can place additional IP-addresses or URL's in the list somehow, they will be put in a Firepower trust rule, and might cause the malicious actor to bypass security.


## Author(s)

* Christopher van der Made (chrivand@cisco.com)
