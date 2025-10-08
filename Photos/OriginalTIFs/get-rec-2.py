import csv

with open('OriginalTIFs.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if row['Title'] == '2008-901':
            print(row)
            break

