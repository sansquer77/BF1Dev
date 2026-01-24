\"\"\"
Interface de Gestão de Regras de Temporada
\"\"\"

import streamlit as st
import pandas as pd
import datetime

from db.rules_utils import (
    criar_regra,
    atualizar_regra,
    excluir_regra,
    listar_regras,
    associar_regra_temporada,
    get_regra_temporada,
    get_regra_by_id
)
from db.backup_utils import list_temporadas


def main():
    \"\"\"View principal de Gestão de Regras\"\"\"
    col1, col2 = st.columns([1, 16])
    with col1:
        st.image(\"BF1.jpg\", width=75)
    with col2:
        st.title(\"Gestão de Regras\")
    
    st.markdown(\"---\")
    
    tabs = st.tabs([\"Regras por Temporada\", \"Criar/Editar Regras\"])
    
    # ========== ABA: Regras por Temporada ==========
    with tabs[0]:
        st.subheader(\"Associar Regras às Temporadas\")
        
        try:
            temporadas = list_temporadas() or []
        except Exception:
            temporadas = []
        
        if not temporadas:
            # Fallback: anos recentes
            ano_atual = datetime.datetime.now().year
            temporadas = [str(ano_atual - 1), str(ano_atual), str(ano_atual + 1)]
        
        regras_disponiveis = listar_regras()
        if not regras_disponiveis:
            st.warning(\"Nenhuma regra cadastrada. Crie uma regra na aba 'Criar/Editar Regras'.\")
            return
        
        regras_nomes = {r['id']: r['nome_regra'] for r in regras_disponiveis}
        
        st.write(\"### Configuração Atual\")
        dados_config = []
        for temp in temporadas:
            regra_atual = get_regra_temporada(temp)
            dados_config.append({
                \"Temporada\": temp,
                \"Regra Aplicada\": regra_atual['nome_regra'] if regra_atual else \"Nenhuma\"
            })
        
        df_config = pd.DataFrame(dados_config)
        st.table(df_config)
        
        st.write(\"### Associar Nova Regra\")
        col_temp, col_regra = st.columns(2)
        
        with col_temp:
            temporada_selecionada = st.selectbox(
                \"Selecione a Temporada\",
                temporadas,
                key=\"temp_associar\"
            )
        
        with col_regra:
            regra_selecionada = st.selectbox(
                \"Selecione a Regra\",
                options=list(regras_nomes.keys()),
                format_func=lambda x: regras_nomes[x],
                key=\"regra_associar\"
            )
        
        if st.button(\"Associar Regra à Temporada\"):
            if associar_regra_temporada(temporada_selecionada, regra_selecionada):
                st.success(f\"Regra '{regras_nomes[regra_selecionada]}' associada à temporada {temporada_selecionada}!\")
                st.rerun()
            else:
                st.error(\"Erro ao associar regra à temporada.\")
    
    # ========== ABA: Criar/Editar Regras ==========
    with tabs[1]:
        st.subheader(\"Gerenciar Regras\")
        
        # Modo: Criar ou Editar
        regras_existentes = listar_regras()
        modo = st.radio(
            \"Modo\",
            [\"Criar Nova Regra\", \"Editar Regra Existente\", \"Excluir Regra\"],
            horizontal=True
        )
        
        if modo == \"Criar Nova Regra\":
            criar_regra_form()
        elif modo == \"Editar Regra Existente\":
            editar_regra_form(regras_existentes)
        else:  # Excluir Regra
            excluir_regra_form(regras_existentes)


def criar_regra_form():
    \"\"\"Formulário de criação de regra\"\"\"
    st.write(\"### Criar Nova Regra\")
    
    with st.form(\"form_criar_regra\"):
        nome_regra = st.text_input(\"Nome da Regra *\", placeholder=\"Ex: Regra 2025\")
        
        col1, col2 = st.columns(2)
        with col1:
            quantidade_fichas = st.number_input(
                \"Quantidade de Fichas *\",
                min_value=1,
                max_value=100,
                value=15,
                help=\"Total de fichas a serem distribuídas\"
            )
            
            mesma_equipe = st.selectbox(
                \"Permite Mesma Equipe? *\",
                [\"Não\", \"Sim\"],
                help=\"Permite apostar em 2 pilotos da mesma equipe?\"
            )
            
            fichas_por_piloto = st.number_input(
                \"Máximo Fichas por Piloto *\",
                min_value=1,
                max_value=100,
                value=15,
                help=\"Máximo de fichas que um piloto pode receber\"
            )
            
            descarte = st.selectbox(
                \"Descarte do Pior Resultado? *\",
                [\"Não\", \"Sim\"],
                help=\"Descarta o pior resultado da pontuação final?\"
            )
            
            pontos_11_colocado = st.number_input(
                \"Pontos pelo 11º Colocado *\",
                min_value=0,
                max_value=1000,
                value=25,
                help=\"Pontos por acertar o 11º colocado\"
            )
            
            qtd_minima_pilotos = st.number_input(
                \"Quantidade Mínima de Pilotos *\",
                min_value=1,
                max_value=20,
                value=3,
                help=\"Mínimo de pilotos que devem receber apostas\"
            )
            
            penalidade_abandono = st.selectbox(
                \"Penalidade por Abandono? *\",
                [\"Não\", \"Sim\"],
                help=\"Aplica penalidade se piloto apostado abandonar?\"
            )
        
        with col2:
            pontos_penalidade = st.number_input(
                \"Pontos de Penalidade\",
                min_value=0,
                max_value=1000,
                value=0,
                help=\"Pontos de penalidade (se opção anterior for Sim)\"
            )
            
            regra_sprint = st.selectbox(
                \"Regra Diferenciada para Sprint? *\",
                [\"Não\", \"Sim\"],
                help=\"Sprint limita fichas a 10 e mínimo de 2 pilotos?\"
            )
            
            provas_wildcard = st.selectbox(
                \"Provas Wildcard (Pontuação Dobrada)? *\",
                [\"Não\", \"Sim\"],
                help=\"Sprints contam com pontuação dobrada?\"
            )
            
            pontos_campeao = st.number_input(
                \"Pontos por Campeão *\",
                min_value=0,
                max_value=1000,
                value=150,
                help=\"Pontos por acertar o campeão do campeonato\"
            )
            
            pontos_vice = st.number_input(
                \"Pontos por Vice-Campeão *\",
                min_value=0,
                max_value=1000,
                value=100,
                help=\"Pontos por acertar o vice do campeonato\"
            )
            
            pontos_equipe = st.number_input(
                \"Pontos por Equipe Campeã *\",
                min_value=0,
                max_value=1000,
                value=80,
                help=\"Pontos por acertar a equipe campeã\"
            )
        
        submitted = st.form_submit_button(\"Criar Regra\")
        
        if submitted:
            if not nome_regra:
                st.error(\"Nome da regra é obrigatório!\")
                return
            
            sucesso = criar_regra(
                nome_regra=nome_regra,
                quantidade_fichas=quantidade_fichas,
                mesma_equipe=(mesma_equipe == \"Sim\"),
                fichas_por_piloto=fichas_por_piloto,
                descarte=(descarte == \"Sim\"),
                pontos_11_colocado=pontos_11_colocado,
                qtd_minima_pilotos=qtd_minima_pilotos,
                penalidade_abandono=(penalidade_abandono == \"Sim\"),
                pontos_penalidade=pontos_penalidade,
                regra_sprint=(regra_sprint == \"Sim\"),
                provas_wildcard=(provas_wildcard == \"Sim\"),
                pontos_campeao=pontos_campeao,
                pontos_vice=pontos_vice,
                pontos_equipe=pontos_equipe
            )
            
            if sucesso:
                st.success(f\"Regra '{nome_regra}' criada com sucesso!\")
                st.rerun()
            else:
                st.error(\"Erro ao criar regra. Verifique se o nome já não existe.\")


def editar_regra_form(regras_existentes):
    \"\"\"Formulário de edição de regra\"\"\"
    st.write(\"### Editar Regra Existente\")
    
    if not regras_existentes:
        st.warning(\"Nenhuma regra cadastrada para editar.\")
        return
    
    regras_dict = {r['nome_regra']: r['id'] for r in regras_existentes}
    regra_nome_selecionada = st.selectbox(
        \"Selecione a Regra para Editar\",
        list(regras_dict.keys())
    )
    
    regra_id = regras_dict[regra_nome_selecionada]
    regra_atual = get_regra_by_id(regra_id)
    
    if not regra_atual:
        st.error(\"Regra não encontrada.\")
        return
    
    with st.form(\"form_editar_regra\"):
        nome_regra = st.text_input(\"Nome da Regra *\", value=regra_atual['nome_regra'])
        
        col1, col2 = st.columns(2)
        with col1:
            quantidade_fichas = st.number_input(
                \"Quantidade de Fichas *\",
                min_value=1,
                max_value=100,
                value=regra_atual['quantidade_fichas']
            )
            
            mesma_equipe = st.selectbox(
                \"Permite Mesma Equipe? *\",
                [\"Não\", \"Sim\"],
                index=int(regra_atual['mesma_equipe'])
            )
            
            fichas_por_piloto = st.number_input(
                \"Máximo Fichas por Piloto *\",
                min_value=1,
                max_value=100,
                value=regra_atual['fichas_por_piloto']
            )
            
            descarte = st.selectbox(
                \"Descarte do Pior Resultado? *\",
                [\"Não\", \"Sim\"],
                index=int(regra_atual['descarte'])
            )
            
            pontos_11_colocado = st.number_input(
                \"Pontos pelo 11º Colocado *\",
                min_value=0,
                max_value=1000,
                value=regra_atual['pontos_11_colocado']
            )
            
            qtd_minima_pilotos = st.number_input(
                \"Quantidade Mínima de Pilotos *\",
                min_value=1,
                max_value=20,
                value=regra_atual['qtd_minima_pilotos']
            )
            
            penalidade_abandono = st.selectbox(
                \"Penalidade por Abandono? *\",
                [\"Não\", \"Sim\"],
                index=int(regra_atual['penalidade_abandono'])
            )
        
        with col2:
            pontos_penalidade = st.number_input(
                \"Pontos de Penalidade\",
                min_value=0,
                max_value=1000,
                value=regra_atual['pontos_penalidade'] or 0
            )
            
            regra_sprint = st.selectbox(
                \"Regra Diferenciada para Sprint? *\",
                [\"Não\", \"Sim\"],
                index=int(regra_atual['regra_sprint'])
            )
            
            provas_wildcard = st.selectbox(
                \"Provas Wildcard (Pontuação Dobrada)? *\",
                [\"Não\", \"Sim\"],
                index=int(regra_atual['provas_wildcard'])
            )
            
            pontos_campeao = st.number_input(
                \"Pontos por Campeão *\",
                min_value=0,
                max_value=1000,
                value=regra_atual['pontos_campeao']
            )
            
            pontos_vice = st.number_input(
                \"Pontos por Vice-Campeão *\",
                min_value=0,
                max_value=1000,
                value=regra_atual['pontos_vice']
            )
            
            pontos_equipe = st.number_input(
                \"Pontos por Equipe Campeã *\",
                min_value=0,
                max_value=1000,
                value=regra_atual['pontos_equipe']
            )
        
        submitted = st.form_submit_button(\"Atualizar Regra\")
        
        if submitted:
            if not nome_regra:
                st.error(\"Nome da regra é obrigatório!\")
                return
            
            sucesso = atualizar_regra(
                regra_id=regra_id,
                nome_regra=nome_regra,
                quantidade_fichas=quantidade_fichas,
                mesma_equipe=(mesma_equipe == \"Sim\"),
                fichas_por_piloto=fichas_por_piloto,
                descarte=(descarte == \"Sim\"),
                pontos_11_colocado=pontos_11_colocado,
                qtd_minima_pilotos=qtd_minima_pilotos,
                penalidade_abandono=(penalidade_abandono == \"Sim\"),
                pontos_penalidade=pontos_penalidade,
                regra_sprint=(regra_sprint == \"Sim\"),
                provas_wildcard=(provas_wildcard == \"Sim\"),
                pontos_campeao=pontos_campeao,
                pontos_vice=pontos_vice,
                pontos_equipe=pontos_equipe
            )
            
            if sucesso:
                st.success(f\"Regra '{nome_regra}' atualizada com sucesso!\")
                st.rerun()
            else:
                st.error(\"Erro ao atualizar regra.\")


def excluir_regra_form(regras_existentes):
    \"\"\"Formulário de exclusão de regra\"\"\"
    st.write(\"### Excluir Regra\")
    
    if not regras_existentes:
        st.warning(\"Nenhuma regra cadastrada para excluir.\")
        return
    
    regras_dict = {r['nome_regra']: r['id'] for r in regras_existentes}
    regra_nome_selecionada = st.selectbox(
        \"Selecione a Regra para Excluir\",
        list(regras_dict.keys()),
        key=\"excluir_regra_select\"
    )
    
    regra_id = regras_dict[regra_nome_selecionada]
    
    st.warning(f\"⚠️ Tem certeza que deseja excluir a regra '{regra_nome_selecionada}'?\")
    st.info(\"Nota: Regras em uso por temporadas não podem ser excluídas.\")
    
    if st.button(\"Confirmar Exclusão\", type=\"primary\"):
        if excluir_regra(regra_id):
            st.success(f\"Regra '{regra_nome_selecionada}' excluída com sucesso!\")
            st.rerun()
        else:
            st.error(\"Erro ao excluir regra. Ela pode estar em uso por uma temporada.\")


if __name__ == \"__main__\":
    main()
