"""
DIALECTICA API — FastAPI application entry point.

Title: "DIALECTICA API"
Version: "1.0.0"
Description: "The Universal Data Layer for Human Friction"
"""
from __future__ import annotations

import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dialectica_api.config import get_settings
from dialectica_api.middleware.auth import AuthMiddleware, validate_production_config
from dialectica_api.middleware.tenant import TenantMiddleware
from dialectica_api.middleware.rate_limit import RateLimitMiddleware
from dialectica_api.middleware.logging import LoggingMiddleware
from dialectica_api.middleware.usage import UsageMiddleware
from dialectica_api.routers import (
    health, workspaces, entities, relationships,
    extraction, graph, reasoning, theory, admin, developers,
    sdk_info, benchmark,
)

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(message)s")
logger = logging.getLogger("dialectica.api")


def create_app() -> FastAPI:
    settings = get_settings()

    # ── Production safety checks ──────────────────────────────────────────
    validate_production_config()

    app = FastAPI(
        title="DIALECTICA API",
        version="2.0.0",
        description=(
            "The Universal Data Layer for Human Friction. "
            "A neurosymbolic conflict intelligence platform."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    origins = [o.strip() for o in settings.cors_origins.split(",")]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Middleware order: outermost applied last (LIFO for Starlette)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(UsageMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(TenantMiddleware)
    app.add_middleware(AuthMiddleware)

    # ── Prometheus metrics ────────────────────────────────────────────────
    try:
        from prometheus_fastapi_instrumentator import Instrumentator

        Instrumentator(
            should_group_status_codes=True,
            should_ignore_untemplated=True,
            excluded_handlers=["/health", "/health/", "/metrics"],
        ).instrument(app).expose(app, endpoint="/metrics", include_in_schema=True)
        logger.info('{"event":"prometheus_enabled","endpoint":"/metrics"}')
    except ImportError:
        logger.warning(
            '{"event":"prometheus_disabled","reason":"prometheus-fastapi-instrumentator not installed"}'
        )

    app.include_router(health.router)
    app.include_router(workspaces.router)
    app.include_router(entities.router)
    app.include_router(relationships.router)
    app.include_router(extraction.router)
    app.include_router(graph.router)
    app.include_router(reasoning.router)
    app.include_router(theory.router)
    app.include_router(admin.router)
    app.include_router(developers.router)
    app.include_router(sdk_info.router)
    app.include_router(benchmark.router)

    @app.on_event("startup")
    async def startup() -> None:
        logger.info('{"event":"startup","backend":"%s"}', settings.graph_backend)
        from dialectica_api.deps import get_graph_client
        client = get_graph_client(settings)
        if client is not None:
            try:
                await client.initialize_schema()
                logger.info('{"event":"schema_initialized"}')
            except Exception as exc:
                logger.warning('{"event":"schema_init_failed","error":"%s"}', exc)

    @app.on_event("shutdown")
    async def shutdown() -> None:
        from dialectica_api.deps import _graph_client_instance
        if _graph_client_instance is not None:
            try:
                await _graph_client_instance.close()
            except Exception:
                pass

        # Clean up rate-limit backend
        from dialectica_api.middleware.rate_limit import get_rate_limit_backend
        try:
            backend = get_rate_limit_backend()
            await backend.close()
        except Exception:
            pass

        logger.info('{"event":"shutdown"}')

    return app


app = create_app()
