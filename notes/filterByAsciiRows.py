#!/opt/local/bin/python2.7

print '\nrunning...\n'

from xlrd import *
from xlsxwriter.workbook import Workbook

source = 'Nigeria practice file.xlsx'


# http://stackoverflow.com/questions/196345/how-to-check-if-a-string-in-python-is-in-ascii
def is_ascii(s):
    return all(ord(c) < 128 for c in s)

### STEP 1: ANALYSE WORKBOOK

workbook = open_workbook(filename=source,encoding_override="cp1252")
print 'file %s loaded.' % source

sheet1 = workbook.sheet_by_index(0)

colNames = {}
for col in range(0, sheet1.ncols):
  value = sheet1.cell(0,col)
  name = str(value.value)
  colNames[name] = col
  colNames[col] = name # this is a fun trick

asciiRows = []
nonAsciiRows = []
# note that we don't check the title row. 
for i in range(1,sheet1.nrows):
#for i in range(2):
  row = sheet1.row(i)
  success = True # is all the text on this row valid ASCII?
  for j in range(sheet1.ncols):
    cell = sheet1.cell(i,j)
    # type 1 means it contains text. see the xlrd docs. 
    if cell.ctype == 1: 
      if not is_ascii(cell.value): success = False
  if success == True:
    asciiRows.append(i) # store the row number
  else:
    nonAsciiRows.append(i) # store the row number

print 'asciiRows:', len(asciiRows)
print 'nonAsciiRows:', len(nonAsciiRows)


### STEP 2: OUTPUT 

output1 = 'Nigeria_locations_ascii_rows.xlsx' 
output2 = 'Nigeria_locations_NON_ascii_rows.xlsx'

print 'writing ascii rows to %s' % output1

wb1 = Workbook(output1)
sh1 = wb1.add_worksheet()

# write first row containing column names
row = 0
for i in range(sheet1.ncols):
  name = colNames[i]
  sh1.write(row, i, name)
  
# write all other rows
newRowNumber = 1 # we aren't leaving gaps / empty rows
for rowNumber in asciiRows:
  # write each cell of the row
  for colNumber in range(sheet1.ncols):
    cell = sheet1.cell(rowNumber, colNumber)
    sh1.write(newRowNumber, colNumber, cell.value)
  newRowNumber += 1
  

print 'writing NON ascii rows to %s' % output2

wb2 = Workbook(output2)
sh2 = wb2.add_worksheet()

# write first row containing column names
row = 0 
for colNumber in range(sheet1.ncols):
  name = colNames[colNumber]
  sh2.write(row, colNumber, name)
  
# write all other rows
newRowNumber = 1 # we aren't leaving gaps / empty rows
for rowNumber in nonAsciiRows:
  # write each cell of the row
  for colNumber in range(sheet1.ncols):
    cell = sheet1.cell(rowNumber, colNumber)
    sh2.write(newRowNumber, colNumber, cell.value)
  newRowNumber += 1

wb1.close()
wb2.close()





print '\ndone.\n'











