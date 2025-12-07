"""
Hall da Fama - Classificações Históricas
Exibe uma tabela pivot com todos os anos (colunas) e posições de classificação (linhas),
mostrando o nome do participante em cada célula para cada ano/posição.
"""

import streamlit as st
import pandas as pd
from db.db_utils import (
    db_connect,
    get_usuarios_df
)


def hall_da_fama():
    """Exibe hall da fama com histórico plurianual."""
    st.title("🏆 Hall da Fama")
    st.write("Histórico de classificações por temporada - Melhores posições em cada ano")

    conn = db_connect()
    try:
        # Get all unique years/seasons from posicoes_participantes
        c = conn.cursor()
        c.execute("SELECT DISTINCT temporada FROM posicoes_participantes ORDER BY temporada DESC")
        seasons = [r[0] for r in c.fetchall()]
        
        if not seasons:
            st.info("Nenhuma classificação registrada ainda.")
            return
        
        st.write(f"**Temporadas disponíveis:** {', '.join(seasons)}")
        
        # Get all users
        usuarios = get_usuarios_df()
        if usuarios.empty:
            st.warning("Nenhum usuário cadastrado.")
            return
        
        # Build the hall of fame table
        # For each user, find their best position in each season
        hall_data = []
        
        for _, user in usuarios.iterrows():
            user_id = user['id']
            user_name = user['nome']
            row = {'Participante': user_name}
            
            for season in seasons:
                c.execute('''
                    SELECT MIN(posicao) as melhor_posicao 
                    FROM posicoes_participantes 
                    WHERE usuario_id = ? AND temporada = ?
                ''', (user_id, season))
                result = c.fetchone()
                
                if result and result[0]:
                    row[season] = f"{result[0]}º"
                else:
                    row[season] = "-"
            
            hall_data.append(row)
        
        # Sort by overall best position (number of top-10 finishes, then best position)
        # Simple heuristic: count how many seasons participated and best position
        def score_user(row):
            participated = sum(1 for v in row.values() if v != "-")
            best_pos = min([int(v.replace("º", "")) for v in row.values() if v != "-"], default=9999)
            return (-participated, best_pos)
        
        hall_data.sort(key=score_user)
        
        # Create DataFrame and display
        df_hall = pd.DataFrame(hall_data)
        
        st.markdown("---")
        st.subheader("Classificações Históricas")
        st.dataframe(
            df_hall.set_index('Participante'),
            use_container_width=True,
            column_config={season: st.column_config.TextColumn() for season in seasons}
        )
        
        # Summary stats
        st.markdown("---")
        st.subheader("Estatísticas")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Participantes", len(usuarios))
        with col2:
            c.execute("SELECT COUNT(DISTINCT temporada) FROM posicoes_participantes")
            unique_seasons = c.fetchone()[0]
            st.metric("Temporadas com Resultados", unique_seasons)
        with col3:
            c.execute("SELECT COUNT(*) FROM posicoes_participantes")
            total_records = c.fetchone()[0]
            st.metric("Total de Registros", total_records)
        
        # Per-season breakdown
        st.markdown("---")
        st.subheader("Resumo por Temporada")
        
        season_stats = []
        for season in seasons:
            c.execute('''
                SELECT COUNT(DISTINCT usuario_id) as participants,
                       MIN(posicao) as best_pos,
                       AVG(posicao) as avg_pos
                FROM posicoes_participantes
                WHERE temporada = ?
            ''', (season,))
            result = c.fetchone()
            if result:
                season_stats.append({
                    'Temporada': season,
                    'Participantes': result[0],
                    'Melhor Posição': f"{result[1]}º" if result[1] else "-",
                    'Posição Média': f"{result[2]:.1f}" if result[2] else "-"
                })
        
        if season_stats:
            st.dataframe(
                pd.DataFrame(season_stats),
                use_container_width=True,
                hide_index=True
            )
        
        # Podium view (optional - top 3 of all time)
        st.markdown("---")
        st.subheader("🥇 Podium (Melhor Posição All-Time)")
        
        c.execute('''
            SELECT u.nome, MIN(pp.posicao) as best_ever, COUNT(DISTINCT pp.temporada) as temporadas
            FROM posicoes_participantes pp
            JOIN usuarios u ON pp.usuario_id = u.id
            GROUP BY pp.usuario_id
            ORDER BY best_ever ASC, temporadas DESC
            LIMIT 10
        ''')
        
        podium = c.fetchall()
        if podium:
            medals = ['🥇', '🥈', '🥉']
            for idx, (name, best_pos, seasons_count) in enumerate(podium):
                medal = medals[idx] if idx < 3 else f"{idx + 1}."
                st.write(f"{medal} **{name}** - Melhor posição: {best_pos}º (em {seasons_count} temporadas)")
    
    finally:
        conn.close()


if __name__ == "__main__":
    hall_da_fama()
