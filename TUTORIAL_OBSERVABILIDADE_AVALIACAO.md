# Tutorial: Testes, Métricas, Observabilidade e Avaliação

Este tutorial guia você na implementação de testes, métricas de tempo, observabilidade e avaliação para o sistema multi-agentes **LinkedInContentAgent**.

---

## 📋 Índice

1. [Testando o Sistema](#1-testando-o-sistema)
2. [Métricas de Tempo por Sub-Agente](#2-métricas-de-tempo-por-sub-agente)
3. [Observabilidade com OpenTelemetry](#3-observabilidade-com-opentelemetry)
4. [Avaliação de Qualidade (Evals)](#4-avaliação-de-qualidade-evals)
5. [Próximos Passos](#5-próximos-passos)

---

## 1. Testando o Sistema

### 1.1 Teste Manual via ADK Web

O ADK Web é a forma mais rápida de testar interativamente:

```bash
# Ative o ambiente virtual
source ~/Documentos/LAMIA/FC_Agentes/card10/.env_AKD/bin/activate

# Navegue até a pasta do projeto
cd ~/Documentos/LAMIA/FC_Agentes/card10/aula/13-pratica

# Inicie o servidor
adk web
```

Acesse `http://127.0.0.1:8000` e selecione **LinkedInContentAgent**.

**Prompt de teste básico:**
```
Leia o arquivo /home/augusto/Documentos/LAMIA/FC_Agentes/card10/aula/13-pratica/README.md e gere um post para LinkedIn sobre o projeto
```

### 1.2 Teste via Código Python

Crie um arquivo `test_agent.py` na pasta `13-pratica`:

```python
"""
Teste básico do LinkedInContentAgent
"""
import asyncio
import time
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv("LinkedInContentAgent/.env")

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from LinkedInContentAgent import root_agent


async def test_agent():
    """Executa um teste básico do agente"""
    
    # Configuração
    session_service = InMemorySessionService()
    runner = Runner(
        agent=root_agent,
        app_name="LinkedInContentAgent",
        session_service=session_service,
    )
    
    # Cria sessão
    session = await session_service.create_session(
        app_name="LinkedInContentAgent",
        user_id="test_user"
    )
    
    # Prompt de teste
    test_prompt = "Crie um post sobre sistemas multi-agentes com IA"
    
    print(f"\n{'='*60}")
    print(f"🧪 TESTE DO LINKEDIN CONTENT AGENT")
    print(f"{'='*60}")
    print(f"📝 Prompt: {test_prompt}")
    print(f"{'='*60}\n")
    
    start_time = time.time()
    
    # Executa o agente
    async for event in runner.run_async(
        user_id="test_user",
        session_id=session.id,
        new_message=test_prompt
    ):
        # Log de eventos
        if hasattr(event, 'content') and event.content:
            print(f"📤 {event.author}: {event.content.parts[0].text[:100]}...")
    
    elapsed = time.time() - start_time
    
    print(f"\n{'='*60}")
    print(f"⏱️  Tempo total: {elapsed:.2f}s")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(test_agent())
```

Execute:
```bash
python test_agent.py
```

---

## 2. Métricas de Tempo por Sub-Agente

### 2.1 Usando Callbacks do ADK

O Google ADK permite usar **callbacks** para interceptar eventos e medir tempos. Crie o arquivo `metrics_callback.py`:

```python
"""
Callback para métricas de tempo por sub-agente
"""
import time
from typing import Optional
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse


class MetricsCallback:
    """Callback que coleta métricas de tempo de execução"""
    
    def __init__(self):
        self.agent_times = {}
        self.current_agent = None
        self.start_time = None
    
    async def before_agent(
        self, 
        callback_context: CallbackContext
    ) -> Optional[LlmResponse]:
        """Chamado antes de cada agente executar"""
        agent_name = callback_context.agent_name
        self.current_agent = agent_name
        self.start_time = time.time()
        
        print(f"\n🚀 Iniciando: {agent_name}")
        return None  # Continua execução normal
    
    async def after_agent(
        self,
        callback_context: CallbackContext,
        response: LlmResponse
    ) -> Optional[LlmResponse]:
        """Chamado após cada agente executar"""
        if self.current_agent and self.start_time:
            elapsed = time.time() - self.start_time
            self.agent_times[self.current_agent] = elapsed
            
            print(f"✅ Finalizado: {self.current_agent} ({elapsed:.2f}s)")
        
        return response  # Retorna resposta sem modificar
    
    def print_summary(self):
        """Imprime resumo das métricas"""
        print(f"\n{'='*60}")
        print("📊 MÉTRICAS DE TEMPO POR AGENTE")
        print(f"{'='*60}")
        
        total = 0
        for agent, time_sec in self.agent_times.items():
            bar = "█" * int(time_sec * 2)  # Barra visual
            print(f"{agent:25} │ {time_sec:6.2f}s │ {bar}")
            total += time_sec
        
        print(f"{'='*60}")
        print(f"{'TOTAL':25} │ {total:6.2f}s")
        print(f"{'='*60}")
```

### 2.2 Usando o Callback no Agente

Modifique o `agent.py` para usar callbacks:

```python
from google.adk.agents import SequentialAgent
from .metrics_callback import MetricsCallback

# Instância do callback de métricas
metrics = MetricsCallback()

root_agent = SequentialAgent(
    name="LinkedInContentAgent",
    sub_agents=[...],
    before_agent_callback=metrics.before_agent,
    after_agent_callback=metrics.after_agent,
)
```

---

## 3. Observabilidade com OpenTelemetry

O Google ADK tem suporte nativo a **OpenTelemetry** para tracing distribuído.

### 3.1 Instalação

```bash
pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp
```

### 3.2 Configuração Básica

Crie `tracing_config.py`:

```python
"""
Configuração de OpenTelemetry para observabilidade
"""
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)
from opentelemetry.sdk.resources import Resource


def setup_tracing(service_name: str = "LinkedInContentAgent"):
    """Configura OpenTelemetry tracing"""
    
    # Recurso que identifica o serviço
    resource = Resource.create({
        "service.name": service_name,
        "service.version": "1.0.0",
    })
    
    # Provider de tracing
    provider = TracerProvider(resource=resource)
    
    # Exportador para console (para debug)
    console_exporter = ConsoleSpanExporter()
    provider.add_span_processor(BatchSpanProcessor(console_exporter))
    
    # Registra o provider globalmente
    trace.set_tracer_provider(provider)
    
    return trace.get_tracer(service_name)


def get_tracer():
    """Retorna o tracer configurado"""
    return trace.get_tracer("LinkedInContentAgent")
```

### 3.3 Instrumentando os Agentes

Adicione tracing nas ferramentas, por exemplo em `document_reader.py`:

```python
from opentelemetry import trace

tracer = trace.get_tracer("LinkedInContentAgent.tools")

def read_markdown_file(file_path: str) -> dict:
    """Lê arquivo Markdown com tracing"""
    
    with tracer.start_as_current_span("read_markdown_file") as span:
        span.set_attribute("file.path", file_path)
        
        # ... código existente ...
        
        span.set_attribute("file.size", len(content))
        span.set_status(trace.Status(trace.StatusCode.OK))
        
        return result
```

### 3.4 Usando Jaeger ou Zipkin (Opcional)

Para visualização avançada, use Jaeger:

```bash
# Sobe Jaeger via Docker
docker run -d --name jaeger \
  -p 16686:16686 \
  -p 4317:4317 \
  jaegertracing/all-in-one:latest
```

Modifique `tracing_config.py` para exportar para Jaeger:

```python
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

def setup_tracing_with_jaeger():
    # ... configuração anterior ...
    
    # Exportador OTLP para Jaeger
    otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4317")
    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
```

Acesse `http://localhost:16686` para visualizar os traces.

---

## 4. Avaliação de Qualidade (Evals)

O Google ADK possui sistema de **Evals** para avaliar a qualidade das respostas.

### 4.1 Criando um Eval Set

Na pasta `LinkedInContentAgent`, crie `eval_sets/basic_tests.json`:

```json
{
  "name": "basic_tests",
  "description": "Testes básicos do LinkedIn Content Agent",
  "test_cases": [
    {
      "id": "test_simple_post",
      "input": "Crie um post sobre inteligência artificial",
      "expected_tool_calls": ["search_web"],
      "expected_output_contains": ["#IA", "#AI"],
      "tags": ["basic", "no-document"]
    },
    {
      "id": "test_with_document",
      "input": "Leia o README.md e gere um post sobre o projeto",
      "expected_tool_calls": ["read_markdown_file"],
      "expected_output_contains": ["LinkedIn", "multi-agentes"],
      "tags": ["basic", "document"]
    }
  ]
}
```

### 4.2 Executando Avaliações

```bash
# Via CLI do ADK
adk eval LinkedInContentAgent --eval-set basic_tests

# Via ADK Web (aba Evals)
adk web
# Acesse http://127.0.0.1:8000 → Aba "Evals"
```

### 4.3 Métricas de Avaliação

O ADK calcula automaticamente:

| Métrica | Descrição |
|---------|-----------|
| **Tool Call Accuracy** | % de ferramentas corretas chamadas |
| **Output Match Rate** | % de outputs com conteúdo esperado |
| **Latency P50/P95** | Tempo de resposta (percentis) |
| **Token Usage** | Consumo de tokens por execução |

### 4.4 Avaliação com LLM-as-a-Judge

Para avaliação qualitativa, use um LLM como juiz:

```python
"""
Avaliação usando LLM como juiz
"""
from google import genai

def evaluate_post_quality(post_content: str) -> dict:
    """Usa Gemini para avaliar qualidade do post"""
    
    client = genai.Client()
    
    evaluation_prompt = f"""
    Avalie o seguinte post de LinkedIn de 1 a 10 nos critérios:
    
    1. HOOK (gancho inicial): A primeira linha prende atenção?
    2. VALOR: O post entrega valor técnico real?
    3. ESTRUTURA: Está bem formatado e escaneável?
    4. CTA: O call-to-action é efetivo?
    5. AUTENTICIDADE: Parece genuíno ou artificial?
    
    POST:
    ---
    {post_content}
    ---
    
    Responda em JSON:
    {{"hook": X, "valor": X, "estrutura": X, "cta": X, "autenticidade": X, "nota_geral": X, "feedback": "..."}}
    """
    
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=evaluation_prompt
    )
    
    return response.text
```

---

## 5. Próximos Passos

### ✅ Checklist de Implementação

- [ ] **Fase 1: Testes Básicos**
  - [ ] Criar `test_agent.py`
  - [ ] Testar via ADK Web
  - [ ] Verificar logs de execução

- [ ] **Fase 2: Métricas**
  - [ ] Implementar `MetricsCallback`
  - [ ] Registrar tempos por agente
  - [ ] Gerar relatório de performance

- [ ] **Fase 3: Observabilidade**
  - [ ] Instalar OpenTelemetry
  - [ ] Configurar tracing básico
  - [ ] (Opcional) Integrar com Jaeger

- [ ] **Fase 4: Avaliação**
  - [ ] Criar eval set com casos de teste
  - [ ] Executar avaliações via ADK
  - [ ] Implementar LLM-as-a-Judge

---

## 📚 Referências

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [OpenTelemetry Python](https://opentelemetry.io/docs/languages/python/)
- [Jaeger Tracing](https://www.jaegertracing.io/)

---

> **Dica**: Comece pela Fase 1 (testes básicos) e avance progressivamente. Cada fase adiciona uma camada de maturidade ao seu sistema de observabilidade.
