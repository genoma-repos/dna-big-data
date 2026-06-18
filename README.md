# Automation Platform

Plataforma modular de automação e processamento de dados em Python.

## Estrutura principal

- orchestrator/flows: orquestração central com Prefect
- orchestrator/schedules: definição de agendas
- orchestrator/workers: workers de execução
- automations/: automações independentes por domínio
- data/: zonas raw, processed e curated
- shared/: código compartilhado entre automações
- tests/: testes automatizados
- docker/: arquivos de containerização
- docs/: documentação do projeto

## Execução local

1. Copie `.env.example` para `.env`
2. Ative o ambiente Python
3. Execute:

```powershell
python -m orchestrator.flows.main
```

## Docker

```powershell
docker compose -f docker/docker-compose.yml up --build
```

## Testes

```powershell
pytest
```
