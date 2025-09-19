from fastapi import APIRouter, Depends

from src.clients.discord_client import DiscordClient
from src.schemas.logging_schemas import SendLogInput
from src.utils.dependencies import get_discord_client


router = APIRouter(tags=["Logging"], prefix="/logging")


@router.post("/send-log")
async def send_log(
    send_log_input: SendLogInput,
    discord_client: DiscordClient = Depends(get_discord_client),
) -> None:
    await discord_client.send_log(
        channel_id=send_log_input.channel_id,
        message=send_log_input.logging_message.get_ansi(),
    )
