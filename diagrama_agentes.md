# Diagrama do Sistema Multi-Agentes - LinkedIn Content Engine

Este diagrama representa a arquitetura do sistema multi-agentes para geração de conteúdo no LinkedIn.

## Arquitetura do Pipeline

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#E8F4FD', 'primaryTextColor': '#1E3A5F', 'primaryBorderColor': '#5B9BD5', 'lineColor': '#4A90D9', 'secondaryColor': '#F0F9E8', 'tertiaryColor': '#FFF5E6', 'background': '#FFFFFF'}}}%%
flowchart TB
    subgraph ROOT["🎯 LinkedInContentEngine<br/><i>SequentialAgent</i>"]
        direction TB
        
        subgraph ANALYST["📊 AnalystAgent"]
            direction TB
            A_DESC["Analisa documentos e gera briefing"]
            A_TOOLS["🔧 Ferramentas:<br/>• read_markdown_file<br/>• read_pdf_file<br/>• scan_obsidian_vault"]
            A_MODEL["🤖 GPT-4.1-nano"]
            A_OUT["📤 output: analyst_briefing"]
        end
        
        subgraph RESEARCHER["🔍 ResearcherAgent"]
            direction TB
            R_DESC["Pesquisa tendências e notícias"]
            R_TOOLS["🔧 Ferramentas:<br/>• search_web<br/>• search_news"]
            R_MODEL["🤖 GPT-4.1-nano"]
            R_OUT["📤 output: research_context"]
        end
        
        subgraph COPYWRITER["✍️ CopywriterAgent"]
            direction TB
            C_DESC["Gera post otimizado para LinkedIn"]
            C_TOOLS["🔧 Sem ferramentas externas"]
            C_MODEL["🤖 Claude-3.5-Sonnet"]
            C_OUT["📤 output: linkedin_post"]
        end
        
        subgraph IMAGE_GEN["🎨 ImageGeneratorAgent"]
            direction TB
            I_DESC["Cria imagem para o post"]
            I_TOOLS["🔧 Ferramentas:<br/>• generate_image"]
            I_MODEL["🤖 GPT-4.1-nano"]
            I_OUT["📤 output: image_url"]
        end
        
        subgraph PUBLISHER["📤 PublisherAgent"]
            direction TB
            P_DESC["Publica no LinkedIn"]
            P_TOOLS["🔧 Ferramentas:<br/>• publish_to_linkedin"]
            P_MODEL["🤖 GPT-4.1-nano"]
            P_OUT["📤 output: publish_result"]
        end
        
        ANALYST --> RESEARCHER
        RESEARCHER --> COPYWRITER
        COPYWRITER --> IMAGE_GEN
        IMAGE_GEN --> PUBLISHER
    end

    %% Input/Output
    INPUT["📄 Documento de Entrada<br/>(Markdown/PDF)"] --> ROOT
    ROOT --> OUTPUT["✅ Post Publicado no LinkedIn"]

    %% Styling
    style ROOT fill:#E8F4FD,stroke:#5B9BD5,stroke-width:3px
    style ANALYST fill:#F0F9E8,stroke:#7BC96F,stroke-width:2px
    style RESEARCHER fill:#FFF5E6,stroke:#F5A623,stroke-width:2px
    style COPYWRITER fill:#FCE4EC,stroke:#E91E63,stroke-width:2px
    style IMAGE_GEN fill:#E3F2FD,stroke:#2196F3,stroke-width:2px
    style PUBLISHER fill:#E8F5E9,stroke:#4CAF50,stroke-width:2px
    style INPUT fill:#FAFAFA,stroke:#9E9E9E,stroke-width:2px
    style OUTPUT fill:#E8F5E9,stroke:#4CAF50,stroke-width:2px
```

---

## Legenda dos Agentes

| Agente | Função | Ferramentas | Modelo |
|--------|--------|-------------|--------|
| **📊 AnalystAgent** | Lê documentos técnicos e extrai insights principais, gerando um briefing estruturado com tipo de post, palavras-chave e resumo otimizado | `read_markdown_file`, `read_pdf_file`, `scan_obsidian_vault` | GPT-4.1-nano (custo baixo) |
| **🔍 ResearcherAgent** | Busca contexto real-time relacionado ao tema, incluindo tendências, notícias recentes e dados relevantes | `search_web`, `search_news` | GPT-4.1-nano (custo baixo) |
| **✍️ CopywriterAgent** | Redige o post final aplicando técnicas de copywriting para LinkedIn (hook, storytelling, CTA técnico) | Nenhuma (LLM puro) | Claude-3.5-Sonnet (alta qualidade) |
| **🎨 ImageGeneratorAgent** | Gera uma imagem minimalista e profissional para acompanhar o post | `generate_image` | GPT-4.1-nano + Gemini 2.0 Flash |
| **📤 PublisherAgent** | Publica o post e a imagem diretamente no LinkedIn via API oficial | `publish_to_linkedin` | GPT-4.1-nano (custo baixo) |

---

## Legenda das Ferramentas

| Ferramenta | Descrição | Usada por |
|------------|-----------|-----------|
| `read_markdown_file` | Lê arquivos Markdown (.md) e extrai conteúdo | AnalystAgent |
| `read_pdf_file` | Lê arquivos PDF e extrai texto | AnalystAgent |
| `scan_obsidian_vault` | Lista arquivos de um Vault do Obsidian | AnalystAgent |
| `search_web` | Realiza buscas gerais na web para contexto | ResearcherAgent |
| `search_news` | Busca notícias recentes sobre o tema | ResearcherAgent |
| `generate_image` | Gera imagens usando Gemini 2.0 Flash | ImageGeneratorAgent |
| `publish_to_linkedin` | Publica posts na API oficial do LinkedIn | PublisherAgent |

---

## Fluxo de Dados

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#E8F4FD', 'lineColor': '#4A90D9'}}}%%
flowchart LR
    subgraph STATE["Estado Compartilhado"]
        direction TB
        S1["analyst_briefing"]
        S2["research_context"]
        S3["linkedin_post"]
        S4["image_url"]
        S5["publish_result"]
    end

    A["📊 Analyst"] -->|"gera"| S1
    S1 -->|"usa"| R["🔍 Researcher"]
    R -->|"gera"| S2
    S1 & S2 -->|"usam"| C["✍️ Copywriter"]
    C -->|"gera"| S3
    S3 -->|"usa"| I["🎨 ImageGen"]
    I -->|"gera"| S4
    S3 & S4 -->|"usam"| P["📤 Publisher"]
    P -->|"gera"| S5

    style STATE fill:#FFFDE7,stroke:#FBC02D,stroke-width:2px
    style A fill:#F0F9E8,stroke:#7BC96F
    style R fill:#FFF5E6,stroke:#F5A623
    style C fill:#FCE4EC,stroke:#E91E63
    style I fill:#E3F2FD,stroke:#2196F3
    style P fill:#E8F5E9,stroke:#4CAF50
```

---

## Notas Técnicas

- **Tipo de Orquestração**: `SequentialAgent` - executa os agentes em sequência fixa
- **Economia de Tokens**: Usamos GPT-4.1-nano (modelo barato) para a maioria das tarefas e Claude-3.5-Sonnet (modelo premium) apenas para o Copywriter
- **Estado Compartilhado**: Cada agente escreve seu output em uma chave específica (`output_key`) que fica disponível para os próximos agentes via template `{nome_da_chave}`
