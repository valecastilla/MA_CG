from traffic_base.agent import *
from traffic_base.model import CityModel

from mesa.visualization import Slider, SolaraViz, make_space_component
from mesa.visualization.components import AgentPortrayalStyle


def agent_portrayal(agent):

    if agent is None:
        return

    portrayal = AgentPortrayalStyle(
        marker="s",
    )

    if isinstance(agent, Road):
        portrayal.marker = "o"
        if agent.direction == "Up":
            portrayal.color = "#aaf"
        elif agent.direction == "Down":
            portrayal.color = "#faa"
        elif agent.direction == "Right":
            portrayal.color = "#afa"
        elif agent.direction == "Left":
            portrayal.color ="#ffa"
#
    if isinstance(agent, Destination):
        portrayal.color = "lightgreen"

    if isinstance(agent, Traffic_Light):
        #TODO: cambiar colores A QUE SE VEAN
        portrayal.color = "#EE909000" if not agent.state else "#90EE9000"

    if isinstance(agent, Obstacle):
        portrayal.color = "#555"

    return portrayal


def post_process(ax):
    ax.set_aspect("equal")


model_params = {
    "N": 5,
    "seed": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
}

model = CityModel(model_params["N"])

space_component = make_space_component(
    agent_portrayal, draw_grid=False, post_process=post_process
)

page = SolaraViz(
    model,
    components=[space_component],
    model_params=model_params,
    name="Random Model",
)
