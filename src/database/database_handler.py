# Este arquivo lida com a base de dados do manifesto
import sqlite3
import json
import pickle
import os
from src.config.config import MANIFEST_FOLDER, hash_dict
from src.api.manifest_manager import ensure_manifest_folder

# Função que cria um dicionário com os dados do manifesto
def build_dict(hash_dict):
    # Garante que a pasta do manifesto existe
    manifestPath = ensure_manifest_folder()
    # Caminho do arquivo da base de dados
    dbPath = os.path.join(manifestPath, 'Manifest.content')
    
    # Conecta à base de dados
    conection = sqlite3.connect(dbPath)
    print('Conectado à base de dados do manifesto')
    # Cria um indicator para executar comandos
    indicator = conection.cursor()
    
    # Dicionário para guardar todos os dados
    allData = {}
    # Para cada tabela no dicionário hash_dict
    for tableName in hash_dict.keys():
        try:
            # Pega todos os dados da tabela
            indicator.execute('SELECT json from ' + tableName)
            print(f"A criar dicionário para {tableName}...")
            
            # Obtém todos os items da tabela
            items = indicator.fetchall()
            
            # Converte cada item para um objeto JSON
            jsons_items = [json.loads(item[0]) for item in items]
            
            # Cria um dicionário onde a chave é o hash
            dictionaryItems = {}
            hashKey = hash_dict[tableName]
            for item in jsons_items:   
                dictionaryItems[item[hashKey]] = item
            
            # Adiciona o dicionário à coleção de dados
            allData[tableName] = dictionaryItems
        except sqlite3.OperationalError as e:
            print(f"Tabela {tableName} não encontrada: {e}")
            continue
    
    # Fecha a conexão com a base de dados
    conection.close()
    print('Dicionário criado!')
    return allData

# Função que cria ou carrega os dados do manifesto
def create_manifest_data():
    # Garante que a pasta do manifesto existe
    manifestPath = ensure_manifest_folder()
    # Caminho do arquivo pickle
    picklePath = os.path.join(manifestPath, 'manifest.pickle')
    
    # Verifica se o arquivo pickle já existe
    if not os.path.isfile(picklePath):
        print("A criar novos dados do manifesto...")
        # Baixa o manifesto
        from src.api.manifest_manager import get_manifest
        get_manifest()        
        # Cria o dicionário com os dados
        allData = build_dict(hash_dict)
        # Salva os dados num arquivo pickle
        with open(picklePath, 'wb') as arquivo:
            pickle.dump(allData, arquivo)
        print(f"'manifest.pickle' criado em {manifestPath}!\nCONCLUÍDO!")
    else:
        print('A carregar dados existentes do manifesto...')
        # Carrega os dados do arquivo pickle
        with open(picklePath, 'rb') as arquivo:
            allData = pickle.load(arquivo)
    
    return allData