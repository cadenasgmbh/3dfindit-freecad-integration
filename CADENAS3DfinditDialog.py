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

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtWebChannel
from PySide2 import QtWebEngineWidgets

import Browser
import FreeCADGui

# We only have one widget, ever.
browserWidget = None


class MyWebEnginePage(QtWebEngineWidgets.QWebEnginePage):
  def certificateError(self, error):
    # Ask the user if we should proceed with an invalid certifacate.
    msgBox = QtWidgets.QMessageBox()
    msgBox.setIcon(QtWidgets.QMessageBox.Warning)
    msgBox.setWindowTitle("3DfindIT.com")
    msgBox.setText("An invalid certificate was encountered while loading 3DFindIT. Proceed anyway?")
    msgBox.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
    msgBox.setWindowModality(QtCore.Qt.ApplicationModal)
    if (msgBox.exec_() == QtWidgets.QMessageBox.Yes):
      return True
    return False

class CADENAS3DfinditDialog(QtWidgets.QDialog):
  def __init__(self):
    super(CADENAS3DfinditDialog, self).__init__()

    # Setup the widget.
    self.setObjectName("3Dfindit_Dialog")
    self.setWindowTitle("3DfindIT.com")
    
    # Grab the browser.
    self.webView = Browser.getInstance().getBrowser()
    self.threeDNativeAPI = Browser.getInstance().getThreeDNativeAPI()

    # Prepare a simple layout.
    self.layout = QtWidgets.QVBoxLayout(self)
    self.layout.addLayout(QtWidgets.QHBoxLayout())
    self.layout.addWidget(self.webView)

    # Setup our page. We want our own profile so other browsers in FreeCAD
    # can't interfere with our cookies. We also want our own page so we can
    # ask the user what to do if we encounter any SSL errors.
    profile = QtWebEngineWidgets.QWebEngineProfile("3Dfindit", self.webView)
    page = MyWebEnginePage(QtWebEngineWidgets.QWebEnginePage(profile, self.webView))
    self.webView.setPage(page)

    # Setup our webchannel.
    channel = QtWebChannel.QWebChannel(self)
    channel.registerObject("ThreeDfinditNativeAPI", self.threeDNativeAPI)
    self.webView.page().setWebChannel(channel)

    # Re-direct to landing page.
    self.webView.setUrl("https://freecad-embedded.3dfindit.com/?webview=QTWEBCHANNEL")

  def showEvent(self, event):
    super(CADENAS3DfinditDialog, self).showEvent(event)

  def hideEvent(self, event):
    super(CADENAS3DfinditDialog, self).hideEvent(event)

  def event(self, event):
    if event.type() == QtCore.QEvent.ShortcutOverride:
        event.accept()
    return super(CADENAS3DfinditDialog, self).event(event)


def createWidget():
  # Create a new dock widget containing our dialog.
  browserWidget = QtWidgets.QDockWidget()
  browserWidget.setObjectName("3Dfindit_Widget")
  browserWidget.setWidget(CADENAS3DfinditDialog())

  # Add dock widget to main window.
  FreeCADGui.getMainWindow().addDockWidget(QtCore.Qt.RightDockWidgetArea, browserWidget)

  # Return!
  return browserWidget

def getWidget():
  # Have we already created the widget?
  global browserWidget
  if browserWidget is None:
    browserWidget = createWidget()
  return browserWidget

def show():
  getWidget().toggleViewAction().setChecked(True)

def hide():
  getWidget().toggleViewAction().setChecked(False)

def toggle():
  getWidget().toggleViewAction().trigger()