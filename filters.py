import datetime
import os
import PyPDF2

####################################################################################
start_year = 2015
fin_year = datetime.datetime.now().year
min_pgs = 5
####################################################################################

def verify_filters():
    if fin_year < start_year:
        raise TypeError("Invalid Argument: start year should be bigger than final year")
    if fin_year < 0 or start_year < 0:
        raise TypeError("Invalid Argument: start and final year should be bigger than 0")

    if min_pgs < 0:
        raise TypeError("Invalid Argument: minimum number of pages should be higher than 0")


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

def get_start_year():
    return start_year

def get_final_year():
    return fin_year

def get_min_pgs():
    return min_pgs
