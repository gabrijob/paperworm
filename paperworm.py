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
import logging

import filters
import translateURLs

##########################################################################################
ALLOW_PROXY_ON_SCHOLAR = False
DOWNLOAD_LOG_FILE = "download.log"
# Set up a specific logger with our desired output level
logger = logging.getLogger('Download Log')
logger.setLevel(logging.INFO)
# Add the log message handler to the logger
handler = logging.FileHandler(DOWNLOAD_LOG_FILE)
logger.addHandler(handler)
dir = "papers/"

dry = False
http_proxy = None
https_proxy = None
current_lib = ''
libraries = []
search_query = None
current_pub = {}
publications_found = []
publications_pre_filtered = []
publications_post_filtered = []
##########################################################################################


def usage():
    print('\nUsage:  python3 paperworm [options] [--from <YYYY>] [--lib <lib1,lib2,lib3...>] <search_string>')
    print('\nOptions:')
    print(' -h, --help                   Print this text.')
    print(' --from <YYYY>                Start year to include on the search.')
    print(' --to <YYYY>                  Final year to include on the search. Default: current year.')
    print(' --minpgs <min>               Minimum number of pages accepted. Default: 1 page.')
    print(' --dry                        Dry run without downloading found publications')
    print(' --lib <lib1,lib2,lib3...>    Specific library to perform the search, possible values [ieee, acm, sdirect, wiley, springer, mdpi, all].')
    print('\nProxy Settings:')
    print('Obs. Proxy settings allow UFRGS students\' to download papers from many sources. If you have a different case, you need to adapt the code to use the libraries.')
    print('\t --http_proxy <addr:port>    Proxy to be used for HTTP')
    print('\t --https_proxy <addr:port>   Proxy to be used for HTTPS')
    print('\nExamples:')
    print("$ python3 paperworm.py --http_proxy 127.0.0.1:3128 -T --from 2015 --lib ieee '\"* learning\" (\"resource*\" OR \"task*\") (\"management\" OR \"scheduling\" OR \"orchestration\" OR \"provisioning\")'")
    print("$ python3 paperworm.py -T --lib acm --dry '\"* learning\" (\"resource*\" OR \"task*\") (\"management\" OR \"scheduling\" OR \"orchestration\" OR \"provisioning\")'")
    print("$ python3 paperworm.py --https_proxy=127.0.0.1:3128 -T --from 2015 --lib acm '\"* learning\" (\"resource*\" OR \"task*\") (\"management\" OR \"scheduling\" OR \"orchestration\" OR \"provisioning\")'")


def do_search(search_string):
    global publications_found, current_pub, search_query
    publications_found = []

    if http_proxy or https_proxy:
        print("\n--Using HTTP proxy: " + http_proxy)
        print("--Using HTTPS proxy: " + https_proxy)
        set_proxy()

    print("\nStarting Google Scholar search.")
    print("--Using search string: \n" + search_string)

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
        current_pub = {}
        if pub:
            current_pub['LIBRARY'] = current_lib
            current_pub['YEAR'] = pub.bib['year']
            current_pub['CITATIONS'] = pub.bib['cites']
            current_pub['URL'] = pub.bib['url']
            current_pub['TITLE'] = pub.bib['title']
            if 'abstract' in pub.bib: current_pub['ABSTRACT'] = pub.bib['abstract']
            else: current_pub['ABSTRACT'] = 'NA'

            publications_found.append(current_pub)
        else:
            end = True

    print('\n{} publications found'.format(len(publications_found)))
    header = ['LIBRARY', 'YEAR', 'CITATIONS', 'URL', 'TITLE', 'ABSTRACT']
    csv_filename = 'raw-' + current_lib + '-' + str(filters.get_start_year()) + '-' + str(filters.get_final_year()) + '.csv'
    write_result(csv_filename, publications_found, header)

    logging.shutdown() # stop scholar.log logging

def process_pre_filtered_papers():
    global current_pub, publications_pre_filtered
    publications_pre_filtered = []

    print("\n...Applying pre filters.")

    for pub in publications_found:
        current_pub = {}
        if filters.pre_filter(pub):
            current_pub['LIBRARY'] = pub['LIBRARY']
            current_pub['YEAR'] = pub['YEAR']
            current_pub['CITATIONS'] = pub['CITATIONS']
            current_pub['URL'] = pub['URL']
            current_pub['TITLE'] = pub['TITLE']

            publications_pre_filtered.append(current_pub)

    header = ['LIBRARY', 'YEAR', 'CITATIONS', 'URL', 'TITLE']
    csv_filename = 'pre-' + current_lib + '-' + str(filters.get_start_year()) + '-' + str(filters.get_final_year()) + '.csv'
    write_result(csv_filename, publications_pre_filtered, header)


def process_post_filtered_papers():
    global current_pub, publications_post_filtered
    publications_post_filtered = []

    if not dry:
        print("\n...Starting files download and applying post filters.\n")

        for pub in publications_pre_filtered:
            current_pub = {'LIBRARY': pub['LIBRARY'], 'YEAR': pub['YEAR'], 'CITATIONS': pub['CITATIONS']}
            if download_paper(pub['URL']):
                current_pub['TITLE'] = pub['TITLE']
                publications_post_filtered.append(current_pub)

        header = ['LIBRARY', 'YEAR', 'CITATIONS', 'ID', 'PAGES', 'TITLE']
        csv_filename = 'post-' + current_lib + '-' + str(filters.get_start_year()) + '-' + str(filters.get_final_year()) + '.csv'
        write_result(csv_filename, publications_post_filtered, header)


def set_proxy():
    if ALLOW_PROXY_ON_SCHOLAR:
        pg = ProxyGenerator()
        pg.SingleProxy(http_proxy, https_proxy)
        scholarly.use_proxy(pg)


def parse_opts(opts, args):
    base_search_string = ""
    in_title = False
    global dry, http_proxy, https_proxy, libraries

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
            libraries = a.split(',')
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

    for lib in libraries:
        lib.lower()
        if lib != 'ieee' and lib != 'acm' and lib != 'sdirect' and lib != 'wiley' and lib != 'springer' and lib != 'mdpi' and lib != 'all':
            print("\nInvalid library selected.")
            sys.exit()
        if lib == 'all':
            libraries = ['ieee', 'acm', 'sdirect', 'wiley', 'springer', 'mdpi']
            break

    filters.verify_filters()

    if http_proxy and not https_proxy:
        https_proxy = http_proxy
    elif https_proxy and not http_proxy:
        http_proxy = https_proxy

    # Create search string in google scholar format
    if in_title:
        base_search_string += "allintitle: "

    base_search_string += args[0]

    return base_search_string


def write_result(filename, dict_data, csv_columns):
    try:
        with open(dir + filename, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in dict_data:
                writer.writerow(data)
    except IOError:
        print("I/O error")


def download_paper(base_url):
    cmd = 'echo \"Download URL not found\"'
    options = '-e robots=off -U "Mozilla" -A.pdf '
    env_proxy = None

    if http_proxy or https_proxy:
        env_proxy = {"http_proxy": http_proxy, "https_proxy": https_proxy}

    down_url, paper_id = translateURLs.get_download_url(current_lib, base_url)
    current_pub['ID'] = paper_id

    if down_url:
        cmd = 'wget ' + options + down_url + ' -O ' + dir + paper_id + '.pdf'
    else:
        logger.error("[FAILED]: Unable to generate download URL from base URL " + base_url)
        return False

    try:
        process = subprocess.run(cmd, shell=True, check=True, env=env_proxy)
    except subprocess.CalledProcessError:
        logger.error("[FAILED]: Unable to download from URL " + down_url)
        return False
    finally:
        logger.info("[OK]: Successful download from URL " + down_url)
        passed = filters.post_filter(paper_id + '.pdf', current_pub, logger)
        sleep(randint(10, 100))
        return passed


def main():
    global current_lib

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hT", [
                                   "help", "dry", "from=", "to=", "minpgs=", "lib=", "http_proxy=", "https_proxy="])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)
    base_search_str = parse_opts(opts, args)

    if not os.path.exists(dir):
        os.makedirs(dir)

    if dry:
        print("\n############## DRY RUN ##################")

    for lib in libraries:
        current_lib = lib
        search_str = base_search_str +  " +site:" + translateURLs.get_source_site(lib)

        do_search(search_str)
        process_pre_filtered_papers()
        process_post_filtered_papers()

        print("\n\n########################### FINISHED ####################")
        print("Processing for library " + current_lib + " ended. Please wait before the next query can be run...")
        sleep(randint(120, 180))

    return 0


if __name__ == '__main__':
    main()
