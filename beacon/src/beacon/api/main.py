from fastapi import APIRouter, FastAPI, Request, status

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    logger = setup_logger(log_level=get_log_level_from_env())
    app.state.logger = logger
    logger.info("Starting up (env=%s)", settings.APP_ENV)

    app.state.slack = SlackService(
        settings.SLACK_BOT_TOKEN,
        settings.SLACK_CHANNEL,
        settings.SLACK_API_BASE_URL,
        logger,
    )
    await app.state.slack.connect()

    app.state.traceability = TraceabilityService(
        settings.TRACEABILITY_API_BASE_URL,
        settings.TRACEABILITY_TIMEOUT_SECONDS,
        logger,
    )
    await app.state.traceability.connect()

    app.state.qrmac_db = AsyncSQLServerClient(
        settings.INT_QRMAC_DB_DSN, settings.DB_POOL_SIZE, logger
    )
    app.state.trace_db = AsyncSQLServerClient(
        settings.TRACE_DB_DSN, settings.DB_POOL_SIZE, logger
    )
    # app.state.shipping_db = AsyncSQLServerClient(
    #     settings.SHIPPING_DB_DSN, settings.DB_POOL_SIZE, logger
    # )
    await app.state.qrmac_db.connect()
    await app.state.trace_db.connect()
    # await app.state.shipping_db.connect()

    app.state.product_config_list = await _load_product_configs(
        app.state.trace_db, logger
    )

    yield
    logger.info("Shutting down")
    await app.state.qrmac_db.disconnect()
    await app.state.trace_db.disconnect()
    # await app.state.shipping_db.disconnect()
    await app.state.slack.disconnect()
    await app.state.traceability.disconnect()


app = FastAPI(lifespan=lifespan)
