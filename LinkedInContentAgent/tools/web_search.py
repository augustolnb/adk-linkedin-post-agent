"""
LinkedIn Content Engine - Ferramenta de Busca Web

Este módulo fornece ferramenta de busca usando DuckDuckGo.
"""

from typing import Any, Dict, List

from google.adk.tools.tool_context import ToolContext


def search_web(query: str, max_results: int = 5) -> Dict[str, Any]:
    """
    Realiza busca na web usando DuckDuckGo para encontrar tendências e notícias.
    Requer: pip install duckduckgo-search

    Args:
        query: Termo de busca
        max_results: Número máximo de resultados (padrão: 5)

    Returns:
        Dict com resultados da busca
    """
    try:
        try:
            from duckduckgo_search import DDGS
        except ImportError:
            return {
                "success": False,
                "error": "duckduckgo-search não instalado. Execute: pip install duckduckgo-search"
            }
        
        print(f"\n[SEARCH] Buscando: {query}")
        
        results = []
        
        with DDGS() as ddgs:
            # Busca geral
            search_results = list(ddgs.text(query, max_results=max_results))
            
            for result in search_results:
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("href", ""),
                    "snippet": result.get("body", "")
                })
        
        print(f"[SEARCH] Encontrados {len(results)} resultados")
        
        return {
            "success": True,
            "query": query,
            "results_count": len(results),
            "results": results
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Erro na busca: {str(e)}"
        }


def search_news(query: str, max_results: int = 5) -> Dict[str, Any]:
    """
    Busca notícias recentes sobre um tema usando DuckDuckGo News.
    Requer: pip install duckduckgo-search

    Args:
        query: Termo de busca para notícias
        max_results: Número máximo de resultados (padrão: 5)

    Returns:
        Dict com notícias encontradas
    """
    try:
        try:
            from duckduckgo_search import DDGS
        except ImportError:
            return {
                "success": False,
                "error": "duckduckgo-search não instalado. Execute: pip install duckduckgo-search"
            }
        
        print(f"\n[NEWS] Buscando notícias: {query}")
        
        results = []
        
        with DDGS() as ddgs:
            # Busca de notícias
            news_results = list(ddgs.news(query, max_results=max_results))
            
            for news in news_results:
                results.append({
                    "title": news.get("title", ""),
                    "url": news.get("url", ""),
                    "snippet": news.get("body", ""),
                    "source": news.get("source", ""),
                    "date": news.get("date", "")
                })
        
        print(f"[NEWS] Encontradas {len(results)} notícias")
        
        return {
            "success": True,
            "query": query,
            "results_count": len(results),
            "news": results
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Erro na busca de notícias: {str(e)}"
        }
