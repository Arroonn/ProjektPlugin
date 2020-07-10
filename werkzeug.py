#Wir importieren verschiedene Funktionen der Bibliothek PyQt5 sowie das os Modul.
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import os
from qgis.utils import iface

from qgis.core import Qgis, QgsProject, QgsMessageLog

#Wir holen uns alles aus werkzeug_dialog.
from .werkzeug_dialog import WerkzeugDialog

#Wir legen eine Klasse namens QuickQA an und definieren ihre Methoden.
#Diese Klasse ist das funktionale Kernstück des Plugins.
class QuickQA:

    def __init__(self, iface):
        self.iface = iface #Das iface soll eine Eigenschaft des Plugins werden.

    def initGui(self):
        #Dynamischer Pfad zum Plugin-Directory, in dem die werkzeug.py liegt
        self.plugin_dir = os.path.dirname(__file__)
        #Eine Action wird erstellt, die sich die Icons aus dem Plugin Directory
        self.action1 = QAction(QIcon(os.path.join(self.plugin_dir,"icons","CheckAll.svg")), u"Check CRS of all layers", self.iface.mainWindow())
        self.action2 = QAction(QIcon(os.path.join(self.plugin_dir,"icons","CheckActive.svg")), u"Check CRS of active layers", self.iface.mainWindow())
        self.action3 = QAction(QIcon(os.path.join(self.plugin_dir,"icons","CheckSelected.svg")), u"Check CRS of selected layers", self.iface.mainWindow())
        self.action4 = QAction(QIcon(os.path.join(self.plugin_dir,"icons","CheckSpatialIndex.svg")), u"Check Spatial Indexes", self.iface.mainWindow())
        
        #Beim Klick auf die 'Check CRS of...'-Buttons soll die jeweilige run-Methode ausgeführt werden.
        self.action1.triggered.connect(self.runAll)
        self.action2.triggered.connect(self.runActive)
        self.action3.triggered.connect(self.runSelected)
        self.action4.triggered.connect(self.runSIndex)
        
        #Adds actions to the plugins menu
        self.iface.addPluginToMenu('QuickQA', self.action1)
        self.iface.addPluginToMenu('QuickQA', self.action2)
        self.iface.addPluginToMenu('QuickQA', self.action3)
        self.iface.addPluginToMenu('QuickQA', self.action4)
        
        #Toolbar Menu
        self.popupMenu = QMenu( self.iface.mainWindow() )
        self.popupMenu.addAction( self.action1 )
        self.popupMenu.addAction( self.action2 )
        self.popupMenu.addAction( self.action3 )
        #self.popupMenu.addAction( self.action4 )

        #QToolbutton class provides a quick-access button to commands; used inside QToolBar.
        self.toolButton = QToolButton()
        #self.toolButtonSIndex = QToolButton() ##2. Button - auch mit QToolButton() ???

        self.toolButton.setMenu( self.popupMenu ) # 
        self.toolButton.setDefaultAction( self.action1 ) #setzt action1 als default action
        self.toolButton.setPopupMode( QToolButton.InstantPopup ) #macht, dass Dropdown aufpoppt beim Klick auf Toolbarbutton
        
        self.myToolBar = self.iface.mainWindow().findChild( QToolBar, u'QuickQA' )
        if not self.myToolBar:
            self.myToolBar = self.iface.addToolBar( u'QuickQA' ) #macht die Toolbar anwählbar in der Toolbarliste
            self.myToolBar.setObjectName( u'QuickQA' )
        
        self.toolbar_object = self.myToolBar.addWidget( self.toolButton )
        #self.toolbar_object_SIndex = self.myToolBar.addWidget( self.toolButtonSIndex )
        
        self.gui = WerkzeugDialog(self.iface.mainWindow())
        self.list_badCRS = self.gui.list_badCRS
        

    def unload(self):
        self.iface.removePluginMenu('QuickQA', self.action1)
        self.iface.removePluginMenu('QuickQA', self.action2)
        self.iface.removePluginMenu('QuickQA', self.action3)
        self.iface.removePluginMenu('QuickQA', self.action4)
        
        self.popupMenu.removeAction(self.action1)
        self.popupMenu.removeAction(self.action2)
        self.popupMenu.removeAction(self.action3)
        self.popupMenu.removeAction(self.action4)
        self.iface.removeToolBarIcon(self.toolbar_object)
        del self.popupMenu
        self.popupMeni = None
        del self.toolButton
        self.toolButton = None
        del self.myToolBar

    def runAll(self):
        layers = QgsProject.instance().mapLayers()
        project_crs = QgsProject.instance().crs().authid()
        bad_crs_layer=[]
        
        layertree_root=QgsProject.instance().layerTreeRoot()

        for layer_id, layer in layers.items():
            
            if layer.crs().authid()!=project_crs:
                bad_crs_layer.append(layer.name())
                if layertree_root.findLayer(layer.id()).isVisible():
                    QgsMessageLog.logMessage("Layer "+layer.name()+" ist sichtbar", 'QuickQA', level=Qgis.Info)

        # self.gui = WerkzeugDialog(self.iface.mainWindow())
        # self.gui.list_badCRS.addItems(bad_crs_layer)
        # self.gui.show()
        self.showResult(bad_crs_layer)
        
    def runActive(self):
        layers = QgsProject.instance().mapLayers()
        project_crs = QgsProject.instance().crs().authid()
        bad_crs_layer=[]
        
        layertree_root=QgsProject.instance().layerTreeRoot()

        #for layer_id, layer in layers.items():
        for layer in iface.mapCanvas().layers():
            if layertree_root.findLayer(layer.id()).isVisible():
                if layer.crs().authid()!=project_crs:
                    bad_crs_layer.append(layer.name())

        #print(bad_crs_layer)
        
        #self.gui = WerkzeugDialog(self.iface.mainWindow())
        # self.gui.list_badCRS.addItems(bad_crs_layer)
        # self.gui.show()
        self.showResult(bad_crs_layer)
        
    def runSelected(self):
        layers = self.iface.layerTreeView().selectedLayers()
        project_crs = QgsProject.instance().crs().authid()
        bad_crs_layer=[]
        
        layertree_root=QgsProject.instance().layerTreeRoot()

        #for layer_id, layer in layers.items():
        for layer in layers:
            if layer.crs().authid()!=project_crs:
                bad_crs_layer.append(layer.name())

        #print(bad_crs_layer)
        self.showResult(bad_crs_layer)
        
    def runSIndex(self):
        pass
        
    def showResult(self,result_layer):
            
            if len(result_layer)<1:
                self.showMessage('Alle betreffenden Layer stimmen mit dem Kooridinatensystem des Projekts überein.', Qgis.Success)
                #self.logMessage('Alle betreffenden Layer stimmen mit dem Kooridinatensystem des Projekts überein.')
                #sichtbar im Protokoll widget im Reiter QuickQA
            else:
                self.list_badCRS.clear()
                self.list_badCRS.addItems(result_layer)
                self.gui.show()


                
    def showMessage(self, message, level=Qgis.Info, target=None, shortmessage=None):
        """
        
        :param message:
        :param level:
        :param target:
        
        """
        if target is None:
            target = self.iface
            target.messageBar().pushMessage(message, level, self.iface.messageTimeout())
        else:
            if shortmessage is not None:
                target.bar.pushMessage("Info", shortmessage, level=level)
            self.iface.messageBar().pushMessage(message, level, self.iface.messageTimeout())


    def logMessage(self, message, level=Qgis.Info):
        QgsMessageLog.logMessage(message, 'QuickQA', level)



