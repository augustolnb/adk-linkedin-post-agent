"""
Agente para publicações no LinkedInContentAgent com suporte a arquivos PDF e MD

Uso:
  python agent.py

O script irá perguntar:
  1. Caminho do arquivo (opcional) - PDF ou MD
  2. Prompt/instruções para o agente
"""
import asyncio
import time
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from LinkedInContentAgent import root_agent


def get_file_input() -> tuple[str | None, str]:
    """
    Solicita entrada do usuário para arquivo e prompt.
    
    Returns:
        Tuple com (caminho_arquivo, prompt)
    """
    print("\n" + "=" * 60)
    print("📁 ENTRADA DE ARQUIVO (opcional)")
    print("=" * 60)
    print("Formatos suportados: .pdf, .md")
    print("Deixe em branco para pular e usar apenas o prompt.")
    print("-" * 60)
    
    file_path = input("Caminho do arquivo: ").strip()
    
    # Valida o arquivo se fornecido
    if file_path:
        # Expande ~ para o diretório home
        file_path = os.path.expanduser(file_path)
        
        if not os.path.exists(file_path):
            print(f"⚠️  Arquivo não encontrado: {file_path}")
            file_path = None
        elif not file_path.endswith(('.pdf', '.md')):
            print(f"⚠️  Formato não suportado. Use .pdf ou .md")
            file_path = None
        else:
            # Converte para caminho absoluto
            file_path = os.path.abspath(file_path)
            print(f"✅ Arquivo válido: {file_path}")
    else:
        file_path = None
    
    print("\n" + "-" * 60)
    print("📝 PROMPT/INSTRUÇÕES")
    print("-" * 60)
    
    if file_path:
        print("Exemplo: 'Crie um post para LinkedIn com imagem'")
        print("         'Crie um post sem imagem sobre o conteúdo'")
    
    prompt = input("Prompt: ").strip()
    
    return file_path, prompt


def build_full_prompt(file_path: str | None, user_prompt: str) -> str:
    """
    Constrói o prompt completo para o agente.
    
    Args:
        file_path: Caminho do arquivo (opcional)
        user_prompt: Instruções do usuário
        
    Returns:
        Prompt completo formatado
    """
    if file_path:
        ext = os.path.splitext(file_path)[1].lower()
        file_type = "PDF" if ext == ".pdf" else "Markdown"
        
        full_prompt = f"""Leia o arquivo {file_type} localizado em: {file_path}

{user_prompt}"""
    else:
        full_prompt = user_prompt
    
    return full_prompt


async def test_agent():
    """Executa um teste do agente com suporte a arquivos"""
    
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
    
    # Obtém entrada do usuário (arquivo + prompt)
    file_path, user_prompt = get_file_input()
    
    # Constrói o prompt completo
    test_prompt = build_full_prompt(file_path, user_prompt)
    
    print(f"\n{'='*60}")
    print(f"🧪 TESTE DO LINKEDIN CONTENT AGENT")
    print(f"{'='*60}")
    print(f"📝 Prompt: {test_prompt}")
    print(f"{'='*60}\n")
    
    start_time = time.time()
    
    # Cria mensagem do usuário no formato correto
    user_message = types.Content(
        role="user",
        parts=[types.Part(text=test_prompt)]
    )
    
    # Executa o agente
    async for event in runner.run_async(
        user_id="test_user",
        session_id=session.id,
        new_message=user_message
    ):
        # Log de eventos
        if hasattr(event, 'content') and event.content:
            try:
                text = event.content.parts[0].text
                if text:  # Verifica se text não é None
                    preview = text[:100] + "..." if len(text) > 100 else text
                    print(f"📤 {event.author}: {preview}")
            except (IndexError, AttributeError):
                pass
    
    elapsed = time.time() - start_time
    
    print(f"\n{'='*60}")
    print(f"⏱️  Tempo total: {elapsed:.2f}s")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(test_agent())
