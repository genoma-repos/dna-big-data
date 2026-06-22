# Midas Access ETL

Automação responsável por extrair, tratar, validar e persistir os acessos de corretores a imóveis registrados no sistema Midas Web.

## Visão geral

```
Midas Web (AJAX)
    ↓ extract/
SessionAuthenticator  →  MidasWebClient  →  MidasAccessExtractor
    ↓
AccessQueryResult (rows brutas + RawPayload)
    ↓ transform/
HTMLCleaner → Normalizer → Fingerprint → Deduplicator → QualityReport
    ↓
list[AccessRecord]
    ↓ load/
MidasAccessLoader → SupabaseMidasAccessRepository (ou InMemory)
    ↓
Supabase: midas.access_records, midas.raw_payloads, monitoring.*
```

## Módulos

| Módulo | Responsabilidade |
|--------|-----------------|
| `extract/` | Autenticação de sessão, aplicação de filtros e consulta AJAX. Sessão é reutilizável entre chamadas (`is_authenticated`). |
| `transform/` | Limpeza de HTML, normalização de campos, cálculo de fingerprint, deduplicação e validação de qualidade. |
| `load/` | Upsert de registros curados, raw payloads, execuções, logs e alertas no Supabase. |
| `monitor/` | `ExecutionMonitor` persiste cada run em `monitoring.pipeline_executions`. Logs estruturados via `structlog`. |
| `analytics/` | Agregações e indicadores diários (desativado — reativar via tarefa `NEXT`). |
| `flow.py` | `MidasAccessPipelineRunner` — orquestra as etapas. Aceita `data_de`/`data_ate` para rodar em qualquer janela de tempo. Flow Prefect 3 exportado como `midas_access_etl_flow`. |
| `backfill.py` | `BackfillRunner` — itera dia a dia num intervalo, reutilizando a mesma sessão HTTP para todos os dias. |

## Execução direta

```bash
# Execução padrão (datas configuradas no .env)
python -m automations.midas_access_etl.automation

# Com parâmetros de data
python -c "
from automations.midas_access_etl.automation import MidasAccessETL
result = MidasAccessETL().run(data_de='01/06/2026', data_ate='30/06/2026')
print(result.status, result.rows_loaded)
"

# Backfill de um intervalo
python scripts/run_backfill.py 01/06/2026 22/06/2026
```

## Variáveis de ambiente

| Variável | Obrigatória | Descrição |
|----------|-------------|-----------|
| `MIDAS_USUARIO` | Sim (online) | Usuário de login no Midas Web |
| `MIDAS_SENHA` | Sim (online) | Senha de login |
| `SUPABASE_URL` | Sim (online) | URL do projeto Supabase |
| `SUPABASE_KEY` | Sim (online) | Service role key do Supabase |
| `MIDAS_OFFLINE_MODE` | Não | `true` para usar dados mock (dev/testes) |
| `MIDAS_DATA_DE` | Não | Data inicial padrão (`DD/MM/YYYY`) |
| `MIDAS_DATA_ATE` | Não | Data final padrão (`DD/MM/YYYY`) |
| `MIDAS_MINIMUM_RECORDS` | Não | Mínimo de registros esperados (padrão: `1`) |
| `MIDAS_TIMEOUT_SECONDS` | Não | Timeout HTTP em segundos (padrão: `900`) |

## Schemas Supabase

| Tabela | Descrição |
|--------|-----------|
| `midas.access_records` | Registros curados de acesso (upsert por fingerprint) |
| `midas.raw_payloads` | Payload bruto de cada extração |
| `midas.functionalities` | Dimensão de funcionalidades do sistema |
| `monitoring.pipeline_executions` | Histórico de execuções do pipeline |
| `monitoring.pipeline_logs` | Logs por etapa de cada execução |
| `monitoring.pipeline_alerts` | Alertas gerados durante as execuções |

## Sessão HTTP

`MidasWebClient.login()` é idempotente — se já houver um cookie `PHPSESSID` válido na sessão, o login não é repetido. Isso permite que o `BackfillRunner` faça um único login e reutilize a sessão para N dias de extração.

```python
extractor = MidasAccessExtractor(client=MidasWebClient(...))
extractor.login(usuario, senha)          # login único

for day in days:
    result = extractor.extract(filters)  # reusa a sessão
```
