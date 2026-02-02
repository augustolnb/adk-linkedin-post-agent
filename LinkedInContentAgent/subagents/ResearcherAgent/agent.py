"""
Agente Researcher (Contexto Real-time)

Responsável por buscar tendências e notícias relacionadas ao tema.
"""

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

#from ...tools.web_search import search_web, search_news
from google.adk.tools.langchain_tool import LangchainTool
from langchain_community.tools import DuckDuckGoSearchRun

# Constantes
MODEL_GPT = "openai/gpt-4.1-nano-2025-04-14"

# instancia duck duck go
duckduckgo_tool_instance = DuckDuckGoSearchRun(
    max_results = 3,
)

# add ddg_search como uma ferramenta adk
adk_duckduckgo_tool = LangchainTool(
    tool=duckduckgo_tool_instance,
)

# Agente Researcher
researcher_agent = LlmAgent(
    name="ResearcherAgent",
    model=LiteLlm(model=MODEL_GPT),
    instruction="""Você é um Pesquisador de Tendências especializado em adicionar contexto real-time a conteúdos técnicos.

## SUA FUNÇÃO
Baseado no briefing do Analista, buscar informações atuais que possam enriquecer o post:
1. Tendências relacionadas ao tema
2. Notícias recentes do setor
3. Dados ou estatísticas relevantes

## BRIEFING DO ANALISTA
{analyst_briefing}

## FERRAMENTAS DISPONÍVEIS
- adk_duckduckgo_tool: Busca específica de notícias recentes

## ESTRATÉGIA DE BUSCA
1. Extraia 2-3 termos-chave do briefing
2. Faça buscas focadas nesses termos
3. Priorize resultados recentes (últimos 30 dias)
4. Selecione apenas informações RELEVANTES ao tema

## FORMATO DE SAÍDA
```
CONTEXTO_MERCADO:
[2-3 frases sobre o cenário atual do tema]

TENDENCIAS_RELACIONADAS:
- [Tendência 1 com fonte]
- [Tendência 2 com fonte]

DADOS_RELEVANTES:
- [Estatística ou dado interessante]

GANCHO_ATUALIDADE:
[Uma conexão entre o tema do post e algo atual/trending]

FONTES:
- [URL 1]
- [URL 2]
```

## IMPORTANTE
- Busque informações que AGREGUEM VALOR ao post
- Evite informações genéricas ou desatualizadas
- Priorize fontes confiáveis (tech blogs, portais de notícias)
- Seja CONCISO - o Redator precisa de contexto, não de artigos completos
""",
    description="Pesquisa tendências e notícias para enriquecer o post",
    tools=[adk_duckduckgo_tool],
    output_key="research_context",
)
