from django.http import JsonResponse


def SucResponse(**kwargs):
    resp_json = {}
    if kwargs:
        resp_json["payload"] = kwargs
    resp_json["errCode"] = 0
    resp_json["errMsg"] = "suc"
    return JsonResponse(resp_json)


def FailResponse(errCode, errMsg):
    resp_json = {}
    resp_json["payload"] = {}
    resp_json["errCode"] = errCode
    resp_json["errMsg"] = errMsg
    return JsonResponse(resp_json)


def NoLoginResponse():
    resp_json = {}
    resp_json["payload"] = {}
    resp_json["errCode"] = 210
    resp_json["errMsg"] = "Please login."
    resp = JsonResponse(resp_json)
    resp.status_code = 210
    return resp

def TokenExpireResponse():
    resp_json = {}
    resp_json["payload"] = {}
    resp_json["errCode"] = 211
    resp_json["errMsg"] = "Token is invalid or expired."
    resp = JsonResponse(resp_json)
    resp.status_code = 211
    return resp
