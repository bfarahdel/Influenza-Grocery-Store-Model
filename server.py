from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import ModularServer
from model import *


def agent_portrayal(agent):
    portrayal = {
        "Shape": "circle",
        "Layer": 0,
        "r": 0.4,
        "Color": "purple",
        "Filled": "true",
    }

    if agent.age == "adult":
        portrayal["Shape"] = "circle"
        portrayal["Color"] = "darkslateblue"
        portrayal["r"] = 0.9

    if agent.age == "elderly":
        portrayal["Shape"] = "circle"
        portrayal["Color"] = "orange"
        portrayal["r"] = 0.7

    if agent.age == "child":
        portrayal["Shape"] = "circle"
        portrayal["Color"] = "purple"
        portrayal["r"] = 0.4

    if agent.infected == True:
        portrayal["Shape"] = "rect"
        portrayal["w"] = 0.8
        portrayal["h"] = 0.8

    if agent.immune == True:
        portrayal["Color"] = "green"

    if agent.type == "wall":
        portrayal["Color"] = "lightgray"
        portrayal["Filled"] = "true"
        portrayal["Shape"] = "rect"
        portrayal["w"] = 1
        portrayal["h"] = 1

    return portrayal


grid = CanvasGrid(agent_portrayal, 50, 50, 700, 500)

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
