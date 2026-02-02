"""
LinkedIn Content Engine - Ferramenta de Publicação no LinkedIn

Este módulo fornece ferramenta para publicar posts diretamente no LinkedIn
usando a API oficial (gratuita para uso pessoal).
"""

import os
import requests
from typing import Any, Dict, Optional

from google.adk.tools.tool_context import ToolContext


def publish_to_linkedin(
    post_content: str,
    image_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Publica um post no LinkedIn usando a API oficial.
    Gratuita para uso pessoal (postar no próprio perfil).

    Requer no .env:
    - LINKEDIN_ACCESS_TOKEN: Token OAuth 2.0
    - LINKEDIN_PERSON_URN: URN do perfil (formato: urn:li:person:XXXXX)

    Args:
        post_content: Texto do post a ser publicado
        image_path: Caminho local da imagem (opcional)

    Returns:
        Dict com status da publicação
    """
    try:
        access_token = os.environ.get("LINKEDIN_ACCESS_TOKEN")
        person_urn = os.environ.get("LINKEDIN_PERSON_URN")
        
        if not access_token:
            return {
                "success": False,
                "error": "LINKEDIN_ACCESS_TOKEN não configurado no .env"
            }
        
        if not person_urn:
            return {
                "success": False,
                "error": "LINKEDIN_PERSON_URN não configurado no .env"
            }
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        print(f"\n[LINKEDIN] Publicando post...")
        
        # Se tem imagem, faz upload primeiro
        image_urn = None
        if image_path and os.path.exists(image_path):
            image_urn = _upload_image(access_token, person_urn, image_path)
            if image_urn:
                print(f"[LINKEDIN] Imagem enviada: {image_urn}")
        
        # Monta o payload do post
        if image_urn:
            # Post com imagem
            payload = {
                "author": person_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": post_content
                        },
                        "shareMediaCategory": "IMAGE",
                        "media": [
                            {
                                "status": "READY",
                                "media": image_urn
                            }
                        ]
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
        else:
            # Post apenas texto
            payload = {
                "author": person_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": post_content
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
        
        # Faz a requisição
        response = requests.post(
            "https://api.linkedin.com/v2/ugcPosts",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 201:
            post_id = response.headers.get("X-RestLi-Id", "")
            post_url = f"https://www.linkedin.com/feed/update/{post_id}"
            
            print(f"[LINKEDIN] ✅ Post publicado com sucesso!")
            print(f"[LINKEDIN] URL: {post_url}")
            
            return {
                "success": True,
                "post_id": post_id,
                "post_url": post_url,
                "message": "Post publicado com sucesso no LinkedIn!"
            }
        else:
            return {
                "success": False,
                "error": f"Erro ao publicar: {response.status_code} - {response.text}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Erro ao publicar no LinkedIn: {str(e)}"
        }


def _upload_image(access_token: str, person_urn: str, image_path: str) -> Optional[str]:
    """
    Faz upload de imagem para o LinkedIn.

    Args:
        access_token: Token de acesso
        person_urn: URN do perfil
        image_path: Caminho da imagem

    Returns:
        URN da imagem ou None se falhar
    """
    try:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        # Passo 1: Registrar o upload
        register_payload = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": person_urn,
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }
                ]
            }
        }
        
        register_response = requests.post(
            "https://api.linkedin.com/v2/assets?action=registerUpload",
            headers=headers,
            json=register_payload
        )
        
        if register_response.status_code != 200:
            print(f"[LINKEDIN] Erro ao registrar upload: {register_response.text}")
            return None
        
        register_data = register_response.json()
        upload_url = register_data["value"]["uploadMechanism"][
            "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"
        ]["uploadUrl"]
        asset_urn = register_data["value"]["asset"]
        
        # Passo 2: Fazer upload da imagem
        with open(image_path, "rb") as image_file:
            upload_response = requests.put(
                upload_url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "image/png"
                },
                data=image_file
            )
        
        if upload_response.status_code in [200, 201]:
            return asset_urn
        else:
            print(f"[LINKEDIN] Erro no upload da imagem: {upload_response.status_code}")
            return None
            
    except Exception as e:
        print(f"[LINKEDIN] Erro no upload: {str(e)}")
        return None


def get_linkedin_profile() -> Dict[str, Any]:
    """
    Obtém informações do perfil do usuário autenticado.
    Útil para verificar se o token está funcionando.

    Returns:
        Dict com informações do perfil
    """
    try:
        access_token = os.environ.get("LINKEDIN_ACCESS_TOKEN")
        
        if not access_token:
            return {
                "success": False,
                "error": "LINKEDIN_ACCESS_TOKEN não configurado"
            }
        
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        response = requests.get(
            "https://api.linkedin.com/v2/userinfo",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "name": data.get("name"),
                "email": data.get("email"),
                "sub": data.get("sub")  # Este é o ID do usuário
            }
        else:
            return {
                "success": False,
                "error": f"Erro: {response.status_code} - {response.text}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
