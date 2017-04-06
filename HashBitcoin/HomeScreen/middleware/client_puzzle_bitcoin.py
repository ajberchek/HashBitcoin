from django.http import HttpResponse
import time

current_milli_time = lambda: int(round(time.time() * 1000))

class ClientPuzzleBitcoinMiddleware(object):
    def __init__(self,get_response):
        self.get_response = get_response
        self.puzzleExpireTime = 10000

    def __call__(self,request):
        #todo change request.session to request.POST.get("solution") which should have the client's response
        #todo or just set the requst.session.solution to be the request.POST.get("solution")
        print(request.session.items())
        if(request.session.get("solution",None) is not None):
            if(request.session.get("SolutionRecvdTime",None) is not None):
                #We have already received this solution lets see if it has expired
                if(request.session.get("SolutionRecvdTime") + self.puzzleExpireTime > current_milli_time()):
                    #solution is still valid, you shall pass
                    print("valid time")
                    return self.get_response(request)
                else:
                    del request.session["SolutionRecvdTime"]
                    #solution is no longer valid, needs to reauth
                    #it will do that in the code below this outermost if statement
            else:
                #Check users solution
                if(request.session.get("solution") == "hi"):
                    #solution is valid
                    #set recvd time
                    print("added time")

                    request.session["SolutionRecvdTime"] = current_milli_time()
                    return self.get_response(request)
                #else:
                    #solution is invalid, resend
                    #it will do this in the code below this outermost if statment

        print("Here have a cookie!")
        request.session["solution"] = "hi"
        response = HttpResponse("Refresh the page to get access!")

        return response

    def getBtcVals(self):
        user = "btcminer4242.worker1"


