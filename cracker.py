#!/usr/bin/env python3
import hashlib,sys,getopt,io,base64,execnet

def chunks(l, n):
    return [l[i:i+n] for i in range(0, len(l), n)]

def get_sha256(word):
    word = word.rstrip()
    hash = hashlib.sha256(word.encode('utf-8')).digest()
    encoded = base64.b64encode(hash)
    return str(encoded,'ascii')

client_code = """
import hashlib, base64, socket
def hash_list(channel,target_hash,dictionary):
    for i in range(len(dictionary)):
        word = dictionary[i]
        hash = hashlib.sha256(word.encode('utf-8')).digest()
        encoded = base64.b64encode(hash)
        final_hash = str(encoded, 'ascii')
        if final_hash == target_hash:
            channel.send(dictionary[i])
"""

def master(gws,t,dictionary):
    #split dictionary
    parted = chunks(dictionary, round(len(dictionary)/len(gws)))
    node_data = zip(gws, list(parted))
    channels,result = [],[]
    for node, data in node_data:
        channels.append(node.remote_exec(hash_list, target_hash = t, dictionary = data))
    for c in channels: result += c.receive()
    return result

def create_group(hostfile):
    f = open('slacr.hosts')
    gws = [execnet.makegateway("ssh="+host.rstrip()) for host in f]
    return gws

def main():
    mode = sys.argv[1] #default sha256
    wordlist = sys.argv[2]
    input_hash = sys.argv[3]
    f = io.open(wordlist,"r",-1,'utf-8')
    lines = f.readlines()
    
    gws = create_group('slacr.hosts')

    result = master(gws, input_hash, lines)
    print(result)

    # print(lines)
    # for line in lines:
    #     if string == input_hash:
    #         print("Calculated hash: " + line +  " == " + string)


if __name__ == '__main__':
    main() 

