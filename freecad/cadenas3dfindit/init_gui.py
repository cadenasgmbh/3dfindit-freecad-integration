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

import os
import sys

import FreeCAD
import FreeCADGui



class CADENAS3DFinditShowCommand:
    def GetResources(self):
        from freecad.cadenas3dfindit import module_path
        return { 
          'Pixmap': os.path.join(module_path, "resources", "icons", "3dfindit.svg"),
          'MenuText': "3DfindIT",
          'ToolTip': "Show/Hide 3DfindIT"}

    def IsActive(self):
        return True

    def Activated(self):
        try:
          from freecad.cadenas3dfindit import dialog
          dialog.toggle()
        except Exception as e:
          FreeCAD.Console.PrintError(str(e) + "\n")


class CADENAS3DFinditGeoSearchCommand:
    def GetResources(self):
        from freecad.cadenas3dfindit import module_path
        return { 
          'Pixmap': os.path.join(module_path, "resources", "icons", "geomsearch.svg"),
          'MenuText': "Geometrical search",
          'ToolTip': "Start a geometrical search on 3DfindIT"}

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

    def Activated(self):
        # Make sure our dialog is visible.
        try:
          from freecad.cadenas3dfindit import dialog
          dialog.show()
        except Exception as e:
          FreeCAD.Console.PrintError(str(e) + "\n")
          return False

        # Export currently active document to STP.
        import tempfile
        tmpSTPPath = tempfile.mkstemp(prefix="3df", suffix=".stp")[1]
        FreeCAD.ActiveDocument.ActiveObject.Shape.exportStep(tmpSTPPath)

        # Read file into memory.
        with open(tmpSTPPath) as f:
          # Read the whole file.
          content = f.read()
          if not content:
            return False

        # Encode to Base64.
        import base64
        contentBase64 = base64.b64encode(content.encode("ascii")).decode()

        # Make sure we stay below 50 MB in size.
        if (len(contentBase64) > 50 * 1024 * 1024):
          FreeCAD.Console.PrintError("File exceeds the maximum size, aborting.\n")
          return False

        # Init geometrical search.
        from freecad.cadenas3dfindit import browser
        api = browser.getInstance().getThreeDAPI()
        api.startGeoSearch(os.path.basename(tmpSTPPath))

        # Split content into chunks and pass it to our API. Make sure to encode the
        # file as base64 before splitting the data into chunks. In JS, all chunks
        # are concatenated before decoding them.
        from textwrap import wrap
        for chunk in wrap(contentBase64, 2 * 1024 * 1024):
          api.sendGeoSearchChunkBase64(chunk)

        # Data send, run geometrical search.
        api.doGeoSearch(True)

        # Done!
        return True


class CADENAS3DFinditSketchSearchCommand:
    def GetResources(self):
        from freecad.cadenas3dfindit import module_path
        return {
          'Pixmap': os.path.join(module_path, "resources", "icons", "sketchsearch.svg"),
          'MenuText': "Sketch search",
          'ToolTip': "Start a sketch search on 3DfindIT"}

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

    def Activated(self):
        return True


class CADENAS3DfinditWorkbench(FreeCADGui.Workbench):
    def __init__(self):
        from freecad.cadenas3dfindit import module_path
        self.__class__.Icon = os.path.join(module_path, "resources", "icons", "3dfindit.svg")
        self.__class__.MenuText = "3DfindIT"
        self.__class__.ToolTip = "3DfindIT by CADENAS"

    def Initialize(self):
        self.commandList = ["CADENAS3Df_Show", "CADENAS3Df_GeoSearch"]
        self.appendToolbar("&3DfindIT", self.commandList)
        self.appendMenu("&3DfindIT", self.commandList)

    def Activated(self):
        return

    def Deactivated(self):
        return

    def ContextMenu(self, recipient):
        return

    def GetClassName(self): 
        return "Gui::PythonWorkbench"

freeCadVersion = int(FreeCAD.Version()[1])
pythonVersion = int(sys.version[0:1])
if freeCadVersion >= 19 and pythonVersion >= 3:
    FreeCADGui.addWorkbench(CADENAS3DfinditWorkbench())
    FreeCADGui.addCommand("CADENAS3Df_Show", CADENAS3DFinditShowCommand())
    FreeCADGui.addCommand("CADENAS3Df_GeoSearch", CADENAS3DFinditGeoSearchCommand())
else:
    if freeCadVersion < 19:
        FreeCAD.Console.PrintError("3DfindIT: FreeCAD below version 0.19 is not supported. Please update to a recent version.\n")

    if pythonVersion < 3:
        FreeCAD.Console.PrintError("3DfindIT: Python below version 3 is not supported. Please update to a recent version.\n")
