from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import ModularServer
from model import *


def agent_portrayal(agent):
    portrayal = {
        "Shape": "circle",
        "Layer": 0,
        "r": 1,
        "Color": "mediumpurple",
        "Filled": "true",
    }

    if agent.infected == True:
        portrayal["Color"] = "red"

    if agent.immune == True:
        portrayal["Color"] = "green"

    if agent.type == "wall":
        portrayal["Color"] = "lightgray"
        portrayal["Filled"] = "true"
        portrayal["Shape"] = "rect"
        portrayal["w"] = 1
        portrayal["h"] = 1

    return portrayal


grid = CanvasGrid(agent_portrayal, 50, 50, 500, 500)

line_charts = ChartModule(
    [
        {"Label": "Susceptible", "Color": "mediumpurple"},
        {"Label": "Infected", "Color": "red"},
        {"Label": "Recovered", "Color": "green"},
    ],
    canvas_height=190,
    canvas_width=500,
)

server = ModularServer(SIR, [grid, line_charts], "SIR Model", model_params)
