from __future__ import annotations

PIPELINE_NAME = "midas-access-etl"
PIPELINE_SLUG = "midas_access_etl"
SOURCE_NAME = "Midas Web"

MIDAS_LOGIN_URL = "https://sistema.midasweb.imb.br/midasmais/controle_login/controle_login.php"
MIDAS_ACCESS_FILTER_URL = "https://sistema.midasweb.imb.br/midasmais/_aplicacoes/php/acessos_imoveis_proprietarios/"
MIDAS_ACCESS_QUERY_URL = (
    "https://sistema.midasweb.imb.br/midasmais/_aplicacoes/php/acessos_imoveis_proprietarios/"
    "busca_acessos_ajax.php"
)

KNOWN_FUNCTIONALITIES: list[str] = [
    "Agenda Telefonica Recepção",
    "Atendimento a Cliente (novo)",
    "Cad. Imóveis - Troca Proprietário",
    "Cadastro de Clientes (novo)",
    "Cadastro de Imóveis (novo)",
    "Con. Atividades Realizadas",
    "Con. Clientes (Novo)",
    "Con. Detalhamento dos Leads Captados",
    "Con. Pipeline Venda",
    "Consulta de Opções",
    "Detalhamento do Cliente (novo)",
    "Detalhamento do Imóvel (novo)",
    "Emissão Proposta",
    "Imóveis que necessitam de Atualização Cadastral",
    "Mov. envio e-mail para Cliente",
    "Recepção Cliente",
]

DEFAULT_MIN_RECORDS = 1
DEFAULT_TIMEOUT_SECONDS = 900
DEFAULT_SOURCE = SOURCE_NAME
DEFAULT_ORIGEM_ACESSO = SOURCE_NAME
