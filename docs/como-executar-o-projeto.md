# Como executar todo o projeto

Este documento descreve como preparar e executar a plataforma localmente.

## Pré-requisitos

- Python 3.10+
- Docker e Docker Compose
- Acesso ao Supabase, caso deseje usar a camada real de persistência
- Navegador compatível com Playwright, se for executar automações web

## Estrutura de ambiente

O repositório já possui um ambiente virtual em `.venv`.

### 1. Ativar o ambiente virtual

No Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

No CMD:

```bat
.venv\Scripts\activate.bat
```

## Instalação das dependências

Se necessário, reinstale as dependências do projeto com:

```powershell
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

## Configuração de variáveis de ambiente

1. Copie `.env.example` para `.env`
2. Preencha os valores:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `SENTRY_DSN`
   - `APP_ENV`
   - `APP_NAME`
   - `LOG_LEVEL`

## Executar localmente

### Executar a automação inicial

```powershell
python -m orchestrator.flows.main
```

Esse comando:

- Carrega as configurações
- Inicializa logging estruturado
- Registra a automação de exemplo
- Executa o orquestrador central
- Persiste o histórico em memória na versão inicial

## Executar testes

```powershell
pytest
```

## Executar com Docker

### Build da imagem

```powershell
docker compose -f docker/docker-compose.yml build
```

### Subir o container da aplicação

```powershell
docker compose -f docker/docker-compose.yml up
```

## Execução com Prefect

A base já está preparada para flows do Prefect 3.

Quando o projeto evoluir para ambientes reais, o fluxo principal deverá ser executado pelo orquestrador do Prefect com:

- agendamento
- retries automáticos
- observabilidade de tarefas
- histórico centralizado de execuções

## Observações sobre a camada de dados

Hoje o projeto usa Supabase como camada operacional inicial.
A arquitetura foi desenhada para permitir migração futura para Databricks/Delta Lake sem alterar as regras de negócio do domínio.

## Resumo dos comandos principais

- `python -m orchestrator.flows.main`
- `pytest`
- `docker compose -f docker/docker-compose.yml build`
- `docker compose -f docker/docker-compose.yml up`
