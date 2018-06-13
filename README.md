# Firepower O365 Feed Parser

_This is a Sample Script that can parse the O365 XML feed and upload it to Firepower Management Center as Group Objects._

---

This is a sample script that parses the XML feed (https://support.content.office.net/en-us/static/O365IPAddresses.xml) that Microsoft publishes with URL, IPv4 and IPv6 addresses. These addresses are used for the infrastructure of the Microsoft cloud applications (e.g. Office 365). The script will parse the XML file into 3 separate lists and use the FMC API's to upload them into 3 Group Objects. These Group Objects can be used in a Firepower trust/prefilter rule. By doing so the traffic is excluded from further inspection, to prevent  latency issues with the applications. 

Please contact me if you have any questions or remarks.

## Features

* Parsing O365 XML File into 3 lists;
* Creating right JSON format for FMC API PUT requests;
* Uploading this JSON to FMC, overwriting the previous Group Object;
* Checking if O365 file was updated, using MD5 hashes (optional);
* Continuously checking for updates with a specified time interval (optional).

### Potential next steps

* Email / Webex Teams alert when changes were made to Objects;
* Automatic policy deploy using API when changes were made to Objects;
* Update script to use new feed from MSFT (roadmapped by MSFT);
* Create extra modules for other SaaS applications;
* Create extra modules for other Cisco solutions (WSA, Umbrella etc.).


## Solution Components

The script consists of 2 python files. The main script can run indefinitely, leveraging a function that is built in, to rerun the script every x amount of seconds (it can also just be executed once). Then, using the MD5 hash of the XML file, it is checked if changes were made to the XML file. If changes happened, the XML file is parsed and uploaded using a PUT request to FMC.  

### Cisco Products / Services

* Cisco Firepower Management Center;
* Cisco Firepower Threat Defense NGFW.


## Installation

These instructions will enable you to download the script and run it, so that the output can be used in Firepower as Group Objects. What do you need to get started? Please find a list of tasks below:

1. You need the IP address (or domain) of the FMC, the username and password. These need to be added to the APIcaller function and are obviously also needed for the FMC API explorer. It is recommended to create a separate FMC login account for the API usage, otherwise the admin will be logged out during the API calls. 

2. Create 3 Group Objects in FMC: *"O365_XML_URL"* (URL Group Object), *"O365_XML_IPv4"* (Network Group Object) and *"O365_XML_IPv6"* (Network Group Object). At first you will have to put in a random URL/Network, to enable the objects. 

3. In FMC, go to System > Configuration > REST API Preferences to make sure that the REST API is enabled on the FMC.

4. Use the FMC API Explorer to do a GET request for the Group Objects. This is done by going into the FMC API Explorer (can be reached at https://IP-addressOfFMC/api/api-explorer), and then clicking on *"Object"* in the left menu. The scroll down to *"networkgroups"* and click on *"GET"* and then again on *"GET"* in the right menu. 

5. Now you will need to copy-paste the the Object ID's of the 2 Network Group Objects (*"O365_XML_IPv4"* and *"O365_XML_IPv6"*). The ID's will look like the following format: *"000XXXX-YYYY-ZZZZ-0000-01234567890"*. This is displayed in the *"Response Text"* output box in the right menu. You will need these later in the PUT requests to update the objects. Below is an example of how this output would look for the *"O365_XML_IPv4"* Network Group Object:

```
"type": "NetworkGroup",
"name": "O365_XML_IPv4",
"id": "000XXXX-YYYY-ZZZZ-0000-01234567890"
```

6. You will also need the ID for the FMC Domain, to include in the API path. This can also be obtained from the FMC API explorer. When clicking on GET when doing to request above, the ID of the domain is showed in the path and has the same syntax as the Object ID's: 

![Networkobjects](https://github.com/chrivand/Firepower_O365_Feed_Parser/blob/master/screenshots_FMC_O365/screenshotAPIexplorer.png)

7. Repeat the GET request of step 4 as well for *"urlgroups"*, to obtain the ID for the URL Group Object (*"O365_XML_URL"*). You should now have 4 ID's copy-pasted, which you can put inside the APIcaller function and in the XMLFeedParser function.

8. It is also recommended to download a SSL certificate from FMC and put it in the same folder as the scripts. This will be used to securely connect to FMC. In the APIcaller function, there is an option to enable SSL verification that uses this certificate.

9. More instructions are in comments in the 2 sample scripts. It will say *# INPUT REQUIRED* after the variables where you are required to fill in the FMC login, the Domain ID and the Group Object ID's. All of these fields are in the APIcaller function (Domain ID and login) and XMLFeedParser function (3 Group Object ID's).


### How to use the Group Objects in Firepower Management Center.

For better understanding of the packet flow in Firepower Threat Defense, and how the Fastpath action in the Prefilter Policy works, please review the following flow diagram:

![Networkobjects](https://github.com/chrivand/Firepower_O365_Feed_Parser/blob/master/screenshots_FMC_O365/packetflowftd.png)

After the successful PUT requests, the 3 Group Objects will have been updated with the new IP-addresses and URLs. Please find screenshots of the 3 Group Objects, after the API call:

![Networkobjects](https://github.com/chrivand/Firepower_O365_Feed_Parser/blob/master/screenshots_FMC_O365/urlgroupobject.png)

![Networkobjects](https://github.com/chrivand/Firepower_O365_Feed_Parser/blob/master/screenshots_FMC_O365/networkgroupobjects.png)

These objects can be used in either Prefilter Policy Fastpath-rule (for the Network Objects), or in an Access Control Policy Trust-rule (for the URL Object). This is how to configure the Prefilter Policy rule in FMC:

![Networkobjects](https://github.com/chrivand/Firepower_O365_Feed_Parser/blob/master/screenshots_FMC_O365/prefilterpolicyrule.png)

This will result in the following rule:

![Networkobjects](https://github.com/chrivand/Firepower_O365_Feed_Parser/blob/master/screenshots_FMC_O365/prefilterpolicy.png)

Likewise, this can be done with a Trust Rule in the Access Control Policy for the URL Group Object:

![Networkobjects](https://github.com/chrivand/Firepower_O365_Feed_Parser/blob/master/screenshots_FMC_O365/ACPtrustrule.png)

As a final step you will need to do a Policy Deploy, each time that the Group Objects have been updated. This can be done from the FMC by clicking on *"DEPLOY"* and by selecting the device that need this Policy Deploy.

### Please take caution on the following notes:

* Please be aware that a policy redeploy is needed to update the Group Objects in the used Policies. Currently there is no API call built in to do a policy redeploy, since this might cause other unfinished policies or objects to be deployed (e.g. if a network administrator is working on a Policy in the GUI).

* Important is to use SSL verification and to test the script before running this in a production environment.

* Please test this properly before implementing in a production environment. This is a sample script.

* In case the intervalScheduler is used: the running script should be hosted in a secure environment! For example: if a malicious actor can place additional IP-addresses or URL's in the list somehow, they will be put in a Firepower trust rule, and might cause the malicious actor to bypass security.


## Author(s)

* Christopher van der Made (Cisco)
