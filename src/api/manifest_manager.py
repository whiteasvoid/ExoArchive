# Este arquivo lida com o download e extração do manifest do Destiny 2
import requests
import os
import zipfile
from src.config.config import HEADERS, MANIFEST_FOLDER

# Função que cria a pasta para o manifest, se não existir
def ensure_manifest_folder():
    # Obtém o diretório raiz do projeto
    scriptFolder = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    # Junta o diretório com o nome da pasta do manifest
    manifestPath = os.path.join(scriptFolder, MANIFEST_FOLDER)
    
    # Verifica se a pasta não existe
    if not os.path.exists(manifestPath):
        # Cria a pasta
        os.makedirs(manifestPath)
        print(f"Pasta criada: {manifestPath}")
    
    # Retorna o caminho da pasta
    return manifestPath

# Função que baixa e extrai o manifest
def get_manifest():
    # Garante que a pasta do manifest existe
    manifestPath = ensure_manifest_folder()
    
    # URL para obter informações do manifest
    manifestUrl = 'https://www.bungie.net/Platform/Destiny2/Manifest/'
    
    print("A obter localização do manifest...")
    # Faz um pedido à API para obter os dados do manifest
    answer = requests.get(manifestUrl, headers=HEADERS)
    manifest = answer.json()
    
    # Cria a URL completa para baixar o manifest
    downloadUrl = 'https://www.bungie.net' + manifest['Response']['mobileWorldContentPaths']['en']
    
    print(f"A baixar manifest de: {downloadUrl}")
    # Caminho onde o arquivo zip será salvo
    zipPath = os.path.join(manifestPath, "MANZIP")
    # Baixa o arquivo
    answer = requests.get(downloadUrl)
    with open(zipPath, "wb") as zipFile:
        zipFile.write(answer.content)
    print("Download concluído!")
    
    # Extrai o conteúdo do arquivo zip
    with zipfile.ZipFile(zipPath) as zipFile:
        fileName = zipFile.namelist()
        zipFile.extractall(manifestPath)
    
    # Renomeia o arquivo extraído
    oldPath = os.path.join(manifestPath, fileName[0])
    newPath = os.path.join(manifestPath, 'Manifest.content')
    os.rename(oldPath, newPath)
    
    # Remove o arquivo zip
    os.remove(zipPath)
    print('Descompactado e limpo!')