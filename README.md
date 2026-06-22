# DNA Imóveis — Automation Platform

Plataforma modular de automação e processamento de dados em Python, orientada a domínio, com Prefect 3 como orquestrador e Supabase como camada de persistência.

## Automações ativas

| Automação | Domínio | Cron | Status |
|-----------|---------|------|--------|
| `midas-access-etl` | Acessos de corretores a imóveis (Midas Web) | Seg–Sex 06h (BRT) | Ativo |

## Estrutura do projeto

```
.
├── automations/
│   └── midas_access_etl/      # ETL Midas Web (extract → transform → load)
│       ├── extract/           # Autenticação, filtros e consulta AJAX
│       ├── transform/         # Limpeza HTML, normalização, deduplicação
│       ├── load/              # Persistência Supabase / InMemory
│       ├── monitor/           # Logs estruturados, execuções e alertas
│       ├── flow.py            # Flow Prefect 3
│       ├── automation.py      # Ponto de entrada da automação
│       └── backfill.py        # Runner de backfill por intervalo de datas
├── orchestrator/
│   ├── flows/                 # Orquestrador central e registro de automações
│   ├── schedules/             # Configuração de agendas e deployments Prefect
│   └── workers/               # Worker local
├── shared/
│   ├── config/                # Settings globais
│   ├── database/              # Adapters de storage (Delta Lake, Supabase)
│   ├── logging/               # Logger JSON
│   ├── notifications/         # Notificador (Console, extensível)
│   └── utils/                 # Contratos (Protocols) e modelos compartilhados
├── scripts/
│   ├── serve_prefect.py       # Inicia o runner Prefect com cron diário (blocking)
│   └── run_backfill.py        # Executa backfill para um intervalo de datas
├── tests/
├── prefect.yaml               # Deployment declarativo para `prefect deploy --all`
└── pyproject.toml
```

## Pré-requisitos

- Python 3.10+
- Conta Supabase (ou modo offline para desenvolvimento)
- Prefect 3 (`pip install prefect>=3.0.0`)

## Configuração

Copie `.env.example` para `.env` e preencha:

```dotenv
# Supabase
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=your-service-role-key

# Midas Web
MIDAS_USUARIO=seu_usuario
MIDAS_SENHA=sua_senha

# Desenvolvimento sem acesso ao sistema real
MIDAS_OFFLINE_MODE=true
```

## Execução

### ETL único (execução pontual)

```bash
python -m orchestrator.flows.main
```

### Backfill histórico

```bash
# 01/06/2026 até hoje (padrão)
python scripts/run_backfill.py

# Intervalo explícito
python scripts/run_backfill.py 01/06/2026 30/06/2026
```

### Cron diário com Prefect

**Modo serve** (processo único, recomendado para VPS):

```bash
python scripts/serve_prefect.py
```

**Modo deploy + worker** (Prefect Server ou Cloud):

```bash
prefect deploy --all
prefect worker start --pool default-agent-pool
```

## Testes

```bash
pytest
# ou somente os testes do Midas ETL:
pytest tests/test_midas_backfill.py tests/test_midas_run_params.py tests/test_midas_extractor_session.py tests/test_midas_access_transform.py -v
```

## Variáveis de ambiente relevantes

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `MIDAS_OFFLINE_MODE` | `true` | Desativa chamadas HTTP ao Midas (usa dados mock) |
| `MIDAS_DATA_DE` | `01/01/1970` | Data inicial padrão dos filtros |
| `MIDAS_DATA_ATE` | `31/12/2099` | Data final padrão dos filtros |
| `MIDAS_TIMEOUT_SECONDS` | `900` | Timeout da sessão HTTP |
| `APP_ENV` | `development` | Ambiente (`development` / `production`) |
| `LOG_LEVEL` | `INFO` | Nível de log |
