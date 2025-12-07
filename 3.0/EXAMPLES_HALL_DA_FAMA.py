"""
EXEMPLOS DE USO - Hall da Fama Service
Casos práticos e snippets de código
"""

# ============================================================================
# EXEMPLO 1: Adicionar um resultado manual
# ============================================================================

from services.hall_da_fama_service import adicionar_resultado_historico

# Adicionar João em 1º lugar em 2023
resultado = adicionar_resultado_historico(
    usuario_id=5,           # ID do usuário
    posicao=1,              # Posição (1-100)
    temporada="2023"        # Ano/Temporada
)

if resultado["success"]:
    print(f"✅ Registro adicionado com ID: {resultado['id']}")
    print(f"   Mensagem: {resultado['message']}")
else:
    print(f"❌ Erro: {resultado['message']}")

# Saída esperada:
# ✅ Registro adicionado com ID: 42
#    Mensagem: Resultado adicionado com sucesso


# ============================================================================
# EXEMPLO 2: Lidar com erros de validação
# ============================================================================

# Tentar adicionar duplicata
resultado = adicionar_resultado_historico(
    usuario_id=5,
    posicao=1,
    temporada="2023"  # Mesmo registro anterior
)

# resultado["success"] será False
# resultado["message"] será algo como:
# "Esse usuário já possui um registro para a temporada 2023"


# ============================================================================
# EXEMPLO 3: Editar um resultado existente
# ============================================================================

from services.hall_da_fama_service import editar_resultado_historico

# Corrigir a posição do registro anterior
resultado_edit = editar_resultado_historico(
    registro_id=42,     # ID do registro a editar
    posicao=2           # Nova posição
)

if resultado_edit["success"]:
    print(f"✅ Registro editado: {resultado_edit['message']}")


# ============================================================================
# EXEMPLO 4: Deletar um resultado
# ============================================================================

from services.hall_da_fama_service import deletar_resultado_historico

resultado_delete = deletar_resultado_historico(registro_id=42)

if resultado_delete["success"]:
    print(f"✅ Deletado: {resultado_delete['message']}")


# ============================================================================
# EXEMPLO 5: Importar múltiplos resultados em lote
# ============================================================================

from services.hall_da_fama_service import importar_resultados_em_lote

# Dados de uma temporada (exemplo 2022)
dados_2022 = [
    {"usuario_id": 1, "posicao": 1, "temporada": "2022"},
    {"usuario_id": 2, "posicao": 2, "temporada": "2022"},
    {"usuario_id": 3, "posicao": 3, "temporada": "2022"},
    {"usuario_id": 4, "posicao": 4, "temporada": "2022"},
    {"usuario_id": 5, "posicao": 5, "temporada": "2022"},
]

resultado_lote = importar_resultados_em_lote(dados_2022)

print(f"Importados: {resultado_lote['imported']}")
print(f"Ignorados: {resultado_lote['skipped']}")
print(f"Erros: {resultado_lote['errors']}")

# Saída esperada:
# Importados: 5
# Ignorados: 0
# Erros: []


# ============================================================================
# EXEMPLO 6: Obter histórico de um usuário
# ============================================================================

from services.hall_da_fama_service import obter_historico_usuario

# Pegar toda a história de um participante
historico = obter_historico_usuario(usuario_id=5)

for registro in historico:
    id_reg, posicao, temporada, data_atualizacao = registro
    print(f"{temporada}: {posicao}º lugar")

# Saída esperada:
# 2023: 2º lugar
# 2022: 5º lugar
# 2021: 3º lugar


# ============================================================================
# EXEMPLO 7: Listar todas as temporadas
# ============================================================================

from services.hall_da_fama_service import listar_todas_temporadas

temporadas = listar_todas_temporadas()
print(f"Temporadas disponíveis: {', '.join(temporadas)}")

# Saída esperada:
# Temporadas disponíveis: 2023, 2022, 2021, 2020


# ============================================================================
# EXEMPLO 8: Obter ranking de uma temporada específica
# ============================================================================

from services.hall_da_fama_service import obter_historico_temporada

ranking_2023 = obter_historico_temporada("2023")

for usuario_id, nome, posicao in ranking_2023:
    print(f"{posicao}º - {nome}")

# Saída esperada:
# 1º - João
# 2º - Maria
# 3º - Pedro


# ============================================================================
# EXEMPLO 9: Integração em uma função customizada
# ============================================================================

def adicionar_top_3_por_ano(ano: str, vencedor: int, segundo: int, terceiro: int):
    """Adiciona os 3 primeiros colocados de um ano."""
    from services.hall_da_fama_service import adicionar_resultado_historico
    
    resultados = []
    
    for usuario_id, posicao in [
        (vencedor, 1),
        (segundo, 2),
        (terceiro, 3),
    ]:
        resultado = adicionar_resultado_historico(
            usuario_id=usuario_id,
            posicao=posicao,
            temporada=ano
        )
        resultados.append(resultado)
    
    return resultados

# Uso:
# resultados = adicionar_top_3_por_ano("2024", vencedor=1, segundo=2, terceiro=3)


# ============================================================================
# EXEMPLO 10: Migração de dados legados
# ============================================================================

def migrar_dados_legados(dados_old_format: list):
    """
    Converte dados de formato antigo e importa.
    Formato antigo: [{"name": "João", "year": 2023, "rank": 1}, ...]
    """
    from db.db_utils import db_connect
    from services.hall_da_fama_service import importar_resultados_em_lote
    
    # Mapear nomes para IDs
    with db_connect() as conn:
        c = conn.cursor()
        c.execute("SELECT id, nome FROM usuarios")
        usuario_map = {nome: id_ for id_, nome in c.fetchall()}
    
    # Converter para novo formato
    dados_novo = []
    for item in dados_old_format:
        usuario_id = usuario_map.get(item["name"])
        if usuario_id:
            dados_novo.append({
                "usuario_id": usuario_id,
                "posicao": item["rank"],
                "temporada": str(item["year"])
            })
    
    # Importar em lote
    resultado = importar_resultados_em_lote(dados_novo)
    return resultado

# Uso:
# dados_legados = [{"name": "João", "year": 2023, "rank": 1}]
# resultado = migrar_dados_legados(dados_legados)


# ============================================================================
# EXEMPLO 11: Validação e tratamento de erros
# ============================================================================

def adicionar_com_validacao(usuario_id: int, posicao: int, temporada: str):
    """Adiciona resultado com validação customizada."""
    from services.hall_da_fama_service import adicionar_resultado_historico
    
    # Validação customizada
    if temporada and len(temporada) > 10:
        print("❌ Temporada muito longa")
        return None
    
    if posicao < 1 or posicao > 100:
        print("❌ Posição fora do intervalo 1-100")
        return None
    
    # Chamar serviço
    resultado = adicionar_resultado_historico(usuario_id, posicao, temporada)
    
    # Tratamento de resposta
    if resultado["success"]:
        print(f"✅ Sucesso: ID {resultado['id']}")
        return resultado["id"]
    else:
        print(f"❌ Erro: {resultado['message']}")
        return None


# ============================================================================
# EXEMPLO 12: Uso em Streamlit (UI)
# ============================================================================

import streamlit as st
from services.hall_da_fama_service import adicionar_resultado_historico
from db.db_utils import get_usuarios_df

def hall_da_fama_admin():
    """Painel de administração do Hall da Fama."""
    
    st.title("Hall da Fama - Administração")
    
    # Proteger acesso
    if st.session_state.get('user_role') != 'master':
        st.error("❌ Acesso restrito a Master")
        return
    
    # Form para adicionar resultado
    with st.form("add_result_form"):
        usuarios = get_usuarios_df()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            nome = st.selectbox("Participante", usuarios['nome'])
            usuario_id = usuarios[usuarios['nome'] == nome]['id'].values[0]
        
        with col2:
            temporada = st.number_input("Ano", 1990, 2100)
        
        with col3:
            posicao = st.number_input("Posição", 1, 100)
        
        if st.form_submit_button("Adicionar"):
            resultado = adicionar_resultado_historico(
                usuario_id=usuario_id,
                posicao=posicao,
                temporada=str(temporada)
            )
            
            if resultado["success"]:
                st.success(f"✅ {nome} adicionado!")
                st.balloons()
            else:
                st.error(f"❌ {resultado['message']}")

# Chamada: hall_da_fama_admin()


# ============================================================================
# NOTAS GERAIS
# ============================================================================

"""
PADRÕES DE RESPOSTA:

1. Sucesso de adição:
   {
       "success": True,
       "message": "Resultado adicionado com sucesso",
       "id": 42
   }

2. Erro de duplicata:
   {
       "success": False,
       "message": "Esse usuário já possui um registro para a temporada 2023"
   }

3. Sucesso de importação:
   {
       "success": True,
       "imported": 5,
       "skipped": 2,
       "errors": [],
       "message": "Importação concluída: 5 registros adicionados, 2 ignorados"
   }

4. Erro em importação:
   {
       "success": False,
       "imported": 0,
       "skipped": 5,
       "errors": ["Erro no item 0: usuario_id inválido"],
       "message": "Erro na importação: usuario_id inválido"
   }

LOGGING:
Todas as operações são logadas em "services.hall_da_fama"
Consulte os logs para auditoria e debugging.

PERFORMANCE:
- Operações únicas: ~100ms
- Importação lote (100 itens): ~1s
- Consultas: <10ms com índices

SEGURANÇA:
- Sempre usar prepared statements
- Validar tipos de dados
- Verificar permissões de usuário
- Usar transações para operações críticas
"""
