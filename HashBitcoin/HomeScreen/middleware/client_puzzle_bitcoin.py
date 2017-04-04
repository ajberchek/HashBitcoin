from django.http import HttpResponse
from django.template import Context,loader
from django.shortcuts import render
import time
import socket
import json
import hashlib
import binascii
import os
import struct

clientDifficultyLevel = 3
btcStalenessMillis = 10000
puzzleExpireTime = 10000

current_milli_time = lambda: int(round(time.time() * 1000))

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





class ClientPuzzleBitcoinMiddleware(object):
    def __init__(self,get_response):
        self.get_response = get_response
        self.puzzleExpireTime = puzzleExpireTime
        self.extraNonce1 = 0
        self.extraNonce2Size = 0
        self.jobID = 0
        self.prevHash = 0
        self.coinb1 = 0
        self.coinb2 = 0
        self.merklebranch = []
        self.version = 0
        self.nbits = 0
        self.ntime = 0
        self.target_hexstr = 0
        self.lastCoinbaseCheck = current_milli_time()

        self.computeCoinbaseVals()

    def __call__(self,request):
        #todo change request.session to request.POST.get("solution") which should have the client's response
        #todo or just set the requst.session.solution to be the request.POST.get("solution")
        if(request.session.get("SolutionRecvdTime",None) is not None):
                #We have already received this solution lets see if it has expired
                if(request.session.get("SolutionRecvdTime") + self.puzzleExpireTime > current_milli_time()):
                    #solution is still valid, you shall pass
                    print("valid time")
                    return self.get_response(request)
                else:
                    del request.session["SolutionRecvdTime"]
                    print("Client just expired")
                    #response = http message with code to do the client puzzle
                    #solution is no longer valid, needs to reauth
                    #it will do that in the code below this outermost if statement
        else:
            if(request.method == "POST" and request.POST.get("PuzzleNonce",None) is not None):
                #Check users solution
                puzzleNonce = request.POST.get("PuzzleNonce")
                completeNonce = request.session.get("NoncePrefix") + puzzleNonce
                TotalHeader = request.session.get("TotalPacked") + completeNonce
                #print("Total Packed: " + str(TotalHeader))

                hashedData = hashlib.sha256(hashlib.sha256(binascii.unhexlify(TotalHeader)).digest()).digest()
                hashedData = binascii.hexlify(hashedData)
                print("Hashed Data: " + str(hashedData))
                #print("Hashed data int: " + str(int(hashedData,16)) + " modded: " + str(int(hashedData,16) % (16**clientDifficultyLevel)))


                if(int(hashedData,16) % (16**clientDifficultyLevel) == 0):
                    #solution is valid
                    #set recvd time
                    print("VALID")
                    print("added time")

                    request.session["SolutionRecvdTime"] = current_milli_time()
                    return self.get_response(request)
                else:
                    print("Invalid hash")
                    #response = http message with code to do the client puzzle
                    #solution is invalid, resend
                    #it will do this in the code below this outermost if statment
        if(request.session.get("SolutionRecvdTime",None) is None):
            print("No solution recvd time")
            self.giveClientMiningData(request)
            cont = {"TotalPacked": request.session.get("TotalPacked"), "NoncePrefix" : request.session.get("NoncePrefix"), "NZeros" : clientDifficultyLevel}
            print(cont)
            return render(context=cont, request=request, template_name='Client.html')

        print("Made it to the very outside")
        return self.get_response(request)


    def computeCoinbaseVals(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("stratum.slushpool.com", 3333))

        #retrieves mining information
        sock.send("""{"id": 1, "method": "mining.subscribe", "params": []}\n""".encode('utf-8'))
        data = sock.recv(4000)

        data = data.decode('utf-8')
        data = data.split('\n')
        lineJson1 = json.loads(data[0])["result"]
        lineJson2 = json.loads(data[2])["params"]

        self.extraNonce1 = lineJson1[1]
        self.extraNonce2Size = int(lineJson1[2])
        self.jobID = lineJson2[0]
        self.prevHash = lineJson2[1]
        self.coinb1 = lineJson2[2]
        self.coinb2 = lineJson2[3]
        self.merkleBranch = lineJson2[4]
        self.version = lineJson2[5]
        self.nbits = lineJson2[6]
        self.ntime = lineJson2[7]

        bits = int(self.nbits,16)
        exp = bits >> 24
        mant = bits & 0xffffff
        self.target_hexstr = '%064x' % (mant * (1<<(8*(exp - 3))))

        #adds us to the mining pool
        sock.send("""{"params": ["btcminer4242.worker1", "Nything"], "id": 2, "method": "mining.authorize"}\n""".encode('utf-8'))
        sock.recv(4000)

        self.lastCoinbaseCheck = current_milli_time()


    def giveClientMiningData(self,request):
        print("client mining data")

        if(self.lastCoinbaseCheck + btcStalenessMillis < current_milli_time()):
            self.computeCoinbaseVals()

        extraNonce2 = binascii.hexlify(os.urandom(self.extraNonce2Size)).decode('utf-8')

        coinbaseTransaction = hashlib.sha256(hashlib.sha256(binascii.unhexlify(self.coinb1) + binascii.unhexlify(self.extraNonce1) + binascii.unhexlify(extraNonce2) + binascii.unhexlify(self.coinb2)).digest()).digest()
        coinbaseTransaction = binascii.hexlify(coinbaseTransaction)

        merkleRoot = merkle(self.merkleBranch,coinbaseTransaction)

        #print("job id: " + str(jobID))
        #print("previous hash: " + str(prevHash))
        #print("coinbase 1: " + str(coinb1))
        #print("coinbase 2: " + str(coinb2))
        #print("Merkle branch: " + str(merkleBranch))
        #print("version: " + str(version))
        #print("nbits: " + str(nbits))
        #print("ntime: " + str(ntime))
        #print("Merkle root: " + str(merkleRoot))

        versionPack = struct.pack("<L",int(self.version,16))
        prevBlock = binascii.unhexlify(self.prevHash)
        mrklRoot = binascii.unhexlify(merkleRoot)[::-1]
        timeAndBits = struct.pack("<LL",int(self.ntime,16),int(self.nbits,16))

        totalPacked = versionPack + prevBlock + mrklRoot + timeAndBits
        totalPacked = binascii.hexlify(totalPacked).decode('utf-8')

        StartsWith = binascii.hexlify(os.urandom(2)).decode('utf-8')



        clientsTarget = '0'*clientDifficultyLevel + 'F'*(64-clientDifficultyLevel)





        request.session['NoncePrefix'] = StartsWith
        request.session['TotalPacked'] = totalPacked
        request.session['ClientTarget'] = clientDifficultyLevel
        request.session['ExtraNonce2'] = extraNonce2


        #self.submitBTCSoln(request)

        return request

    def submitBTCSoln(self,request):
        #todo test

        #nonceVal = request.POST.get("nonce")
        nonceVal = 42

        btcreq = "{\"params\": [\"btcminer4242.worker1\", " + str(self.jobID) + ", " + str(request.session.get("ExtraNonce2")) + ", " + str(self.ntime) + ", " + str(nonceVal) + "], \"id\": 4, \"method\": \"mining.submit\"}"

        btcreq = btcreq.encode('utf-8')

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("stratum.slushpool.com", 3333))
        sock.send(btcreq)
        print(sock.recv(4000))

