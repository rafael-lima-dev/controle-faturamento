import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

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
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        padding: 0.5rem 1rem;
        border: none;
        border-radius: 4px;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .css-1d391kg {
        padding: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

ARQUIVO_DADOS = "faturamento.json"

# Função para formatar valores monetários
def formatar_valor(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Função para carregar dados do arquivo
def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        with open(ARQUIVO_DADOS, "r") as f:
            return json.load(f)
    return {}

# Função para salvar dados
def salvar_dados(dados):
    with open(ARQUIVO_DADOS, "w") as f:
        json.dump(dados, f, indent=4)

# Função principal
def main():
    # Título com ícone
    st.markdown("# 💰 Sistema de Faturamento")
    st.markdown("---")

    dados = carregar_dados()

    # Sidebar com menu
    with st.sidebar:
        st.markdown("### 📊 Menu")
        st.markdown("---")
        menu = ["Inserir Faturamento", "Ver Lucro do Mês", "Ver Lucro do Ano"]
        escolha = st.selectbox("Selecione uma opção", menu)

    # Container principal
    with st.container():
        if escolha == "Inserir Faturamento":
            st.markdown("### 📝 Inserir Novo Faturamento")
            col1, col2 = st.columns(2)
            
            with col1:
                data = st.date_input("📅 Data", value=datetime.today())
            with col2:
                valor = st.number_input("💵 Valor (R$)", min_value=0.0, step=0.5)

            if st.button("💾 Salvar Faturamento"):
                ano = str(data.year)
                mes = str(data.month).zfill(2)
                dia = str(data.day).zfill(2)

                if ano not in dados:
                    dados[ano] = {}
                if mes not in dados[ano]:
                    dados[ano][mes] = {}

                dados[ano][mes][dia] = valor
                salvar_dados(dados)
                st.success(f"✅ Faturamento de {data.strftime('%d/%m/%Y')} salvo com sucesso!")

        elif escolha == "Ver Lucro do Mês":
            st.markdown("### 📈 Análise Mensal")
            if dados:
                col1, col2 = st.columns(2)
                with col1:
                    ano = st.selectbox("📅 Ano", sorted(dados.keys()))
                if ano:
                    with col2:
                        mes = st.selectbox("📅 Mês", sorted(dados[ano].keys()))
                    if mes:
                        dias = dados[ano][mes]
                        total = sum(dias.values())
                        
                        # Métricas
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Mensal", formatar_valor(total))
                        with col2:
                            st.metric("Média Diária", formatar_valor(total/len(dias)))
                        with col3:
                            st.metric("Dias Registrados", len(dias))

                        # Tabela
                        st.markdown("### 📊 Detalhamento Diário")
                        df = pd.DataFrame(list(dias.items()), columns=["Dia", "Faturamento (R$)"])
                        df["Dia"] = df["Dia"].astype(int)
                        df["Faturamento (R$)"] = df["Faturamento (R$)"].apply(formatar_valor)
                        df = df.sort_values("Dia")
                        st.dataframe(df, use_container_width=True)
            else:
                st.warning("⚠️ Nenhum dado registrado ainda.")

        elif escolha == "Ver Lucro do Ano":
            st.markdown("### 📊 Análise Anual")
            if dados:
                ano = st.selectbox("📅 Selecione o Ano", sorted(dados.keys()))
                if ano:
                    total = 0
                    meses_totais = {}
                    
                    for mes in dados[ano]:
                        mes_total = sum(dados[ano][mes].values())
                        meses_totais[mes] = mes_total
                        total += mes_total

                    # Métricas
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total Anual", formatar_valor(total))
                    with col2:
                        st.metric("Média Mensal", formatar_valor(total/len(meses_totais)))

                    # Tabela mensal
                    st.markdown("### 📈 Faturamento Mensal")
                    df_mensal = pd.DataFrame(list(meses_totais.items()), columns=["Mês", "Faturamento (R$)"])
                    df_mensal["Mês"] = df_mensal["Mês"].astype(int)
                    df_mensal["Faturamento (R$)"] = df_mensal["Faturamento (R$)"].apply(formatar_valor)
                    df_mensal = df_mensal.sort_values("Mês")
                    st.dataframe(df_mensal, use_container_width=True)
            else:
                st.warning("⚠️ Nenhum dado registrado ainda.")

if __name__ == "__main__":
    main()

