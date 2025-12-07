#!/usr/bin/env python3
"""
Import users from a V2.0 SQLite DB into the current BF1Dev (3.0) DB.

Features:
- Backups the target DB before any changes
- Optionally adds a `temporada` column to core tables to enable plurianual usage
- Imports users, mapping common fields and preserving hashes when possible

Usage:
  python3 scripts/import_v2_users.py --v2-db /path/to/v2.db --target-db bolao_f1.db --season 2025

Notes:
- This is a safe, best-effort script. It will skip users with duplicate emails in the target DB.
- If V2 stores plain passwords (column `senha`), the script will re-hash them using bcrypt.
"""
import sqlite3
import argparse
import shutil
import os
import sys
import bcrypt
import datetime
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def backup_db(path: str) -> str:
    ts = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')
    dst = f"{path}.bak.{ts}"
    shutil.copy2(path, dst)
    logger.info(f"Backup created: {dst}")
    return dst


def add_temporada_columns(target_db: str, season: str, tables=None):
    if tables is None:
        tables = ['provas', 'apostas', 'resultados', 'posicoes_participantes']
    conn = sqlite3.connect(target_db)
    c = conn.cursor()
    for table in tables:
        try:
            # Add a TEXT temporada column with default season if it does not exist
            c.execute(f"ALTER TABLE {table} ADD COLUMN temporada TEXT DEFAULT '{season}'")
            logger.info(f"Added column `temporada` to table: {table}")
        except sqlite3.OperationalError as e:
            # Likely the column already exists or table doesn't exist — skip
            logger.debug(f"Skipping ALTER for {table}: {e}")
    conn.commit()
    conn.close()


def detect_columns(cursor, table_name: str):
    cursor.execute(f"PRAGMA table_info('{table_name}')")
    return [r[1] for r in cursor.fetchall()]


def import_users(v2_db: str, target_db: str, rehash_plain=True):
    src = sqlite3.connect(v2_db)
    src.row_factory = sqlite3.Row
    dst = sqlite3.connect(target_db)
    dst.row_factory = sqlite3.Row

    src_cur = src.cursor()
    dst_cur = dst.cursor()

    # Detect available columns in V2 users table
    try:
        src_cur.execute('SELECT * FROM usuarios LIMIT 1')
    except sqlite3.OperationalError as e:
        logger.error(f"Could not read usuarios table from V2 DB: {e}")
        return

    src_cols = detect_columns(src_cur, 'usuarios')
    logger.info(f"V2 usuarios columns: {src_cols}")

    rows = src_cur.execute('SELECT * FROM usuarios').fetchall()
    logger.info(f"Found {len(rows)} users in V2 DB")

    inserted = 0
    skipped = 0

    for r in rows:
        row = dict(r)
        email = row.get('email') or row.get('login')
        if not email:
            logger.warning('Skipping user with no email or login')
            skipped += 1
            continue

        # Check if user already exists
        dst_cur.execute('SELECT id FROM usuarios WHERE email = ?', (email,))
        if dst_cur.fetchone():
            logger.info(f"Skipping existing user: {email}")
            skipped += 1
            continue

        nome = row.get('nome') or row.get('username') or email.split('@')[0]

        # Determine password/hash handling
        senha_hash = None
        if 'senha_hash' in row and row.get('senha_hash'):
            senha_hash = row['senha_hash']
            logger.debug(f"Preserving senha_hash for {email}")
        elif 'senha' in row and row.get('senha'):
            # Plaintext password in V2 — re-hash
            if rehash_plain:
                salt = bcrypt.gensalt(rounds=int(os.environ.get('BCRYPT_ROUNDS', '12')))
                senha_hash = bcrypt.hashpw(row['senha'].encode('utf-8'), salt).decode('utf-8')
                logger.debug(f"Re-hashed plain senha for {email}")
            else:
                logger.warning(f"Plain password found for {email} but rehash disabled — skipping user")
                skipped += 1
                continue
        else:
            # No password info — create a random unusable password
            senha_hash = bcrypt.hashpw(os.urandom(16), bcrypt.gensalt()).decode('utf-8')
            logger.debug(f"Generated random senha for {email}")

        perfil = row.get('perfil') or row.get('role') or 'usuario'
        status = row.get('status') or 'Ativo'

        try:
            dst_cur.execute(
                'INSERT INTO usuarios (nome, email, senha_hash, perfil, status) VALUES (?,?,?,?,?)',
                (nome, email, senha_hash, perfil, status)
            )
            inserted += 1
        except sqlite3.IntegrityError as e:
            logger.warning(f"Integrity error inserting {email}: {e}")
            skipped += 1

    dst.commit()
    src.close()
    dst.close()

    logger.info(f"Import complete — inserted: {inserted}, skipped: {skipped}")


def main():
    parser = argparse.ArgumentParser(description='Import users from V2 DB into BF1Dev 3.0')
    parser.add_argument('--v2-db', required=True, help='Path to V2 SQLite DB')
    parser.add_argument('--target-db', default='bolao_f1.db', help='Target (3.0) SQLite DB path')
    parser.add_argument('--season', default=str(datetime.datetime.utcnow().year), help='Season/year to set when adding temporada columns')
    parser.add_argument('--add-temporada', action='store_true', help='Add temporada column to core tables (plurianual support)')
    parser.add_argument('--no-rehash-plain', dest='rehash_plain', action='store_false', help='If V2 has plaintext passwords, do NOT rehash (skip these users)')

    args = parser.parse_args()

    if not os.path.exists(args.v2_db):
        logger.error('V2 DB not found: %s' % args.v2_db)
        sys.exit(1)

    if not os.path.exists(args.target_db):
        logger.error('Target DB not found: %s' % args.target_db)
        sys.exit(1)

    # Backup target DB
    backup_db(args.target_db)

    # Optionally add temporada columns
    if args.add_temporada:
        add_temporada_columns(args.target_db, args.season)

    import_users(args.v2_db, args.target_db, rehash_plain=args.rehash_plain)


if __name__ == '__main__':
    main()
