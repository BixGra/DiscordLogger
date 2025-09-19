from fastapi import APIRouter, Depends
from fastapi_utils.tasks import repeat_every

from src.clients.discord_client import DiscordClient
from src.clients.monitoring_client import MonitoringClient

from src.schemas.monitoring_schemas import (
    AddRequestInput,
    GraphInput,
    RouteGraphInput,
)
from src.utils.dependencies import (
    get_discord_client,
    get_monitoring_client,
)
from src.utils.tools import get_wait_first


router = APIRouter(tags=["Monitoring"], prefix="/monitoring")


@repeat_every(seconds=60 * 60 * 24, wait_first=get_wait_first())
async def get_graphs(
    discord_client: DiscordClient = next(get_discord_client()),
    monitoring_client: MonitoringClient = next(get_monitoring_client()),
):
    for graph_type in ["VOLUME", "LATENCY"]:
        graphs = monitoring_client.get_graphs(last_hours=24, graph_type=graph_type)
        await discord_client.send_graphs(graphs)


@router.post("/add-request")
async def add_request(
    add_request_input: AddRequestInput,
    monitoring_client: MonitoringClient = Depends(get_monitoring_client),
) -> None:
    monitoring_client.add_request(
        service_name=add_request_input.service_name,
        route_name=add_request_input.route_name,
        timestamp=add_request_input.request.timestamp,
        response_time=add_request_input.request.response_time,
        response_code=add_request_input.request.response_code,
    )


@router.post("/graph-service")
async def graph_route(
    graph_input: GraphInput,
    discord_client: DiscordClient = Depends(get_discord_client),
    monitoring_client: MonitoringClient = Depends(get_monitoring_client),
) -> None:
    service = monitoring_client.get_service(service_name=graph_input.service_name)
    graph = service.get_graph(
        last_hours=graph_input.last_hours,
        graph_type=graph_input.graph_type,
    )
    await discord_client.send_graph(service.channel_id, graph)


@router.post("/graph-route")
async def graph_route(
    route_graph_input: RouteGraphInput,
    discord_client: DiscordClient = Depends(get_discord_client),
    monitoring_client: MonitoringClient = Depends(get_monitoring_client),
) -> None:
    route = monitoring_client.get_service(
        service_name=route_graph_input.service_name,
    ).get_route(
        route_name=route_graph_input.route_name,
    )
    graph = route.get_graph(
        last_hours=route_graph_input.last_hours,
        graph_type=route_graph_input.graph_type,
    )
    await discord_client.send_graph(route.channel_id, graph)
