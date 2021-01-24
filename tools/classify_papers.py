import subprocess
import csv
import math

directoryPath = '../papers/'
start_year = 3000
final_year = 0
avg_nb_cites = 0
avg_nb_pages = 0
dp = 0
all_papers = []
nb_papers_per_lib = {}

# Find post csv files
file_list_1 = subprocess.check_output(['find', directoryPath, '-name', 'post*.csv'])
file_list_2 = file_list_1.split('\n'.encode())
file_list = file_list_2[:-1]

# Read csv files and initialize variables
for i,file_name in enumerate(file_list):
    paper_count = 0
    lib = ''

    with open(file_name, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            lib = row['LIBRARY']
            if int(row['YEAR']) > final_year:
                final_year = int(row['YEAR'])
            elif int(row['YEAR']) < start_year:
                start_year = int(row['YEAR'])

            avg_nb_cites += int(row['CITATIONS'])

            if row['PAGES'] != 'NA':
                avg_nb_pages += int(row['PAGES'])

            paper_count += 1
            row['GOOGLE_POINTS'] = paper_count
            row['FILENAME'] = row['LIBRARY'] + '-' + str(row['YEAR']) + '-' + str(row['CITATIONS']) + '-' + str(row['ID']) + '-' + str(row['PAGES']) + '.pdf'
            all_papers.append(row)

        nb_papers_per_lib[lib] = paper_count

avg_nb_pages = avg_nb_pages / len(all_papers)
avg_nb_cites = avg_nb_cites / len(all_papers)

# Calculate standard deviation of the number of citations
for paper in all_papers:
    total = int(nb_papers_per_lib[paper['LIBRARY']])
    google_points = (total - int(paper['GOOGLE_POINTS']) + 1) / total
    paper['GOOGLE_POINTS'] = round(google_points, 2)
    dp += (int(paper['CITATIONS']) - avg_nb_cites)**2
dp = dp / (len(all_papers) - 1)
dp = math.sqrt(dp)

print("Mean number of cites " + str(avg_nb_cites))
print("Mean number of pages " + str(avg_nb_pages))
print("Standard deviation of cites: " + str(dp))
print("Start year: " + str(start_year))
print("Final year: " + str(final_year))

# Calculate papers' ranking
for paper in all_papers:
    cite_points = 0
    pages_points = 0
    #if int(paper['CITATIONS']) > 448:
    #    cite_points = 2
    #else:
    #    cite_points = 2*int(paper['CITATIONS']) /448

    if (int(paper['CITATIONS']) - avg_nb_cites) > 2*dp:
        cite_points = 1
    elif int(paper['CITATIONS']) > avg_nb_cites:
        cite_points = 0.5 + 0.5*(int(paper['CITATIONS']) - avg_nb_cites)/(2*dp)
    else:
        cite_points = 0.5 * int(paper['CITATIONS']) / avg_nb_cites
    paper['CITE_POINTS'] = round(cite_points, 2)

    if paper['PAGES'] == 'NA':
        pages_points = 0
    elif int(paper['PAGES']) > avg_nb_pages:
        pages_points = 1
    else:
        pages_points = int(paper['PAGES']) / avg_nb_pages
    paper['PAGES_POINTS'] = round(pages_points, 2)

    year_points = (int(paper['YEAR'])-start_year + 1) / (final_year - start_year + 1)
    paper['YEAR_POINTS'] = round(year_points, 2)

    google_points = paper['GOOGLE_POINTS']

    classification = year_points + cite_points + pages_points + google_points
    paper['CLASSIFICATION'] = round(classification, 2)

paper_ranking = sorted(all_papers, key=lambda i: i['CLASSIFICATION'], reverse=True)

# Write ranking on csv file
csv_name = directoryPath + 'ranking.csv'
csv_columns = ['CLASSIFICATION',
               'GOOGLE_POINTS',
               'YEAR_POINTS',
               'CITE_POINTS',
               'PAGES_POINTS',
               'FILENAME',
               'TITLE']
with open(csv_name, 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    writer.writerow(csv_columns)
    for paper in paper_ranking:
        writer.writerow([paper['CLASSIFICATION'],
                         paper['GOOGLE_POINTS'],
                         paper['YEAR_POINTS'],
                         paper['CITE_POINTS'],
                         paper['PAGES_POINTS'],
                         paper['FILENAME'],
                         paper['TITLE']])
