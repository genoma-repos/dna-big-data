# Midas Access ETL

Automação responsável por extrair, tratar, validar, monitorar e armazenar acessos de corretores a imóveis no sistema Midas Web.

## Visão geral

- `extract`: autenticação, filtros e consulta AJAX
- `transform`: limpeza HTML, normalização, deduplicação e qualidade
- `load`: persistência em Supabase/PostgreSQL ou memória local para desenvolvimento
- `monitor`: logs estruturados, execução, alertas e métricas
- `analytics`: agregações para indicadores diários (DESATIVADO)
- `flow`: fluxo Prefect 3 de alto nível

## Execução

Configuração esperada via variáveis de ambiente:

- `MIDAS_USUARIO`
- `MIDAS_SENHA`
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `MIDAS_OFFLINE_MODE=true` para execução local sem acesso ao sistema

## Observabilidade

Persistência prevista em:

- `monitoring.pipeline_executions`
- `monitoring.pipeline_logs`
- `monitoring.pipeline_alerts`

## Segurança operacional

- Falhas de login e consulta geram alertas
- Funcionalidades novas são registradas na dimensão sem interromper o fluxo
- O pipeline mantém fallback local para desenvolvimento e testes
