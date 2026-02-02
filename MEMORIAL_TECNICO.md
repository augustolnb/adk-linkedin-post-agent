# Memorial Técnico: LinkedIn Content Engine

## 1. Introdução

O **LinkedIn Content Engine** é um sistema multi-agentes desenvolvido para automatizar o processo de transformação de documentos técnicos em publicações otimizadas para a plataforma LinkedIn. A aplicação implementa um pipeline sequencial composto por cinco agentes especializados, cada um responsável por uma etapa específica do fluxo de produção de conteúdo, desde a análise inicial do documento até a publicação final na rede social.

O sistema foi desenvolvido utilizando o framework **Google Agent Development Kit (ADK)**, que fornece abstrações de alto nível para construção de agentes baseados em Large Language Models (LLMs). A arquitetura adota o padrão de orquestração sequencial (`SequentialAgent`), garantindo que cada etapa do pipeline seja executada em ordem determinística, com passagem de estado entre os agentes através de chaves de output definidas.

## 2. Arquitetura do Sistema

A arquitetura do LinkedIn Content Engine segue o paradigma de sistemas multi-agentes com orquestração centralizada. O agente raiz (`LinkedInContentEngine`) atua como orquestrador, coordenando a execução sequencial de cinco sub-agentes especializados. Cada sub-agente opera de forma autônoma dentro de seu escopo de responsabilidade, comunicando-se com os demais através de um estado compartilhado gerenciado pelo framework.

O fluxo de execução segue a seguinte ordem: **AnalystAgent → ResearcherAgent → CopywriterAgent → ImageGeneratorAgent → PublisherAgent**. Esta sequência foi projetada para simular o workflow de uma equipe de marketing de conteúdo, onde cada profissional contribui com sua especialidade para a produção do material final.

A comunicação entre agentes é realizada através do mecanismo de `output_key`, onde cada agente escreve seu resultado em uma chave específica do estado da sessão. Os agentes subsequentes podem acessar estes dados através de templates de interpolação no formato `{nome_da_chave}`, permitindo um fluxo de informação unidirecional e bem definido.

## 3. Descrição dos Componentes

### 3.1 AnalystAgent (Agente Analista)

O AnalystAgent constitui a primeira etapa do pipeline e é responsável pela ingestão e análise de documentos técnicos. Este agente utiliza o modelo `GPT-4.1-nano` através da integração LiteLLM, priorizando custo-benefício para operações que não requerem capacidades avançadas de geração de texto.

As ferramentas disponíveis para este agente incluem: `read_markdown_file` para leitura de arquivos Markdown, `read_pdf_file` para extração de texto de documentos PDF, e `scan_obsidian_vault` para listagem de arquivos em vaults do Obsidian. O output gerado (`analyst_briefing`) contém uma classificação do tipo de post (TECNICO, LIFESTYLE_ENGENHARIA ou NOTICIA_MERCADO), insights principais extraídos, palavras-chave identificadas e um resumo otimizado para consumo pelo agente redator.

### 3.2 ResearcherAgent (Agente Pesquisador)

O ResearcherAgent é responsável por enriquecer o briefing inicial com contexto real-time obtido através de buscas na web. Utilizando as ferramentas `search_web` e `search_news`, este agente consulta fontes externas para identificar tendências relacionadas ao tema, notícias recentes do setor e dados estatísticos relevantes.

O output produzido (`research_context`) inclui contexto de mercado, tendências relacionadas com fontes citadas, dados relevantes e sugestões de ganchos de atualidade que podem aumentar a relevância temporal do conteúdo. Este agente também utiliza o modelo `GPT-4.1-nano` para manter os custos operacionais controlados.

### 3.3 CopywriterAgent (Agente Redator)

O CopywriterAgent representa o componente central de geração de conteúdo do sistema. Diferentemente dos demais agentes, este utiliza o modelo `Claude-3.5-Sonnet` da Anthropic, reconhecido por sua capacidade superior de geração de texto criativo e contextualmente adequado.

Este agente não possui ferramentas externas, operando exclusivamente com as capacidades do LLM. Sua instrução de sistema incorpora diretrizes específicas para o algoritmo do LinkedIn, incluindo técnicas de hook de impacto, estruturação com white space para escaneabilidade, storytelling de engenharia e calls-to-action baseados em engajamento técnico. O output (`linkedin_post`) consiste no post completo pronto para publicação, com formatação adequada e hashtags posicionadas.

### 3.4 ImageGeneratorAgent (Agente Gerador de Imagem)

O ImageGeneratorAgent é responsável pela criação de assets visuais para acompanhar o post textual. Este agente analisa o conteúdo do post gerado e formula prompts descritivos para geração de imagens através da ferramenta `generate_image`, que internamente utiliza o modelo Gemini 2.0 Flash.

As diretrizes de geração priorizam imagens minimalistas e profissionais, sem texto embarcado, utilizando paletas de cores adequadas ao ambiente corporativo. O output (`image_url`) contém o caminho local do arquivo de imagem gerado.

### 3.5 PublisherAgent (Agente Publicador)

O PublisherAgent constitui a etapa final do pipeline, sendo responsável pela publicação efetiva do conteúdo no LinkedIn. Através da ferramenta `publish_to_linkedin`, que implementa integração com a API oficial da plataforma, este agente publica o post textual acompanhado da imagem gerada.

O output (`publish_result`) contém o status da operação de publicação, incluindo a URL do post publicado em caso de sucesso ou a descrição do erro em caso de falha.

## 4. Ferramentas Implementadas

O sistema implementa um conjunto de sete ferramentas especializadas, organizadas em módulos funcionais:

O módulo de **leitura de documentos** (`document_reader.py`) implementa funções para processamento de arquivos Markdown e PDF, além de integração com vaults do Obsidian para descoberta de conteúdo. O módulo de **busca web** (`web_search.py`) encapsula funcionalidades de pesquisa geral e busca específica de notícias. O módulo de **geração de imagem** (`image_generation.py`) implementa a integração com modelos generativos de imagem. Por fim, o módulo de **publicação** (`linkedin_publisher.py`) implementa a comunicação com a API do LinkedIn para posting automatizado.

## 5. Estratégia de Otimização de Custos

A arquitetura do sistema implementa uma estratégia deliberada de otimização de custos operacionais. O modelo de alto custo (`Claude-3.5-Sonnet`) é utilizado exclusivamente no CopywriterAgent, onde a qualidade superior de geração de texto justifica o investimento. Os demais agentes utilizam o modelo `GPT-4.1-nano`, um modelo de menor custo adequado para tarefas de análise, coordenação e execução de ferramentas.

Esta abordagem permite que o sistema processe um volume significativo de documentos mantendo os custos de inferência controlados, concentrando o investimento na etapa que mais impacta a qualidade final do conteúdo produzido.

## 6. Considerações Finais

O LinkedIn Content Engine demonstra a aplicação prática de arquiteturas multi-agentes para automação de workflows de produção de conteúdo. A modularização em agentes especializados permite manutenção independente de cada componente, facilitando ajustes de prompts, substituição de modelos ou adição de novas etapas ao pipeline.

A utilização do framework Google ADK proporciona abstrações robustas para gerenciamento de estado, orquestração de agentes e integração com múltiplos provedores de LLM através do LiteLLM. O padrão de `SequentialAgent` garante previsibilidade na execução, enquanto o mecanismo de `output_key` estabelece contratos claros de comunicação entre componentes.
