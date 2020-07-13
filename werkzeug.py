#Wir importieren verschiedene Funktionen der Bibliothek PyQt5 sowie das os Modul.
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import os
from qgis.utils import iface
import processing
from qgis.core import Qgis, QgsProject, QgsMapLayer, QgsFeatureSource, QgsMessageLog

from qgis.core import Qgis, QgsProject, QgsMessageLog

#Wir holen uns alles aus werkzeug_dialog.
from .werkzeug_dialog import WerkzeugDialog

#Wir legen eine Klasse namens QuickQA an und definieren ihre Methoden.
#Diese Klasse ist das funktionale Kernstück des Plugins.
class QuickQA:

    def __init__(self, iface):
        self.iface = iface #Das iface soll eine Eigenschaft des Plugins werden

    def initGui(self):
        #Dynamischer Pfad zum Plugin-Directory, in dem die werkzeug.py liegt
        self.plugin_dir = os.path.dirname(__file__)
        #Eine Action wird erstellt, die sich die Icons aus dem Plugin Directory holt
        self.action1 = QAction(QIcon(os.path.join(self.plugin_dir,"icons","CheckAll.svg")), u"Check CRS of all layers", self.iface.mainWindow())
        self.action2 = QAction(QIcon(os.path.join(self.plugin_dir,"icons","CheckActive.svg")), u"Check CRS of active layers", self.iface.mainWindow())
        self.action3 = QAction(QIcon(os.path.join(self.plugin_dir,"icons","CheckSelected.svg")), u"Check CRS of selected layers", self.iface.mainWindow())
        self.action4 = QAction(QIcon(os.path.join(self.plugin_dir,"icons","CheckSpatialIndex.svg")), u"Check Spatial Index", self.iface.mainWindow())
        
        #Beim Klick auf die 'Check CRS of...'-Buttons soll die jeweilige run-Methode ausgeführt werden.
        self.action1.triggered.connect(self.runAll)
        self.action2.triggered.connect(self.runActive)
        self.action3.triggered.connect(self.runSelected)
        self.action4.triggered.connect(self.runSIndex)
        
        #Adds actions to the plugins menu
        self.iface.addPluginToMenu('QuickQA', self.action1)
        self.iface.addPluginToMenu('QuickQA', self.action2)
        self.iface.addPluginToMenu('QuickQA', self.action3)
        
        #Toolbar Menu
        self.popupMenu = QMenu( self.iface.mainWindow() )
        self.popupMenu.addAction( self.action1 )
        self.popupMenu.addAction( self.action2 )
        self.popupMenu.addAction( self.action3 )

        #QToolbutton class provides a quick-access button to commands; used inside QToolBar.
        self.toolButton = QToolButton()

        self.toolButton.setMenu( self.popupMenu ) # 
        self.toolButton.setDefaultAction( self.action1 ) #setzt action1 als default action
        self.toolButton.setPopupMode( QToolButton.InstantPopup ) #macht, dass Dropdown aufpoppt beim Klick auf Toolbarbutton
        
        self.myToolBar = self.iface.mainWindow().findChild( QToolBar, u'QuickQA' )
        if not self.myToolBar: #if-clause
            self.myToolBar = self.iface.addToolBar( u'QuickQA' ) #macht die Toolbar anwählbar in der Toolbarliste
            self.myToolBar.setObjectName( u'QuickQA' )
        
        self.toolbar_object = self.myToolBar.addWidget( self.toolButton )
        self.myToolBar.addAction( self.action4 )
        
        self.gui = WerkzeugDialog(self.iface.mainWindow())
        self.list_results = self.gui.list_results
        

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
        # self.gui.list_results.addItems(bad_crs_layer)
        # self.gui.show()
        self.showResult(bad_crs_layer, 'CRS')
        
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
        # self.gui.list_results.addItems(bad_crs_layer)
        # self.gui.show()
        self.showResult(bad_crs_layer, 'CRS')
        
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
        self.showResult(bad_crs_layer, 'CRS')
        
    def runSIndex(self):
        layers = QgsProject.instance().mapLayers()
        missingSIndex = []

        for layer_id, layer in layers.items():
            #print(layer.name())
            if layer.type() == QgsMapLayer.VectorLayer:
                if layer.hasSpatialIndex() == QgsFeatureSource.SpatialIndexNotPresent:
                    print("not present")
                    erzeugt=layer.dataProvider().createSpatialIndex()
                    print(erzeugt)
                elif layer.hasSpatialIndex() == QgsFeatureSource.SpatialIndexUnknown:
                    #print("unknown")
                    missingSIndex.append(layer.name())
                    erzeugt=layer.dataProvider().createSpatialIndex()
                    if erzeugt==True:
                        myfile= unicode( layer.dataProvider().dataSourceUri() ) 
                        (myDirectory,nameFile) = os.path.split(myfile)

                        print(nameFile.split('|')[0])
                        print("index erzeugt oder aktualisiert--\n--fuer Layer "+layer.name())
                elif layer.hasSpatialIndex() == QgsFeatureSource.SpatialIndexPresent:
                    print ("present")
                else:
                    print ("something else")
        self.showResult(missingSIndex, 'MissingSIndex')
        
#        layers = QgsProject.instance().mapLayers() # ist ein Dictionary mit {'layerkennung' : layer}
#
#        for x in layers.values():
#            if '.gpkg' in x.source():   # wird ausgeführt, nur wenn '.gpkg' im Pfad vorkommt (x.source() gibt Pfad als String wieder)
#                # Parameter zu processing-Funktionen bekommt man mit: processing:algorithmHelp('algorithmName') in der Python-Konsole
#                params = {
#                    'INPUT' : x,
#                    'SQL' : f"SELECT EXISTS(SELECT 1 FROM sqlite_master WHERE tbl_name like 'rtree_{x.name()}_%') as has_spatial_index",
#                    'DIALECT':0,
#                    'OUTPUT' : 'TEMPORARY_OUTPUT'}
#                hasSP = processing.run('gdal:executesql', params)   # führt Funktion mit den Parametern aus
#                #print(hasSP['OUTPUT'])
#
#                gpg = hasSP['OUTPUT'] + "|layername=SELECT"     # Pfadname des Outputs (String) und LayerName (ist hier immer SELECT aufgrund der SQL-Anweisung)
#                layer = QgsVectorLayer(gpg, 'outputsql', 'ogr') # als Vektorlayer aufrufen
#                print(x.name(), layer.getFeature(1)['has_spatial_index'])   #Ergebnis der Spalte 'has_spatial_index' ausgeben (layer hat immer nur ein feature

    def showResult(self,result_layer, mode):
        if mode == 'CRS':
            if len(result_layer)<1:
                self.showMessage('Alle betreffenden Layer stimmen mit dem Koordinatensystem des Projekts überein.', Qgis.Success)
                #self.logMessage('Alle betreffenden Layer stimmen mit dem Koordinatensystem des Projekts überein.')
                #sichtbar im Protokoll widget im Reiter QuickQA
            else:
                self.list_results.clear()
                self.list_results.addItems(result_layer)
                self.gui.show()
                
        elif mode == 'MissingSIndex':
            if len(result_layer)<1:
                self.showMessage('Alle betreffenden Layer haben einen Spatial Index.', Qgis.Success)
                #self.logMessage('Alle betreffenden Layer haben einen Spatial Index.')
                #sichtbar im Protokoll widget im Reiter QuickQA
            else:
                self.gui.label.setText("The layers listed don't have a spatial index:")
                self.gui.label_2.setText("Spatial Index Ergebnis")
                self.list_results.clear()
                self.list_results.addItems(result_layer)
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



