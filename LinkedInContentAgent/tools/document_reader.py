"""
LinkedIn Content Engine - Ferramentas de Leitura de Documentos

Este módulo fornece ferramentas para ler arquivos Markdown e PDF.
"""

import os
import glob
from datetime import datetime
from typing import Any, Dict, List, Optional

from google.adk.tools.tool_context import ToolContext


def read_markdown_file(file_path: str) -> Dict[str, Any]:
    """
    Lê um arquivo Markdown e retorna seu conteúdo.

    Args:
        file_path: Caminho absoluto para o arquivo .md

    Returns:
        Dict com o conteúdo do arquivo e metadados
    """
    try:
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"Arquivo não encontrado: {file_path}"
            }
        
        if not file_path.endswith('.md'):
            return {
                "success": False,
                "error": "O arquivo deve ter extensão .md"
            }
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extrai metadados básicos
        lines = content.split('\n')
        title = ""
        tags = []
        
        for line in lines:
            if line.startswith('# ') and not title:
                title = line[2:].strip()
            if line.startswith('tags:') or '#' in line:
                # Extrai tags do formato Obsidian
                import re
                found_tags = re.findall(r'#(\w+)', line)
                tags.extend(found_tags)
        
        # Obtém data de modificação
        mod_time = os.path.getmtime(file_path)
        mod_date = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')
        
        return {
            "success": True,
            "file_path": file_path,
            "title": title or os.path.basename(file_path),
            "content": content,
            "char_count": len(content),
            "word_count": len(content.split()),
            "tags": list(set(tags)),
            "modified_date": mod_date
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Erro ao ler arquivo: {str(e)}"
        }


def read_pdf_file(file_path: str) -> Dict[str, Any]:
    """
    Lê um arquivo PDF e extrai seu texto.
    Requer: pip install pymupdf

    Args:
        file_path: Caminho absoluto para o arquivo .pdf

    Returns:
        Dict com o conteúdo extraído do PDF
    """
    try:
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"Arquivo não encontrado: {file_path}"
            }
        
        if not file_path.endswith('.pdf'):
            return {
                "success": False,
                "error": "O arquivo deve ter extensão .pdf"
            }
        
        try:
            import fitz  # PyMuPDF
        except ImportError:
            return {
                "success": False,
                "error": "PyMuPDF não instalado. Execute: pip install pymupdf"
            }
        
        doc = fitz.open(file_path)
        text_content = []
        
        for page_num, page in enumerate(doc):
            text = page.get_text()
            text_content.append({
                "page": page_num + 1,
                "content": text
            })
        
        full_text = "\n\n".join([p["content"] for p in text_content])
        
        return {
            "success": True,
            "file_path": file_path,
            "title": os.path.basename(file_path),
            "content": full_text,
            "page_count": len(doc),
            "char_count": len(full_text),
            "word_count": len(full_text.split())
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Erro ao ler PDF: {str(e)}"
        }


def scan_obsidian_vault(
    vault_path: str,
    filter_tag: Optional[str] = None,
    modified_after: Optional[str] = None
) -> Dict[str, Any]:
    """
    Percorre um diretório (Vault Obsidian) buscando arquivos .md.

    Args:
        vault_path: Caminho para o diretório do Vault
        filter_tag: Filtrar por tag específica (opcional)
        modified_after: Filtrar por data de modificação YYYY-MM-DD (opcional)

    Returns:
        Dict com lista de arquivos encontrados
    """
    try:
        if not os.path.isdir(vault_path):
            return {
                "success": False,
                "error": f"Diretório não encontrado: {vault_path}"
            }
        
        # Busca todos os arquivos .md recursivamente
        pattern = os.path.join(vault_path, '**', '*.md')
        files = glob.glob(pattern, recursive=True)
        
        results = []
        
        for file_path in files:
            # Pula arquivos de configuração do Obsidian
            if '.obsidian' in file_path:
                continue
            
            file_info = read_markdown_file(file_path)
            
            if not file_info["success"]:
                continue
            
            # Aplica filtro de tag
            if filter_tag and filter_tag not in file_info.get("tags", []):
                continue
            
            # Aplica filtro de data
            if modified_after:
                mod_date = file_info.get("modified_date", "")[:10]
                if mod_date < modified_after:
                    continue
            
            results.append({
                "path": file_path,
                "title": file_info["title"],
                "tags": file_info["tags"],
                "modified_date": file_info["modified_date"],
                "word_count": file_info["word_count"]
            })
        
        # Ordena por data de modificação (mais recente primeiro)
        results.sort(key=lambda x: x["modified_date"], reverse=True)
        
        return {
            "success": True,
            "vault_path": vault_path,
            "files_found": len(results),
            "files": results[:20]  # Limita a 20 resultados
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Erro ao escanear vault: {str(e)}"
        }
