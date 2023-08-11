import os
import threading
import time
import json
import requests

class ApiHandler(threading.Thread):
    def __init__(self, submitData):
        threading.Thread.__init__(self)
        self._submitData = submitData
        self._accessToken = ""

    # thread在创建后会运行run函数
    def run(self):
        self.getAccessToken()
        submitRes = self.submitRequest()
        searchRes = self.searchResult(submitRes)
        self._result =  searchRes

    def getRes(self):
        try:
            return self._result
        except Exception:
            return None

    # 返回用户AccessToken
    def getAccessToken(self):
        API_KEY = "W59kHvqE8ftttrkxoiladkKj"
        SECRET_KEY = "xdQ4GDP20HDY77ZpL0VZTqVWtckhv7uC"
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials", 
            "client_id": API_KEY, 
            "client_secret": SECRET_KEY
        }
        self._accessToken = str(requests.post(url, params=params).json().get("access_token"))
    
    
    # 提交API请求，返回格式为json
    def submitRequest(self):

        accessToken = self._accessToken
        url = "https://aip.baidubce.com/rpc/2.0/ernievilg/v1/txt2imgv2?access_token=" + accessToken

        self._submitData["version"] = "v2"
        payload = json.dumps(self._submitData)

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.text)
        return response


    # 获取API结果，返回格式为json
    def searchResult(self, res):

        accessToken = self._accessToken
        url = "https://aip.baidubce.com/rpc/2.0/ernievilg/v1/getImgv2?access_token=" + accessToken
    
        task_id = json.loads(res.text)["data"]["primary_task_id"]

        payload = json.dumps({
            "task_id": task_id
        })

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        time.sleep(20)
        response = requests.request("POST", url, headers=headers, data=payload)
        imageUrl = json.loads(response.text)["data"]['sub_task_result_list'][0]['final_image_list'][0]['img_url']
        print(response.text)
        return imageUrl


    # def setSubmitData(self, key, value):
    #     if value != "":
    #         if key == "Width" or key == "Height":
    #             value = int(value)
    #         self._submitData[key.lower()] = value
    #     print(self._submitData)
