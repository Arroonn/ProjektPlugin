#Wir importieren verschiedene Funktionen der Bibliothek PyQt5.
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
#Wir holen uns alles aus werkzeug_funtionalitaet.
from ProjektPlugin.werkzeug_funktionalitaet import *

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
        self.startButton.triggered.connect(self.maskeAufrufen)

    def unload(self):
        self.iface.removePluginMenu('CheckCRS', self.startButton)

    def maskeAufrufen(self):
        pass
#        self.gui = MaskeUndFunktionalitaet(self.iface.mainWindow())
#        self.gui.show()

