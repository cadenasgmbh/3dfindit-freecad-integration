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
import threading
import queue


class JsTaskWatcher(QtCore.QObject):
  # Prepare a simple signal that we emit once the
  # blocking queue has some work for us.
  hasWork = QtCore.Signal(str)

  class JsTask:
    def __init__(self, order, script):
      # Save parameters for later.
      self.order = order
      self.script = script

    def __lt__(self, other):
      return self.order < other.order

    def __le__(self, other):
      return self.order <= other.order

    def __gt__(self, other):
      return self.order > other.order

    def __ge__(self, other):
      return self.order >= other.order

  def __init__(self, threeDNativeAPI):
    # Init our base class.
    QtCore.QObject.__init__(self)
    
    # Save the native API object for later.
    self.threeDNativeAPI = threeDNativeAPI

    # We'll use a priority-based queue instead of the normal queue.
    self.queue = queue.PriorityQueue()

    # Just an incrementing number to ensure all calls with the same
    # priority are done in the order they are placed.
    self.order = 0

    # Configure the thread that will do the actual work.
    self.thread = threading.Thread(target=self._executor, daemon=True)
    self.thread.start()

  def _executor(self):
    while True:
      # Wait. We need to make sure the API is ready before taking
      # a task. Any amount of time can pass while waiting for a task
      # so we need to make sure the API is still ready after we got a
      # task.
      self.threeDNativeAPI.isReady.wait()
      task = self.queue.get(block=True)[1]
      self.threeDNativeAPI.isReady.wait()

      # Run the task. There is still a slim chance that we run into
      # a reload very, very shortly before this task is run. Nothing
      # I can do...
      self.hasWork.emit(task.script)

  def submit(self, script, priority):
      # Queue up the task and increment the order.
      self.queue.put((priority, JsTaskWatcher.JsTask(self.order, script)))
      self.order += 1

class API:
  def __init__(self, webView, three3DNativeAPI):
    self.webView = webView
    self.watcher = JsTaskWatcher(three3DNativeAPI)
    self.watcher.hasWork.connect(self._hasWork)

  def _hasWork(self, script):
    self.webView.page().runJavaScript("(function(){ return " + script + ";})();")

  def runJs(self, script, priority=50):
    self.watcher.submit(script, priority)

  def loadByMident(self, mident):
    self.runJs("window.ThreeDfinditAPI.loadByMident('" + mident + "')")

  def loadByMidentBase64(self, midentBase64):
    self.runJs("window.ThreeDfinditAPI.loadByMidentBase64('" + midentBase64 + "')")

  def loadByIDStr(self, idStr):
    self.runJs("window.ThreeDfinditAPI.loadByIDStr('" + idStr + "')")

  def loadByIDStrBase64(self, idStrBase64):
    self.runJs("window.ThreeDfinditAPI.loadByIDStrBase64('" + idStrBase64 + "')")

  def setProperty(self, prop, value):
    self.runJs("window.ThreeDfinditAPI.setProperty('" + prop + "', '" + value + "')", 1)

  def startGeoSearch(self, filename):
    self.runJs("window.ThreeDfinditAPI.startGeoSearch('" + filename + "')")

  def sendGeoSearchChunkBase64(self, chunk):
    self.runJs("window.ThreeDfinditAPI.sendGeoSearchChunkBase64('" + chunk + "')")

  def endGeoSearchChunkBase64(self):
    self.runJs("window.ThreeDfinditAPI.endGeoSearchChunkBase64()")

  def doGeoSearch(self, openSearchResults):
    self.runJs("window.ThreeDfinditAPI.doGeoSearch(" + str(openSearchResults).lower() + ")")

  def doSketchSearch(self, front, top, side, type, openSearchResults):
    self.runJs("window.ThreeDfinditAPI.doSketchSearch('" + front + "', '" + top + "', '" + side + "', '" + type + "', " + str(openSearchResults).lower() + ")")