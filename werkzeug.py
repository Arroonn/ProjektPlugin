#Wir importieren verschiedene Funktionen der Bibliothek PyQt5.
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
#Wir holen uns alles aus werkzeug_dialog.
from .werkzeug_dialog import WerkzeugDialog
from qgis.core import Qgis, QgsProject, QgsMessageLog
#Wir legen eine Klasse namens CheckCRS an.
#Hier werden die Methoden (init, initGui, etc.) der Klasse definiert.
##iface soll eine Eigenschaft des Plugins werden.
import os

class CheckCRS:

    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        self.startButton = QAction('Starten', self.iface.mainWindow())
        self.iface.addPluginToMenu('CheckCRS', self.startButton)
        #Ziel: Bei Klick auf den Starten-Button, soll die Methode maskeAufrufen
        #aufgerufen werden und die Gui soll angezeigt werden.
        self.startButton.triggered.connect(self.run)
        
        #2 Optionen zur Layerauswahl
        #plugin directory pfad ermitteln
        #pfad = r"C:\Users\nkn\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\ProjektPlugin\icons"
        self.plugin_dir = os.path.dirname(__file__)
        #ansprechen des Icons mein_icon.svg im Plugin directory
        self.action1 = QAction(QIcon(os.path.join(self.plugin_dir,"icons","noun_internet_checkAll.svg")), u"CheckAll", self.iface.mainWindow())
        self.action2 = QAction(QIcon(os.path.join(self.plugin_dir,"icons","noun_savetheworld_checkActive.svg")), u"CheckActive", self.iface.mainWindow())
        self.popupMenu = QMenu( self.iface.mainWindow() )
        self.popupMenu.addAction( self.action1 )
        self.popupMenu.addAction( self.action2 )


        self.toolButton = QToolButton()

        self.toolButton.setMenu( self.popupMenu )
        self.toolButton.setDefaultAction( self.action1 )
        self.toolButton.setPopupMode( QToolButton.InstantPopup )

        self.iface.addToolBarWidget( self.toolButton )


    def unload(self):
        self.iface.removePluginMenu('CheckCRS', self.startButton)
        self.popupMenu.removeAction(self.action1)
        self.popupMenu.removeAction(self.action2)
        del self.popupMenu
        del self.toolButton

    def run(self):
        layers = QgsProject.instance().mapLayers()
        project_crs = QgsProject.instance().crs().authid()
        bad_crs_layer=[]
        
        layertree_root=QgsProject.instance().layerTreeRoot()

        for layer_id, layer in layers.items():
            
            if layer.crs().authid()!=project_crs:
                bad_crs_layer.append(layer.name())
                if layertree_root.findLayer(layer.id()).isVisible():
                    QgsMessageLog.logMessage("Layer "+layer.name()+" ist sichtbar", 'CheckCRS', level=Qgis.Info)

        #print(bad_crs_layer)
        
        self.gui = WerkzeugDialog(self.iface.mainWindow())
        self.gui.listWidget.addItems(bad_crs_layer)
        self.gui.show()
        



