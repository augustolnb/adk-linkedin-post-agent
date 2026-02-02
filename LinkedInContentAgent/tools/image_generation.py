"""
LinkedIn Content Engine - Ferramenta de Geração de Imagem

Este módulo fornece ferramenta para gerar imagens usando OpenAI GPT-4.1-mini.
"""

import os
import base64
from datetime import datetime
from typing import Any, Dict

from google.adk.tools.tool_context import ToolContext


def generate_image(prompt: str, style: str = "minimalist") -> Dict[str, Any]:
    """
    Gera uma imagem usando OpenAI GPT-4.1-mini.
    Requer: pip install openai

    Args:
        prompt: Descrição do que a imagem deve representar
        style: Estilo da imagem (minimalist, professional, creative)

    Returns:
        Dict com caminho da imagem gerada ou erro
    """
    try:
        try:
            from openai import OpenAI
        except ImportError:
            return {
                "success": False,
                "error": "openai não instalado. Execute: pip install openai"
            }
        
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return {
                "success": False,
                "error": "OPENAI_API_KEY não configurada no ambiente"
            }
        
        # Configura o cliente OpenAI
        client = OpenAI(api_key=api_key)
        
        # Aprimora o prompt para LinkedIn
        enhanced_prompt = f"""
        Generate a {style} and professional image for a LinkedIn post.
        The image should be:
        - Clean and minimalist design
        - No text or words in the image
        - Professional color palette (blues, greens, or neutral tones)
        - Visually represents: {prompt}
        - Suitable for a tech/engineering audience
        - Abstract or conceptual representation preferred
        - High quality, suitable for social media
        """
        
        print(f"\n[IMAGE] Gerando imagem com OpenAI GPT-4.1-mini...")
        print(f"[IMAGE] Prompt: {prompt[:100]}...")
        
        # Gera a imagem usando OpenAI GPT-4.1-mini
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=enhanced_prompt,
            tools=[{"type": "image_generation"}],
        )
        
        # Extrai dados da imagem da resposta
        image_data = [
            output.result
            for output in response.output
            if output.type == "image_generation_call"
        ]
        
        if image_data:
            # Salva a imagem
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_path = f"linkedin_post_image_{timestamp}.png"
            
            image_base64 = image_data[0]
            with open(image_path, "wb") as f:
                f.write(base64.b64decode(image_base64))
            
            print(f"[IMAGE] ✅ Imagem salva: {image_path}")
            
            return {
                "success": True,
                "image_path": os.path.abspath(image_path),
                "prompt_used": prompt,
                "style": style,
                "model": "gpt-4.1-mini"
            }
        else:
            return {
                "success": False,
                "error": "Imagem não foi gerada. Verifique o prompt ou tente novamente."
            }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Erro ao gerar imagem: {str(e)}"
        }


def generate_image_from_post(post_content: str) -> Dict[str, Any]:
    """
    Extrai conceitos-chave de um post e gera imagem apropriada.

    Args:
        post_content: Conteúdo do post LinkedIn

    Returns:
        Dict com caminho da imagem gerada
    """
    # Extrai as primeiras linhas para contexto
    lines = post_content.strip().split('\n')
    context = ' '.join(lines[:5])[:500]
    
    prompt = f"Abstract visual representation of: {context}"
    
    return generate_image(prompt, style="minimalist")
