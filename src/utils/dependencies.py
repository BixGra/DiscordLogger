from src.clients.discord_client import DiscordClient
from src.clients.monitoring_client import MonitoringClient

discord_client = DiscordClient()
monitoring_client = MonitoringClient()


def get_discord_client():
    try:
        yield discord_client
    finally:
        pass


def get_monitoring_client():
    try:
        yield monitoring_client
    finally:
        pass
