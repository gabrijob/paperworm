import datetime
import os
import sys
import PyPDF2


MAX_POSSIBLE_PAGES = 1000
####################################################################################
start_year = None
fin_year = datetime.datetime.now().year
min_pgs = 1
####################################################################################

def verify_filters():
    if not start_year:
        print("\nMissing start year argument --from <YYYY>.")
        sys.exit()
    if fin_year < start_year:
        raise TypeError("Invalid Argument: start year should be bigger than final year.")
    if fin_year < 0 or start_year < 0:
        raise TypeError("Invalid Argument: start and final year should be bigger than 0.")


def pre_filter(publication):
    passed = True

    if start_year > 0 and int(publication.bib['year']) < start_year:
        passed = False
    elif int(publication.bib['year']) > fin_year:
        passed = False

    return passed


def post_filter(filename, current_pub):
    passed = True
    reader = PyPDF2.PdfFileReader(open(filename, 'rb'))
    nb_pages = reader.getNumPages()

    current_pub.append(nb_pages)

    if nb_pages < min_pgs:
        os.remove(filename)
        passed = False
    else:
        new_filename = '-'.join([str(elem) for elem in current_pub])
        os.rename(filename, new_filename)

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
