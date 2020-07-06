#Wir importieren verschiedene Funktionen der Bibliothek PyQt5.
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
#Wir holen uns alles aus werkzeug_funtionalitaet.
from .werkzeug_dialog import WerkzeugDialog
from qgis.core import Qgis, QgsProject, QgsMessageLog
#Wir legen eine Klasse namens CheckCRS an.
#Hier werden die Methoden (init, initGui, etc.) der Klasse definiert.
##iface soll eine Eigenschaft des Plugins werden.
class CheckCRS:

    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        self.startButton = QAction('Starten', self.iface.mainWindow())
        self.iface.addPluginToMenu('CheckCRS', self.startButton)
        #Ziel: Bei Klick auf den Starten-Button, soll die Methode maskeAufrufen
        #aufgerufen werden und die Gui soll angezeigt werden.
        self.startButton.triggered.connect(self.run)

    def unload(self):
        self.iface.removePluginMenu('CheckCRS', self.startButton)

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



