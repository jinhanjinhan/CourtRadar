from app.services.parsing.parser import CourtTransferParser


class TelegramIngestionService:
    def __init__(self):
        self.parser = CourtTransferParser()

    async def ingest_event(self, event) -> None:
        message = event.message
        text = message.message or ""

        if not text.strip():
            return

        parsed = self.parser.parse(text)

        if parsed is None:
            print("Irrelevant Telegram message:", text)
            return

        print("Relevant court transfer found!")
        print(parsed)