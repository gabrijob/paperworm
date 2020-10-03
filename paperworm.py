# Authors:
# gabriel.grabher@inf.ufrgs.br
# kassianoj@gmail.com


#!/usr/bin/env python3

from scholarly import scholarly, ProxyGenerator
import getopt
import sys
import os
import subprocess
import csv
from random import randint
from time import sleep

import filters
import translateURLs

##########################################################################################
dir = "papers/"

dry = False
http_proxy = None
https_proxy = None
library = ''
current_pub = []
publications_found = []
##########################################################################################


def usage():
    print('\nUsage:  python3 paperworm [options] [--from <YYYY>] [--lib <lib_name>] <search_string>')
    print('\nOptions:')
    print(' -h, --help              Print this text.')
    print(' --from <YYYY>           Start year to include on the search.')
    print(' --to <YYYY>             Final year to include on the search. Default: current year.')
    print(' --minpgs <min>          Minimum number of pages accepted. Default: 1 page.')
    print(' --dry                   Dry run without downloading found publications')
    print(' --lib <lib_name>        Specific library to perform the search, possible values [ieee, acm, sdirect, wiley, springer, mdpi].')
    print('\nProxy Settings:')
    print('Obs. Proxy settings allow UFRGS students\' to download papers from many sources. If you have a different case, you need to adapt the code to use the libraries.')
    print('\t --http_proxy <addr:port>    Proxy to be used for HTTP')
    print('\t --https_proxy <addr:port>   Proxy to be used for HTTPS')
    print('\nExamples:')
    print("$ python3 paperworm.py --http_proxy 127.0.0.1:3128 -T --from 2015 --lib ieee '\"* learning\" (\"resource*\" OR \"task*\") (\"management\" OR \"scheduling\" OR \"orchestration\" OR \"provisioning\")'")
    print("$ python3 paperworm.py -T --lib acm --dry '\"* learning\" (\"resource*\" OR \"task*\") (\"management\" OR \"scheduling\" OR \"orchestration\" OR \"provisioning\")'")
    print("$ python3 paperworm.py --https_proxy=127.0.0.1:3128 -T --from 2015 --lib acm '\"* learning\" (\"resource*\" OR \"task*\") (\"management\" OR \"scheduling\" OR \"orchestration\" OR \"provisioning\")'")


def do_search(search_string):
    global current_pub

    if http_proxy or https_proxy:
        print("\n--Using HTTP proxy: " + http_proxy)
        print("--Using HTTPS proxy: " + https_proxy)
        set_proxy()

    print("\n--Using search string: \n" + search_string)

    search_query = None
    try:
        search_query = scholarly.search_pubs(search_string)
    except Exception:
        print("\nCannot fetch the page from Google Scholar.")
        print("You may have been blocked by Google Scholar, please check your internet connection.")
        sys.exit()

    # Iterate through retrieved publications
    end = False
    while not end:
        pub = next(search_query, None)
        current_pub = []
        if pub:
            if filters.pre_filter(pub):
                current_pub.append(library)
                current_pub.append(pub.bib['year'])
                current_pub.append(pub.bib['cites'])

                if download_paper(pub.bib['url']):
                    current_pub.append(pub.bib['title'])
                    if 'abstract' in pub.bib: current_pub.append(pub.bib['abstract'])
                    publications_found.append(current_pub)
        else:
            end = True

    print('\n{} publications found'.format(len(publications_found)))


def set_proxy():
    pg = ProxyGenerator()
    pg.SingleProxy(http_proxy, https_proxy)
    scholarly.use_proxy(pg)


def parse_opts(opts, args):
    search_string = ""
    in_title = False
    global dry, http_proxy, https_proxy, library

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o == "-T":
            in_title = True
        elif o == "--from":
            filters.set_start_year(a)
        elif o == "--to":
            filters.set_final_year(a)
        elif o == "--minpgs":
            filters.set_min_pgs(a)
        elif o == "--dry":
            dry = True
        elif o == "--lib":
            library = a
        elif o == "--http_proxy":
            http_proxy = a
        elif o == "--https_proxy":
            https_proxy = a
        else:
            print("Unhandled option " + o + "\n")
            usage()
            sys.exit()

    if len(args) > 1:
        print("\nArgument Error: Too many Arguments.")
        usage()
        sys.exit()
    elif not args:
        print("\nArgument Error: Missing Arguments.")
        usage()
        sys.exit()

    library = library.lower()
    if library != 'ieee' and library != 'acm' and library != 'sdirect' and library != 'wiley' and library != 'springer' and library != 'mdpi':
        print("\nMissing library argument --lib <lib_name>")
        sys.exit()

    filters.verify_filters()

    if http_proxy and not https_proxy:
        https_proxy = http_proxy
    elif https_proxy and not http_proxy:
        http_proxy = https_proxy

    # Create search string in google scholar format
    if in_title:
        search_string += "allintitle: "

    search_string += args[0]

    if library:
        print(library)
        search_string += " +site:" + translateURLs.get_source_site(library)

    return search_string


def write_result():
    f = open(dir + 'search_result.csv', 'w')

    first_row = ['LIBRARY', 'YEAR', 'CITATIONS',
                 'ID', 'PAGES', 'TITLE', 'ABSTRACT']

    with f:
        writer = csv.writer(f)
        writer.writerow(first_row)

        for pub in publications_found:
            writer.writerow(pub)


def download_paper(base_url):
    cmd = 'echo \"Download URL not found\"'
    options = '-e robots=off -U "Mozilla" -A.pdf'
    env_proxy = None

    if http_proxy or https_proxy:
        env_proxy = {"http_proxy": http_proxy, "https_proxy": https_proxy}

    down_url, paper_id = translateURLs.get_download_url(library, base_url)
    current_pub.append(paper_id)

    if down_url:
        cmd = 'wget ' + options + down_url + ' -O ' + dir + paper_id + '.pdf'

    if not dry:
        process = subprocess.run(cmd, shell=True, check=True, env=env_proxy)
        passed = filters.post_filter(paper_id + '.pdf', current_pub)
        sleep(randint(10, 100))
        return passed
    else:
        current_pub.append("NA")
        return True


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hT", [
                                   "help", "dry", "from=", "to=", "lib=", "http_proxy=", "https_proxy="])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)
    search_str = parse_opts(opts, args)

    if not os.path.exists(dir):
        os.makedirs(dir)

    if dry:
        print("\n############## DRY RUN ##################")
    do_search(search_str)
    write_result()

    return 0


if __name__ == '__main__':
    main()
