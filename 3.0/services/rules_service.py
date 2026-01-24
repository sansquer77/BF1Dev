\"\"\"
Serviço de Gestão de Regras
\"\"\"

import logging
from typing import Optional, Dict
from db.rules_utils import (
    get_regra_temporada,
    get_regra_by_nome
)

logger = logging.getLogger(__name__)


def get_regras_aplicaveis(temporada: str, tipo_prova: str = \"Normal\") -> Dict:
    \"\"\"
    Retorna as regras aplicáveis para uma temporada e tipo de prova
    
    Args:
        temporada: Ano da temporada
        tipo_prova: \"Normal\" ou \"Sprint\"
    
    Returns:
        Dict com parâmetros de regras aplicáveis
    \"\"\"
    regra = get_regra_temporada(temporada)
    
    # Fallback para regra padrão
    if not regra:
        regra = get_regra_by_nome(\"Padrão BF1\")
    
    if not regra:
        # Retorna regra hard-coded como último fallback
        logger.warning(f\"Nenhuma regra encontrada para temporada {temporada}, usando padrão hard-coded\")
        regra = {
            'quantidade_fichas': 15,
            'mesma_equipe': 0,
            'fichas_por_piloto': 15,
            'descarte': 0,
            'pontos_11_colocado': 25,
            'qtd_minima_pilotos': 3,
            'penalidade_abandono': 0,
            'pontos_penalidade': 0,
            'regra_sprint': 0,
            'provas_wildcard': 0,
            'pontos_campeao': 150,
            'pontos_vice': 100,
            'pontos_equipe': 80
        }
    
    # Ajusta regras para Sprint se configurado
    if tipo_prova == \"Sprint\" and regra.get('regra_sprint', 0):
        return {
            'quantidade_fichas': 10,  # Limitado para Sprint
            'mesma_equipe': regra.get('mesma_equipe', 0),
            'fichas_por_piloto': 10,  # Limitado para Sprint
            'qtd_minima_pilotos': 2,  # Ajustado para Sprint
            'pontos_11_colocado': regra.get('pontos_11_colocado', 25),
            'penalidade_abandono': regra.get('penalidade_abandono', 0),
            'pontos_penalidade': regra.get('pontos_penalidade', 0),
            'provas_wildcard': regra.get('provas_wildcard', 0),
            'descarte': regra.get('descarte', 0)
        }
    
    return {
        'quantidade_fichas': regra.get('quantidade_fichas', 15),
        'mesma_equipe': regra.get('mesma_equipe', 0),
        'fichas_por_piloto': regra.get('fichas_por_piloto', 15),
        'qtd_minima_pilotos': regra.get('qtd_minima_pilotos', 3),
        'pontos_11_colocado': regra.get('pontos_11_colocado', 25),
        'penalidade_abandono': regra.get('penalidade_abandono', 0),
        'pontos_penalidade': regra.get('pontos_penalidade', 0),
        'provas_wildcard': regra.get('provas_wildcard', 0),
        'descarte': regra.get('descarte', 0)
    }


def validar_aposta_regras(
    pilotos: list,
    fichas: list,
    equipes_apostadas: list,
    temporada: str,
    tipo_prova: str = \"Normal\"
) -> tuple[bool, Optional[str]]:
    \"\"\"
    Valida uma aposta contra as regras da temporada
    
    Returns:
        tuple: (valido: bool, mensagem_erro: Optional[str])
    \"\"\"
    regras = get_regras_aplicaveis(temporada, tipo_prova)
    
    # Validação: total de fichas
    total_fichas = sum(fichas)
    if total_fichas != regras['quantidade_fichas']:
        return False, f\"A soma das fichas deve ser exatamente {regras['quantidade_fichas']}.\"
    
    # Validação: fichas por piloto
    for ficha in fichas:
        if ficha > regras['fichas_por_piloto']:
            return False, f\"Um piloto não pode receber mais que {regras['fichas_por_piloto']} fichas.\"
    
    # Validação: mesma equipe
    if not regras['mesma_equipe']:
        if len(set(equipes_apostadas)) < len(equipes_apostadas):
            return False, \"Não é permitido apostar em dois pilotos da mesma equipe.\"
    
    # Validação: quantidade mínima de pilotos
    if len(pilotos) < regras['qtd_minima_pilotos']:
        return False, f\"Você deve apostar em pelo menos {regras['qtd_minima_pilotos']} pilotos.\"
    
    return True, None


def get_pontos_campeonato(temporada: str) -> Dict[str, int]:
    \"\"\"
    Retorna os pontos configurados para o campeonato
    
    Returns:
        Dict com pontos_campeao, pontos_vice, pontos_equipe
    \"\"\"
    regra = get_regra_temporada(temporada)
    
    if not regra:
        regra = get_regra_by_nome(\"Padrão BF1\")
    
    if not regra:
        return {
            'pontos_campeao': 150,
            'pontos_vice': 100,
            'pontos_equipe': 80
        }
    
    return {
        'pontos_campeao': regra.get('pontos_campeao', 150),
        'pontos_vice': regra.get('pontos_vice', 100),
        'pontos_equipe': regra.get('pontos_equipe', 80)
    }
