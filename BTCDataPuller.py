import socket
import json
import hashlib
import binascii
import os
import struct

clientDifficultyLevel = 4

#below merkle function taken from: http://www.righto.com/2014/02/bitcoin-mining-hard-way-algorithms.html
# Hash pairs of items recursively until a single value is obtained
def merkle(hashList,coinbaseHashBin):
    merkle_root = coinbaseHashBin
    for h in hashList:
        merkle_root = hash2(merkle_root,h)
    return merkle_root

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
lineJson1 = json.loads(data[0])["result"]
print(lineJson1[2])
lineJson2 = json.loads(data[2])["params"]

extraNonce1 = lineJson1[1]
extraNonce2 = binascii.hexlify(os.urandom(int(lineJson1[2]))).decode('utf-8')


jobID = lineJson2[0]
prevHash = lineJson2[1]
coinb1 = lineJson2[2]
coinb2 = lineJson2[3]
merkleBranch = lineJson2[4]
version = lineJson2[5]
nbits = lineJson2[6]
ntime = lineJson2[7]



coinbaseTransaction = hashlib.sha256(hashlib.sha256(binascii.unhexlify(coinb1) + binascii.unhexlify(extraNonce1) + binascii.unhexlify(extraNonce2) + binascii.unhexlify(coinb2)).digest()).digest()
coinbaseTransaction = binascii.hexlify(coinbaseTransaction)

merkleRoot = merkle(merkleBranch,coinbaseTransaction)

#print("job id: " + str(jobID))
print("previous hash: " + str(prevHash))
#print("coinbase 1: " + str(coinb1))
#print("coinbase 2: " + str(coinb2))
#print("Merkle branch: " + str(merkleBranch))
#print("version: " + str(version))
#print("nbits: " + str(nbits))
#print("ntime: " + str(ntime))

#print("Merkle root: " + str(merkleRoot))

print(version)
versionPack = struct.pack("<L",int(version,16))
prevBlock = binascii.unhexlify(prevHash)
mrklRoot = binascii.unhexlify(merkleRoot)[::-1]
timeAndBits = struct.pack("<LL",int(ntime,16),int(nbits,16))

totalPacked = versionPack + prevBlock + mrklRoot + timeAndBits
totalPacked = binascii.hexlify(totalPacked)
print(totalPacked)

StartsWith = binascii.hexlify(os.urandom(2))
print(StartsWith)

bits = int(nbits,16)
exp = bits >> 24
mant = bits & 0xffffff
target_hexstr = '%064x' % (mant * (1<<(8*(exp - 3))))
print(target_hexstr)

clientsTarget = '0'*clientDifficultyLevel + 'F'*(64-clientDifficultyLevel)
print(clientsTarget)

sock.send("""{"params": ["btcminer4242.worker1", "Nything"], "id": 2, "method": "mining.authorize"}\n""".encode('utf-8'))
print(sock.recv(4000))




