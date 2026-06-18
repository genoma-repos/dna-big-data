# Fluxo do projeto

Este documento explica o fluxo completo da plataforma e como os módulos se conectam.

## Visão geral do fluxo

A plataforma segue uma arquitetura modular, orientada a domínio, com separação clara entre:

- orchestrator/
- automations/
- data/
- shared/
- tests/
- docker/
- docs/

O objetivo é permitir novas automações sem impacto nas automações existentes.

## Fluxo macro

1. O orquestrador central recebe a solicitação de execução.
2. A automação é localizada no registro.
3. O histórico de execução é iniciado.
4. A automação executa o pipeline ETL.
5. Os dados são extraídos, transformados e carregados.
6. O resultado final é persistido no histórico.
7. Notificações e monitoramento são acionados em caso de sucesso ou falha.

## Camadas do sistema

### 1. Shared

Contém os contratos, modelos e utilitários centrais da plataforma.

Principais elementos:

- `AutomationMetadata`
- `AutomationResult`
- `ExecutionRecord`
- `ExecutionStatus`
- contratos para automações, repositórios, notificações e storage
- abstração de pipeline ETL

Essa camada não depende de Supabase, Prefect, Playwright ou qualquer tecnologia externa.

### 2. Orchestrator

Coordena os casos de uso da plataforma.

Principais elementos:

- `AutomationRegistry`
- `Orchestrator`
- `RunAutomationUseCase`

Responsabilidades:

- registrar automações
- selecionar a automação a executar
- executar e controlar o ciclo de vida da automação
- registrar status e histórico
- disparar notificações

### 3. Automations

Implementa as automações independentes.

Exemplos:

- repositório em memória para desenvolvimento local
- repositório Supabase para persistência real
- camada de data lake abstrata
- adaptador para futura migração Delta Lake
- integração com Sentry
- runner de Playwright
- notificador console

### 4. Data

Concentra as zonas de dados do projeto.

Responsabilidades:

- agendar execuções
- acionar automações
- organizar tarefas paralelas ou sequenciais
- preparar a evolução para workers distribuídos

### 5. Execução central

Cada automação deve viver em um módulo isolado e ser registrada no orquestrador central.

Exemplo atual:

- `midas-access-etl`

Cada automação deve encapsular:

- extração de dados
- transformação
- carregamento
- regras específicas do domínio

## Fluxo ETL padronizado

O pipeline padrão segue esta ordem:

### Extract

- coleta dados de origem
- pode vir de APIs, banco, páginas web ou arquivos
- produz um contexto inicial do processamento

### Transform

- aplica regras de negócio
- normaliza dados
- converte estruturas
- valida registros

### Load

- grava os dados em Supabase na fase inicial
- futuramente poderá gravar em Delta Lake ou outro data lake corporativo

## Fluxo de execução de uma automação

### Exemplo da automação de referência

1. O `Orchestrator` busca a automação pelo nome.
2. Cria um `ExecutionRecord` com status `running`.
3. Executa o método `run()` da automação.
4. A automação monta um `ETLPipeline`.
5. O pipeline chama `extract`, `transform` e `load`.
6. O resultado é convertido em `AutomationResult`.
7. O orquestrador salva o resultado final.
8. O sistema envia notificação de conclusão.

## Tratamento de falhas

Se ocorrer erro:

1. o erro é capturado pelo orquestrador
2. a execução recebe status `failed`
3. o histórico é atualizado
4. a notificação de falha é enviada
5. o log estruturado registra o evento
6. o Sentry captura a exceção, se configurado

## Histórico de execuções

O histórico deve guardar, no mínimo:

- nome da automação
- status
- início
- fim
- tentativas de retry
- payload resumido
- mensagem de erro, quando existir

## Preparação para migração de Data Lake

A arquitetura foi desenhada para evitar acoplamento à tecnologia atual de armazenamento.

Para migrar de Supabase para Delta Lake no futuro, deve ser necessário trocar apenas o adaptador de infraestrutura, mantendo:

- entidades de domínio
- casos de uso
- regras das automações
- contrato do pipeline

## Evolução esperada

Nas próximas fases, o projeto pode incluir:

- catálogo de automações com versionamento
- persistência real do histórico no Supabase
- retries automáticos com políticas por automação
- métricas e dashboards
- filas e execução distribuída
- segregação por domínio ou por cliente
- integração com notificações por e-mail, Slack ou Teams

## Resumo do desenho arquitetural

- O domínio define as regras
- A aplicação coordena os casos de uso
- A infraestrutura conecta tecnologia externa
- O Prefect orquestra a execução
- As automações são plugáveis e independentes
- O storage é abstrato para suportar migração futura
