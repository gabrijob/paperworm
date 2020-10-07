# Authors:
# gabriel.grabher@inf.ufrgs.br
# kassianoj@gmail.com

# File with translating functions for source and download URLs from known libraries.

# You can add support for new libraries by writing bellow a "get_<lib_name>_download_url()" and a  "<lib_name>_site()" functions, with its respective entry in the switchers.



def get_ieee_download_url(url):
    splited_url = url.split('/')
    paper_id = splited_url[-2]

    down_url = '"http://ieeexplore.ieee.org/stampPDF/getPDF.jsp?tp=&isnumber=&arnumber=' + paper_id + '"'

    return down_url,paper_id


def get_acm_download_url(url):
    splited_url = url.split('/')
    paper_id = splited_url[-1]
    section_id = splited_url[-2]

    down_url = '"https://dl.acm.org/doi/pdf/' + section_id + '/' + paper_id + '"'

    return down_url,paper_id


def get_sdirect_download_url(url):
    splited_url = url.split('/')
    paper_id = splited_url[-1]

    down_url = '"https://www.sciencedirect.com/science/article/pii/' + paper_id + '/pdfft?isDTMRedir=true&download=true"'

    return down_url, paper_id

def get_wiley_download_url(url):
    splited_url = url.split('/')
    paper_id = splited_url[-1]
    section_id = splited_url[-2]

    down_url = '"https://onlinelibrary.wiley.com/doi/pdfdirect/' + section_id + '/' + paper_id + '?download=true"'

    return down_url,paper_id


def get_springer_download_url(url):
    splited_url = url.split('/')
    paper_id = splited_url[-1]
    section_id = splited_url[-2]

    down_url = '"https://link.springer.com/content/pdf/' + section_id + '/' + paper_id +'.pdf"'

    return down_url, paper_id


def get_mdpi_download_url(url):
    splited_url = url.split('/')
    paper_id = splited_url[-1]

    down_url = url + '/pdf'

    return down_url, paper_id


def get_download_url(library, base_url):
    switcher = {
        'ieee': get_ieee_download_url,
        'acm': get_acm_download_url,
        'sdirect': get_sdirect_download_url,
        'wiley': get_wiley_download_url,
        'springer': get_springer_download_url,
        'mdpi': get_mdpi_download_url
    }

    func = switcher.get(library, lambda: "Invalid library")
    return func(base_url)


def ieee_site():
    return "ieee.org"

def acm_site():
    return "dl.acm.org"

def sciencedirect_site():
    return "sciencedirect.com"

def wiley_site():
    return "onlinelibrary.wiley.com"

def springer_site():
    return "springer.com"

def mdpi_site():
    return "mdpi.com"

def get_source_site(library):
    switcher = {
        'ieee': ieee_site,
        'acm': acm_site,
        'sdirect': sciencedirect_site,
        'wiley': wiley_site,
        'springer': springer_site,
        'mdpi': mdpi_site
    }

    func = switcher.get(library, lambda: "Invalid library")
    return func()
