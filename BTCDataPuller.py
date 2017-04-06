import socket
import json
import hashlib
import binascii

#below merkle function taken from: http://www.righto.com/2014/02/bitcoin-mining-hard-way-algorithms.html
# Hash pairs of items recursively until a single value is obtained
def merkle(hashList,coinbaseHashBin):
    merkle_root = coinbaseHashBin
    for h in hashList:
        merkle_root = hash2(merkle_root,h)
    return binascii.hexlify(merkle_root)

def hash2(a, b):
    # Reverse inputs before and after hashing
    # due to big-endian / little-endian nonsense
    a1 = binascii.unhexlify(a)[::-1]
    b1 = binascii.unhexlify(b)[::-1]
    h = hashlib.sha256(hashlib.sha256(a1+b1).digest()).digest()
    return binascii.hexlify(h[::-1])


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("stratum.slushpool.com", 3333))

sock.send("""{"id": 1, "method": "mining.subscribe", "params": []}\n""".encode('utf-8'))
data = sock.recv(4000)

data = data.decode('utf-8')
data = data.split('\n')
lineJson1 = json.loads(data[1])
print(lineJson1)
lineJson2 = json.loads(data[2])["params"]

extraNonce1 =1
extraNonce2 = 1

jobID = lineJson2[0]
prevHash = lineJson2[1]
coinb1 = lineJson2[2]
coinb2 = lineJson2[3]
merkleBranch = lineJson2[4]
version = lineJson2[5]
nbits = lineJson2[6]
ntime = lineJson2[7]

#merkleRoot = merkle(merkleBranch)

print("job id: " + str(jobID))
print("previous hash: " + str(prevHash))
print("coinbase 1: " + str(coinb1))
print("coinbase 2: " + str(coinb2))
print("Merkle branch: " + str(merkleBranch))
print("version: " + str(version))
print("nbits: " + str(nbits))
print("ntime: " + str(ntime))


#print("Computed merkle root: " + str(merkleRoot))


sock.send("""{"params": ["btcminer4242.worker1", "Nything"], "id": 2, "method": "mining.authorize"}\n""".encode('utf-8'))
print(sock.recv(4000))




