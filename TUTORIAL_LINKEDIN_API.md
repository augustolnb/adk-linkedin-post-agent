# Tutorial: Configurando a API do LinkedIn

Este tutorial mostra como obter as credenciais necessárias para publicar automaticamente no LinkedIn.

---

## Pré-requisitos

- Conta no LinkedIn (pessoal ou empresa)
- Navegador web

---

## Passo 1: Criar App no LinkedIn Developers

### 1.1 Acessar o Portal de Desenvolvedores

1. Acesse: **https://developer.linkedin.com**
2. Clique em **"Create app"** (ou "Criar aplicativo")

### 1.2 Preencher Informações do App

| Campo | Valor Sugerido |
|-------|----------------|
| App name | `LinkedIn Content Engine` |
| LinkedIn Page | Selecione sua página (ou crie uma) |
| Privacy policy URL | Pode usar qualquer URL válida |
| App logo | Upload de uma imagem 100x100px |

3. Marque a caixa de termos e clique em **"Create app"**

---

## Passo 2: Configurar Produtos e Permissões

### 2.1 Adicionar Produtos

1. Na página do seu app, vá para a aba **"Products"**
2. Solicite acesso aos seguintes produtos:
   - **Share on LinkedIn** → Clique em "Request access"
   - **Sign In with LinkedIn using OpenID Connect** → Clique em "Request access"

> ⚠️ **Nota**: A aprovação pode levar alguns minutos.

### 2.2 Verificar Permissões (Scopes)

Após aprovação, vá na aba **"Auth"** e verifique se você tem:
- `openid`
- `profile`
- `email`
- `w_member_social` (permite postar)

---

## Passo 3: Obter Credenciais

### 3.1 Client ID e Client Secret

1. Na aba **"Auth"**, copie:
   - **Client ID**: `77xxxxxxxxxxxxxxx`
   - **Client Secret**: `xxxxxxxxxxxxxxxx`

### 3.2 Configurar Redirect URL

1. Na seção **"OAuth 2.0 settings"**
2. Adicione em **Authorized redirect URLs**:
   ```
   http://localhost:8000/callback
   ```

---

## Passo 4: Gerar Access Token

### Método A: Via LinkedIn Token Generator (Mais Fácil)

1. Na aba **"Auth"** do seu app
2. Role até **"OAuth 2.0 tools"**
3. Clique em **"Generate Member Token"**
4. Selecione os scopes:
   - [x] `openid`
   - [x] `profile`
   - [x] `email`
   - [x] `w_member_social`
5. Clique em **"Request access token"**
6. Faça login quando solicitado
7. Copie o **Access Token** gerado

### Método B: Via Script Python (Para Renovação)

```python
# linkedin_oauth.py
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import requests

# Suas credenciais
CLIENT_ID = "seu_client_id"
CLIENT_SECRET = "seu_client_secret"
REDIRECT_URI = "http://localhost:8000/callback"
SCOPES = "openid profile email w_member_social"

class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Extrai o código da URL
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        
        if "code" in params:
            code = params["code"][0]
            
            # Troca o código pelo token
            token_url = "https://www.linkedin.com/oauth/v2/accessToken"
            token_data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET
            }
            
            response = requests.post(token_url, data=token_data)
            tokens = response.json()
            
            print("\n" + "="*50)
            print("ACCESS TOKEN:")
            print(tokens.get("access_token", "Erro"))
            print("="*50 + "\n")
            
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h1>Token gerado! Volte ao terminal.</h1>")
        else:
            self.send_response(400)
            self.end_headers()

# Abre o navegador para autorização
auth_url = (
    f"https://www.linkedin.com/oauth/v2/authorization?"
    f"response_type=code&"
    f"client_id={CLIENT_ID}&"
    f"redirect_uri={urllib.parse.quote(REDIRECT_URI)}&"
    f"scope={urllib.parse.quote(SCOPES)}"
)

print("Abrindo navegador para autorização...")
webbrowser.open(auth_url)

# Inicia servidor para receber o callback
server = HTTPServer(("localhost", 8000), OAuthHandler)
print("Aguardando callback...")
server.handle_request()
```

Execute:
```bash
pip install requests
python linkedin_oauth.py
```

---

## Passo 5: Obter o Person URN

### 5.1 Via API

```bash
curl -X GET "https://api.linkedin.com/v2/userinfo" \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN"
```

A resposta contém o campo `sub` que é seu ID:
```json
{
  "sub": "abc123xyz",
  "name": "Seu Nome",
  "email": "seu@email.com"
}
```

### 5.2 Montar o URN

O **LINKEDIN_PERSON_URN** é:
```
urn:li:person:abc123xyz
```

---

## Passo 6: Configurar o .env

Edite o arquivo `linkedin_content_engine/.env`:

```env
# OpenAI e Anthropic (para os agentes)
OPENAI_API_KEY=sk-sua-chave-openai
ANTHROPIC_API_KEY=sk-ant-sua-chave-anthropic

# Google AI (para Gemini)
GOOGLE_API_KEY=sua-chave-google-ai

# LinkedIn API
LINKEDIN_ACCESS_TOKEN=AQVxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
LINKEDIN_PERSON_URN=urn:li:person:abc123xyz
```

---

## Passo 7: Testar a Conexão

### 7.1 Script de Teste

```python
# test_linkedin.py
import os
import requests
from dotenv import load_dotenv

load_dotenv("linkedin_content_engine/.env")

token = os.getenv("LINKEDIN_ACCESS_TOKEN")
headers = {"Authorization": f"Bearer {token}"}

response = requests.get(
    "https://api.linkedin.com/v2/userinfo",
    headers=headers
)

if response.status_code == 200:
    data = response.json()
    print(f"✅ Conectado como: {data['name']}")
    print(f"   Email: {data['email']}")
    print(f"   URN: urn:li:person:{data['sub']}")
else:
    print(f"❌ Erro: {response.status_code}")
    print(response.text)
```

Execute:
```bash
pip install python-dotenv requests
python test_linkedin.py
```

---

## Passo 8: Executar o Sistema

```bash
cd caminho_do_diretorio/
adk web
```

ou

```bash
cd caminho_do_diretorio/
python agent.py
```

Prompt de teste:
```
Leia o arquivo exemplo_nota_teste.md e publique um post no LinkedIn
```

---

## ⚠️ Notas Importantes

### Validade do Token
- O Access Token expira em **60 dias**
- Para renovar, repita o Passo 4

### Limites da API
- **100 posts por dia** para apps em desenvolvimento
- Sem limite para apps aprovados em produção

### Modo de Desenvolvimento vs Produção
- Em **desenvolvimento**: Só você pode usar o app
- Para **produção**: Submeta para revisão do LinkedIn

---

## 🔧 Troubleshooting

### Erro: "Unauthorized"
→ Token expirado. Gere um novo.

### Erro: "Insufficient permissions"
→ Verifique se o scope `w_member_social` está ativo.

### Erro: "Invalid URN"
→ Verifique o formato: `urn:li:person:SEU_ID`

### Post não aparece no perfil
→ Aguarde alguns segundos. O LinkedIn pode ter delay.

---

## Links Úteis

- [LinkedIn Developer Portal](https://developer.linkedin.com)
- [Documentação da API](https://learn.microsoft.com/en-us/linkedin/)
- [OAuth 2.0 Guide](https://learn.microsoft.com/en-us/linkedin/shared/authentication/authorization-code-flow)
