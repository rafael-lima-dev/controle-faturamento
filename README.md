# Sistema de Faturamento

Sistema web para controle e análise de faturamentos, desenvolvido com Streamlit.

## Funcionalidades

- 🔐 Login e Registro de usuários
- 📧 Recuperação de senha por e-mail
- 💰 Registro de faturamentos
- 📊 Análise de faturamento por mês e ano
- 🗑️ Gerenciamento de registros

## Configuração

1. Clone o repositório
2. Crie um arquivo `.env` baseado no `.env.example`
3. Configure suas credenciais de e-mail no arquivo `.env`
4. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
5. Execute o aplicativo:
   ```bash
   streamlit run main.py
   ```

## Variáveis de Ambiente

- `EMAIL_REMETENTE`: E-mail para envio de recuperação de senha
- `EMAIL_SENHA_APP`: Senha de aplicativo do Gmail
- `BASE_URL`: URL base do aplicativo (para links de recuperação)

## Tecnologias

- Python
- Streamlit
- SQLite
- Pandas
- Yagmail
