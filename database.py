import os
import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime
from urllib.parse import urlparse
import sqlite3

# Configuração do banco de dados
DATABASE_URL = os.getenv('DATABASE_URL')
DB_LOCAL_PATH = 'rfcell.db' # Caminho explícito para SQLite local

def get_db_connection():
    if DATABASE_URL:
        # Conexão PostgreSQL
        url = urlparse(DATABASE_URL)
        conn = psycopg2.connect(
            dbname=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        print("Conectado ao PostgreSQL") # Debug
        return conn
    else:
        # Conexão SQLite local (desenvolvimento)
        # --- INÍCIO: CÓDIGO TEMPORÁRIO PARA DEBUG LOCAL ---
        # Remove o arquivo do banco para garantir uma inicialização limpa (APENAS PARA DEBUG!)
        # if os.path.exists(DB_LOCAL_PATH):
        #     print(f"[DEBUG] Removendo banco SQLite local: {DB_LOCAL_PATH}")
        #     os.remove(DB_LOCAL_PATH)
        # --- FIM: CÓDIGO TEMPORÁRIO PARA DEBUG LOCAL ---

        conn = sqlite3.connect(DB_LOCAL_PATH)
        conn.row_factory = sqlite3.Row
        # Registrar adaptadores de data para SQLite
        sqlite3.register_adapter(datetime, adapt_date)
        sqlite3.register_converter("DATE", convert_date)
        print(f"Conectado ao SQLite local: {DB_LOCAL_PATH}") # Debug
        return conn

def adapt_date(val):
    return val.isoformat()

def convert_date(val):
    return datetime.fromisoformat(val.decode())

def init_db():
    print("--- Iniciando init_db ---")
    conn = get_db_connection()
    c = conn.cursor()
    
    if DATABASE_URL:
        print("Usando lógica de inicialização para PostgreSQL")
        # Criar tabelas para PostgreSQL
        c.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                nome TEXT,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("CREATE TABLE IF NOT EXISTS usuarios (PostgreSQL) executado")
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS faturamentos (
                id SERIAL PRIMARY KEY,
                usuario_id INTEGER NOT NULL,
                data DATE NOT NULL,
                valor REAL NOT NULL,
                descricao TEXT,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
        ''')
        print("CREATE TABLE IF NOT EXISTS faturamentos (PostgreSQL) executado")
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS recovery_tokens (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                token TEXT NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                used INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                FOREIGN KEY (user_id) REFERENCES usuarios (id)
            )
        ''')
        print("CREATE TABLE IF NOT EXISTS recovery_tokens (PostgreSQL) executado")
        
    else:
        print("Usando lógica de inicialização para SQLite")
        # Criar tabelas para SQLite
        c.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                nome TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("CREATE TABLE IF NOT EXISTS usuarios (SQLite) executado")
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS faturamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER,
                data DATE NOT NULL,
                valor REAL NOT NULL,
                descricao TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
        ''')
        print("CREATE TABLE IF NOT EXISTS faturamentos (SQLite) executado")
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS recovery_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                used INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES usuarios (id)
            )
        ''')
        print("CREATE TABLE IF NOT EXISTS recovery_tokens (SQLite) executado")
        
    conn.commit()
    print("Commit executado em init_db")
    conn.close()
    print("Conexão fechada em init_db")
    print("--- init_db finalizado ---")

def verificar_usuario(email):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT id, email, senha, nome, data_criacao FROM usuarios WHERE email = %s', (email,))
    usuario = c.fetchone()
    conn.close()
    return usuario  # Retorna a tupla diretamente

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

def salvar_faturamento(usuario_id, data, valor, descricao):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO faturamentos (usuario_id, data, valor, descricao) VALUES (%s, %s, %s, %s)',
             (usuario_id, data, valor, descricao))
    conn.commit()
    conn.close()

def get_faturamentos(usuario_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT id, usuario_id, data, valor, descricao, data_criacao FROM faturamentos WHERE usuario_id = %s ORDER BY data DESC',
             (usuario_id,))
    faturamentos = c.fetchall()
    conn.close()
    
    # Converter lista de tuplas para lista de dicionários
    return [{
        'id': f[0],
        'usuario_id': f[1],
        'data': f[2],
        'valor': f[3],
        'descricao': f[4],
        'data_criacao': f[5]
    } for f in faturamentos]

