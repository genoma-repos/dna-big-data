from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def init_sentry(
    dsn: str,
    environment: str = "development",
    release: str | None = None,
    traces_sample_rate: float = 0.2,
) -> bool:
    """Inicializa o Sentry SDK. Retorna True se inicializado, False se DSN ausente.

    Só inicializa em ambientes não-development quando traces_sample_rate > 0,
    para não poluir o Sentry com runs locais.
    """
    if not dsn:
        logger.debug("SENTRY_DSN não configurado — Sentry desabilitado")
        return False

    try:
        import sentry_sdk
        from sentry_sdk.integrations.logging import LoggingIntegration
    except ImportError:  # pragma: no cover
        logger.warning("sentry-sdk não instalado — Sentry desabilitado")
        return False

    sentry_logging = LoggingIntegration(
        level=logging.WARNING,      # captura WARNING e acima como breadcrumbs
        event_level=logging.ERROR,  # envia ERROR e acima como eventos
    )

    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        release=release,
        traces_sample_rate=traces_sample_rate if environment != "development" else 0.0,
        integrations=[sentry_logging],
        send_default_pii=False,
    )

    logger.info("Sentry inicializado (env=%s)", environment)
    return True
