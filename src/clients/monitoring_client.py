import enum
import io
import random
from datetime import timedelta, datetime
from enum import Enum
from io import BytesIO
from itertools import groupby

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
from matplotlib.axes import Axes
from matplotlib.ticker import MaxNLocator
from scipy.interpolate import make_smoothing_spline

from src.schemas.monitoring_schemas import (
    GraphType,
    Interval,
)
from src.utils.errors import (
    DuplicateRouteError,
    DuplicateServiceError,
    RouteNotFoundError,
    ServiceNotFoundError,
)
from src.utils.errors import (
    PlainHourError,
)


class MonitoredRequest:
    def __init__(self, timestamp: datetime, response_time: float, response_code: str):
        self.timestamp: datetime = timestamp
        self.response_time: float = response_time
        self.response_code: str = response_code

    def __eq__(self, other):
        if isinstance(other, MonitoredRequest):
            return self.timestamp == other.timestamp
        else:
            return self.timestamp == other

    def __gt__(self, other):
        if isinstance(other, MonitoredRequest):
            return self.timestamp > other.timestamp
        else:
            return self.timestamp > other

    def __ge__(self, other):
        if isinstance(other, MonitoredRequest):
            return self.timestamp >= other.timestamp
        else:
            return self.timestamp >= other

    def __lt__(self, other):
        if isinstance(other, MonitoredRequest):
            return self.timestamp < other.timestamp
        else:
            return self.timestamp < other

    def __le__(self, other):
        if isinstance(other, MonitoredRequest):
            return self.timestamp <= other.timestamp
        else:
            return self.timestamp <= other

    def __str__(self):
        return f"{self.timestamp} - {self.response_time} - {self.response_code}"

    def __repr__(self):
        return str(self)


class MonitoredRoute:
    def __init__(self, service_name: str, route_name: str, channel_id: int):
        self.service_name: str = service_name
        self.route_name: str = route_name
        self.requests: list[MonitoredRequest] = []
        self.channel_id: int = channel_id

    # TODO : remove
    def populate(self):
        for i in range(200):
            timestamp = datetime.now() - timedelta(
                hours=random.randint(0, 72),
                minutes=random.randint(0, 60),
            )
            response_time = random.randint(0, 300) / 100
            response_code = random.choice(
                ["200", "200", "200", "200", "200", "200", "404", "404", "500"]
            )
            request = MonitoredRequest(
                timestamp=timestamp,
                response_time=response_time,
                response_code=response_code,
            )
            self.add_request(request)

    def add_request(self, request: MonitoredRequest):
        self.requests.append(request)
        self.requests = sorted(self.requests)

    def get_requests(
        self, hours: int = 24, now: datetime = datetime.now()
    ) -> list[MonitoredRequest]:
        requests = []
        if index := next(
            (
                i
                for i, request in enumerate(self.requests)
                if (now - timedelta(hours=hours)).replace(
                    minute=0, second=0, microsecond=0
                )
                < request
            ),
            None,
        ):
            requests = self.requests[index:]
        return requests

    def get_graph(self, last_hours: int, graph_type: GraphType) -> BytesIO:
        return get_graph(to_graph=self, last_hours=last_hours, graph_type=graph_type)


class MonitoredService:
    def __init__(self, service_name: str, channel_id: int):
        self.service_name: str = service_name
        self.routes: dict[str, MonitoredRoute] = {}
        self.channel_id: int = channel_id

    def add_route(self, route_name: str, channel_id: int):
        if route_name in self.routes.keys():
            raise DuplicateRouteError
        self.routes[route_name] = MonitoredRoute(
            service_name=self.service_name,
            route_name=route_name,
            channel_id=channel_id,
        )

    # TODO : remove
    def populate(self, route_name: str):
        if route_name not in self.routes.keys():
            raise RouteNotFoundError
        self.routes[route_name].populate()

    def add_request(self, route_name: str, request: MonitoredRequest):
        if route_name not in self.routes.keys():
            raise RouteNotFoundError
        self.routes[route_name].add_request(request)

    def get_route(self, route_name: str) -> MonitoredRoute:
        return self.routes.get(route_name, None)

    def get_routes(self) -> dict[str, MonitoredRoute]:
        return self.routes

    def get_graph(self, last_hours: int, graph_type: GraphType) -> BytesIO:
        return get_graph(to_graph=self, last_hours=last_hours, graph_type=graph_type)


class MonitoringClient:
    def __init__(self):
        self.services: dict[str, MonitoredService] = {}
        self.add_service("service1", 1415770234442219600)
        self.add_route("service1", "route1", 1415770272489013318)
        self.populate("service1", "route1")
        self.add_route("service1", "route2", 1415770272489013318)
        self.populate("service1", "route2")

    def add_service(self, service_name: str, channel_id: int):
        if service_name in self.services.keys():
            raise DuplicateServiceError
        self.services[service_name] = MonitoredService(
            service_name=service_name,
            channel_id=channel_id,
        )

    def add_route(self, service_name: str, route_name: str, channel_id: int):
        if service_name not in self.services.keys():
            raise ServiceNotFoundError
        self.services[service_name].add_route(
            route_name=route_name,
            channel_id=channel_id,
        )

    # TODO : remove
    def populate(self, service_name: str, route_name: str):
        if service_name not in self.services.keys():
            raise ServiceNotFoundError
        self.services[service_name].populate(route_name)

    def add_request(
        self,
        service_name: str,
        route_name: str,
        timestamp: datetime,
        response_time: float,
        response_code: str,
    ):
        request = MonitoredRequest(
            timestamp=timestamp,
            response_time=response_time,
            response_code=response_code,
        )
        if service_name not in self.services.keys():
            raise ServiceNotFoundError
        self.services[service_name].add_request(route_name, request)

    def get_service(self, service_name: str) -> MonitoredService:
        return self.services.get(service_name, None)

    def get_services(self) -> dict[str, MonitoredService]:
        return self.services

    def get_graphs(
        self, last_hours: int, graph_type: GraphType
    ) -> list[tuple[int, BytesIO]]:
        print("2")
        graphs = []
        print(self.get_services().items())
        for service_name, service in self.get_services().items():
            graphs.append(
                (
                    service.channel_id,
                    service.get_graph(last_hours=last_hours, graph_type=graph_type),
                )
            )
            for route_name, route in service.get_routes().items():
                graphs.append(
                    (
                        route.channel_id,
                        route.get_graph(last_hours=last_hours, graph_type=graph_type),
                    )
                )
        return graphs


def get_intervals(
    start: datetime, end: datetime, delta_hours: int = 1
) -> list[Interval]:
    if start.minute or start.second or start.microsecond:
        raise PlainHourError
    if end.minute or end.second or end.microsecond:
        raise PlainHourError
    intervals = []
    delta = timedelta(hours=delta_hours)
    lower = start
    higher = lower + delta
    i = 0
    while lower <= end:
        intervals.append(Interval(lower, higher, i))
        lower = higher
        higher = lower + delta
        i += 1
    return intervals


def get_volumes(_requests: npt.NDArray) -> int:
    return len(_requests)


def get_latencies(_requests: npt.NDArray) -> float | None:
    if len(_requests):
        return float(np.mean(list(map(lambda x: x.response_time, _requests))))
    return None


class GraphDataFunction(Enum):
    VOLUME = enum.member(get_volumes)
    LATENCY = enum.member(get_latencies)


def get_graph_data(
    intervals: list[Interval], requests: list[MonitoredRequest], graph_type: GraphType
) -> list:
    _requests = np.array(requests)
    f = GraphDataFunction[graph_type].value
    data = [
        f(_requests[(interval.start <= _requests) & (_requests < interval.end)])
        for interval in intervals
    ]
    return data


COLORS = [
    "red",
    "blue",
    "green",
    "orange",
    "pink",
]


def plot_volumes(
    ax: Axes,
    x_offsets: list[float],
    data: list[int],
    bottom: npt.NDArray,
    route_name: str,
    i: int,
) -> npt.NDArray:
    ax.bar(
        x_offsets,
        data,
        width=0.95,
        align="edge",
        color=COLORS[i % len(COLORS)],
        bottom=bottom,
        zorder=3,
        label=f"{route_name}",
    )
    bottom += data
    return bottom


def plot_latencies(
    ax: Axes,
    x_offsets: list[float],
    data: list[float],
    bottom: npt.NDArray,
    route_name: str,
    i: int,
) -> npt.NDArray:
    x_offsets_, data_ = zip(*[(x, d) for x, d in zip(x_offsets, data) if d])
    ax.plot(
        x_offsets_, data_, ".", color=COLORS[i % len(COLORS)], label=f"{route_name}"
    )

    x_offsets_smooth = np.linspace(x_offsets_[0], x_offsets_[-1], 10 * len(x_offsets_))
    sspl = make_smoothing_spline(x_offsets_, data_, lam=0.1)
    ax.plot(
        x_offsets_smooth,
        sspl(x_offsets_smooth),
        "-",
        color=COLORS[i % len(COLORS)],
        label=f"{route_name} tendency",
    )
    return bottom


class PlotFunction(Enum):
    VOLUME = enum.member(plot_volumes)
    LATENCY = enum.member(plot_latencies)


def plot_style_volumes(ax: Axes):
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.grid(axis="y")


def plot_style_latencies(ax: Axes):
    ax.set_ylim(bottom=0)
    ax.grid()


class PlotStyleFunction(Enum):
    VOLUME = enum.member(plot_style_volumes)
    LATENCY = enum.member(plot_style_latencies)


def plot_graph(
    intervals: list[Interval],
    data_list: list[list],
    service_name: str,
    route_names: list[str],
    now: datetime,
    graph_type: GraphType,
) -> BytesIO:
    fig = plt.figure(figsize=(16, 9))
    ax = fig.gca()

    x_offsets = [interval.x_offset for interval in intervals]
    labels = [
        f"{interval.day}\n{interval.hour}" if i == 0 else f"{interval.hour}"
        for _, group in groupby(intervals, key=lambda x: x.day)
        for i, interval in enumerate(group)
    ]
    bottom = np.zeros_like(data_list[0])

    ax.set_title(
        f"{graph_type.capitalize()} for [{service_name}] on {now.day:0>2}/{now.month:0>2}/{now.year} at {now.hour:0>2}:{now.minute:0>2}"
    )
    ax.set_xticks(x_offsets, labels, rotation=45, ha="right")
    ax.set_xlim(left=0, right=len(intervals))
    plt.xlabel("Time")
    plt.ylabel(graph_type.capitalize())

    for i, (data, route_name) in enumerate(zip(data_list, route_names)):
        bottom = PlotFunction[graph_type].value(
            ax, x_offsets, data, bottom, route_name, i
        )

    PlotStyleFunction[graph_type].value(ax)
    ax.legend()
    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, dpi=250, format="png")
    buffer.seek(0)

    return buffer


def get_graph(
    to_graph: MonitoredService | MonitoredRoute, last_hours: int, graph_type: GraphType
) -> BytesIO:
    end = datetime.now().replace(minute=0, second=0, microsecond=0)
    start = end - timedelta(hours=last_hours)
    intervals = get_intervals(start, end)
    if isinstance(to_graph, MonitoredService):
        routes = [to_graph.get_route(r) for r in to_graph.get_routes()]
    elif isinstance(to_graph, MonitoredRoute):
        routes = [to_graph]
    service_name = to_graph.service_name
    routes_names, data = zip(
        *[
            (
                route.route_name,
                get_graph_data(
                    intervals, route.get_requests(last_hours, end), graph_type
                ),
            )
            for route in routes
        ]
    )
    graph = plot_graph(intervals, data, service_name, routes_names, end, graph_type)
    return graph
