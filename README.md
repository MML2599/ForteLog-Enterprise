// ForteLog Enterprise v2 //

Sistema corporativo de gerenciamento de ativos críticos e trilha de auditoria de segurança em tempo real, projetado para operar 100% offline em redes restritas.

// Tecnologias Utilizadas //
- **Back-end**: Python, FastAPI, Uvicorn, SQLAlchemy (ORM)
- **Banco de Dados**: SQLite Relacional
- **Front-end**: HTML5, CSS3 nativo embutido, JavaScript Assíncrono (Fetch API & Polling)
- **Testes**: Script de automação HTTP com a biblioteca `requests`

// Funcionalidades Desenvolvidas //
- **Autenticação Segura**: Geração e validação de Tokens JWT (JSON Web Tokens).
- **Inventário de Ativos**: Cadastro de equipamentos com restrição de número de série único (`UNIQUE`) no banco de dados para evitar duplicidade.
- **Mudança de Status via PUT**: Atualização dinâmica e segura do estado operacional dos equipamentos direto na tabela.
- **Sincronização em Tempo Real (Polling)**: Mecanismo JavaScript que atualiza a interface a cada 5 segundos de forma silenciosa e exibe um indicador visual do estado da conexão (`Sincronizado`, `Atualizando`, `Erro Conexão`).
- **Trilha de Auditoria**: Registro imutável de logs de conformidade de segurança.
