import os
import unittest
from __main__ import vtk, qt, ctk, slicer

#
# PathTipTransform
#

class PathTipTransform:
  def __init__(self, parent):
    parent.title = "PathTipTransform" # TODO make this more human readable by adding spaces
    parent.categories = ["Examples"]
    parent.dependencies = []
    parent.contributors = ["Junichi Tokuda (BWH)"] # replace with "Firstname Lastname (Org)"
    parent.helpText = """
    This is an example of scripted loadable module bundled in an extension.
    """
    parent.acknowledgementText = """
    This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc. and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.
    self.parent = parent


#
# qPathTipTransformWidget
#

class PathTipTransformWidget:
  def __init__(self, parent = None):
    if not parent:
      self.parent = slicer.qMRMLWidget()
      self.parent.setLayout(qt.QVBoxLayout())
      self.parent.setMRMLScene(slicer.mrmlScene)
    else:
      self.parent = parent
    self.layout = self.parent.layout()
    if not parent:
      self.setup()
      self.parent.show()
    self.logic = PathTipTransformLogic()

  def setup(self):
    # Instantiate and connect widgets ...

    #
    # Reload and Test area
    #
    reloadCollapsibleButton = ctk.ctkCollapsibleButton()
    reloadCollapsibleButton.text = "Reload && Test"
    self.layout.addWidget(reloadCollapsibleButton)
    reloadFormLayout = qt.QFormLayout(reloadCollapsibleButton)

    # reload button
    # (use this during development, but remove it when delivering
    #  your module to users)
    self.reloadButton = qt.QPushButton("Reload")
    self.reloadButton.toolTip = "Reload this module."
    self.reloadButton.name = "PathTipTransform Reload"
    reloadFormLayout.addWidget(self.reloadButton)
    self.reloadButton.connect('clicked()', self.onReload)

    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    #
    # Target point (vtkMRMLMarkupsFiducialNode)
    #
    self.SourceSelector = slicer.qMRMLNodeComboBox()
    self.SourceSelector.nodeTypes = ( ("vtkMRMLMarkupsFiducialNode"), "" )
    self.SourceSelector.addEnabled = False
    self.SourceSelector.removeEnabled = False
    self.SourceSelector.noneEnabled = True
    self.SourceSelector.showHidden = False
    self.SourceSelector.renameEnabled = True
    self.SourceSelector.showChildNodeTypes = False
    self.SourceSelector.setMRMLScene( slicer.mrmlScene )
    self.SourceSelector.setToolTip( "Pick up the target point" )
    parametersFormLayout.addRow("Source: ", self.SourceSelector)

    #
    # Target point (vtkMRMLMarkupsFiducialNode)
    #
    self.DestinationSelector = slicer.qMRMLNodeComboBox()
    self.DestinationSelector.nodeTypes = ( ("vtkMRMLLinearTransformNode"), "" )
    self.DestinationSelector.addEnabled = True
    self.DestinationSelector.removeEnabled = False
    self.DestinationSelector.noneEnabled = True
    self.DestinationSelector.showHidden = False
    self.DestinationSelector.renameEnabled = True
    self.DestinationSelector.selectNodeUponCreation = True
    self.DestinationSelector.showChildNodeTypes = False
    self.DestinationSelector.setMRMLScene( slicer.mrmlScene )
    self.DestinationSelector.setToolTip( "Pick up the target point" )
    parametersFormLayout.addRow("Destination: ", self.DestinationSelector)

    #
    # check box to trigger transform conversion
    #
    self.EnableCheckBox = qt.QCheckBox()
    self.EnableCheckBox.checked = 0
    self.EnableCheckBox.setToolTip("If checked, take screen shots for tutorials. Use Save Data to write them to disk.")
    parametersFormLayout.addRow("Enable", self.EnableCheckBox)

    # connections
    self.EnableCheckBox.connect('toggled(bool)', self.onEnable)
    self.SourceSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.DestinationSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)

    # Add vertical spacer
    self.layout.addStretch(1)
    
  def cleanup(self):
    pass

  def onEnable(self, state):
    print ("onEnable() is called ")
    if (state == True and self.SourceSelector.currentNode() != None and self.DestinationSelector.currentNode() != None):
      self.logic.activateEvent(self.SourceSelector.currentNode(), self.DestinationSelector.currentNode())
    else:
      self.logic.deactivateEvent()
      self.EnableCheckBox.setCheckState(False)

  def onSelect(self):
    if (self.SourceSelector.currentNode() == None or self.DestinationSelector.currentNode() == None):
      self.logic.deactivateEvent()
      self.EnableCheckBox.setCheckState(False)

  def onReload(self,moduleName="PathTipTransform"):
    """Generic reload method for any scripted module.
    ModuleWizard will subsitute correct default moduleName.
    """
    globals()[moduleName] = slicer.util.reloadScriptedModule(moduleName)


#
# PathTipTransformLogic
#

class PathTipTransformLogic:
  """This class should implement all the actual 
  computation done by your module.  The interface 
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget
  """
  def __init__(self):
    #self.SourceTransformNode = None
    self.SourceFiducialNode = None
    self.DestinationTransformNode = None
    self.tag = 0;

  def convertTransform(self, caller, event):
    if (caller.IsA('vtkMRMLMarkupsFiducialNode') and event == 'ModifiedEvent'):
      nFiducials = self.SourceFiducialNode.GetNumberOfFiducials();
      if nFiducials >= 2:
        pos0 = [0.0, 0.0, 0.0, 0.0]
        pos1 = [0.0, 0.0, 0.0, 0.0]
        #self.SourceFiducialNode.GetNthFiducialPosition(nFiducials-2, pos0);
        #self.SourceFiducialNode.GetNthFiducialPosition(nFiducials-1, pos1);
        self.SourceFiducialNode.GetNthFiducialWorldCoordinates(nFiducials-2, pos0)
        self.SourceFiducialNode.GetNthFiducialWorldCoordinates(nFiducials-1, pos1)
        
        nz = vtk.vtkVector3d()
        nz.SetX(pos1[0]-pos0[0])
        nz.SetY(pos1[1]-pos0[1])
        nz.SetZ(pos1[2]-pos0[2])
        nz.Normalize()

        ny = vtk.vtkVector3d()
        ny.SetX(0.0)
        ny.SetY(0.0)
        ny.SetZ(1.0)

        nx = ny.Cross(nz)
        ny = nz.Cross(nx)
        nx.Normalized()
        ny.Normalized()
        nz.Normalized()

        print("(%f, %f, %f" % (nx[0], nx[1], nx[2]))
        print("(%f, %f, %f" % (ny[0], ny[1], ny[2]))
        print("(%f, %f, %f" % (nz[0], nz[1], nz[2]))

        matrix = self.DestinationTransformNode.GetMatrixTransformToParent()
        matrix.SetElement(0, 0, nx[0])
        matrix.SetElement(1, 0, nx[1])
        matrix.SetElement(2, 0, nx[2])
        matrix.SetElement(0, 1, ny[0])
        matrix.SetElement(1, 1, ny[1])
        matrix.SetElement(2, 1, ny[2])
        matrix.SetElement(0, 2, nz[0])
        matrix.SetElement(1, 2, nz[1])
        matrix.SetElement(2, 2, nz[2])
        matrix.SetElement(0, 3, pos1[0])
        matrix.SetElement(1, 3, pos1[1])
        matrix.SetElement(2, 3, pos1[2])

        self.DestinationTransformNode.SetMatrixTransformToParent(matrix)
      
      
  def activateEvent(self, srcNode, destNode):
    if (srcNode and destNode):
      #self.SourceTransformNode = srcNode
      self.SourceFiducialNode = srcNode
      self.DestinationTransformNode = destNode
      #self.tag = self.SourceTransformNode.AddObserver('ModifiedEvent', self.convertTransform)
      self.tag = self.SourceFiducialNode.AddObserver('ModifiedEvent', self.convertTransform)

  def deactivateEvent(self):
    #if (self.SourceTransformNode):
    if (self.SourceFiducialNode):
      #self.SourceTransformNode.RemoveObserver(self.tag)
      self.SourceFiducialNode.RemoveObserver(self.tag)
      #self.SourceTransformNode = None
      self.SourceFiducialNode = None
      self.DestinationTransformNode = None

