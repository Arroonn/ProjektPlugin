#Wir importieren verschiedene Funktionen der Bibliothek PyQt5 sowie das os Modul.
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import os
from qgis.utils import iface
import processing
from qgis.core import Qgis, QgsProject, QgsMapLayer, QgsFeatureSource, QgsMessageLog

from qgis.core import Qgis, QgsProject, QgsMessageLog
from qgis.utils import spatialite_connect
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
        self.gui.btn_sanitize.clicked.connect(self.sanitize)
        

    def unload(self):
        self.iface.removePluginMenu('QuickQA', self.action1)
        self.iface.removePluginMenu('QuickQA', self.action2)
        self.iface.removePluginMenu('QuickQA', self.action3)
        self.iface.removePluginMenu('QuickQA', self.action4)
        
        self.popupMenu.removeAction(self.action1)
        self.popupMenu.removeAction(self.action2)
        self.popupMenu.removeAction(self.action3)
        self.myToolBar.removeAction(self.action4)
        self.iface.removeToolBarIcon(self.toolbar_object)
        del self.popupMenu
        self.popupMenu = None
        del self.toolButton
        self.toolButton = None
        del self.myToolBar
        self.myToolBar = None

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
        self.missingSIndex = []
        for layer_id, layer in layers.items():
            #print(layer.name())
            if layer.type() == QgsMapLayer.VectorLayer:
                if layer.hasSpatialIndex() == QgsFeatureSource.SpatialIndexNotPresent:
                    print("not present")
                    erzeugt=layer.dataProvider().createSpatialIndex()
                    print(erzeugt)
                elif layer.hasSpatialIndex() == QgsFeatureSource.SpatialIndexUnknown:
                    #print("unknown")
                    
                    #ueberpruefung fuer gpkg und shapefiles:
                    
                    myfile= unicode( layer.dataProvider().dataSourceUri() ) #pfad abgreifen
                    (myDirectory,nameFile) = os.path.split(myfile) #pfadordner und dateiname trennen
                    #print(myfile)
                    layersource_absolute_path=myfile.split('|')[0] #absoluter pfad ohne layernamen
                    #Test fuer geopackages
                    if ".gpkg" in myfile:
                        con = spatialite_connect(layersource_absolute_path)
                        tablename=nameFile.split('|')[1]
                        print(tablename)
                        #Now, you can create a new point layer in your database in this way (see the docs):

                        cur = con.cursor()
                        # Run next line if your DB was just created, it may take a while...
                        gpkg_tablename=tablename.split('=')[1] #tabellennamen isolieren
                        sql_string="SELECT EXISTS(SELECT name FROM sqlite_master WHERE type='table' and name like 'rtree_"+gpkg_tablename+"_%')" 
                        #sql_string="select ST_AsText(geometry) from "+gpkg_tablename+";" 
                        
                        print(sql_string)

                        cur.execute(sql_string) #sql ausfuehrenn
                        result = cur.fetchone() #erstes ergebnis holen
                        #result = cur.fetchall() #alle ergebnisse holen
                        print(result)
                        if result[0]==1:
                            print(layer.name()+" hat einen spatial index")
                        else:
                            print(layer.name()+" hat keinen spatial index")
                            self.missingSIndex.append(layer)
                            #layer.dataProvider().createSpatialIndex()

                        cur.close()
                        con.close()
                    #Test fuer Shapefiles    
                    elif ".shp" in myfile:
                        (myDirectory,nameFile) = os.path.split(myfile)
                        layername_w_o_extension=os.path.splitext(nameFile.split('|')[0])[0]  #layername ohne extension
                        qix_path=os.path.join(myDirectory,layername_w_o_extension+'.qix') #pfad zur qix Datei bauen ...imselben ordner wie die shapedatei
                        if os.path.isfile ( qix_path):   #ueberpruefen ob die qix datei existiert
                            print("Shapefile "+layer.name()+" hat eine qix-Datei.\n"+
                            "Die liegt hier: \n"
                            +qix_path)
                        else:
                            self.missingSIndex.append(layer)
                        
                    
                    
                    # erzeugt=layer.dataProvider().createSpatialIndex()
                    # print(erzeugt)
                    # if erzeugt==True:
                        # myfile= unicode( layer.dataProvider().dataSourceUri() ) 
                        # (myDirectory,nameFile) = os.path.split(myfile)

                        # print(nameFile.split('|')[0])
                        # print("index erzeugt oder aktualisiert--\n--fuer Layer "+layer.name())
                elif layer.hasSpatialIndex() == QgsFeatureSource.SpatialIndexPresent:
                    print ("present")
                else:
                    print ("something else")
        self.showResult(self.missingSIndex, 'MissingSIndex')
        
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
        sanitize_button=self.gui.btn_sanitize
        sanitize_button.hide() #beim thema crs den sanitize button ausblenden
        if mode == 'CRS':
            if len(result_layer)<1:
                self.showMessage('Alle betreffenden Layer stimmen mit dem Koordinatensystem des Projekts überein.', Qgis.Success)
                #self.logMessage('Alle betreffenden Layer stimmen mit dem Koordinatensystem des Projekts überein.')
                #sichtbar im Protokoll widget im Reiter QuickQA
            else:
                self.gui.label.setText("The layers listed have a different coordinate\n reference system than the project:")
                self.gui.label_2.setText("Reproject or export the layer using the project's\n coordinate reference system.")
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
                result_layer_names =[] #leeres array fuer die layernamen weil hier wirklich die layer als objekte in der liste stehen
                for layer in result_layer:  #for loop
                    result_layer_names.append(layer.name()) # fuer jeden layer seinen namen hinzufuegen fuer die liste im dialog
                self.list_results.addItems(result_layer_names)
                
                sanitize_button.show()
                
                self.gui.show()
    
    #sanitize Funktion ausgelagert. wuerde ich nur fuer die Indizes anbieten. Layer reprojezzieren per batch ist kniffelig
    def sanitize(self,layer):
        for layer in self.missingSIndex:
            layer.dataProvider().createSpatialIndex()
        self.showMessage('Spatial Index erzeugt', Qgis.Success)
        self.gui.close()
            
                
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



