from PySide2 import QtWidgets
from PySide2 import QtWebEngineWidgets

import ThreeDfinditNativeAPI
import ThreeDfinditAPI


class Browser:
  # Our single browser.
  _instance = None

  def __init__(self):
    if self._instance is None:
      # Init browser.
      self.webView = QtWebEngineWidgets.QWebEngineView()
      self.webView.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

      # Init native API.
      self.threeDNativeAPI = ThreeDfinditNativeAPI.ThreeDfinditNativeAPI(self.webView)

      # Init API.
      self.threeDAPI = ThreeDfinditAPI.ThreeDfinditAPI(self.webView, self.threeDNativeAPI)
    else:
      raise Exception("Invalid state.")

  def getBrowser(self):
    return self.webView

  def getThreeDNativeAPI(self):
    return self.threeDNativeAPI

  def getThreeDAPI(self):
    return self.threeDAPI

def getInstance():
    if Browser._instance == None:
      Browser._instance = Browser()
    return Browser._instance