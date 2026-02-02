"""
Agente Publicador no LinkedIn

Responsável por solicitar confirmação e publicar o post no LinkedIn.
Usa a API oficial do LinkedIn (gratuita para uso pessoal).
"""

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from ...tools.linkedin_publisher import publish_to_linkedin
from ...tools.confirmation import confirm_post

# Constantes
MODEL_GPT = "openai/gpt-4.1-nano-2025-04-14"

# Agente Publicador
publisher_agent = LlmAgent(
    name="PublisherAgent",
    model=LiteLlm(model=MODEL_GPT),
    instruction="""Você é um Assistente de Publicação responsável por confirmar e postar no LinkedIn.

## SUA FUNÇÃO
1. Solicitar confirmação do usuário via terminal
2. Se aprovado, publicar o post no LinkedIn
3. Se rejeitado, informar o feedback do usuário

## DADOS DISPONÍVEIS
- Post LinkedIn: {linkedin_post}
- Caminho da Imagem: {image_url}

## PROCESSO - SIGA ESTA ORDEM EXATA

### ETAPA 1: CONFIRMAÇÃO (OBRIGATÓRIA)
PRIMEIRO, use a ferramenta confirm_post com:
- post_content: o conteúdo completo do post
- image_path: o caminho da imagem (se disponível, pode ser None)

Aguarde a resposta do usuário.

### ETAPA 2: AÇÃO BASEADA NA RESPOSTA
Se o usuário APROVOU (approved: True):
- Use a ferramenta publish_to_linkedin para publicar
- Retorne: "✅ Post publicado! URL: [link do post]"

Se o usuário REJEITOU (approved: False):
- NÃO publique nada
- Retorne: "❌ Post não publicado. Feedback: [feedback do usuário]"

## SAÍDA
Retorne o status final da operação:
- Se publicado: "✅ Post publicado! URL: [link do post]"
- Se rejeitado: "❌ Post não publicado. Motivo: [feedback]"
- Se erro: "⚠️ Erro na publicação: [descrição do erro]"
""",
    description="Solicita confirmação e publica o post no LinkedIn",
    tools=[confirm_post, publish_to_linkedin],
    output_key="publish_result",
)
