import asyncio

from app.services.ingestion.telegram_ingestion.telegram_client import client


async def main():
    await client.start()

    async for dialog in client.iter_dialogs():
        print(dialog.name, dialog.id)


if __name__ == "__main__":
    asyncio.run(main())