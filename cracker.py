#!/usr/bin/env python3
import hashlib,sys,getopt,io,base64

def main():
    mode = sys.argv[1] #default sha256
    wordlist = sys.argv[2]
    input_hash = sys.argv[3]
    f = io.open(wordlist,"r",-1,'utf-8')
    lines = f.readlines()
    print(lines)
    for line in lines:
        line = line.rstrip()
        hash = hashlib.sha256(line.encode('utf-8')).digest()
        encoded = base64.b64encode(hash)
        string = str(encoded,'ascii')
        if string == input_hash:
            print("Calculated hash: " + line +  " == " + string)


if __name__ == '__main__':
    main() 

