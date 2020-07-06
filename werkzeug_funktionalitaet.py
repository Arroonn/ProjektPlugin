from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
import os
from qgis.core import *
import processing

#Vorbereitung: Wir kombinieren Pfad zum Ordner und die Ui-Datei zu einem Pfad.
pluginPath = os.path.dirname(__file__)
pathUi = os.path.join(pluginPath,'ui_v1.ui')

#ui laden
WIDGET, BASE = uic.loadUiType(pathUi)

#Eine Klasse anlegen und zwei Klassen erben.
class MaskeUndFunktionalitaet(BASE, WIDGET):

    #wir bereiten in der __init__ die Gui vor.
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        #Ergebnis: self ist jetzt die 'einsatzbereite' Gui in QGIS.
        #ueber self koennen ab jetzt also Buttons, line edits etc. angesprochen
        #und mit Funktionen belegt werden.
        #self = meineGui :)
        
        #Buttons mit Methoden verknuepfen
        self.btn_cancel.clicked.connect(self.closePlugin)
        self.btn_run.clicked.connect(self.NonMatchingCRS)
    
    def closePlugin(self):
        self.close()
    
    #Find all layers not using the project CRS
    def NonMatchingCRS(self):
        layers = QgsProject.instance().mapLayers()
        warnings = 'The following layers do not match with the project:'
        
        for layer in layers.values():
            if layer.crs() != QgsProject.instance().crs():
                warnings += '\n' + layer.name()
                
        QMessageBox.warning(None, 'Do layers match the project\'s CRS?', warnings)
        print(warnings) 



