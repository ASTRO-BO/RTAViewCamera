#!/usr/bin/env python

############################################################################
#    begin                : Apr 2 2014
#    copyright            : (C) 2014 Valentina Fioretti, Andrea Zoli
#    email                : fioretti@iasfbo.inaf.it, zoli@iasfbo.inaf.it
############################################################################

############################################################################
#                                                                          #
#   This program is free software for non commercial purpose               #
#   and for public research institutes; you can redistribute it and/or     #
#   modify it under the terms of the GNU General Public License.           #
#   For commercial purpose see appropriate license terms                   #
#                                                                          #
############################################################################

# load modules
import pyfits
import Ice
import numpy as np
import sys
import random

# Chaco modules 
from chaco.api import ArrayPlotData, Plot, OverlayPlotContainer, jet, \
    ColorBar, LinearMapper, HPlotContainer
from enable.api import Window, Component, ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, Group, View
from chaco.tools.api import PanTool, ZoomTool, DragZoom

# Load slice definition
Ice.loadSlice('RTAViewCamera.ice')
Ice.updateModules()
import CTA

# open the fits file
hdulist_conf = pyfits.open('./PROD2_telconfig.fits.gz')
datal0_conf = hdulist_conf[1].data
colsl0_conf = hdulist_conf[1].columns
namesl0_field = colsl0_conf.names

datal1_conf = hdulist_conf[2].data
colsl1_conf = hdulist_conf[2].columns
namesl1_field = colsl1_conf.names

L0ID = datal0_conf.field(namesl0_field[0])
TelID = datal0_conf.field(namesl0_field[1])
TelType = datal0_conf.field(namesl0_field[2])
TelX = datal0_conf.field(namesl0_field[3])
TelY = datal0_conf.field(namesl0_field[4])
TelZ = datal0_conf.field(namesl0_field[5])
FocalLength = datal0_conf.field(namesl0_field[6])
FOV = datal0_conf.field(namesl0_field[7])
CameraScaleFactor = datal0_conf.field(namesl0_field[8])
CameraCentreOffset = datal0_conf.field(namesl0_field[9])
CameraRotation = datal0_conf.field(namesl0_field[10])
NPixel = datal0_conf.field(namesl0_field[11])
NPixel_active = datal0_conf.field(namesl0_field[12])
NSamples = datal0_conf.field(namesl0_field[13])
Sample_time_slice = datal0_conf.field(namesl0_field[14])
NGains = datal0_conf.field(namesl0_field[15])
HiLoScale = datal0_conf.field(namesl0_field[16])
HiLoThreshold = datal0_conf.field(namesl0_field[17])
HiLoOffset = datal0_conf.field(namesl0_field[18])
NTubesOFF = datal0_conf.field(namesl0_field[19])
NMirrors = datal0_conf.field(namesl0_field[20])
MirrorArea = datal0_conf.field(namesl0_field[21])

L0ID_L1 = datal1_conf.field(namesl1_field[1])
XTubeMM = datal1_conf.field(namesl1_field[3])
YTubeMM = datal1_conf.field(namesl1_field[4])
RTubeMM = datal1_conf.field(namesl1_field[5])
XTubeDeg = datal1_conf.field(namesl1_field[6])
YTubeDeg = datal1_conf.field(namesl1_field[7])
RTubeDeg = datal1_conf.field(namesl1_field[8])
TubeOFF = datal1_conf.field(namesl1_field[9])

NTel = len(TelID)
max_NPixel = int(max(NPixel))

# Looking for the telescope types for L, M and S
newTelType = list(set(TelType))
NTelType = np.zeros(len(newTelType))
listTelType = list(TelType)
for jtype in xrange(len(newTelType)):
    NTelType[jtype] = listTelType.count(newTelType[jtype])
    fromLargerToSmaller = np.argsort(NTelType)
    LType = newTelType[fromLargerToSmaller[0]]
    MType = newTelType[fromLargerToSmaller[1]]        
    SType = newTelType[fromLargerToSmaller[2]]
    
TelNames = ["SST", "MST", "LST"]
LSTelID = TelID[np.where(TelType == LType)]
LSTelX = TelX[np.where(TelType == LType)]
LSTelY = TelY[np.where(TelType == LType)]
MSTelID = TelID[np.where(TelType == MType)]
MSTelX = TelX[np.where(TelType == MType)]
MSTelY = TelY[np.where(TelType == MType)]
SSTelID = TelID[np.where(TelType == SType)]
SSTelX = TelX[np.where(TelType == SType)]
SSTelY = TelY[np.where(TelType == SType)]

# Setting the configuration and starting variables
size=(700,700)
title="CTA Quick Look"

class ViewerI(CTA.RTAViewCamera):
    def __init__(self, viewer):
        CTA.RTAViewCamera.__init__(self)
        self._viewer = viewer

    def update(self, pixels, current=None):
        print "UPDATE!"
        self._viewer.jtrig += 1
        self._viewer.CAMERAlayout.set_data('FADCpixel', pixels)


class ChacoViewCamera(HasTraits, Ice.Application):
    plot = Instance(Component)

    traits_view = View(
                  Group(
                  Item('plot', editor=ComponentEditor(size=size),
                  show_label=False),
                  orientation = "vertical"),
                  resizable=True, title=title,
                  width=size[0], height=size[1])

    def __init__(self, **traits):
        Ice.Application.__init__(self)
        HasTraits.__init__(self,**traits)

        plots = {}
        container = OverlayPlotContainer(padding = 50, fill_padding = True,
                                         bgcolor = "lightgray", use_backbuffer=True)
        self.jtrig = 0

        # HERE goes the telescope type given by the "real" event
        self.trigTelType = LType
        print self.trigTelType
        # HERE use RTAConfig to load the pixel position
        L0ID_sel = L0ID[np.where(TelType == self.trigTelType)]
        L0ID_sel = L0ID_sel[0]

        selXTubeMM = XTubeMM[np.where(L0ID_L1 == L0ID_sel)]
        selYTubeMM = YTubeMM[np.where(L0ID_L1 == L0ID_sel)]
        print len(selXTubeMM)

        # starting FADC values = 0
        startFADC = np.zeros(len(selXTubeMM))
        selFADC = startFADC

        # Plot all telescopes
        self.CAMERAlayout = ArrayPlotData()
        self.CAMERAlayout.set_data('xpixel', selXTubeMM)
        self.CAMERAlayout.set_data('ypixel', selYTubeMM)
        self.CAMERAlayout.set_data('FADCpixel', selFADC)

        self.plotCAMERA = Plot(self.CAMERAlayout)
        self.rCAMERA = self.plotCAMERA.plot(('xpixel', 'ypixel', 'FADCpixel'), type = "cmap_scatter", color_mapper=jet, marker = 'square')
        self.rCAMERA[0].marker_size = 6
        self.plotCAMERA.range2d.x_range.high = np.max(XTubeMM + 100.)
        self.plotCAMERA.range2d.x_range.low = np.min(XTubeMM - 100.)
        self.plotCAMERA.range2d.y_range.high = np.max(YTubeMM + 100.)
        self.plotCAMERA.range2d.y_range.low = np.min(YTubeMM - 100.)
        if (self.trigTelType == SType):    self.plotCAMERA.title = "SST"
        if (self.trigTelType == MType):    self.plotCAMERA.title = "MST"
        if (self.trigTelType == LType):    self.plotCAMERA.title = "LST"

        self.plotCAMERA.tools.append(PanTool(self.plotCAMERA))

        # The ZoomTool tool is stateful and allows drawing a zoom
        # box to select a zoom region.
        zoom = ZoomTool(self.plotCAMERA, tool_mode="box", always_on=False)
        self.plotCAMERA.overlays.append(zoom)

        # The DragZoom tool just zooms in and out as the user drags
        # the mouse vertically.
        dragzoom = DragZoom(self.plotCAMERA, drag_button="right")
        self.plotCAMERA.tools.append(dragzoom)

        #selection = ColormappedSelectionOverlay(self.plotCAMERA, fade_alpha=0.35, selection_type="mask")
        #self.plotCAMERA.overlays.append(selection)

        # Create the colorbar, handing in the appropriate range and colormap
        self.colorbar = ColorBar(index_mapper=LinearMapper(range=self.plotCAMERA.color_mapper.range),
                        color_mapper=self.plotCAMERA.color_mapper,
                        orientation='v',
                        resizable='v',
                        width=20,
                        padding=10)
        self.colorbar.plot = self.plotCAMERA
        self.colorbar.padding_top = self.plotCAMERA.padding_top
        self.colorbar.padding_bottom = self.plotCAMERA.padding_bottom

        # Create a container to position the plot and the colorbar side-by-side
        container = HPlotContainer(use_backbuffer = True)
        container.add(self.plotCAMERA)
        container.add(self.colorbar)
        container.bgcolor = "lightgray"

        self.plot = container
        print "End init."

    def run(self, args):
        print "running!"
        if len(args) > 1:
            print(self.appName() + ": too many arguments")
            return 1

        adapter = self.communicator().createObjectAdapter("RTAViewCamera")
        adapter.add(ViewerI(self), self.communicator().stringToIdentity("viewcamera"))
        adapter.activate()

		# start the chaco draw loop
        self.configure_traits()

        return 0

if __name__ == "__main__":
    viewer = ChacoViewCamera()
    sys.exit(viewer.main(sys.argv, "config.server"))
