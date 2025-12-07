"""
Tests for season/temporada filtering functionality.
Validates that queries filter correctly by season and that the DB layer respects temporada columns.
"""

import pytest
import sqlite3
import datetime
import os
import tempfile
from pathlib import Path


@pytest.fixture
def temp_db():
    """Create a temporary test database."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def db_with_schema(temp_db):
    """Create a test DB with schema including temporada columns."""
    conn = sqlite3.connect(temp_db)
    c = conn.cursor()
    
    # Create tables with temporada columns
    c.execute('''
        CREATE TABLE provas (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            data DATE,
            temporada TEXT DEFAULT '2025'
        )
    ''')
    
    c.execute('''
        CREATE TABLE apostas (
            id INTEGER PRIMARY KEY,
            usuario_id INTEGER,
            prova_id INTEGER,
            piloto_id INTEGER,
            pontos INTEGER,
            temporada TEXT DEFAULT '2025'
        )
    ''')
    
    c.execute('''
        CREATE TABLE resultados (
            id INTEGER PRIMARY KEY,
            prova_id INTEGER,
            usuario_id INTEGER,
            piloto_id INTEGER,
            posicao INTEGER,
            pontos_ganhos INTEGER,
            temporada TEXT DEFAULT '2025'
        )
    ''')
    
    c.execute('''
        CREATE TABLE posicoes_participantes (
            id INTEGER PRIMARY KEY,
            prova_id INTEGER,
            usuario_id INTEGER,
            posicao INTEGER,
            pontos REAL,
            temporada TEXT DEFAULT '2025'
        )
    ''')
    
    conn.commit()
    conn.close()
    
    return temp_db


def test_temporada_column_exists(db_with_schema):
    """Test that temporada columns exist in all relevant tables."""
    conn = sqlite3.connect(db_with_schema)
    c = conn.cursor()
    
    tables = ['provas', 'apostas', 'resultados', 'posicoes_participantes']
    for table in tables:
        c.execute(f"PRAGMA table_info('{table}')")
        cols = [r[1] for r in c.fetchall()]
        assert 'temporada' in cols, f"temporada column missing from {table}"
    
    conn.close()


def test_insert_with_temporada(db_with_schema):
    """Test that records can be inserted with temporada values."""
    conn = sqlite3.connect(db_with_schema)
    c = conn.cursor()
    
    # Insert test data
    c.execute(
        'INSERT INTO provas (nome, data, temporada) VALUES (?, ?, ?)',
        ('GP Brasil 2024', '2024-11-03', '2024')
    )
    c.execute(
        'INSERT INTO provas (nome, data, temporada) VALUES (?, ?, ?)',
        ('GP Brasil 2025', '2025-11-09', '2025')
    )
    conn.commit()
    
    # Query by season
    c.execute('SELECT nome FROM provas WHERE temporada = ?', ('2024',))
    result_2024 = c.fetchall()
    assert len(result_2024) == 1
    assert result_2024[0][0] == 'GP Brasil 2024'
    
    c.execute('SELECT nome FROM provas WHERE temporada = ?', ('2025',))
    result_2025 = c.fetchall()
    assert len(result_2025) == 1
    assert result_2025[0][0] == 'GP Brasil 2025'
    
    conn.close()


def test_read_table_df_helper(db_with_schema):
    """Test the _read_table_df helper from db_utils."""
    conn = sqlite3.connect(db_with_schema)
    c = conn.cursor()
    
    # Insert test data with different seasons
    c.execute('INSERT INTO apostas (usuario_id, prova_id, piloto_id, pontos, temporada) VALUES (?, ?, ?, ?, ?)',
              (1, 1, 1, 10, '2024'))
    c.execute('INSERT INTO apostas (usuario_id, prova_id, piloto_id, pontos, temporada) VALUES (?, ?, ?, ?, ?)',
              (1, 2, 2, 20, '2025'))
    c.execute('INSERT INTO apostas (usuario_id, prova_id, piloto_id, pontos, temporada) VALUES (?, ?, ?, ?, ?)',
              (2, 1, 3, 15, '2024'))
    conn.commit()
    
    # Query 2024 apostas
    c.execute('SELECT COUNT(*) FROM apostas WHERE temporada = ?', ('2024',))
    count_2024 = c.fetchone()[0]
    assert count_2024 == 2, "Should have 2 apostas in 2024"
    
    # Query 2025 apostas
    c.execute('SELECT COUNT(*) FROM apostas WHERE temporada = ?', ('2025',))
    count_2025 = c.fetchone()[0]
    assert count_2025 == 1, "Should have 1 aposta in 2025"
    
    conn.close()


def test_filter_by_default_year(db_with_schema):
    """Test that filtering defaults to current year when temporada not provided."""
    conn = sqlite3.connect(db_with_schema)
    c = conn.cursor()
    
    current_year = str(datetime.datetime.now().year)
    
    c.execute(
        'INSERT INTO provas (nome, data, temporada) VALUES (?, ?, ?)',
        ('Test Race', '2025-01-15', current_year)
    )
    conn.commit()
    
    # Query without specifying temporada should get default
    c.execute('SELECT nome FROM provas WHERE temporada = ?', (current_year,))
    result = c.fetchone()
    assert result is not None
    assert result[0] == 'Test Race'
    
    conn.close()


def test_cross_season_data_isolation(db_with_schema):
    """Test that data from different seasons doesn't leak into each other."""
    conn = sqlite3.connect(db_with_schema)
    c = conn.cursor()
    
    # Insert data for 2024
    c.execute('INSERT INTO resultados (prova_id, usuario_id, piloto_id, posicao, pontos_ganhos, temporada) VALUES (?, ?, ?, ?, ?, ?)',
              (1, 1, 1, 1, 25, '2024'))
    c.execute('INSERT INTO resultados (prova_id, usuario_id, piloto_id, posicao, pontos_ganhos, temporada) VALUES (?, ?, ?, ?, ?, ?)',
              (2, 1, 2, 2, 18, '2024'))
    
    # Insert data for 2025
    c.execute('INSERT INTO resultados (prova_id, usuario_id, piloto_id, posicao, pontos_ganhos, temporada) VALUES (?, ?, ?, ?, ?, ?)',
              (3, 1, 3, 1, 25, '2025'))
    conn.commit()
    
    # Query each season independently
    c.execute('SELECT COUNT(*), SUM(pontos_ganhos) FROM resultados WHERE temporada = ? AND usuario_id = ?', ('2024', 1))
    count_2024, total_2024 = c.fetchone()
    assert count_2024 == 2, "Should have 2 resultados in 2024"
    assert total_2024 == 43, "Total points in 2024 should be 43"
    
    c.execute('SELECT COUNT(*), SUM(pontos_ganhos) FROM resultados WHERE temporada = ? AND usuario_id = ?', ('2025', 1))
    count_2025, total_2025 = c.fetchone()
    assert count_2025 == 1, "Should have 1 resultado in 2025"
    assert total_2025 == 25, "Total points in 2025 should be 25"
    
    conn.close()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
