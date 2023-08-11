# Copyright (c) 2017 Ultimaker B.V.
# This example is released under the terms of the AGPLv3 or higher.

import os
from PyQt6.QtCore import pyqtSlot, pyqtProperty, pyqtSignal, QObject, QUrl, QDir  #To find the QML for the dialogue window.
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtQml import QQmlComponent, QQmlContext #To create the dialogue window.

from cura.CuraApplication import CuraApplication
from UM.Application import Application #To listen to the event of creating the main window, and get the QML engine.
from UM.Extension import Extension #The PluginObject we're going to extend.
from UM.Logger import Logger #Adding messages to the log.
from UM.PluginRegistry import PluginRegistry #Getting the location of Hello.qml.

from . import ApiHandler
from . import ProgressBar
import requests
import json
import time
import threading

class ExampleExtension(Extension, QObject): 
    def __init__(self):
        Extension.__init__(self)
        QObject.__init__(self)
    
        self.setMenuName("AI Extension")
        self.addMenuItem("Inspiration", self.sayHello) 
        self.hello_window = None
        self._currentImageId = ""
        self._imagesList = os.listdir(os.path.join(os.path.dirname(__file__), "images"))
        self._submitData = {}
        Application.getInstance().mainWindowChanged.connect(self.logMessage)


    def sayHello(self):
        if not self.hello_window: 
            self.hello_window = self._createDialogue()
        self.hello_window.show()

    def logMessage(self):
        Logger.log("i", "This is an example log message.")

    def _createDialogue(self):
        qml_file_path = os.path.join(PluginRegistry.getInstance().getPluginPath(self.getPluginId()), "Hello.qml")
        component = CuraApplication.getInstance().createQmlComponent(qml_file_path, {"manager" : self}) # 与qml文件绑定，使用manager进行通信

        return component
    
    def downloadImage(self, url):
        dir_path = os.path.join(os.path.dirname(__file__), "images", self._submitData["prompt"] + ".jpg")
        con = requests.get(url)
        with open(dir_path, "wb") as f:
            f.write(con.content)
    
    @pyqtSlot(str)
    def output(self, string):
        print(string)

    @pyqtProperty(str)
    def getQtCurrentDir(self):
        path = QDir.fromNativeSeparators(os.path.dirname(__file__))
        return path


    imagesListChanged = pyqtSignal()

    def setImagesList(self):
        dir_path = os.path.join(os.path.dirname(__file__), "images")
        self._imagesList = os.listdir(dir_path)
        self.imagesListChanged.emit()

    def getImagesList(self):
        return self._imagesList
    
    def clearImagesList(self):
        self._imagesList = []
        self.imagesListChanged.emit()
    
    imagesList = pyqtProperty(list, fget=getImagesList, notify=imagesListChanged)

    

    currentImageChanged = pyqtSignal()

    @pyqtSlot(str)
    def setCurrentImageId(self, id):
        self._currentImageId = id
        self.currentImageChanged.emit()

    def getCurrentImageId(self):
        return self._currentImageId
    
    currentImageId = pyqtProperty(str, fset=setCurrentImageId, fget=getCurrentImageId, notify=currentImageChanged)



    currentImageDeleted = pyqtSignal()

    @pyqtSlot()
    def removeImage(self):
        imageId = self.getCurrentImageId()
        target = os.path.join(os.path.dirname(__file__), "images", imageId)
        os.remove(target)
        self.currentImageDeleted.emit()
        self.setImagesList()
    
    @pyqtProperty(str)
    def deleteIconPath(self):
        path = "./deleteIcon.jpg"
        return path
    
    @pyqtSlot()
    def popDeleteBox(self):
        reply = QMessageBox.question(None, "提示", "确定要删除吗？", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply ==QMessageBox.StandardButton.Yes:
            self.removeImage()


    
    # @pyqtSlot()
    # def submitRequest(self):
    #     accessToken = self.getAccessToken()
    #     url = "https://aip.baidubce.com/rpc/2.0/ernievilg/v1/txt2imgv2?access_token=" + accessToken

    #     self._submitData["version"] = "v2"
    #     payload = json.dumps(self._submitData)
    #     headers = {
    #         'Content-Type': 'application/json',
    #         'Accept': 'application/json'
    #     }
        
    #     response = requests.request("POST", url, headers=headers, data=payload)
    #     print(response.text)
    #     return response

    # @pyqtSlot()
    # def getAccessToken(self):
    #     API_KEY = "W59kHvqE8ftttrkxoiladkKj"
    #     SECRET_KEY = "xdQ4GDP20HDY77ZpL0VZTqVWtckhv7uC"
    #     url = "https://aip.baidubce.com/oauth/2.0/token"
    #     params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    #     return str(requests.post(url, params=params).json().get("access_token"))
    

    # @pyqtSlot()
    # def searchResult(self):
    #     accessToken = self.getAccessToken()
    #     url = "https://aip.baidubce.com/rpc/2.0/ernievilg/v1/getImgv2?access_token=" + accessToken
    
    #     submitResponse = self.submitRequest()

    #     task_id = json.loads(submitResponse.text)["data"]["primary_task_id"]

    #     payload = json.dumps({
    #         "task_id": task_id
    #     })
    #     headers = {
    #         'Content-Type': 'application/json',
    #         'Accept': 'application/json'
    #     }
        
    #     time.sleep(20)
    #     response = requests.request("POST", url, headers=headers, data=payload)
    #     imageUrl = json.loads(response.text)["data"]['sub_task_result_list'][0]['final_image_list'][0]['img_url']
    #     self.downloadImage(imageUrl)
    #     self.clearImagesList()
    #     self.setImagesList()
    #     print(response.text)


    @pyqtSlot(str, str)
    def setSubmitData(self, key, value):
        if value != "":
            if key == "Width" or key == "Height":
                value = int(value)
            self._submitData[key.lower()] = value
        print(self._submitData)

    @pyqtSlot()
    def getImageViaApi(self):

        myHandler = ApiHandler.ApiHandler(self._submitData)
        myHandler.start()
        myHandler.join()
        imageUrl = myHandler.getRes()
        self.downloadImage(imageUrl)
        self.clearImagesList()
        self.setImagesList()
        print(imageUrl)

    # @pyqtSlot(str)
    # def readImage(path):
    #     img = Image.open(path)
    #     return img

    



