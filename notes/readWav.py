#!/usr/bin/env python

def main():
  
  import sys
  filename = sys.argv[-1]
  f = open(filename, 'rb')
  bytes = f.read()
  f.close()

  bytes2 = [str(byte).encode('hex') for byte in bytes]
  bytes2 = ''.join(bytes2)
  
  chunkID = bytes2[0:4*2]
  if chunkID == '52494646': print 'yes'
  else: print 'no'

  #print bytesToString(bytes2)  
  




def bytesToString(bytes):
  s = ''
  count = 0
  for i in range(len(bytes)):
    byte = bytes[i]
    s += str(byte).encode('hex') + ' '
    count += 1
    if count >= 10:
      s += '\n'
      count = 0
  if s[-1] == '\n': s = s[:-1]
  return s




  
if __name__ == '__main__': main()





