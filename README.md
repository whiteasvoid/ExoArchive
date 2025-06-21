# ExoArchive

ExoArchive é um projeto de aprendizado de APIs que interage com a API do **Bungie.net** para o jogo **Destiny 2**. O objetivo é criar uma ferramenta semelhante a plataformas como **Destiny Item Manager (DIM)**, **light.gg** e **TodayInDestiny**, fornecendo funcionalidades como busca de itens, informações sobre jogadores, inventário de vendedores (ex.: Xur) e gerenciamento de dados do manifesto, tudo em um único programa Python.

Este projeto é projetado a iniciantes que queiram aprender sobre chamadas a APIs REST, autenticação OAuth, manipulação de bases de dados SQLite e organização de projetos Python.

---

## Objetivo do Projeto

O **ExoArchive** tem como objetivo:

- **Aprendizado de APIs**: Explorar a API do Bungie.net, incluindo autenticação OAuth e endpoints específicos do Destiny 2.
- **Funcionalidades Inspiradas em Ferramentas Populares**:
  - Busca de itens por nome, tipo ou hash (similar ao light.gg).
  - Exibição de inventário de vendedores, como o Xur (similar ao TodayInDestiny).
  - Gerenciamento de informações de jogadores e personagens (similar ao DIM).
- **Centralização**: Reunir funcionalidades em um único programa para consulta e gerenciamento de dados do Destiny 2.
- **Escalabilidade**: Criar uma base modular que possa ser expandida com novas funcionalidades, como interface gráfica ou integração com outras APIs.

---

## Pré-requisitos

- **Python 3.8+**
- **Dependências** listadas em `requirements.txt`:
  - `requests`
- **Certificados SSL** para autenticação OAuth (gerados manualmente, veja a seção de Configuração).
- **Chave de API e credenciais OAuth** do Bungie.net (obtidas em https://www.bungie.net/en/Application).

---

## Configuração

1. **Clonar o Repositório** (se aplicável):

   ```bash
   git clone https://github.com/whiteasvoid/ExoArchive/
   cd ExoArchive
   ```

2. **Criar um Ambiente Virtual** (opcional, mas recomendado):

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **Instalar as Dependências**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar as Credenciais da API**:

   - Abrir `src/config/config.py` e inserir a chave API (`X-API-Key`), `CLIENT_ID` e `CLIENT_SECRET` obtidos no portal de desenvolvedores do Bungie.net.

5. **Gerar Certificados SSL**:

   - Criar a pasta `certificates/` no diretório raiz do projeto.
   - No PowerShell, executar os seguintes comandos para gerar certificados autoassinados:
     ```powershell
     New-Item -ItemType Directory -Path {path}\certificates -Force
     cd {path}\certificates
     openssl req -x509 -newkey rsa:2048 -keyout localhost.key -out localhost.crt -days 365 -nodes -subj "/C=PT/ST=Estado/L=Cidade/O=MinhaApp/CN=localhost"
     ```

6. **Executar o Programa**:

   ```bash
   python main.py
   ```

   - O programa abrirá um navegador para autenticação OAuth no Bungie.net.
   - Após o login, o token será guardado em `destiny_manifest/oauth_token.json`.

---

## Como Funciona

O programa utiliza a API do Bungie.net para interagir com dados do Destiny 2. Abaixo estão as principais funcionalidades implementadas:

1. **Autenticação OAuth** (`oauth_manager.py`):

   - Inicia um fluxo OAuth, redirecionando o usuário para o Bungie.net.
   - Usa um servidor HTTPS local (porta 8080) para capturar o código de autorização.
   - Obtém e gerencia tokens de acesso e refresh tokens.

2. **Gerenciamento do Manifesto** (`manifest_manager.py`, `database_handler.py`):

   - Baixa o manifesto do Destiny 2 (banco de dados SQLite com definições de itens, atividades, etc.).
   - Extrai e armazena os dados em um arquivo pickle (`manifest.pickle`) para acesso rápido.
   - Organiza os dados em dicionários para facilitar buscas.

3. **Busca de Itens** (`item_search.py`):

   - Permite buscar itens por nome (ex.: "Gjallarhorn").
   - Busca itens por tipo (ex.: "Exotic") com ou sem descrição.
   - Exibe detalhes de itens específicos usando o hash.

4. **Informações do Jogador** (`player_information.py`):

   - Obtém informações do jogador (membershipId, membershipType) usando nome de usuário e tag.
   - Lista personagens do jogador, incluindo classe, nível de poder, raça e gênero.

5. **Inventário do Xur** (`vendor_manager.py`):

   - Consulta o inventário do vendedor Xur para um personagem específico.
   - Exibe detalhes dos itens à venda, usando dados do manifesto.

6. **Execução Principal** (`main.py`):
   - Integra todas as funcionalidades, permitindo testes com valores hardcoded (ex.: membership_type, destiny_membership_id, character_id).
   - Exibe informações do manifesto, jogador, personagens e itens do Xur.

---

## Exemplos de Uso

1. **Buscar um Item**:

   - No arquivo `main.py`, a função `search_items_by_name(manifest_data, "Gjallarhorn")` procura itens com "Gjallarhorn" no nome e exibe seus detalhes.

2. **Ver Itens do Xur**:

   - A chamada `display_xur_items(manifest_data, membership_type, destiny_membership_id, character_id)` mostra os itens à venda pelo Xur.

3. **Exibir Informações do Jogador**:
   - `display_player_variables("cosmy", "0588")` mostra o membershipId e membershipType do jogador.
   - `display_player_characters(membership_type, destiny_membership_id)` lista os personagens do jogador.

---

## Planos Futuros

- **Interface Gráfica**: Implementar uma interface com **PyQt**, **Tkinter** ou uma aplicação web (ex.: Flask ou FastAPI) para facilitar o uso.
- **Mais Funcionalidades do DIM**:
  - Gerenciamento de inventário do jogador (equipamento, transferência de itens).
  - Criação e aplicação de loadouts.
- **Integração com light.gg**:
  - Exibir avaliações de itens (god rolls) com base em dados da comunidade.
  - Comparação de perks e estatísticas.
- **Funcionalidades do TodayInDestiny**:
  - Mostrar atividades semanais (milestones, nightfalls, etc.).
  - Exibir recompensas disponíveis e progresso.
- **Testes Unitários**: Adicionar testes em `tests/` para validar chamadas à API e manipulação de dados.
- **Cache de Respostas**: Implementar cache local para reduzir chamadas à API e melhorar performance.
- **Suporte Multiplataforma**: Permitir busca de jogadores em diferentes plataformas (Steam, Xbox, PlayStation).
- **Documentação Avançada**: Criar guias detalhados e exemplos de uso em `docs/`.

---

## Contribuições

Este é um projeto de aprendizado, e contribuições são bem-vindas! Para contribuir:

1. Fazer um fork do repositório.
2. Criar uma branch para sua funcionalidade (`git checkout -b feature/nova-funcionalidade`).
3. Commit suas alterações (`git commit -m "Adiciona nova funcionalidade"`).
4. Enviar para o repositório remoto (`git push origin feature/nova-funcionalidade`).
5. Abrir um Pull Request.

---

## Problemas Conhecidos

- **Autenticação OAuth**: Requer certificados SSL locais, o que pode ser complexo para iniciantes.
- **Valores Hardcoded**: O arquivo `main.py` usa valores fixos para `membership_type`, `destiny_membership_id` e `character_id`. Futuras versões devem permitir entrada dinâmica.
- **Dependência de Conexão**: Algumas chamadas à API podem falhar se a conexão for instável ou se o token expirar.

---

## Licença

Este projeto é licenciado sob a [MIT License](LICENSE).

---

## Contato

Para dúvidas ou sugestões, entre em contato via [joaomiguelcurto@outlook.com] ou abra uma issue no repositório.
