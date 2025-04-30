# -*- coding: utf-8 -*-
from qgis.PyQt.QtWidgets import QDialog, QAction
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsProject, QgsVectorLayer
from qgis import processing

from .log_plugin_dialog import FiltroLogDialog  # Classe gerada pelo pyuic5
import os

class LogPluginDialog:
    def __init__(self, iface):
        """
        iface: instância da interface do QGIS passada pela classFactory
        """
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.action = None
        self.dialog = None

    def initGui(self):
        """Adiciona o botão/ícone ao QGIS."""
        icon_path = os.path.join(self.plugin_dir, "icon.png")  # ajuste seu ícone
        self.action = QAction(QIcon(icon_path), "Filtrar Logs", self.iface.mainWindow())
        self.action.triggered.connect(self.showDialog)
        # Adiciona ao menu e à barra
        self.iface.addPluginToMenu("&Logs", self.action)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        """Remove o botão/ícone do QGIS."""
        self.iface.removePluginMenu("&Logs", self.action)
        self.iface.removeToolBarIcon(self.action)

    def showDialog(self):
        """Cria e exibe o diálogo (ou reaproveita se já existir)."""
        if self.dialog is None:
            # Montagem da interface
            self.dialog = QDialog()
            self.ui = FiltroLogDialog()
            self.ui.setupUi(self.dialog)
            # Conecta o botão dentro do diálogo
            self.ui.pushButton_FiltrarLogs.clicked.connect(self.executar)
        self.dialog.show()
        self.dialog.raise_()
        self.dialog.activateWindow()

    def executar(self):
        nome_camada = self.ui.lineEdit_NomeDaCamadaFiltrada.text().strip()
        if not nome_camada:
            self._mensagem("⚠️ Por favor, insira um nome para a camada.")
            return

        camadas = self._filtrar_camadas_log()
        if not camadas:
            self._mensagem("Nenhuma camada 'log' foi encontrada no projeto.")
            return

        mesclada = self._mesclar_camadas(camadas)
        if mesclada:
            mesclada.setName(nome_camada)
            QgsProject.instance().addMapLayer(mesclada)
            self._mensagem(f"✅ Camada '{nome_camada}' adicionada com sucesso!")

    def _filtrar_camadas_log(self):
        layers = []
        for lyr in QgsProject.instance().mapLayers().values():
            if isinstance(lyr, QgsVectorLayer) and 'log' in lyr.name().lower():
                layers.append(lyr)
        return layers

    def _mesclar_camadas(self, layers):
        if not layers:
            print("Nenhuma camada 'log' para mesclar.")
            return None
        params = {
            'LAYERS': layers,
            'CRS': layers[0].crs(),
            'OUTPUT': 'memory:'
        }
        try:
            result = processing.run('native:mergevectorlayers', params)
            return result['OUTPUT']
        except Exception as e:
            self._mensagem(f"Erro ao mesclar: {e}")
            return None

    def _mensagem(self, txt):
        print(txt)  # para debugging; substitua por QMessageBox se preferir
