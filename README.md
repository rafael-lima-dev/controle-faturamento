# RFCell - Sistema de Gestão de Faturamento

Sistema de gestão de faturamento desenvolvido com Streamlit, PostgreSQL e Google Sheets.

## Configuração Local

1. Clone o repositório
2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente:
   - Crie um arquivo `.env` na raiz do projeto
   - Adicione as seguintes variáveis:
```
DB_HOST=seu-host
DB_PORT=5432
DB_NAME=seu-database
DB_USER=seu-usuario
DB_PASSWORD=sua-senha
```

4. Execute o aplicativo:
```bash
streamlit run main.py
```

## Deploy no Streamlit Cloud

1. Crie uma conta no [Streamlit Cloud](https://streamlit.io/cloud)
2. Conecte seu repositório GitHub
3. Configure as secrets no Streamlit Cloud:
   - Vá para Settings > Secrets
   - Adicione as credenciais do banco de dados e Google Sheets no formato TOML
   - Use o mesmo formato do arquivo `.streamlit/secrets.toml`

4. Deploy:
   - Selecione o branch principal
   - Clique em "Deploy"

## Estrutura do Projeto

- `main.py`: Arquivo principal do aplicativo
- `database.py`: Configuração e funções do banco de dados
- `google_sheets.py`: Integração com Google Sheets
- `requirements.txt`: Dependências do projeto
- `.streamlit/secrets.toml`: Configurações sensíveis (não versionado)
- `.env`: Variáveis de ambiente locais (não versionado)

## Funcionalidades

- Registro e login de usuários
- Registro de faturamentos diários
- Visualização de faturamentos por mês e ano
- Exportação de dados para Google Sheets
- Backup automático dos dados
