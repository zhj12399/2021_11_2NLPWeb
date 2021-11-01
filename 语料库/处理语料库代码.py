import os

filepathen = './en'
filelisten = os.listdir(filepathen)
filelisten = sorted(filelisten)
print(filelisten)

filepathcn = './cn'
filelistcn = os.listdir(filepathcn)
filelistcn = sorted(filelistcn)
print(filelistcn)

print(len(filelistcn), len(filelisten))
cnfile = ""
for filename in filelistcn:
    with open('./cn/' + filename) as f:
        for line in f:
            cnfile += line
with open("cnfile.txt","w") as f:
    f.write(cnfile)

enfile = ""
for filename in filelisten:
    with open('./en/' + filename) as f:
        for line in f:
            enfile += line
with open("enfile.txt","w") as f:
    f.write(enfile)
