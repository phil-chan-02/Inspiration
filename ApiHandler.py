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

    # thread在start后会运行run函数
    def run(self):
        self.getApiConfiguration()
        self.getAccessToken()
        submitRes = self.submitRequest()
        searchRes = self.searchResult(submitRes)
        self._result =  searchRes

    def getRes(self):
        try:
            return self._result
        except Exception:
            return None
        
    # 从json文件中读取用户key等信息
    def getApiConfiguration(self):
        file_path = os.path.join(os.path.dirname(__file__), "ApiConfiguration.json")
        with open(file_path, "r") as file:
            data = json.load(file)
            self._apiConfiguration = data

    # 返回用户AccessToken
    def getAccessToken(self):
        API_KEY = self._apiConfiguration["api_key"]
        SECRET_KEY = self._apiConfiguration["secret_key"]
        url = self._apiConfiguration["access_token_url"]
        params = {
            "grant_type": "client_credentials", 
            "client_id": API_KEY, 
            "client_secret": SECRET_KEY
        }
        self._accessToken = str(requests.post(url, params=params).json().get("access_token"))
    
    
    # 提交API请求，返回格式为json
    def submitRequest(self):

        accessToken = self._accessToken
        url = self._apiConfiguration["submit_request_url"] + accessToken

        self._submitData["version"] = "v2"
        payload = json.dumps(self._submitData)

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        response = requests.request("POST", url, headers=headers, data=payload)
        return response


    # 获取API结果，返回格式为json
    def searchResult(self, res):

        accessToken = self._accessToken
        url = self._apiConfiguration["search_result_url"] + accessToken
    
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
        return imageUrl

    # 检查提交数据的合法性
    def checkValidation(self):
        try:
            prompt = self._submitData["prompt"]
            width = self._submitData["width"]
            height = self._submitData["height"]
        except KeyError:
            return False
        ret1 = self.is_all_chinese(prompt)
        resolution = (width, height)
        resoList = [(512, 512), (640, 360), (360, 640), (1024, 1024), (1280, 720), (720, 1280)]
        if resolution in resoList and ret1:
            return True
        else: 
            return False

    def is_all_chinese(self, strs):
        for _char in strs:
            if not '\u4e00' <= _char <= '\u9fa5':
                return False
        return True

