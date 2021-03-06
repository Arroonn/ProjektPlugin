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
class WerkzeugDialog(BASE, WIDGET):

    #wir bereiten in der __init__ die Gui vor.
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        #Ergebnis: self ist jetzt die 'einsatzbereite' Gui in QGIS.
        #ueber self koennen ab jetzt also Buttons, line edits etc. angesprochen
        #und mit Funktionen belegt werden.
        #self = meineGui :)
        
        #self.btn_sanitize.clicked.connect(self.reproject)
        
        #Buttons mit Methoden verknuepfen
        self.btn_cancel.clicked.connect(self.closePlugin)
        #self.btn_run.clicked.connect(self.NonMatchingCRS)
    
    def closePlugin(self):
        self.close()
        
    def reproject(self):
        input_params = {}
        processing.execAlgorithmDialog('native:reprojectlayer', input_params)

