#!/usr/bin/env python3

from scholarly import scholarly, ProxyGenerator
import getopt
import sys
from random import randint
from time import sleep
import subprocess
import csv

dry = False
start_year = 0
last_year = 0
http_proxy = None
https_proxy = None
publications_found = []

# TODO: use input file with strings to search


def usage():
    print('Usage:  python3 paperworm [options] search_string')
    print('  Options:')
    print('\t -h, --help        Print this text')
    print('\t -T        Search in title')
    print('\t --dry        Dry run without downloading found publications')
    print('\t --from YYYY        Start year to consider on the query (eg. 2010)')
    print('\t --to YYYY        Last year to consider on the query (eg. 2019)')
    print('\t --lib library_url        Specific library to perform the search (eg. ieee.org)')
    print('\t --http_proxy addr:port   Proxy to be used for HTTP')
    print('\t --https_proxy addr:port   Proxy to be used for HTTPS')


def do_search(search_string):
    if http_proxy or https_proxy:
        print("Using HTTP proxy: " + http_proxy)
        print("Using HTTPS proxy: " + https_proxy)
        set_proxy()

    print("Using search string: " + search_string)

    search_query = scholarly.search_pubs(search_string)
    # Iterate through retrieved publications
    end = False
    while not end:
        pub = next(search_query, None)
        if pub:
            if pass_filter(pub):
                publications_found.append((pub.bib['title'], pub.bib['url']))
                if not dry:
                    download_papers(pub.bib['url'])
        else:
            end = True

    print('{} Publications found'.format(len(publications_found)))

def set_proxy():
    pg = ProxyGenerator()
    pg.SingleProxy(http_proxy, https_proxy)
    scholarly.use_proxy(pg)


def parse_opts(opts, args):
    search_string = ""
    in_title = False
    library = None
    global dry, start_year, last_year, http_proxy, https_proxy

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o == "-T":
            in_title = True
        elif o == "--dry":
            dry = True
        elif o == "--from":
            start_year = a
        elif o == "--to":
            last_year = a
        elif o == "--lib":
            library = a
        elif o == "--http_proxy":
            http_proxy = a
        elif o == "--https_proxy":
            https_proxy = a
        else:
            assert False, "unhandled option"

    if len(args) > 1:
        raise TypeError("Too many Arguments")
    elif not args:
        raise TypeError("Missing Arguments")

    if last_year < start_year:
        raise TypeError("Invalid Argument: \'--to\' year should be bigger than \'--from\' year")

    if in_title:
        search_string += "allintitle: "

    search_string += args[0]

    if library:
        search_string += " +site:" + library

    return search_string


def write_result():
    f = open('search_result.csv', 'w')

    first_row = ['Title', 'URL']

    with f:
        writer = csv.writer(f)
        writer.writerow(first_row)

        for pub in publications_found:
            writer.writerow(pub)



def download_papers(down_url):
    cmd = 'echo \"Download URL not found\"'
    options = '--content-disposition -e robots=off --user-agent \"Mozilla\" -A.pdf '

    if down_url:
        cmd = 'wget ' + options + down_url

    process = subprocess.run(cmd, shell=True, check=True)

    sleep(randint(10, 100))


def pass_filter(publication):
    passed = True

    if start_year > 0 and int(publication.bib['year']) < start_year:
        passed = False
    elif last_year > 0 and int(publication.bib['year']) > last_year:
        passed = False

    return passed


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hT", ["help", "dry", "from=", "to=", "lib=", "http_proxy=", "https_proxy="])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)
    search_str = parse_opts(opts, args)

    do_search(search_str)
    write_result()

    return 0


if __name__ == '__main__':
    #do_search('allintitle: "* learning" ("resource*" OR "task*") ("management" OR "scheduling" OR "orchestration" OR "provisioning") +site:ieee.org')
    main()
