
import csv

def read_csv(file_csv):
    data = []
    objs = []
    reader = csv.reader(open(file_csv, "r"), delimiter=';')
    for row in reader:
        data.append(row)
    for i in data[1:]:
        obj = {}
        for j in range(0, len(data[0])):
            obj[data[0][j]] = i[j]
        objs.append(obj)
    return objs
