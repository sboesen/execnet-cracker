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
    import hashlib,base64,os
    hashes = []
    for i in range(len(dictionary)):

        word = dictionary[i].rstrip()

        if hash_type == 'ntlm':
            hash = hashlib.new('md4', word.encode('utf-16le','ignore')).hexdigest()
            if "$NT$"+hash == target_hash:
                channel.send([word, hash])

        elif hash_type == 'sha256':
            hash = hashlib.sha256(word.encode('utf-8')).digest()
            encoded = base64.b64encode(hash)
            final_hash = str(encoded)
            if final_hash == target_hash:
                channel.send([word, final_hash])

        if i != 0:
            if i % 30 == 0:
                # send progress
                hostname = os.uname()[1]
                channel.send(["progress",hostname, 30])

def master(gws,t,dictionary, mode):
    #split dictionary
    parted = chunks(dictionary, round(len(dictionary)/len(gws)))
    node_data = zip(gws, list(parted))
    channels,result = [],[]
    for node, data in node_data:
        channels.append(node.remote_exec(hash_list, target_hash = t, dictionary = data, hash_type = mode))
    mch = execnet.MultiChannel(channels)
    queue = mch.make_receive_queue(endmarker=42)
    done = 0
    progress = 0
    ended = 0
    while done == 0:
        result = queue.get()
        if result[1] == 42:
            ended = ended + 1
            if ended == len(gws):
                execnet.default_group.terminate()
                return [42,42]

        elif len(result[1]) == 3:
            progress = result[1][2] + progress
            print("Progress: " + str(progress) + " out of " + str(len(dictionary)) + "\r", end="")


        elif len(result[1]) == 2:
            # we got a hash back
            # print("len result is 2, result: " + str(result))
            execnet.default_group.terminate()
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

    channel, result = master(gws, input_hash, lines, mode)
    print("Progress: " + str(len(lines)) + " out of " + str(len(lines)))
    print(result)
    #if result:
        #print("Found hash: " + hash + " word: " + word)

if __name__ == '__main__':
    main() 

