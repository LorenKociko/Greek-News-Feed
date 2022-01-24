import csv

def csv_to_dict(fname):
    try:
        dl = [] # new list of dictionaries
        infile = csv.DictReader(open(fname, 'r', encoding='utf-8'), delimiter=';')
        for row in infile:
            dl.append(row)
        return [dict(x) for x in dl]
    except: return []

def dict_to_csv(dl, fname):
    try:
        with open(fname, 'w', encoding='utf-8') as fout:
            w = csv.DictWriter(fout, fieldnames=dl[0].keys(), delimiter=';')
            w.writerow(dict((x,x) for x in dl[0].keys()))
            w.writerows(dl)
        return True
    except: return False