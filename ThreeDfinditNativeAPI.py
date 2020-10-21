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

import tempfile
import threading
import webbrowser

from enum import Enum
from PySide2 import QtCore
from urllib.request import urlretrieve
from zipfile import ZipFile

import FreeCADGui
import Part


class ThreeDfinditNativeAPI(QtCore.QObject):
  def __init__(self, webView):
    super(ThreeDfinditNativeAPI, self).__init__(webView)

    # Add an event that is fired when the API becomes ready to use.
    self.isReady = threading.Event()

  @QtCore.Slot()
  def ready(self):
    # Use API to set a few properties.
    import Browser
    api = Browser.getInstance().getThreeDAPI()
    api.setProperty("cadsystem", "freecad")
    api.setProperty("cadversion", "0.19")
    api.setProperty("productname", "FreeCAD")

    # We are now ready. We set this after queuing some API calls to
    # ensure they are processed before other calls.
    self.isReady.set()

  @QtCore.Slot("QJsonObject")
  def downloadReadyObject(self, downloadReadyObj):
    if downloadReadyObj["isExternal"]:
      # Open in system browser.
      webbrowser.open(downloadReadyObj["url"], new=2)
    else:
      # Download file.
      tmpDownloadPath = tempfile.mkstemp(prefix="3df", suffix=".zip")[1]
      urlretrieve(downloadReadyObj["url"], tmpDownloadPath)

      # Extract zip file.
      tmpExtractPath = tempfile.mkdtemp(prefix="3df")
      with ZipFile(tmpDownloadPath, 'r') as zip:
          zip.extractall(tmpExtractPath)

      # Open the STEP file.
      stepFile = tmpExtractPath + "\\" + downloadReadyObj["startFile"]
      Part.show(Part.read(stepFile), downloadReadyObj["NB"])

      # Fit to view.
      FreeCADGui.SendMsgToActiveView("ViewFit")