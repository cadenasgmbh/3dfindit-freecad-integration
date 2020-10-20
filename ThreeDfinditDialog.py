from PySide2 import QtCore
from PySide2 import QtGui
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
    msgBox.setWindowTitle("Ceriticate error")
    msgBox.setText("An invalid certificate was encountered while loading 3DFindIT. Procced anyway?")
    msgBox.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
    msgBox.setWindowModality(QtCore.Qt.ApplicationModal)
    if (msgBox.exec_() == QtWidgets.QMessageBox.Yes):
      return True
    return False

class ThreeDfinditDialog(QtWidgets.QDialog):
  def __init__(self):
    super(ThreeDfinditDialog, self).__init__()

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
    self.webView.setUrl("https://3dfindit.com/?webview=QTWEBCHANNEL")

  def showEvent(self, event):
    super(ThreeDfinditDialog, self).showEvent(event)

  def hideEvent(self, event):
    super(ThreeDfinditDialog, self).hideEvent(event)

  def event(self, event):
    if event.type() == QtCore.QEvent.ShortcutOverride:
        event.accept()
    return super(ThreeDfinditDialog, self).event(event)


def createWidget():
  # Create a new dock widget containing our dialog.
  browserWidget = QtWidgets.QDockWidget()
  browserWidget.setObjectName("3Dfindit_Widget")
  browserWidget.setWidget(ThreeDfinditDialog())

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