[paperworm]

A simple script for downloading publications based on an input search string using Google Scholar.

For usage information:
	$ python3 paperworm.py -h  



Example:
	$ python3 paperworm.py --http_proxy 127.0.0.1:3128 --https_proxy 127.0.0.1:3128 -T --lib ieee '"* learning" ("resource*" OR "task*") ("management" OR "scheduling" OR "orchestration" OR "provisioning")'

	$ python3 paperworm.py --from 2015 -T --lib acm --dry '"* learning" ("resource*" OR "task*") ("management" OR "scheduling" OR "orchestration" OR "provisioning")'

