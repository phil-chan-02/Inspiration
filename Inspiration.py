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
import requests
import json
import time
import threading

class Inspiration(Extension, QObject): 
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
    
    # 将Api生成的图片下载到本地
    def downloadImage(self, url):
        dir_path = os.path.join(os.path.dirname(__file__), "images", self._submitData["prompt"] + ".jpg")
        con = requests.get(url)
        with open(dir_path, "wb") as f:
            f.write(con.content)
    
    
    @pyqtProperty(str)
    def getQtCurrentDir(self):
        path = QDir.fromNativeSeparators(os.path.dirname(__file__))
        return path

    # 该信号主要用于更新box中的图片列表
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

    
    # 该信号用于更新当前显示的图片
    currentImageChanged = pyqtSignal()

    @pyqtSlot(str)
    def setCurrentImageId(self, id):
        self._currentImageId = id
        self.currentImageChanged.emit()

    def getCurrentImageId(self):
        return self._currentImageId
    
    currentImageId = pyqtProperty(str, fset=setCurrentImageId, fget=getCurrentImageId, notify=currentImageChanged)



    # 该信号用来控制图片的删除
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
        imageId = self.getCurrentImageId()
        if imageId == "": return 
        reply = QMessageBox.question(None, "提示", "确定要删除吗？", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply ==QMessageBox.StandardButton.Yes:
            self.removeImage()


    # 获取用户在控制台输入的数据并保存
    @pyqtSlot(str, str)
    def setSubmitData(self, key, value):
        if value != "":
            if key == "Width" or key == "Height":
                value = int(value)
            self._submitData[key.lower()] = value

    # 通过ApiHandler获取图片
    @pyqtSlot()
    def getImageViaApi(self):

        myHandler = ApiHandler.ApiHandler(self._submitData)
        if myHandler.checkValidation() == False:
            reply = QMessageBox.warning(None, "警告", "请求图片格式有误", QMessageBox.StandardButton.Cancel)
        else:
            myHandler.start()
            myHandler.join()
            imageUrl = myHandler.getRes()
            self.downloadImage(imageUrl)
            self.clearImagesList()
            self.setImagesList()

    



