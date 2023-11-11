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
        portrayal["Color"] = "orange"
        portrayal["r"] = 0.9

    if agent.age == "elder":
        portrayal["Shape"] = "circle"
        portrayal["Color"] = "darkslateblue"
        portrayal["r"] = 0.7

    if agent.age == "child":
        portrayal["Shape"] = "circle"
        portrayal["Color"] = "purple"
        portrayal["r"] = 0.4

    if agent.vaccinated == True:
        portrayal["Color"] = "#304ffe"

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


grid = CanvasGrid(agent_portrayal, 50, 50, 862, 500)

sir_curves = ChartModule(
    [
        {"Label": "Total Susceptible", "Color": "turquoise"},
        {"Label": "Total Infected", "Color": "firebrick"},
        {"Label": "Total Recovered", "Color": "forestgreen"},
        {"Label": "Susceptible Adults", "Color": "orange"},
        {"Label": "Susceptible Children", "Color": "purple"},
        {"Label": "Susceptible Elderly", "Color": "darkslateblue"},
        {"Label": "Infected Adults", "Color": "red"},
        {"Label": "Infected Children", "Color": "pink"},
        {"Label": "Infected Elderly", "Color": "brown"},
        {"Label": "Recovered Adults", "Color": "green"},
        {"Label": "Recovered Children", "Color": "lightgreen"},
        {"Label": "Recovered Elderly", "Color": "lightblue"},
    ],
    canvas_height=190,
    canvas_width=500,
)

server = ModularServer(
    SIR,
    [grid, sir_curves],
    "SIR Model of Influenza A/H1N1",
    model_params,
)
