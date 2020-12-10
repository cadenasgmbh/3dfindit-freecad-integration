#***************************************************************************
#*    Copyright (C) 2020 CADENAS GmbH
#*
#*    This library is free software; you can redistribute it and/or
#*    modify it under the terms of the GNU Lesser General Public
#*    License as published by the Free Software Foundation; either
#*    version 2.1 of the License, or (at your option) any later version.
#*
#*    This library is distributed in the hope that it will be useful,
#*    but WITHOUT ANY WARRANTY; without even the implied warranty of
#*    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#*    Lesser General Public License for more details.
#*
#*    You should have received a copy of the GNU Lesser General Public
#*    License along with this library; if not, write to the Free Software
#*    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301
#*    USA
#***************************************************************************

from PySide2 import QtWidgets
try:
  from PySide2 import QtWebEngineWidgets
except ImportError:
  raise Exception("Missing package. Please install: python3-pyside2.qtwebenginewidgets.")


class Browser:
  # Our single browser.
  _instance = None

  def __init__(self):
    if self._instance is None:
      # Init browser.
      self.webView = QtWebEngineWidgets.QWebEngineView()
      self.webView.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

      # Init native API.
      from freecad.cadenas3dfindit import native_api
      self.threeDNativeAPI = native_api.NativeAPI(self.webView)

      # Init API.
      from freecad.cadenas3dfindit import api
      self.threeDAPI = api.API(self.webView, self.threeDNativeAPI)
    else:
      raise Exception("Invalid state.")

  def getBrowser(self):
    return self.webView

  def getThreeDNativeAPI(self):
    return self.threeDNativeAPI

  def getThreeDAPI(self):
    return self.threeDAPI

def getInstance():
    if Browser._instance is None:
      Browser._instance = Browser()
    return Browser._instance
