#Wir importieren verschiedene Funktionen der Bibliothek PyQt5 sowie das os Modul.
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import os
from qgis.utils import iface

from qgis.core import Qgis, QgsProject, QgsMessageLog

#Wir holen uns alles aus werkzeug_dialog.
from .werkzeug_dialog import WerkzeugDialog

#Wir legen eine Klasse namens CheckCRS an und definieren ihre Methoden (init, initGui, etc.).
##iface soll eine Eigenschaft des Plugins werden.
class CheckCRS:

    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        #Erzeugt Buttons im Plugin-Menu
        self.startButtonAll = QAction('Check CRS of all layers', self.iface.mainWindow())
        self.startButtonActive = QAction('Check CRS of active layers', self.iface.mainWindow())
        self.iface.addPluginToMenu('QuickQA', self.startButtonAll)
        self.iface.addPluginToMenu('QuickQA', self.startButtonActive)
        #Ziel: Bei Klick auf die 'Check CRS of...'-Buttons soll die jeweilige run-Methode aufgerufen werden.
        self.startButtonAll.triggered.connect(self.runAll)
        self.startButtonActive.triggered.connect(self.runActive)
        
        #ToolbarIcon mit zwei Optionen zur Layerauswahl
        self.plugin_dir = os.path.dirname(__file__)
        #ansprechen der Icons im Plugin directory
        self.action1 = QAction(QIcon(os.path.join(self.plugin_dir,"icons","CheckAll.svg")), u"Check CRS of all layers", self.iface.mainWindow())
        self.action2 = QAction(QIcon(os.path.join(self.plugin_dir,"icons","CheckActive.svg")), u"Check CRS of active layers", self.iface.mainWindow())
        self.action3 = QAction(QIcon(os.path.join(self.plugin_dir,"icons","CheckSelected.svg")), u"Check CRS of selected layers", self.iface.mainWindow())
        
        self.action1.triggered.connect(self.runAll)
        self.action2.triggered.connect(self.runActive)
        self.action3.triggered.connect(self.runSelected)
        self.popupMenu = QMenu( self.iface.mainWindow() )
        self.popupMenu.addAction( self.action1 )
        self.popupMenu.addAction( self.action2 )
        self.popupMenu.addAction( self.action3 )

        self.toolButton = QToolButton()

        self.toolButton.setMenu( self.popupMenu )
        self.toolButton.setDefaultAction( self.action1 )
        self.toolButton.setPopupMode( QToolButton.InstantPopup )
        
        self.myToolBar = self.iface.mainWindow().findChild( QToolBar, u'Quality Assurance' )
        if not self.myToolBar:
            self.myToolBar = self.iface.addToolBar( u'Quality Assurance' )
            self.myToolBar.setObjectName( u'Quality Assurance' )
            
            
        self.toolbar_object = self.myToolBar.addWidget( self.toolButton )
        
        self.gui = WerkzeugDialog(self.iface.mainWindow())
        self.listWidget = self.gui.listWidget
        

    def unload(self):
        self.iface.removePluginMenu('QuickQA', self.startButtonAll)
        self.iface.removePluginMenu('QuickQA', self.startButtonActive)
        self.popupMenu.removeAction(self.action1)
        self.popupMenu.removeAction(self.action2)
        self.popupMenu.removeAction(self.action3)
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

        #print(bad_crs_layer)
        
        # self.gui = WerkzeugDialog(self.iface.mainWindow())
        # self.gui.listWidget.addItems(bad_crs_layer)
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
        # self.gui.listWidget.addItems(bad_crs_layer)
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
        
    def showResult(self,result_layer):
            
            if len(result_layer)<1:
                self.showMessage('Alles schick. Alle betreffenden Layer haben das gleiche CRS', Qgis.Success)
                #self.logMessage('alle Layer tipptopp')   #sichtbar im Protokoll widget im Reiter QuickQA
            else:
                self.listWidget.clear()
                self.listWidget.addItems(result_layer)
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



