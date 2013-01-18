#!/usr/bin/env python3
import hashlib,sys,getopt,io,base64,execnet

def chunks(l, n):
    return [l[i:i+n] for i in range(0, len(l), n)]

def get_sha256(word):
    word = word.rstrip()
    hash = hashlib.sha256(word.encode('utf-8')).digest()
    encoded = base64.b64encode(hash)
    return str(encoded,'ascii')

def hash_list(channel,target_hash,dictionary, hash_type):
    import hashlib,base64
    hashes = []
    for i in range(len(dictionary)):
        word = dictionary[i].rstrip()

        if hash_type == 'ntlm':
            hash = hashlib.new('md4', word.encode('utf-16le','ignore')).hexdigest()
            hashes.append([word,"$NT$"+ hash])

        elif hash_type == 'sha256':
            hash = hashlib.sha256(word.encode('utf-8')).digest()
            encoded = base64.b64encode(hash)
            final_hash = str(encoded)
            hashes.append([word,final_hash])

    channel.send(hashes)

def master(gws,t,dictionary, mode):
    #split dictionary
    parted = chunks(dictionary, round(len(dictionary)/len(gws)))
    node_data = zip(gws, list(parted))
    channels,result = [],[]
    for node, data in node_data:
        channels.append(node.remote_exec(hash_list, target_hash = t, dictionary = data, hash_type = mode))
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

    result = master(gws, input_hash, lines, mode)
    for word, hash in result:
        if hash == input_hash:
            print("Found hash: " + hash + " word: " + word)
            return
    print("Got input: " + input_hash)
    print("No hashes found. Look for yourself:")
    print(result)

if __name__ == '__main__':
    main() 

