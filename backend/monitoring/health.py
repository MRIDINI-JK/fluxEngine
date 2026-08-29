from typing import Any


async def check_database() -> dict[str, Any]:

    try:

        from backend.database.session import (
            engine,
        )

        async with engine.connect():

            return {
                "status": "healthy",
            }

    except Exception as exc:

        return {
            "status": "unhealthy",
            "error": str(exc),
        }


async def check_rabbitmq(
    rabbitmq,
) -> dict[str, Any]:

    try:

        if rabbitmq.connection is None:

            return {
                "status": "unhealthy",
                "error": "Not connected",
            }

        if rabbitmq.connection.is_closed:

            return {
                "status": "unhealthy",
                "error": "Connection closed",
            }

        return {
            "status": "healthy",
        }

    except Exception as exc:

        return {
            "status": "unhealthy",
            "error": str(exc),
        }


async def check_system(
    rabbitmq=None,
) -> dict[str, Any]:

    result = {
        "status": "healthy",
        "database": {
            "status": "unknown"
        },
        "rabbitmq": {
            "status": "unknown"
        },
    }

    database = await check_database()

    result["database"] = database

    if rabbitmq is not None:

        result["rabbitmq"] = (
            await check_rabbitmq(
                rabbitmq
            )
        )

    services = [
        database,
        result["rabbitmq"],
    ]

    if any(
        service["status"] == "unhealthy"
        for service in services
    ):

        result["status"] = "unhealthy"

    return result