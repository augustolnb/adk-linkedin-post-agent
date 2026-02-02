"""
LinkedIn Content Agent - Agente Root

Sistema Multi-Agentes para transformar notas técnicas em posts de LinkedIn.
Pipeline: Analyst → Researcher → Copywriter → ImageGenerator → Publisher
"""

from google.adk.agents import SequentialAgent

from .subagents.AnalystAgent import analyst_agent
from .subagents.ResearcherAgent import researcher_agent
from .subagents.CopywriterAgent import copywriter_agent
from .subagents.ImageGeneratorAgent import image_generator_agent
from .subagents.PublisherAgent import publisher_agent

# Pipeline Sequencial Principal (5 etapas)
root_agent = SequentialAgent(
    name="LinkedInContentAgent",
    sub_agents=[
        analyst_agent,          # Etapa 1: Analisa documento e gera briefing
        researcher_agent,       # Etapa 2: Busca contexto real-time
        copywriter_agent,       # Etapa 3: Gera post otimizado
        image_generator_agent,  # Etapa 4: Gera imagem para o post
        publisher_agent,        # Etapa 5: Publica no LinkedIn
    ],
    description="Transforma documentos técnicos em posts de alta performance para LinkedIn com imagem e publicação automática",
)
