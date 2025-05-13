import os
import psycopg2
from datetime import datetime
from urllib.parse import urlparse

# Configuração do banco de dados
DATABASE_URL = os.getenv('DATABASE_URL')

def get_db_connection():
    if DATABASE_URL:
        # Parse da URL do PostgreSQL
        url = urlparse(DATABASE_URL)
        conn = psycopg2.connect(
            dbname=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
    else:
        # Fallback para SQLite local (desenvolvimento)
        import sqlite3
        conn = sqlite3.connect('rfcell.db')
        conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Criar tabela de usuários
    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            nome TEXT,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Criar tabela de faturamentos
    c.execute('''
        CREATE TABLE IF NOT EXISTS faturamentos (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER NOT NULL,
            data DATE NOT NULL,
            valor REAL NOT NULL,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def verificar_usuario(email):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM usuarios WHERE email = %s', (email,))
    usuario = c.fetchone()
    conn.close()
    return usuario

def criar_usuario(email, senha, nome):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('INSERT INTO usuarios (email, senha, nome) VALUES (%s, %s, %s)',
                 (email, senha, nome))
        conn.commit()
        conn.close()
        return True
    except psycopg2.IntegrityError:
        return False

def salvar_faturamento(usuario_id, data, valor):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO faturamentos (usuario_id, data, valor) VALUES (%s, %s, %s)',
             (usuario_id, data, valor))
    conn.commit()
    conn.close()

def get_faturamentos(usuario_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM faturamentos WHERE usuario_id = %s ORDER BY data DESC',
             (usuario_id,))
    faturamentos = c.fetchall()
    conn.close()
    return faturamentos 