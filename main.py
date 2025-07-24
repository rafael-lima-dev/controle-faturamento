import streamlit as st
import json
import os
from datetime import datetime, timedelta
import pandas as pd
import sqlite3
import hashlib
from pathlib import Path
import yagmail
from dotenv import load_dotenv
import secrets
import time
from database import init_db, verificar_usuario, criar_usuario, salvar_faturamento, get_faturamentos, DATABASE_URL, get_db_connection

# Inicializar o banco de dados
init_db()

# Configuração da página
st.set_page_config(
    page_title="Sistema de Faturamento",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS personalizado
st.markdown("""
    <style>
    .main {
        padding: 1rem;
    }
    .main-header, .title {
        color: #fff !important;
        text-shadow: 2px 2px 8px #222, 0 1px 0 #fff;
        font-weight: bold;
    }
    .sub-header, .subtitle {
        color: #e0e0e0 !important;
    }
    .success-message {
        color: #2E7D32;
        font-weight: bold;
        text-align: center;
        padding: 1rem;
        background-color: #E8F5E9;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .error-message {
        color: #C62828;
        font-weight: bold;
        text-align: center;
        padding: 1rem;
        background-color: #FFEBEE;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .info-message {
        color: #1565C0;
        font-weight: bold;
        text-align: center;
        padding: 1rem;
        background-color: #E3F2FD;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .stButton>button {
        background-color: #1E88E5;
        color: white;
        font-weight: bold;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        transition: all 0.3s ease;
        width: 100%;
        font-size: 1.1rem;
    }
    .stButton>button:hover {
        background-color: #1565C0;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .stTextInput>div>div>input {
        border: 2px solid #1E88E5;
        border-radius: 5px;
        padding: 0.5rem;
    }
    .stTextInput>div>div>input:focus {
        border-color: #1565C0;
        box-shadow: 0 0 0 2px rgba(30,136,229,0.2);
    }
    .css-1d391kg {
        padding: 1rem;
    }
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 1rem;
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .title {
        text-align: center;
        color: #2c3e50;
        margin-bottom: 1rem;
        font-size: 1.5rem;
    }
    .subtitle {
        text-align: center;
        color: #7f8c8d;
        margin-bottom: 1rem;
        font-size: 1rem;
    }
    .form-container {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .form-container .stTextInput>div>div>input {
        border: 2px solid #1E88E5;
        border-radius: 5px;
        padding: 0.8rem;
        font-size: 1rem;
    }
    .form-container .stTextInput>div>div>input:focus {
        border-color: #1565C0;
        box-shadow: 0 0 0 2px rgba(30,136,229,0.2);
    }
    .link-container {
        text-align: center;
        margin-top: 1rem;
    }
    .link-container a {
        color: #4CAF50;
        text-decoration: none;
        font-weight: 500;
    }
    .link-container a:hover {
        text-decoration: underline;
    }
    /* Estilos para o menu mobile */
    .menu-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background-color: white;
        padding: 0.5rem;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
        z-index: 1000;
    }
    .menu-item {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0.5rem;
        color: #2c3e50;
        text-decoration: none;
        border-radius: 8px;
        margin: 0.25rem;
        transition: all 0.3s ease;
    }
    .menu-item:hover {
        background-color: #f8f9fa;
    }
    .menu-item.active {
        background-color: #4CAF50;
        color: white;
    }
    .menu-icon {
        font-size: 1.5rem;
        margin-right: 0.5rem;
    }
    /* Ajustes para o conteúdo principal */
    .main-content {
        padding-bottom: 4rem;
    }
    /* Ajustes para o sidebar em mobile */
    @media (max-width: 768px) {
        .css-1d391kg {
            display: none;
        }
    }
    /* Header fixo no topo direito */
    .user-header {
        position: fixed;
        top: 1rem;
        right: 2rem;
        background: #222831;
        color: #fff;
        padding: 0.5rem 1.5rem;
        border-radius: 20px;
        font-weight: 600;
        z-index: 2000;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    /* Ocultar menu dos 3 pontinhos do Streamlit */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Footer personalizado */
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background-color: #1E88E5;
        color: white;
        text-align: center;
        padding: 0.8rem;
        font-size: 1rem;
        z-index: 9999;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
    }
    .footer a {
        color: white;
        text-decoration: none;
        font-weight: bold;
        margin: 0 5px;
    }
    .footer a:hover {
        text-decoration: underline;
    }
    </style>
    """, unsafe_allow_html=True)

# Configuração do banco de dados
DB_PATH = "faturamento.db"

load_dotenv()
EMAIL_REMETENTE = os.getenv('EMAIL_REMETENTE')
EMAIL_SENHA_APP = os.getenv('EMAIL_SENHA_APP')

def adapt_date(val):
    return val.isoformat()

def convert_date(val):
    return datetime.fromisoformat(val.decode())

def listar_usuarios():
    conn = get_db_connection()
    c = conn.cursor()
    try:
        if DATABASE_URL:
            c.execute('SELECT id, email, nome FROM usuarios')
        else:
            c.execute('SELECT id, email, nome FROM usuarios')
        return c.fetchall()
    except Exception as e:
        print(f"Erro em listar_usuarios: {e}") # Debug
        return []
    finally:
        conn.close()

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def normalizar_email(email):
    return email.strip().lower()

def verificar_login(email, senha):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        email = normalizar_email(email)
        senha_hash = hash_senha(senha)
        if DATABASE_URL:
            c.execute('SELECT id, nome, senha FROM usuarios WHERE LOWER(email) = %s', (email,))
        else:
            c.execute('SELECT id, nome, senha FROM usuarios WHERE LOWER(email) = ?', (email,))
        result = c.fetchone()
        if result:
            user_id = result[0]
            user_nome = result[1]
            senha_hash_db = result[2]
            
            if senha_hash_db == senha_hash:
                return {
                    'id': user_id,
                    'nome': user_nome,
                    'email': email
                }
            else:
                return None
        else:
            return None
    except Exception as e:
        print(f"Erro em verificar_login: {e}")
        return None
    finally:
        conn.close()

# Função para formatar valores monetários
def formatar_valor(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def salvar_faturamento(usuario_id, data, valor, descricao):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        if DATABASE_URL:
            # PostgreSQL
            c.execute('INSERT INTO faturamentos (usuario_id, data, valor, descricao) VALUES (%s, %s, %s, %s)',
                     (usuario_id, data, valor, descricao))
        else:
            # SQLite
            print(f"Salvando faturamento: usuario_id={usuario_id}, data={data}, valor={valor}, descricao={descricao}")
            c.execute('INSERT INTO faturamentos (usuario_id, data, valor, descricao) VALUES (?, ?, ?, ?)',
                     (usuario_id, data, valor, descricao))
        conn.commit()
        
        # Verificar se foi salvo
        c.execute('SELECT * FROM faturamentos WHERE usuario_id = ? ORDER BY id DESC LIMIT 1', (usuario_id,))
        ultimo = c.fetchone()
        print(f"Último faturamento salvo: {ultimo}")
    finally:
        conn.close()

def obter_faturamentos_mes(usuario_id, ano, mes):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        if DATABASE_URL:
            # PostgreSQL
            c.execute('''
                SELECT EXTRACT(DAY FROM data)::text as dia, valor, descricao 
                FROM faturamentos 
                WHERE usuario_id = %s 
                AND EXTRACT(YEAR FROM data) = %s 
                AND EXTRACT(MONTH FROM data) = %s
                ORDER BY data
            ''', (usuario_id, ano, mes))
        else:
            # SQLite
            # Garantir que ano e mes sejam strings e formatados corretamente para comparação
            ano_str = str(ano)
            mes_str = str(mes).zfill(2) # Mês formatado com zero à esquerda (ex: '05')
            print(f"[DEBUG - obter_faturamentos_mes] SQLite Query - usuario_id: {usuario_id}, Ano: {ano_str}, Mes: {mes_str}") # Debug
            c.execute('''
                SELECT strftime('%d', data) as dia, valor, descricao 
                FROM faturamentos 
                WHERE usuario_id = ? 
                AND strftime('%Y', data) = ? 
                AND strftime('%m', data) = ?
                ORDER BY data
            ''', (usuario_id, ano_str, mes_str))
        result = c.fetchall()
        print(f"[DEBUG - obter_faturamentos_mes] Resultado da consulta: {result}") # Debug
        # Retornar lista de dicionários com dia, valor e descricao
        faturamentos_dia = [{'dia': str(r[0]), 'valor': r[1], 'descricao': r[2]} for r in result]
        print(f"[DEBUG - obter_faturamentos_mes] Lista de dicionários formatada: {faturamentos_dia}") # Debug
        return faturamentos_dia
    finally:
        conn.close()

def obter_faturamentos_ano(usuario_id, ano):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        if DATABASE_URL:
            # PostgreSQL
            c.execute('''
                SELECT EXTRACT(MONTH FROM data)::text as mes, SUM(valor) as total
                FROM faturamentos 
                WHERE usuario_id = %s 
                AND EXTRACT(YEAR FROM data) = %s
                GROUP BY EXTRACT(MONTH FROM data)
                ORDER BY mes
            ''', (usuario_id, ano))
        else:
            # SQLite
            # Garantir que ano seja string formatado corretamente para comparação
            ano_str = str(ano)
            print(f"[DEBUG - obter_faturamentos_ano] SQLite Query - usuario_id: {usuario_id}, Ano: {ano_str}") # Debug
            c.execute('''
                SELECT strftime('%m', data) as mes, SUM(valor) as total
                FROM faturamentos 
                WHERE usuario_id = ? 
                AND strftime('%Y', data) = ?
                GROUP BY strftime('%m', data)
                ORDER BY mes
            ''', (usuario_id, ano_str))
        result = c.fetchall()
        print(f"[DEBUG - obter_faturamentos_ano] Resultado da consulta: {result}") # Debug
        # Retornar lista de dicionários com mes e total
        faturamentos_ano = [{'mes': str(r[0]), 'total': r[1]} for r in result]
        print(f"[DEBUG - obter_faturamentos_ano] Lista de dicionários formatada: {faturamentos_ano}") # Debug
        return faturamentos_ano
    finally:
        conn.close()

# Funções de registro (migradas do 1_Registro.py)
def verificar_email_existe(email):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        email = normalizar_email(email)
        c.execute('SELECT id FROM usuarios WHERE LOWER(email) = ?', (email,))
        return c.fetchone() is not None
    except Exception as e:
        print(f"Erro em verificar_email_existe: {e}") # Debug
        return False
    finally:
        conn.close()

def registrar_usuario(email, senha, nome):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        email = normalizar_email(email)
        if verificar_email_existe(email):
            return False, "Este email já está cadastrado!"
        senha_hash = hash_senha(senha)
        c.execute('INSERT INTO usuarios (email, senha, nome) VALUES (?, ?, ?)',
                 (email, senha_hash, nome))
        conn.commit()
        return True, "Usuário registrado com sucesso!"
    except Exception as e:
        conn.rollback()
        print(f"Erro em registrar_usuario: {e}") # Debug
        return False, f"Erro ao registrar usuário: {str(e)}"
    finally:
        conn.close()

def listar_emails_cadastrados():
    conn = get_db_connection()
    c = conn.cursor()
    try:
        if DATABASE_URL:
            c.execute('SELECT email FROM usuarios')
        else:
            c.execute('SELECT email FROM usuarios')
        emails = c.fetchall()
        return [normalizar_email(e[0]) for e in emails]
    except Exception as e:
        print(f"Erro em listar_emails_cadastrados: {e}") # Debug
        return []
    finally:
        conn.close()

def excluir_faturamento(faturamento_id):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        if DATABASE_URL:
             c.execute('DELETE FROM faturamentos WHERE id = %s', (faturamento_id,))
        else:
            c.execute('DELETE FROM faturamentos WHERE id = ?', (faturamento_id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        st.error(f"Erro ao excluir faturamento: {str(e)}")
        print(f"Erro em excluir_faturamento: {e}") # Debug
        return False
    finally:
        conn.close()

def obter_faturamentos_usuario(usuario_id):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        if DATABASE_URL:
            # PostgreSQL
            c.execute('''
                SELECT id, data, valor, descricao 
                FROM faturamentos 
                WHERE usuario_id = %s 
                ORDER BY data DESC
            ''', (usuario_id,))
        else:
            # SQLite
            c.execute('''
                SELECT id, data, valor, descricao 
                FROM faturamentos 
                WHERE usuario_id = ? 
                ORDER BY data DESC
            ''', (usuario_id,))
        result = c.fetchall()
        return result
    finally:
        conn.close()

def verificar_login_persistente():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute('SELECT id, nome FROM usuarios WHERE id = ?', (st.session_state.get('user_id'),))
        result = c.fetchone()
        if result:
            st.session_state.user_id = result[0]
            st.session_state.user_nome = result[1]
            return True
        return False
    finally:
        conn.close()

# Função para verificar e corrigir emails no banco
def corrigir_emails_banco():
    conn = get_db_connection()
    c = conn.cursor()
    try:
        # Buscar todos os emails
        c.execute('SELECT id, email FROM usuarios')
        usuarios = c.fetchall()
        
        # Atualizar cada email para minúsculo
        for usuario_id, email in usuarios:
            email_normalizado = normalizar_email(email)
            if email != email_normalizado:
                c.execute('UPDATE usuarios SET email = ? WHERE id = ?', 
                         (email_normalizado, usuario_id))
        
        conn.commit()
    finally:
        conn.close()

# Função principal
def main():
    # Footer (profissional, com nome, GitHub, LinkedIn, e-mail e direitos reservados)
    st.markdown("""
        <div style='position: fixed; bottom: 0; left: 0; right: 0; background: #1E88E5; color: #fff; text-align: center; padding: 1rem 0; font-size: 1rem; z-index: 9999; box-shadow: 0 -2px 10px rgba(0,0,0,0.1);'>
            <p style='margin:0;'>Desenvolvido por <strong>Francisco Rafael</strong></p>
            <p style='margin:0;'>
                <a href='https://github.com/rafael-lima-dev' target='_blank' style='color:#fff;font-weight:bold;text-decoration:underline;'>Meu GitHub</a> |
                <a href='https://linkedin.com/in/rafael-lima-dev' target='_blank' style='color:#fff;font-weight:bold;text-decoration:underline;'>Meu LinkedIn</a> |
                <a href='mailto:seu-email@gmail.com' style='color:#fff;font-weight:bold;text-decoration:underline;'>Contato</a>
            </p>
            <p style='margin:0;font-size:0.95em;'>© 2025 - Todos os direitos reservados</p>
        </div>
    """, unsafe_allow_html=True)

    # Corrigir emails no banco (Temporariamente removido para debug)
    # corrigir_emails_banco()
    
    # Checar se há token de redefinição na URL
    query_params = st.query_params
    reset_token = query_params.get('reset_token', [None])[0]
    if reset_token:
        with st.container():
            st.markdown('<div class="register-container">', unsafe_allow_html=True)
            st.markdown('<h2 class="title">🔄 Redefinir Senha</h2>', unsafe_allow_html=True)
            # Validar token
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('SELECT user_id, expires_at, used FROM recovery_tokens WHERE token = ?', (reset_token,))
            token_row = c.fetchone()
            if not token_row:
                st.error("Token inválido!")
                st.markdown('</div>', unsafe_allow_html=True)
                return
            user_id, expires_at, used = token_row
            if used:
                st.error("Este link de redefinição já foi utilizado.")
                st.markdown('</div>', unsafe_allow_html=True)
                return
            if datetime.fromisoformat(expires_at) < datetime.now():
                st.error("Este link de redefinição expirou.")
                st.markdown('</div>', unsafe_allow_html=True)
                return
            # Formulário de nova senha
            with st.form("reset_form"):
                st.markdown('<div class="form-container">', unsafe_allow_html=True)
                nova_senha = st.text_input("🔑 Nova Senha", type="password")
                confirmar_senha = st.text_input("🔒 Confirmar Nova Senha", type="password")
                submit = st.form_submit_button("Redefinir Senha")
                st.markdown('</div>', unsafe_allow_html=True)
                if submit:
                    if nova_senha and confirmar_senha:
                        if nova_senha == confirmar_senha:
                            if len(nova_senha) < 6:
                                st.error("A senha deve ter pelo menos 6 caracteres!")
                            else:
                                # Atualiza senha do usuário
                                senha_hash = hash_senha(nova_senha)
                                c.execute('UPDATE usuarios SET senha = ? WHERE id = ?', (senha_hash, user_id))
                                # Marca token como usado
                                c.execute('UPDATE recovery_tokens SET used = 1 WHERE token = ?', (reset_token,))
                                conn.commit()
                                st.success("Senha redefinida com sucesso! Você já pode fazer login.")
                                st.markdown('<div class="link-container">', unsafe_allow_html=True)
                                st.markdown('Clique <a href="/" target="_self">aqui</a> para fazer login.', unsafe_allow_html=True)
                                st.markdown('</div>', unsafe_allow_html=True)
                                st.markdown('</div>', unsafe_allow_html=True)
                                conn.close()
                                return
                        else:
                            st.error("As senhas não coincidem!")
                    else:
                        st.warning("Por favor, preencha todos os campos!")
            st.markdown('</div>', unsafe_allow_html=True)
            conn.close()
        return

    # Saudação no topo direito
    if st.session_state.get('user_nome'):
        st.markdown(f'<div class="user-header">👋 Olá, {st.session_state.user_nome}!</div>', unsafe_allow_html=True)

    # Container principal
    with st.container():
        st.markdown('<h1 class="title">💰 Sistema de Faturamento</h1>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle">Gerencie seus faturamentos de forma simples e eficiente</p>', unsafe_allow_html=True)

    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'user_nome' not in st.session_state:
        st.session_state.user_nome = None

    if st.session_state.user_id is None:
        if 'show_register' not in st.session_state:
            st.session_state.show_register = False
        if 'show_forgot' not in st.session_state:
            st.session_state.show_forgot = False
        if not st.session_state.show_register and not st.session_state.show_forgot:
            # Container de login
            with st.container():
                st.markdown('<div class="login-container">', unsafe_allow_html=True)
                st.markdown('<h2 class="title">🔐 Login</h2>', unsafe_allow_html=True)
                with st.form("login_form"):
                    st.markdown('<div class="form-container">', unsafe_allow_html=True)
                    email = st.text_input("📧 Email")
                    senha = st.text_input("🔑 Senha", type="password")
                    col1, col2, col3 = st.columns([1,2,1])
                    with col2:
                        submit = st.form_submit_button("Entrar", use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    if submit:
                        usuario = verificar_login(email, senha)
                        if usuario:
                            st.session_state.logged_in = True
                            st.session_state.user_id = usuario['id']
                            st.session_state.user_email = usuario['email']
                            st.session_state.user_name = usuario['nome']
                            st.rerun()
                        else:
                            st.error("Email ou senha incorretos!")
                st.markdown('<div class="link-container">', unsafe_allow_html=True)
                if st.button("Não tem uma conta? Clique aqui para se registrar"):
                    st.session_state.show_register = True
                    st.rerun()
                if st.button("Esqueci minha senha"):
                    st.session_state.show_forgot = True
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            return
        elif st.session_state.show_forgot:
            with st.container():
                st.markdown('<div class="register-container">', unsafe_allow_html=True)
                st.markdown('<h2 class="title">🔑 Recuperar Senha</h2>', unsafe_allow_html=True)
                with st.form("forgot_form"):
                    st.markdown('<div class="form-container">', unsafe_allow_html=True)
                    email = st.text_input("📧 Informe seu e-mail cadastrado")
                    submit = st.form_submit_button("Enviar link de recuperação")
                    st.markdown('</div>', unsafe_allow_html=True)
                    if submit:
                        if email:
                            # Verifica se o e-mail está cadastrado
                            conn = sqlite3.connect(DB_PATH)
                            c = conn.cursor()
                            c.execute('SELECT id FROM usuarios WHERE email = ?', (email,))
                            user = c.fetchone()
                            if user:
                                user_id = user[0]
                                # Gera token único
                                token = secrets.token_urlsafe(32)
                                expires_at = (datetime.now() + timedelta(hours=1)).isoformat()
                                # Salva token no banco
                                c.execute('INSERT INTO recovery_tokens (user_id, token, expires_at) VALUES (?, ?, ?)',
                                          (user_id, token, expires_at))
                                conn.commit()
                                # Monta link de recuperação
                                base_url = os.getenv("BASE_URL", "http://localhost:8501")
                                recovery_link = f"{base_url}?reset_token={token}"
                                # Envia e-mail
                                try:
                                    yag = yagmail.SMTP(EMAIL_REMETENTE, EMAIL_SENHA_APP)
                                    yag.send(
                                        to=email,
                                        subject="Recuperação de Senha - Sistema de Faturamento",
                                        contents=f"Olá!\n\nClique no link abaixo para redefinir sua senha. O link é válido por 1 hora.\n\n{recovery_link}\n\nSe não solicitou, ignore este e-mail."
                                    )
                                    st.success("E-mail de recuperação enviado! Verifique sua caixa de entrada e spam.")
                                except Exception as e:
                                    st.error(f"Erro ao enviar e-mail: {str(e)}")
                            else:
                                st.info("Se o e-mail estiver cadastrado, você receberá um link para redefinir sua senha.")
                            conn.close()
                            st.session_state.show_forgot = False
                            st.rerun()
                        else:
                            st.warning("Por favor, informe seu e-mail!")
                st.markdown('<div class="link-container">', unsafe_allow_html=True)
                if st.button("Voltar para login"):
                    st.session_state.show_forgot = False
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            return
        else:
            # Container de registro
            with st.container():
                st.markdown('<div class="register-container">', unsafe_allow_html=True)
                st.markdown('<h2 class="title">📝 Registro</h2>', unsafe_allow_html=True)
                with st.form("registro_form"):
                    st.markdown('<div class="form-container">', unsafe_allow_html=True)
                    nome = st.text_input("👤 Nome")
                    email = st.text_input("📧 Email")
                    senha = st.text_input("🔑 Senha", type="password")
                    confirmar_senha = st.text_input("🔒 Confirmar Senha", type="password")
                    submit = st.form_submit_button("Registrar")
                    st.markdown('</div>', unsafe_allow_html=True)
                    if submit:
                        if nome and email and senha and confirmar_senha:
                            if senha == confirmar_senha:
                                if len(senha) < 6:
                                    st.error("A senha deve ter pelo menos 6 caracteres!")
                                else:
                                    sucesso, mensagem = registrar_usuario(email, senha, nome)
                                    if sucesso:
                                        st.success(mensagem)
                                        st.session_state.show_register = False
                                        st.rerun()
                                    else:
                                        st.error(mensagem)
                            else:
                                st.error("As senhas não coincidem!")
                        else:
                            st.warning("Por favor, preencha todos os campos!")
                st.markdown('<div class="link-container">', unsafe_allow_html=True)
                if st.button("Já tem uma conta? Clique aqui para fazer login"):
                    st.session_state.show_register = False
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            return

    # Sidebar com selectbox (igual à imagem 2)
    with st.sidebar:
        st.markdown("### 📊 Menu")
        menu_opcao = st.selectbox(
            "Selecione uma opção:",
            ["Inserir Faturamento", "Ver Lucro do Mês", "Ver Lucro do Ano", "Gerenciar Faturamentos"]
        )
        if st.button("🚪 Sair"):
            st.session_state.user_id = None
            st.session_state.user_nome = None
            st.rerun()

    # Conteúdo principal
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    if menu_opcao == "Inserir Faturamento":
        st.markdown("<h2 style='display:flex;align-items:center;gap:8px;'><span style='font-size:2rem;'>📝</span> Inserir Novo Faturamento</h2>", unsafe_allow_html=True)
        if 'valor_faturamento' not in st.session_state:
            st.session_state.valor_faturamento = 0.0
        if 'show_success_faturamento' not in st.session_state:
            st.session_state.show_success_faturamento = False
        with st.form("faturamento_form"):
            col1, col2 = st.columns(2)
            with col1:
                data = st.date_input("📅 Data", value=datetime.now())
            with col2:
                valor = st.number_input("💵 Valor (R$)", min_value=0.0, step=0.01, key="valor_faturamento")
            descricao = st.text_area("📝 Descrição", placeholder="Ex: Troca de tela, Conector J8, etc.")
            submit = st.form_submit_button("💾 Salvar Faturamento")
            if submit:
                if valor > 0:
                    salvar_faturamento(st.session_state.user_id, data, valor, descricao)
                    st.session_state.show_success_faturamento = True
                    if 'valor_faturamento' in st.session_state:
                        del st.session_state['valor_faturamento']
                    st.rerun()
                else:
                    st.warning("Por favor, insira um valor válido!")
        # Exibir mensagem de sucesso e sumir após 2 segundos
        if st.session_state.get('show_success_faturamento', False):
            st.success("Faturamento registrado com sucesso!")
            # Usar st.empty para sumir a mensagem após 2 segundos
            msg_placeholder = st.empty()
            time.sleep(2)
            st.session_state.show_success_faturamento = False
            st.rerun()
    elif menu_opcao == "Ver Lucro do Mês":
        st.markdown("<h2 style='display:flex;align-items:center;gap:8px;'><span style='font-size:2rem;'>📅</span> Lucro do Mês</h2>", unsafe_allow_html=True)
        ano = st.selectbox("Ano", range(2020, datetime.now().year + 1), index=datetime.now().year - 2020)
        mes = st.selectbox("Mês", range(1, 13), index=datetime.now().month - 1)
        faturamentos_dia = obter_faturamentos_mes(st.session_state.user_id, ano, mes)
        if faturamentos_dia:
            # Usar nomes de colunas que correspondem às chaves no dicionário (minúsculo)
            df_dia = pd.DataFrame(faturamentos_dia)
            print(f"[DEBUG - Ver Lucro do Mês] DataFrame criado: {df_dia}") # Debug
            
            # Garantir que a coluna Dia seja string antes de converter para int
            # Usar o nome da coluna em minúsculo
            df_dia['dia'] = df_dia['dia'].astype(str).str.strip()
            # Remover linhas onde Dia não é um número válido
            # Usar o nome da coluna em minúsculo
            df_dia = df_dia[df_dia['dia'].str.isdigit()]
            
            # Agora podemos converter para int com segurança
            # Usar o nome da coluna em minúsculo
            df_dia['dia'] = df_dia['dia'].astype(int)
            # Ordenar pela coluna do dia em minúsculo
            df_dia = df_dia.sort_values('dia')
            
            # Verificar se ainda temos dados após a filtragem por dia válido
            if not df_dia.empty:
                # Calcular total do mês
                # Usar o nome da coluna em minúsculo
                total_mes = df_dia['valor'].sum()
                
                # Encontrar o melhor dia (só se houver dados)> 0, já verificado pela condição if not df_dia.empty
                # Usar o nome da coluna em minúsculo
                melhor_dia = df_dia.loc[df_dia['valor'].idxmax()]
                
                # Converter o dia para uma data completa e obter o nome da semana
                # Usar o nome da coluna em minúsculo
                data_completa = datetime(ano, mes, int(melhor_dia['dia']))
                nome_semana = data_completa.strftime('%A')  # Retorna o nome do dia da semana em inglês
                
                # Dicionário para traduzir os dias da semana
                dias_semana = {
                    'Monday': 'Segunda-feira',
                    'Tuesday': 'Terça-feira',
                    'Wednesday': 'Quarta-feira',
                    'Thursday': 'Quinta-feira',
                    'Friday': 'Sexta-feira',
                    'Saturday': 'Sábado',
                    'Sunday': 'Domingo'
                }
                
                # Mostrar resumo em cards
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                        <div style='background-color: #2c3e50; padding: 1.5rem; border-radius: 8px; margin: 1rem 0;'>
                            <h3 style='margin: 0; color: #ffffff;'>💰 Total do Mês</h3>
                            <p style='margin: 0.5rem 0; font-size: 1.5rem; color: #4CAF50; font-weight: bold;'>
                                {formatar_valor(total_mes)}
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                        <div style='background-color: #2c3e50; padding: 1.5rem; border-radius: 8px; margin: 1rem 0;'>
                            <h3 style='margin: 0; color: #ffffff;'>🏆 Melhor Dia</h3>
                            <p style='margin: 0.5rem 0; font-size: 1.5rem; color: #4CAF50; font-weight: bold;'>
                                {int(melhor_dia['dia'])} ({dias_semana[nome_semana]})
                            </p>
                            <p style='margin: 0.5rem 0; font-size: 1.5rem; color: #4CAF50; font-weight: bold;'>
                                {formatar_valor(melhor_dia['valor'])}
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
                
                # Mostrar tabela com todos os dias
                st.markdown("### 📊 Detalhamento por Dia")
                # Renomear colunas para exibição
                df_dia_display = df_dia.rename(columns={'dia': 'Dia', 'valor': 'Valor', 'descricao': 'Descrição'})
                df_dia_display['Valor'] = df_dia_display['Valor'].apply(formatar_valor)
                # Exibir Dia, Valor e Descrição (usando o DataFrame renomeado)
                st.dataframe(df_dia_display[['Dia', 'Valor', 'Descrição']], hide_index=True)
            else:
                st.info("Nenhum faturamento com dia válido registrado para o período selecionado após filtragem.")
        else:
            st.info("Nenhum faturamento registrado para o período selecionado.")
    elif menu_opcao == "Ver Lucro do Ano":
        st.markdown("<h2 style='display:flex;align-items:center;gap:8px;'><span style='font-size:2rem;'>📈</span> Lucro do Ano</h2>", unsafe_allow_html=True)
        ano = st.selectbox("Ano", range(2020, datetime.now().year + 1), index=datetime.now().year - 2020)
        faturamentos_ano = obter_faturamentos_ano(st.session_state.user_id, ano)
        if faturamentos_ano:
            # Usar nomes de colunas que correspondem às chaves no dicionário (minúsculo)
            df_ano = pd.DataFrame(faturamentos_ano)
            print(f"[DEBUG - Ver Lucro do Ano] DataFrame criado: {df_ano}") # Debug

            # Garantir que a coluna Mês seja string antes de converter
            # Usar o nome da coluna em minúsculo
            df_ano['mes'] = df_ano['mes'].astype(str).str.strip()
            # Remover linhas onde Mês não é um número válido
            # Usar o nome da coluna em minúsculo
            df_ano = df_ano[df_ano['mes'].str.isdigit()]
            
            if not df_ano.empty:
                # Converter mês para nome do mês
                # Usar o nome da coluna em minúsculo
                df_ano['mes'] = pd.to_datetime(df_ano['mes'], format='%m').dt.strftime('%B')
                # A ordenação alfabética do nome do mês pode não ser a ideal, mas pandas.dt.strftime('%B') retorna nomes em inglês por padrão
                # Para ordenar corretamente, precisaríamos de um mapeamento numérico ou uma coluna de ordenação
                # df_ano = df_ano.sort_values('Mês') # Desabilitado pois ordena por nome do mês em inglês

                # Calcular total do ano
                # Usar o nome da coluna em minúsculo
                total_ano = df_ano['total'].sum()
                
                # Verificar se há valores maiores que zero para encontrar o melhor mês
                # Usar o nome da coluna em minúsculo
                if (df_ano['total'] > 0).any():
                    # Encontrar o melhor mês
                    # Usar o nome da coluna em minúsculo
                    melhor_mes = df_ano.loc[df_ano['total'].idxmax()]
                    
                    # Mostrar resumo em cards
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"""
                            <div style='background-color: #2c3e50; padding: 1.5rem; border-radius: 8px; margin: 1rem 0;'>
                                <h3 style='margin: 0; color: #ffffff;'>💰 Total do Ano</h3>
                                <p style='margin: 0.5rem 0; font-size: 1.5rem; color: #4CAF50; font-weight: bold;'>
                                    {formatar_valor(total_ano)}
                                </p>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                            <div style='background-color: #2c3e50; padding: 1.5rem; border-radius: 8px; margin: 1rem 0;'>
                                <h3 style='margin: 0; color: #ffffff;'>🏆 Melhor Mês</h3>
                            <p style='margin: 0.5rem 0; font-size: 1.5rem; color: #4CAF50; font-weight: bold;'>
                                {melhor_mes['mes']}: {formatar_valor(melhor_mes['total'])}
                                </p>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    # Mostrar tabela com todos os meses
                    st.markdown("### 📊 Detalhamento por Mês")
                    # Renomear colunas para exibição
                    df_ano_display = df_ano.rename(columns={'mes': 'Mês', 'total': 'Total'})
                    df_ano_display['Total'] = df_ano_display['Total'].apply(formatar_valor)
                    st.dataframe(df_ano_display, hide_index=True)
                else:
                     st.info("Nenhum faturamento com valor maior que zero registrado para o ano selecionado.")
            else:
                st.info("Nenhum faturamento válido registrado para o ano selecionado.")
        else:
            st.info("Nenhum faturamento registrado para o ano selecionado.")
    elif menu_opcao == "Gerenciar Faturamentos":
        st.markdown("<h2 style='display:flex;align-items:center;gap:8px;'><span style='font-size:2rem;'>📋</span> Gerenciar Faturamentos</h2>", unsafe_allow_html=True)
        
        # Obter todos os faturamentos do usuário
        faturamentos = obter_faturamentos_usuario(st.session_state.user_id)
        
        if faturamentos:
            # Criar DataFrame com os faturamentos
            df = pd.DataFrame(faturamentos, columns=['ID', 'Data', 'Valor', 'Descrição'])
            df['Data'] = pd.to_datetime(df['Data']).dt.strftime('%d/%m/%Y')
            df['Valor'] = df['Valor'].apply(formatar_valor)
            
            # Mostrar tabela com botões de exclusão
            for _, row in df.iterrows():
                col1, col2, col3, col4, col5 = st.columns([2, 2, 3, 2, 1])
                with col1:
                    st.write(f"📅 {row['Data']}")
                with col2:
                    st.write(f"💰 {row['Valor']}")
                with col3:
                    st.write(f"📝 {row['Descrição']}")
                with col4:
                    if st.button("🗑️ Excluir", key=f"excluir_{row['ID']}"):
                        if excluir_faturamento(row['ID']):
                            st.success("Faturamento excluído com sucesso!")
                            st.rerun()
        else:
            st.info("Nenhum faturamento registrado.")
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()

