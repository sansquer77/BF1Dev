#!/usr/bin/env python3
"""
Script para importar resultados históricos (20 anos de dados).
Popula a tabela posicoes_participantes com dados de temporadas anteriores.
"""

import sys
import sqlite3
import argparse
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.db_utils import db_connect

def import_historical_results(db_path, data_file=None):
    """
    Importa resultados históricos de um arquivo CSV ou usa dados de exemplo.
    
    Args:
        db_path: Caminho para o banco de dados SQLite
        data_file: (Opcional) Caminho para arquivo CSV com dados históricos
    
    Formato esperado do CSV:
    temporada,usuario_id,posicao
    2005,1,5
    2005,2,3
    ...
    """
    
    conn = db_connect(db_path)
    cursor = conn.cursor()
    
    # Dados de exemplo: 20 temporadas (2005-2024) com rankings fictícios
    historical_data = [
        # Temporada 2005
        (2005, 1, 1), (2005, 2, 2), (2005, 3, 3), (2005, 4, 4), (2005, 5, 5),
        (2005, 6, 6), (2005, 7, 7), (2005, 8, 8), (2005, 9, 9), (2005, 10, 10),
        
        # Temporada 2006
        (2006, 1, 3), (2006, 2, 1), (2006, 3, 2), (2006, 4, 5), (2006, 5, 4),
        (2006, 6, 7), (2006, 7, 6), (2006, 8, 9), (2006, 9, 8), (2006, 10, 10),
        
        # Temporada 2007
        (2007, 1, 2), (2007, 2, 3), (2007, 3, 1), (2007, 4, 6), (2007, 5, 5),
        (2007, 6, 4), (2007, 7, 8), (2007, 8, 7), (2007, 9, 10), (2007, 10, 9),
        
        # Temporada 2008
        (2008, 1, 4), (2008, 2, 2), (2008, 3, 3), (2008, 4, 1), (2008, 5, 6),
        (2008, 6, 5), (2008, 7, 9), (2008, 8, 8), (2008, 9, 7), (2008, 10, 10),
        
        # Temporada 2009
        (2009, 1, 5), (2009, 2, 4), (2009, 3, 2), (2009, 4, 3), (2009, 5, 1),
        (2009, 6, 8), (2009, 7, 7), (2009, 8, 6), (2009, 9, 9), (2009, 10, 10),
        
        # Temporada 2010
        (2010, 1, 6), (2010, 2, 5), (2010, 3, 4), (2010, 4, 2), (2010, 5, 3),
        (2010, 6, 1), (2010, 7, 9), (2010, 8, 8), (2010, 9, 10), (2010, 10, 7),
        
        # Temporada 2011
        (2011, 1, 7), (2011, 2, 6), (2011, 3, 5), (2011, 4, 4), (2011, 5, 2),
        (2011, 6, 3), (2011, 7, 1), (2011, 8, 10), (2011, 9, 8), (2011, 10, 9),
        
        # Temporada 2012
        (2012, 1, 8), (2012, 2, 7), (2012, 3, 6), (2012, 4, 5), (2012, 5, 4),
        (2012, 6, 2), (2012, 7, 3), (2012, 8, 1), (2012, 9, 10), (2012, 10, 9),
        
        # Temporada 2013
        (2013, 1, 9), (2013, 2, 8), (2013, 3, 7), (2013, 4, 6), (2013, 5, 5),
        (2013, 6, 4), (2013, 7, 2), (2013, 8, 3), (2013, 9, 1), (2013, 10, 10),
        
        # Temporada 2014
        (2014, 1, 10), (2014, 2, 9), (2014, 3, 8), (2014, 4, 7), (2014, 5, 6),
        (2014, 6, 5), (2014, 7, 4), (2014, 8, 2), (2014, 9, 3), (2014, 10, 1),
        
        # Temporada 2015
        (2015, 1, 1), (2015, 2, 10), (2015, 3, 9), (2015, 4, 8), (2015, 5, 7),
        (2015, 6, 6), (2015, 7, 5), (2015, 8, 4), (2015, 9, 2), (2015, 10, 3),
        
        # Temporada 2016
        (2016, 1, 2), (2016, 2, 1), (2016, 3, 10), (2016, 4, 9), (2016, 5, 8),
        (2016, 6, 7), (2016, 7, 6), (2016, 8, 5), (2016, 9, 4), (2016, 10, 3),
        
        # Temporada 2017
        (2017, 1, 3), (2017, 2, 2), (2017, 3, 1), (2017, 4, 10), (2017, 5, 9),
        (2017, 6, 8), (2017, 7, 7), (2017, 8, 6), (2017, 9, 5), (2017, 10, 4),
        
        # Temporada 2018
        (2018, 1, 4), (2018, 2, 3), (2018, 3, 2), (2018, 4, 1), (2018, 5, 10),
        (2018, 6, 9), (2018, 7, 8), (2018, 8, 7), (2018, 9, 6), (2018, 10, 5),
        
        # Temporada 2019
        (2019, 1, 5), (2019, 2, 4), (2019, 3, 3), (2019, 4, 2), (2019, 5, 1),
        (2019, 6, 10), (2019, 7, 9), (2019, 8, 8), (2019, 9, 7), (2019, 10, 6),
        
        # Temporada 2020
        (2020, 1, 6), (2020, 2, 5), (2020, 3, 4), (2020, 4, 3), (2020, 5, 2),
        (2020, 6, 1), (2020, 7, 10), (2020, 8, 9), (2020, 9, 8), (2020, 10, 7),
        
        # Temporada 2021
        (2021, 1, 7), (2021, 2, 6), (2021, 3, 5), (2021, 4, 4), (2021, 5, 3),
        (2021, 6, 2), (2021, 7, 1), (2021, 8, 10), (2021, 9, 9), (2021, 10, 8),
        
        # Temporada 2022
        (2022, 1, 8), (2022, 2, 7), (2022, 3, 6), (2022, 4, 5), (2022, 5, 4),
        (2022, 6, 3), (2022, 7, 2), (2022, 8, 1), (2022, 9, 10), (2022, 10, 9),
        
        # Temporada 2023
        (2023, 1, 9), (2023, 2, 8), (2023, 3, 7), (2023, 4, 6), (2023, 5, 5),
        (2023, 6, 4), (2023, 7, 3), (2023, 8, 2), (2023, 9, 1), (2023, 10, 10),
        
        # Temporada 2024
        (2024, 1, 10), (2024, 2, 9), (2024, 3, 8), (2024, 4, 7), (2024, 5, 6),
        (2024, 6, 5), (2024, 7, 4), (2024, 8, 3), (2024, 9, 2), (2024, 10, 1),
    ]
    
    if data_file and Path(data_file).exists():
        print(f"Lendo dados do arquivo: {data_file}")
        historical_data = []
        with open(data_file, 'r', encoding='utf-8') as f:
            # Skip header
            next(f)
            for line in f:
                parts = line.strip().split(',')
                if len(parts) >= 3:
                    try:
                        temporada = int(parts[0])
                        usuario_id = int(parts[1])
                        posicao = int(parts[2])
                        historical_data.append((temporada, usuario_id, posicao))
                    except ValueError:
                        print(f"  ⚠️  Erro ao processar linha: {line}")
        
        print(f"✅ Lidos {len(historical_data)} registros do arquivo")
    
    # Check if posicoes_participantes table exists and has temporada column
    try:
        cursor.execute("PRAGMA table_info(posicoes_participantes)")
        cols = [r[1] for r in cursor.fetchall()]
        
        if 'temporada' not in cols:
            print("❌ Erro: Coluna 'temporada' não existe em posicoes_participantes")
            print("   Execute primeiro: db/migrations.py")
            return False
    except Exception as e:
        print(f"❌ Erro ao verificar tabela: {e}")
        return False
    
    # Check which users exist
    cursor.execute("SELECT id FROM usuarios")
    existing_users = {r[0] for r in cursor.fetchall()}
    
    print(f"\n📊 Importando {len(historical_data)} posições históricas...")
    print(f"   Usuários existentes: {len(existing_users)}")
    
    imported = 0
    skipped = 0
    
    for temporada, usuario_id, posicao in historical_data:
        # Skip if user doesn't exist
        if usuario_id not in existing_users:
            skipped += 1
            continue
        
        try:
            # Check if record already exists
            cursor.execute(
                "SELECT id FROM posicoes_participantes WHERE usuario_id = ? AND temporada = ?",
                (usuario_id, str(temporada))
            )
            if cursor.fetchone():
                skipped += 1
                continue
            
            # Insert new record
            cursor.execute(
                """INSERT INTO posicoes_participantes 
                   (usuario_id, posicao, temporada, data_atualizacao) 
                   VALUES (?, ?, ?, ?)""",
                (usuario_id, posicao, str(temporada), datetime.now().isoformat())
            )
            imported += 1
        except Exception as e:
            print(f"  ⚠️  Erro ao inserir usuario_id={usuario_id}, temporada={temporada}: {e}")
            skipped += 1
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Importação concluída:")
    print(f"   • Importados: {imported} registros")
    print(f"   • Ignorados: {skipped} registros")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Importar resultados históricos (20 anos) para Hall da Fama"
    )
    parser.add_argument(
        "--db",
        default="/Users/sansquer/Documents/GitHub/BF1Dev/3.0/bolao_f1.db",
        help="Caminho para o banco de dados SQLite (padrão: bolao_f1.db)"
    )
    parser.add_argument(
        "--data-file",
        help="Arquivo CSV com dados históricos (opcional)"
    )
    
    args = parser.parse_args()
    
    success = import_historical_results(args.db, args.data_file)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
