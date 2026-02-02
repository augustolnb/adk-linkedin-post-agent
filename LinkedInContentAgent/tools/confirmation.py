"""
LinkedIn Content Engine - Ferramenta de Confirmação

Este módulo fornece ferramenta para confirmar publicação via terminal.
"""

import os
from typing import Any, Dict, Optional


def confirm_post(
    post_content: str,
    image_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Exibe o post e imagem no terminal e pede confirmação do usuário.
    
    Args:
        post_content: Texto do post a ser publicado
        image_path: Caminho local da imagem (opcional)
    
    Returns:
        Dict com aprovação e feedback do usuário
    """
    try:
        print("\n" + "=" * 70)
        print("📋 REVISÃO DO POST ANTES DA PUBLICAÇÃO")
        print("=" * 70)
        
        # Exibe o post
        print("\n📝 CONTEÚDO DO POST:")
        print("-" * 50)
        print(post_content)
        print("-" * 50)
        
        # Exibe info da imagem
        if image_path and os.path.exists(image_path):
            print(f"\n🖼️  IMAGEM: {image_path}")
            print("   (Abra o arquivo para visualizar a imagem)")
        else:
            print("\n🖼️  IMAGEM: Nenhuma imagem para este post")
        
        print("\n" + "=" * 70)
        
        # Pede confirmação
        while True:
            response = input("\n🤔 Deseja publicar este post? (s/n/editar): ").strip().lower()
            
            if response in ['s', 'sim', 'y', 'yes']:
                print("✅ Post aprovado para publicação!")
                return {
                    "success": True,
                    "approved": True,
                    "message": "Post aprovado pelo usuário"
                }
            
            elif response in ['n', 'nao', 'não', 'no']:
                feedback = input("📝 Motivo da rejeição (opcional): ").strip()
                print("❌ Post rejeitado pelo usuário")
                return {
                    "success": True,
                    "approved": False,
                    "message": "Post rejeitado pelo usuário",
                    "feedback": feedback if feedback else "Sem feedback adicional"
                }
            
            elif response in ['editar', 'edit', 'e']:
                feedback = input("📝 O que você gostaria de mudar? ").strip()
                print("📝 Solicitação de edição registrada")
                return {
                    "success": True,
                    "approved": False,
                    "message": "Usuário solicitou edição",
                    "feedback": feedback,
                    "action": "edit"
                }
            
            else:
                print("⚠️  Resposta inválida. Digite 's' para sim, 'n' para não, ou 'editar' para modificar.")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Operação cancelada pelo usuário")
        return {
            "success": True,
            "approved": False,
            "message": "Operação cancelada pelo usuário (Ctrl+C)"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Erro ao solicitar confirmação: {str(e)}"
        }
