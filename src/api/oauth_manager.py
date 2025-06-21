# Este arquivo gerencia o fluxo de autenticação OAuth para a API do Bungie.net
import requests
import webbrowser
import http.server
import socketserver
import urllib.parse
from src.config.config import HEADERS, CLIENT_ID, CLIENT_SECRET
import json
import os
import ssl

# Obtém o diretório raiz do projeto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Caminho absoluto para o arquivo de token
TOKEN_FILE = os.path.join(BASE_DIR, "destiny_manifest", "oauth_token.json")

# Função para iniciar o fluxo de autenticação OAuth
def start_oauth_flow():
    """
    Inicia o fluxo OAuth redirecionando o usuário para o Bungie.net.
    Retorna o código de autorização após o login.
    """
    auth_url = (
        f"https://www.bungie.net/en/OAuth/Authorize"
        f"?client_id={CLIENT_ID}&response_type=code"
    )
    
    print("Abrindo o navegador para autenticação no Bungie.net...")
    print(f"URL de autenticação: {auth_url}")
    webbrowser.open(auth_url)
    
    # Variável para armazenar o código de autorização
    global authorization_code
    authorization_code = None
    
    # Configura um servidor HTTPS local para capturar o código de autorização
    class OAuthHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            print(f"Requisição recebida no servidor local: {self.path}")
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            
            # Extrai o código da URL de redirecionamento
            parsed_url = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            auth_code = query_params.get("code", [None])[0]
            
            # Salva o código
            global authorization_code
            authorization_code = auth_code
            
            # Responde ao usuário com uma página HTML
            html_response = """
                
                        Autenticação concluída!

                        Você pode fechar esta janela.

                    
            """
            self.wfile.write(html_response.encode('utf-8'))
    
    # Configura o contexto SSL com certificado autoassinado
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    cert_path = os.path.join(BASE_DIR, "certificates")
    try:
        context.load_cert_chain(certfile=os.path.join(cert_path, "localhost.crt"), keyfile=os.path.join(cert_path, "localhost.key"))
        print("Certificados SSL carregados com sucesso.")
    except FileNotFoundError:
        print(f"Erro: Certificados 'localhost.crt' ou 'localhost.key' não encontrados na pasta '{cert_path}'.")
        print("Por favor, gere os certificados com o seguinte comando no PowerShell:")
        print(f"New-Item -ItemType Directory -Path {os.path.join(BASE_DIR, 'certificates')} -Force")
        print(f"cd {os.path.join(BASE_DIR, 'certificates')}")
        print('openssl req -x509 -newkey rsa:2048 -keyout localhost.key -out localhost.crt -days 365 -nodes -subj "/C=PT/ST=Estado/L=Cidade/O=MinhaApp/CN=localhost"')
        return None
    
    # Inicia o servidor HTTPS na porta 8080
    port = 8080
    try:
        with socketserver.TCPServer(("", port), OAuthHandler) as httpd:
            httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
            print(f"Servidor HTTPS iniciado na porta {port}. Aguardando código de autorização...")
            httpd.handle_request()
    except OSError as e:
        print(f"Erro ao iniciar o servidor HTTPS: {e}")
        print(f"Verifique se a porta {port} está livre ou tente outra porta.")
        return None
    
    if authorization_code:
        print(f"Código de autorização recebido: {authorization_code}")
    else:
        print("Falha ao obter o código de autorização. Verifique se o redirecionamento para https://localhost:8080/ funcionou.")
    
    return authorization_code

# Função para obter o token de acesso
def get_access_token(auth_code):
    """
    Usa o código de autorização para obter o token de acesso.
    
    Args:
        auth_code (str): Código de autorização obtido no fluxo OAuth.
    
    Returns:
        dict: Dados do token (access_token, refresh_token, etc.) ou None se houver erro.
    """
    if not auth_code:
        print("Erro: Nenhum código de autorização fornecido.")
        return None
    
    token_url = "https://www.bungie.net/Platform/App/OAuth/Token/"
    payload = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    
    print("Enviando requisição para obter token de acesso...")
    print(f"URL do token: {token_url}")
    print(f"Payload: {payload}")
    response = requests.post(token_url, data=payload)
    
    if response.status_code == 200:
        token_data = response.json()
        print("Token de acesso obtido com sucesso!")
        print(f"Dados do token: {json.dumps(token_data, indent=2)}")
        # Salva o token em um arquivo
        try:
            os.makedirs(os.path.join(BASE_DIR, "destiny_manifest"), exist_ok=True)
            with open(TOKEN_FILE, "w") as f:
                json.dump(token_data, f)
            print(f"Token salvo em: {TOKEN_FILE}")
            # Verifica se o arquivo foi realmente criado
            if os.path.exists(TOKEN_FILE):
                print(f"Arquivo {TOKEN_FILE} confirmado como criado.")
            else:
                print(f"Erro: Arquivo {TOKEN_FILE} não foi criado.")
        except OSError as e:
            print(f"Erro ao salvar o token em {TOKEN_FILE}: {e}")
            return None
        return token_data
    else:
        print(f"Erro ao obter token: {response.status_code} - {response.text}")
        return None

# Função para carregar o token salvo
def load_access_token():
    """
    Carrega o token de acesso do arquivo, se existir.
    
    Returns:
        dict: Dados do token ou None se não existir.
    """
    if not os.path.exists(TOKEN_FILE):
        print(f"Nenhum token de acesso encontrado em {TOKEN_FILE}.")
        return None
    
    print(f"Carregando token de acesso de {TOKEN_FILE}...")
    try:
        with open(TOKEN_FILE, "r") as f:
            token_data = json.load(f)
            print(f"Token carregado: {json.dumps(token_data, indent=2)}")
            # Verifica se o token contém refresh_token
            if "refresh_token" not in token_data:
                print("Token não contém refresh_token. Deletando arquivo e retornando None...")
                os.remove(TOKEN_FILE)
                return None
            return token_data
    except (json.JSONDecodeError, OSError) as e:
        print(f"Erro ao carregar {TOKEN_FILE}: {e}")
        print("Deletando arquivo corrompido e retornando None...")
        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)
        return None

# Função para atualizar os cabeçalhos com o token de acesso
def update_headers_with_token():
    """
    Atualiza os cabeçalhos com o token de acesso, se disponível.
    
    Returns:
        dict: Cabeçalhos atualizados com o token de autorização.
    """
    token_data = load_access_token()
    if token_data and "access_token" in token_data:
        # Testa o token
        headers = HEADERS.copy()
        headers["Authorization"] = f"Bearer {token_data['access_token']}"
        print("Cabeçalhos atualizados com token de acesso.")
        print(f"Cabeçalhos: {headers}")
        test_url = "https://www.bungie.net/Platform/User/GetCurrentBungieNetUser/"
        print(f"Testando token com requisição a: {test_url}")
        response = requests.get(test_url, headers=headers)
        if response.status_code == 200:
            print("Token válido!")
            return headers
        else:
            print(f"Token inválido: {response.status_code} - {response.text}")
            print("Iniciando novo fluxo OAuth...")
            return refresh_access_token()
    else:
        print("Nenhum token de acesso válido encontrado. Iniciando fluxo OAuth...")
        auth_code = start_oauth_flow()
        if auth_code:
            token_data = get_access_token(auth_code)
            if token_data:
                headers = HEADERS.copy()
                headers["Authorization"] = f"Bearer {token_data['access_token']}"
                print("Cabeçalhos atualizados com novo token de acesso.")
                print(f"Cabeçalhos: {headers}")
                return headers
        print("Falha ao obter token de acesso. Usando cabeçalhos padrão.")
        return HEADERS

# Função para verificar e atualizar o token, se necessário
def refresh_access_token():
    """
    Verifica se o token expirou e o atualiza usando o refresh_token, se necessário.
    
    Returns:
        dict: Cabeçalhos atualizados com o novo token.
    """
    token_data = load_access_token()
    if not token_data or "refresh_token" not in token_data:
        print("Nenhum refresh_token encontrado. Iniciando novo fluxo OAuth...")
        auth_code = start_oauth_flow()
        if auth_code:
            token_data = get_access_token(auth_code)
            if token_data:
                headers = HEADERS.copy()
                headers["Authorization"] = f"Bearer {token_data['access_token']}"
                print("Cabeçalhos atualizados com novo token de acesso.")
                print(f"Cabeçalhos: {headers}")
                return headers
        print("Falha ao obter token de acesso. Usando cabeçalhos padrão.")
        return HEADERS
    
    token_url = "https://www.bungie.net/Platform/App/OAuth/Token/"
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": token_data["refresh_token"],
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    
    print("Enviando requisição para atualizar token de acesso...")
    print(f"URL do token: {token_url}")
    print(f"Payload: {payload}")
    response = requests.post(token_url, data=payload)
    
    if response.status_code == 200:
        new_token_data = response.json()
        print("Token atualizado com sucesso!")
        print(f"Novo token: {json.dumps(new_token_data, indent=2)}")
        # Salva o novo token
        try:
            with open(TOKEN_FILE, "w") as f:
                json.dump(new_token_data, f)
            print(f"Novo token salvo em: {TOKEN_FILE}")
            if os.path.exists(TOKEN_FILE):
                print(f"Arquivo {TOKEN_FILE} confirmado como criado.")
            else:
                print(f"Erro: Arquivo {TOKEN_FILE} não foi criado.")
        except OSError as e:
            print(f"Erro ao salvar o token em {TOKEN_FILE}: {e}")
            return update_headers_with_token()
        headers = HEADERS.copy()
        headers["Authorization"] = f"Bearer {new_token_data['access_token']}"
        print(f"Cabeçalhos atualizados: {headers}")
        return headers
    else:
        print(f"Erro ao atualizar token: {response.status_code} - {response.text}")
        print("Iniciando novo fluxo OAuth...")
        auth_code = start_oauth_flow()
        if auth_code:
            token_data = get_access_token(auth_code)
            if token_data:
                headers = HEADERS.copy()
                headers["Authorization"] = f"Bearer {token_data['access_token']}"
                print("Cabeçalhos atualizados com novo token de acesso.")
                print(f"Cabeçalhos: {headers}")
                return headers
        print("Falha ao obter token de acesso. Usando cabeçalhos padrão.")
        return HEADERS