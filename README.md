[paperworm]

A simple script for downloading publications based on an input search string using Google Scholar.

For usage information:
	$ python3 paperworm.py -h  

Dependencies:
	$ sudo apt install python3-pip
	$ pip3 install scholarly
	$ pip3 install PyPDF2


Example:
	$ python3 paperworm.py --https_proxy 127.0.0.1:3128 --from 2015 -T --lib ieee '"* learning" ("resource*" OR "task*") ("management" OR "scheduling" OR "orchestration" OR "provisioning")'

	$ python3 paperworm.py -T --from 2015 --lib acm --dry '"* learning" ("resource*" OR "task*") ("management" OR "scheduling" OR "orchestration" OR "provisioning")'

	$ python3 paperworm.py --http_proxy=127.0.0.1:3128 --from 2015 -T --lib acm '"* learning" ("resource*" OR "task*") ("management" OR "scheduling" OR "orchestration" OR "provisioning")'

Authors:
 gabriel.grabher@inf.ufrgs.br
 kassianoj@gmail.com

