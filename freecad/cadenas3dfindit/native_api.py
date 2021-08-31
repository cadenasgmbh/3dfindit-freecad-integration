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
import os

from PySide2 import QtCore
from PySide2 import QtWidgets
from urllib.request import urlretrieve
from zipfile import ZipFile

import FreeCAD
import FreeCADGui
import Part
import ImportGui


class NativeAPI(QtCore.QObject):
  def __init__(self, webView):
    super(NativeAPI, self).__init__(webView)

    # Add an event that is fired when the API becomes ready to use.
    self.isReady = threading.Event()

  @QtCore.Slot()
  def ready(self):
    # Use API to set a few properties.
    from freecad.cadenas3dfindit import browser
    api = browser.getInstance().getThreeDAPI()
    api.setProperty("cadsystem", "freecad")
    api.setProperty("cadversion", "0.19")
    api.setProperty("productname", "FreeCAD")

    # We are now ready. We set this after queuing some API calls to
    # ensure they are processed before other calls.
    self.isReady.set()

  @QtCore.Slot("QJsonObject")
  def downloadReadyObject(self, downloadReadyObj):
    if downloadReadyObj["isExternal"]:
      # Alert user that this is a crawled document.
      msgBox = QtWidgets.QMessageBox()
      msgBox.setIcon(QtWidgets.QMessageBox.Question)
      msgBox.setWindowTitle("3DfindIT")
      msgBox.setText("Should 3DfindIT redirect you to the website of the supplier?")
      msgBox.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
      msgBox.setWindowModality(QtCore.Qt.ApplicationModal)
      if (msgBox.exec_() == QtWidgets.QMessageBox.Yes):
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
      stepFile = os.path.join(tmpExtractPath, downloadReadyObj["startFile"])
      # Import the file into the active FreeCAD document
      ImportGui.insert(stepFile, FreeCAD.ActiveDocument.Name)

      # Fit to view.
      FreeCADGui.SendMsgToActiveView("ViewFit")
