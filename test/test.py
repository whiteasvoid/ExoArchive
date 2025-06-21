import os
import json

TOKEN_FILE = "destiny_manifest/oauth_token.json"
test_data = {"test": "teste de escrita"}

try:
    os.makedirs("destiny_manifest", exist_ok=True)
    with open(TOKEN_FILE, "w") as f:
        json.dump(test_data, f)
    print(f"Arquivo {TOKEN_FILE} criado com sucesso.")
    if os.path.exists(TOKEN_FILE):
        print(f"Arquivo {TOKEN_FILE} confirmado como criado.")
    else:
        print(f"Erro: Arquivo {TOKEN_FILE} não foi criado.")
except OSError as e:
    print(f"Erro ao criar arquivo {TOKEN_FILE}: {e}")