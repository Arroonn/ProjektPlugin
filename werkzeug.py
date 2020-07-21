#Wir importieren verschiedene Funktionen der Bibliothek PyQt5 sowie das os Modul.
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qgis.utils import iface, showPluginHelp, spatialite_connect
from qgis.core import Qgis, QgsProject, QgsMapLayer, QgsFeatureSource, QgsMessageLog
from .werkzeug_dialog import WerkzeugDialog #Wir holen uns die Klasse WerkzeugDialog aus der werkzeug_dialog.py.

import os
import processing

class QuickQA: #Diese Klasse ist das funktionale Kernstück des Plugins; enthält Methoden.

    def __init__(self, iface):  #Das iface soll eine Eigenschaft des Plugins werden.
        self.iface = iface

    def initGui(self):  # Method to set up toolbar, i.e. buttons, actions, dropdown, Pluginmenu, etc. 
        
        self.plugin_dir = os.path.dirname(__file__)  #Dynamischer Pfad zum Plugin-Directory, in dem die werkzeug.py liegt.
        
        #Actions werden erstellt, die sich die Icons aus dem Plugin Directory holen.
        self.action1 = QAction(QIcon(os.path.join(self.plugin_dir,"icons","CheckAll.svg")), u"Check CRS of all layers", self.iface.mainWindow())
        self.action2 = QAction(QIcon(os.path.join(self.plugin_dir,"icons","CheckActive.svg")), u"Check CRS of active layers", self.iface.mainWindow())
        self.action3 = QAction(QIcon(os.path.join(self.plugin_dir,"icons","CheckSelected.svg")), u"Check CRS of selected layers", self.iface.mainWindow())
        self.action4 = QAction(QIcon(os.path.join(self.plugin_dir,"icons","CheckSpatialIndex.svg")), u"Check Spatial Index", self.iface.mainWindow())
        self.action5 = QAction(QIcon(os.path.join(self.plugin_dir,"icons","Help.svg")), u"Help...", self.iface.mainWindow())
        
        #Beim Klick auf den jeweiligen Button soll die jeweilige run-Methode ausgeführt werden.
        self.action1.triggered.connect(self.runAll)
        self.action2.triggered.connect(self.runActive)
        self.action3.triggered.connect(self.runSelected)
        self.action4.triggered.connect(self.runSIndex)
        self.action5.triggered.connect(self.runHelp)
        
        #Adds actions to the plugin's menu.
        self.iface.addPluginToMenu('QuickQA', self.action1)
        self.iface.addPluginToMenu('QuickQA', self.action2)
        self.iface.addPluginToMenu('QuickQA', self.action3)
        self.iface.addPluginToMenu('QuickQA', self.action4)
        self.iface.addPluginToMenu('QuickQA', self.action5)
        
        
        #Toolbar Menu
        self.popupMenu = QMenu( self.iface.mainWindow() )
        self.popupMenu.addAction( self.action1 )
        self.popupMenu.addAction( self.action2 )
        self.popupMenu.addAction( self.action3 )
        
        self.toolButton = QToolButton() #Generates the main button of the CRS-related buttons in toolbar.

        self.toolButton.setMenu( self.popupMenu ) # Generates the dropdown at the CRS toolbar button. 
        self.toolButton.setDefaultAction( self.action1 ) #setzt action1 als default action
        self.toolButton.setPopupMode( QToolButton.InstantPopup ) #macht, dass Dropdown aufpoppt beim Klick auf Toolbarbutton
        
        self.myToolBar = self.iface.mainWindow().findChild( QToolBar, u'QuickQA' ) #Checks if there is a toolbar with that name already.
        if not self.myToolBar: #If no toolbar is found one gets created. 
            self.myToolBar = self.iface.addToolBar( u'QuickQA' ) #Makes toolbar selectable in the toolbar panel. 
            self.myToolBar.setObjectName( u'QuickQA' )
        
        self.toolbar_object = self.myToolBar.addWidget( self.toolButton ) # Adds spatial index button to toolbar.
        self.myToolBar.addAction( self.action4 )
        self.myToolBar.addAction( self.action5 )
        
        self.gui = WerkzeugDialog(self.iface.mainWindow()) # Ruft die Gui auf
        self.list_results = self.gui.list_results          # ???
        self.gui.btn_sanitize.clicked.connect(self.sanitize)#???
        

    def unload(self):
        self.iface.removePluginMenu('QuickQA', self.action1)
        self.iface.removePluginMenu('QuickQA', self.action2)
        self.iface.removePluginMenu('QuickQA', self.action3)
        self.iface.removePluginMenu('QuickQA', self.action4)
        self.iface.removePluginMenu('QuickQA', self.action5)
        
        self.popupMenu.removeAction(self.action1)
        self.popupMenu.removeAction(self.action2)
        self.popupMenu.removeAction(self.action3)
        self.myToolBar.removeAction(self.action4)
        self.myToolBar.removeAction(self.action5)
        self.iface.removeToolBarIcon(self.toolbar_object)
        del self.popupMenu
        self.popupMenu = None
        del self.toolButton
        self.toolButton = None
        del self.myToolBar
        self.myToolBar = None

    def runAll(self):
        layers = QgsProject.instance().mapLayers()           #Nimmt sich alle Layer aus ToC
        project_crs = QgsProject.instance().crs().authid()   #Nimmt sich ID des CRS vom Projekt
        bad_crs_layer=[]                                     #Erzeugt leere Liste für abweichende Layer
        
        layertree_root=QgsProject.instance().layerTreeRoot() #Returns pointer to the root (invisible) node of the project’s layer tree

        for layer_id, layer in layers.items():               #Compares CRS between layers and project
            if layer.crs().authid()!=project_crs: 
                bad_crs_layer.append(layer.name())

        self.showResult(bad_crs_layer, 'CRS')
        
    def runActive(self):
        layers = iface.mapCanvas().layers()
        project_crs = QgsProject.instance().crs().authid()
        bad_crs_layer=[]
        
        layertree_root=QgsProject.instance().layerTreeRoot()

        #for layer_id, layer in layers.items():
        for layer in layers:
            if layertree_root.findLayer(layer.id()).isVisible():
                if layer.crs().authid()!=project_crs:
                    bad_crs_layer.append(layer.name())
        
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

        self.showResult(bad_crs_layer, 'CRS')
        
    def runSIndex(self):
        layers = QgsProject.instance().mapLayers()
        self.missingSIndex = []
        for layer_id, layer in layers.items():
            if layer.type() == QgsMapLayer.VectorLayer: #checks whether vector layer or not - excludes raster
                if layer.hasSpatialIndex() == QgsFeatureSource.SpatialIndexNotPresent:
                    QgsMessageLog.logMessage(layer.name()+" hat sicher keinen Spatial Index. Data format could be geojson or csv", 'QuickQA', level=Qgis.Info)
                elif layer.hasSpatialIndex() == QgsFeatureSource.SpatialIndexUnknown:
                    #checks for gpkg and shp
                    myfile= unicode( layer.dataProvider().dataSourceUri() ) #Pfad der Datenquelle des Layers abgreifen
                    #Pfadordner und Dateiname trennen, um sich den Pfad zur Geopackage Datei oder zur QIX-Datei bilden zu können
                    (myDirectory,nameFile) = os.path.split(myfile)
                    layersource_absolute_path=myfile.split('|')[0] #absoluter pfad ohne layernamen
                    #Test fuer Geopackages
                    if ".gpkg" in myfile:
                        con = spatialite_connect(layersource_absolute_path)
                        tablename=nameFile.split('|')[1]

                        cur = con.cursor()
                        gpkg_tablename=tablename.split('=')[1] #tabellennamen isolieren
                        sql_string="SELECT EXISTS(SELECT name FROM sqlite_master WHERE type='table' and name like 'rtree_"+gpkg_tablename+"_%')" 

                        cur.execute(sql_string) #sql ausfuehren
                        result = cur.fetchone() #erstes ergebnis holen
                        #result = cur.fetchall() #alle ergebnisse holen
                        if result[0]==1:
                            QgsMessageLog.logMessage("Geopackage "+layer.name()+" has a spatial index", 'QuickQA', level=Qgis.Info)
                        else:
                            QgsMessageLog.logMessage("Geopackage "+layer.name()+" has NO spatial index", 'QuickQA', level=Qgis.Info)
                            self.missingSIndex.append(layer)

                        cur.close() # see link in notes doc
                        con.close()
                    #Test fuer Shapefiles
                    elif ".shp" in myfile:
                        (myDirectory,nameFile) = os.path.split(myfile)
                        layername_w_o_extension=os.path.splitext(nameFile.split('|')[0])[0]  #layername ohne extension, Bsp layer1.shp | layer1 ['layer1' ,'shp']
                        qix_path=os.path.join(myDirectory,layername_w_o_extension+'.qix') #pfad zur qix Datei bauen ...imselben ordner wie die shapedatei
                        if os.path.isfile (qix_path):   #ueberpruefen ob die qix datei existiert
                            QgsMessageLog.logMessage("Shapefile "+layer.name()+" has a spatial index (.qix exists).", 'QuickQA', level=Qgis.Info)
                        else:
                            self.missingSIndex.append(layer)
                        
                elif layer.hasSpatialIndex() == QgsFeatureSource.SpatialIndexPresent:
                    QgsMessageLog.logMessage("present", 'QuickQA', level=Qgis.Info)
                else:
                    QgsMessageLog.logMessage("something else", 'QuickQA', level=Qgis.Info)
        self.showResult(self.missingSIndex, 'MissingSIndex')


    def showResult(self,result_layer, mode):
        sanitize_button=self.gui.btn_sanitize
        sanitize_button.hide() #beim thema crs den sanitize button ausblenden
        if mode == 'CRS':
            if len(result_layer)<1:
                self.showMessage('All layers checked align with the CRS of the project.', Qgis.Success)
            else:
                self.gui.label.setText("The layer(s) listed have a different coordinate\n reference system than the project:")
                self.gui.label_2.setText("Reproject or export the layer using the project's\ncoordinate reference system.")
                self.list_results.clear()
                self.list_results.addItems(result_layer)
                self.gui.show()
                
        elif mode == 'MissingSIndex':
            if len(result_layer)<1:
                self.showMessage('All layers have a spatial index.', Qgis.Success)

            else:
                self.gui.label.setText("The layer(s) listed don't have a spatial index:")
                self.gui.label_2.setText("Important: Shapefile and Geopackage are \ncurrently the only two data providers supported.")
                self.list_results.clear()
                result_layer_names =[] #Empty list containing layer names, weil hier wirklich die layer als objekte in der liste stehen
                for layer in result_layer:
                    result_layer_names.append(layer.name()) # fuer jeden layer seinen namen hinzufuegen fuer die liste im dialog
                self.list_results.addItems(result_layer_names)
                
                sanitize_button.show()
                
                self.gui.show()

    def sanitize(self,layer):
        for layer in self.missingSIndex:
            layer.dataProvider().createSpatialIndex()
        self.showMessage('Spatial Index successfully created', Qgis.Success)
        self.gui.close()
            
                
    def showMessage(self, message, level=Qgis.Info, target=None, shortmessage=None): #enables the displaying of the message bar
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
            

    def runHelp(self):
        showPluginHelp(packageName=None, filename='index', section='')

