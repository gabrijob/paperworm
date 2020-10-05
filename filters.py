import datetime
import os
import sys
import PyPDF2
import logging


MAX_POSSIBLE_PAGES = 1000
DOWNLOAD_LOG_FILE = "download.log"
# Set up a specific logger with our desired output level
#logger = logging.getLogger('Download Log')
#logger.setLevel(logging.INFO)
# Add the log message handler to the logger
#handler = logging.FileHandler(DOWNLOAD_LOG_FILE)
#logger.addHandler(handler)

DIR = "papers/"
####################################################################################
start_year = None
fin_year = datetime.datetime.now().year
min_pgs = 1
####################################################################################
invalid_year_exclusions = 0
start_year_exclusions = 0
final_year_exclusions = 0
min_pgs_exclusions = 0

def verify_filters():
    if not start_year:
        print("\nMissing start year argument --from <YYYY>.")
        sys.exit()
    if fin_year < start_year:
        raise TypeError("Invalid Argument: start year should be bigger than final year.")
    if fin_year < 0 or start_year < 0:
        raise TypeError("Invalid Argument: start and final year should be bigger than 0.")


def pre_filter(publication):
    global start_year_exclusions, final_year_exclusions, invalid_year_exclusions
    passed = True

    if publication['YEAR'] == 'NA':
        passed = False
        invalid_year_exclusions += 1
        print('\nPublication "' + publication['TITLE'] + '" removed due to not having a valid publication year.')
        print('So far ' + str(invalid_year_exclusions) + ' exclusions were made for the same reason.')
    elif start_year > 0 and int(publication['YEAR']) < start_year:
        passed = False
        start_year_exclusions += 1
        print('\nPublication "' + publication['TITLE'] + '" removed for being to old.')
        print('So far ' + str(start_year_exclusions) + ' exclusions were made for the same reason.')
    elif int(publication['YEAR']) > fin_year:
        passed = False
        final_year_exclusions += 1
        print('\nPublication "' + publication['TITLE'] + '" removed for being to recent.')
        print('So far ' + str(final_year_exclusions) + ' exclusions were made for the same reason.')

    return passed


def post_filter(filename, current_pub, logger):
    global min_pgs_exclusions
    passed = True
    reader = None
    filepath = DIR + filename
    try:
        reader = PyPDF2.PdfFileReader(open(filepath, 'rb'))
    except PyPDF2.utils.PdfReadError:
        logger.warning("[FAILED]: The downloaded file for " + current_pub['LIBRARY'] + " " + current_pub['ID'] + " is not a valid PDF")
        os.remove(filepath)
        return False

    nb_pages = reader.getNumPages()

    current_pub['PAGES'] = nb_pages

    if nb_pages < min_pgs:
        os.remove(filepath)
        passed = False
        min_pgs_exclusions += 1
        print('\nPublication ' + current_pub['ID'] + ' removed for not having enough pages.')
        print('So far ' + str(min_pgs_exclusions) + ' exclusions were made for the same reason.')
    else:
        new_filename = current_pub['LIBRARY'] + '-' + str(current_pub['YEAR']) + '-' + str(current_pub['CITATIONS']) + '-' + str(current_pub['ID']) + '-' + str(current_pub['PAGES']) + '.pdf'
        os.rename(filepath, DIR + new_filename)

    return passed

def set_start_year(value):
    global start_year
    int_value = int(value)

    if int_value < 0 or int_value > datetime.datetime.now().year:
        raise TypeError("Invalid Argument: --from <YYYY> is not in a valid period of time.")

    start_year = int_value

def set_final_year(value):
    global fin_year
    int_value = int(value)

    if int_value < 0 or int_value > datetime.datetime.now().year:
        raise TypeError("Invalid Argument: --to <YYYY> is not in a valid period of time.")

    fin_year = int_value

def set_min_pgs(value):
    global min_pgs
    int_value = int(value)

    if min_pgs < 0 or min_pgs > MAX_POSSIBLE_PAGES:
        raise TypeError("Invalid Argument: --minpgs <min> is not in a physically possible value.")

    min_pgs = int_value

def get_start_year():
    return start_year

def get_final_year():
    return fin_year

def get_min_pgs():
    return min_pgs
