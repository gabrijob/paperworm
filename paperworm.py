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
import PyPDF2
from random import randint
from time import sleep
import datetime

import translateURLs

dry = False
start_year = 0
fin_year = datetime.datetime.now().year
min_pgs = 0
http_proxy = None
https_proxy = None
library = ''
current_pub = []
publications_found = []

# TODO: use input file with strings to search


def usage():
    print('Usage:  python3 paperworm [options] [--lib <lib_name>] <search_string>')
    print('  Options:')
    print('\t -h, --help        Print this text')
    print('\t -T        Search in title')
    print('\t --dry        Dry run without downloading found publications')
    print('\t --from <YYYY>        Start year to consider on the query (eg. 2010)')
    print('\t --to <YYYY>        Last year to consider on the query (eg. 2019)')
    print('\t --minpg <min_pages>        Minimum number of pages the paper should have')
    print('\t --lib <library_name>        Specific library to perform the search, possible values [ieee, acm].')
    print('\t --http_proxy <addr:port>   Proxy to be used for HTTP')
    print('\t --https_proxy <addr:port>   Proxy to be used for HTTPS')


def do_search(search_string):
    global current_pub

    if http_proxy or https_proxy:
        print("\n--Using HTTP proxy: " + http_proxy)
        print("--Using HTTPS proxy: " + https_proxy)
        set_proxy()

    print("\n--Using search string: \n" + search_string)

    search_query = scholarly.search_pubs(search_string)
    # Iterate through retrieved publications
    end = False
    while not end:
        pub = next(search_query, None)
        current_pub = []
        if pub:
            if pre_filter(pub):
                current_pub.append(library)
                current_pub.append(pub.bib['year'])

                download_paper(pub.bib['url'])

                current_pub.append(pub.bib['title'])
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
    global dry, start_year, fin_year, min_pgs, http_proxy, https_proxy, library

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o == "-T":
            in_title = True
        elif o == "--dry":
            dry = True
        elif o == "--from":
            start_year = int(a)
        elif o == "--to":
            fin_year = int(a)
        elif o == "--minpg":
            min_pgs = int(a)
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

    library = library.lower()
    if library != 'ieee' and library != 'acm':
        print("\nMissing library argument --lib <lib_name>")
        usage()
        sys.exit()

    if fin_year < start_year:
        raise TypeError("Invalid Argument: \'--to\' year should be bigger than \'--from\' year")

    # Create search string in google scholar format
    if in_title:
        search_string += "allintitle: "

    search_string += args[0]

    if library:
        print(library)
        search_string += " +site:" + translateURLs.get_source_site(library)

    return search_string


def write_result():
    f = open('search_result.csv', 'w')

    first_row = ['LIBRARY', 'YEAR', 'ID', 'PAGES', 'TITLE']

    with f:
        writer = csv.writer(f)
        writer.writerow(first_row)

        for pub in publications_found:
            writer.writerow(pub)


def pre_filter(publication):
    passed = True

    if start_year > 0 and int(publication.bib['year']) < start_year:
        passed = False
    elif int(publication.bib['year']) > fin_year:
        passed = False

    return passed


def post_filter(filename):
    reader = PyPDF2.PdfFileReader(open(filename, 'rb'))
    nb_pages = reader.getNumPages()

    current_pub.append(nb_pages)

    if nb_pages < min_pgs:
        os.remove(filename)
    else:
        new_filename = '-'.join([str(elem) for elem in current_pub])
        os.rename(filename, new_filename)




def download_paper(base_url):
    cmd = 'echo \"Download URL not found\"'
    options = '-e robots=off -U "Mozilla" -A.pdf '
    env_proxy = None

    if http_proxy or https_proxy:
        env_proxy = {"http_proxy": http_proxy, "https_proxy": https_proxy}

    down_url, paper_id = translateURLs.get_download_url(library, base_url)
    current_pub.append(paper_id)

    if down_url:
        cmd = 'wget ' + options + down_url + ' -O ' + paper_id + '.pdf'
        #cmd = 'wget ' + options + down_url + ' -O paper.pdf'

    if not dry:
        process = subprocess.run(cmd, shell=True, check=True, env=env_proxy)
        post_filter(paper_id + '.pdf')
        sleep(randint(10, 100))
    else:
        current_pub.append("NA")


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hT", ["help", "dry", "from=", "to=", "lib=", "http_proxy=", "https_proxy="])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)
    search_str = parse_opts(opts, args)

    if dry:
        print("\n############## DRY RUN ##################")
    do_search(search_str)
    write_result()

    return 0


if __name__ == '__main__':
    main()
