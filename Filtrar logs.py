from qgis.core import (
    QgsProject,
    QgsWkbTypes,
)
from qgis import processing

def filtrar_camadas_log_importadas():
    """
    Filtra todas as camadas carregadas no QGIS que são de tipo vetor e contêm 'log' no nome.
    """
    camadas_log = []
    
    
    for camada in QgsProject.instance().mapLayers().values():
        if isinstance(camada, QgsVectorLayer):
            # Verifica se a camada contém 'log' no nome
            if 'log' in camada.name().lower():
                camadas_log.append(camada)
    
    return camadas_log

def mesclar_camadas(camadas_log):
    """
    Mescla todas as camadas de log em uma única camada, aceitando qualquer tipo de geometria.
    """
    # Verifica se há camadas para mesclar
    if not camadas_log:
        print("Nenhuma camada 'log' encontrada para mesclar.")
        return None

    # Mescla as camadas usando a ferramenta de processamento de mesclagem
    parametros = {
        'LAYERS': camadas_log,
        'CRS': camadas_log[0].crs(),  # Usa o CRS da primeira camada
        'OUTPUT': 'memory:'  # Armazenar em memória
    }

    resultado = processing.run('native:mergevectorlayers', parametros)

    # Retorna a camada mesclada
    return resultado['OUTPUT']

def adicionar_camada_ao_qgis(camada):
    """
    Adiciona a camada mesclada ao QGIS.
    """
    QgsProject.instance().addMapLayer(camada)
    print("Camada mesclada adicionada ao QGIS!")

# Filtra todas as camadas de log carregadas no QGIS
camadas_log = filtrar_camadas_log_importadas()

if camadas_log:
    # Mescla todas as camadas de log em uma única camada
    camada_mesclada = mesclar_camadas(camadas_log)

    if camada_mesclada:
        # Adiciona a camada mesclada ao QGIS
        adicionar_camada_ao_qgis(camada_mesclada)
else:
    print("Nenhuma camada 'log' foi encontrada no projeto.")
