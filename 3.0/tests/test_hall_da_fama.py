"""
Testes para o serviço de Hall da Fama
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from services.hall_da_fama_service import (
    adicionar_resultado_historico,
    editar_resultado_historico,
    deletar_resultado_historico,
    importar_resultados_em_lote,
    obter_historico_usuario,
    obter_historico_temporada,
    listar_todas_temporadas
)
from db.db_utils import db_connect


def test_adicionar_resultado():
    """Testa adição de resultado histórico"""
    print("🧪 Teste 1: Adicionar resultado...")
    
    # Primeiro, garantir que temos um usuário
    with db_connect() as conn:
        c = conn.cursor()
        c.execute("SELECT id FROM usuarios LIMIT 1")
        user = c.fetchone()
        
        if not user:
            print("  ❌ Nenhum usuário disponível para teste")
            return False
        
        user_id = user[0]
    
    resultado = adicionar_resultado_historico(
        usuario_id=user_id,
        posicao=1,
        temporada="2025"
    )
    
    if resultado["success"]:
        print(f"  ✅ Resultado adicionado com ID: {resultado['id']}")
        return resultado["id"]
    else:
        print(f"  ❌ Erro: {resultado['message']}")
        return None


def test_editar_resultado(registro_id):
    """Testa edição de resultado"""
    print("🧪 Teste 2: Editar resultado...")
    
    if not registro_id:
        print("  ⏭️  Pulando - ID não disponível")
        return False
    
    resultado = editar_resultado_historico(
        registro_id=registro_id,
        posicao=2
    )
    
    if resultado["success"]:
        print(f"  ✅ Resultado editado: {resultado['message']}")
        return True
    else:
        print(f"  ❌ Erro: {resultado['message']}")
        return False


def test_obter_historico(usuario_id):
    """Testa obtenção de histórico"""
    print("🧪 Teste 3: Obter histórico do usuário...")
    
    historico = obter_historico_usuario(usuario_id)
    print(f"  ✅ Histórico obtido: {len(historico)} registros")
    return True


def test_listar_temporadas():
    """Testa listagem de temporadas"""
    print("🧪 Teste 4: Listar temporadas...")
    
    temporadas = listar_todas_temporadas()
    print(f"  ✅ Temporadas encontradas: {temporadas}")
    return True


def test_deletar_resultado(registro_id):
    """Testa deleção de resultado"""
    print("🧪 Teste 5: Deletar resultado...")
    
    if not registro_id:
        print("  ⏭️  Pulando - ID não disponível")
        return False
    
    resultado = deletar_resultado_historico(registro_id=registro_id)
    
    if resultado["success"]:
        print(f"  ✅ Resultado deletado: {resultado['message']}")
        return True
    else:
        print(f"  ❌ Erro: {resultado['message']}")
        return False


def test_importar_lote():
    """Testa importação em lote"""
    print("🧪 Teste 6: Importar em lote...")
    
    # Obter alguns usuários para teste
    with db_connect() as conn:
        c = conn.cursor()
        c.execute("SELECT id FROM usuarios LIMIT 3")
        users = [r[0] for r in c.fetchall()]
    
    if len(users) < 2:
        print("  ⏭️  Pulando - Poucos usuários disponíveis")
        return False
    
    dados = [
        {"usuario_id": users[0], "posicao": 1, "temporada": "2020"},
        {"usuario_id": users[1], "posicao": 2, "temporada": "2020"},
    ]
    
    resultado = importar_resultados_em_lote(dados)
    print(f"  ✅ Importação: {resultado['imported']} importados, {resultado['skipped']} ignorados")
    return resultado["success"]


def main():
    print("\n" + "="*60)
    print("🏆 TESTES - Hall da Fama Service")
    print("="*60 + "\n")
    
    # Executar testes
    registro_id = test_adicionar_resultado()
    print()
    
    test_editar_resultado(registro_id)
    print()
    
    # Obter um usuário para os próximos testes
    with db_connect() as conn:
        c = conn.cursor()
        c.execute("SELECT id FROM usuarios LIMIT 1")
        user = c.fetchone()
        user_id = user[0] if user else None
    
    if user_id:
        test_obter_historico(user_id)
        print()
    
    test_listar_temporadas()
    print()
    
    test_importar_lote()
    print()
    
    test_deletar_resultado(registro_id)
    print()
    
    print("="*60)
    print("✅ Testes concluídos!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
