[![python](https://img.shields.io/badge/Python-3.10-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)

# Age-structured SIR Agent-based Modeling of Influenza A/H1N1 in an Artificial Grocery Store

This is an age-structured SIR (Susceptible, Infected, Removed) Agent-based model of influenza A/H1N1 in an artificial Grocery Store.

# Installation

## Clone the GitHub Repository

```
git clone https://github.com/bfarahdel/Influenza-Grocery-Store-Model.git
```

The application can be run locally with a Python virtual environment or deployed as a web

## Python Virtual Environment (Recommended)

1. Install [virtualenv](https://virtualenv.pypa.io/en/latest/)

```
python3 -m pip install --user virtualenv
```

2. Create a virtual environment ("virtual_env" is the name of the environment used in this example)

```
python3 -m venv virtual_env
```

3. Install the required python packages

```
pip3 install -r requirements.txt
```

4. Activate the virtual environment

```
source virtual_env/bin/activate
```

5. Run the application

```
python3 run.py
```

## Deploy as a Web Service

A deployment platform such as [Render](https://render.com/) can be used to host the web application with [Gunicorn](https://gunicorn.org/).
When deploying as a web service on Render, the following build command can be used for Gunicorn: `gunicorn run`.

# Instructions

1. Set the parameters on the left panel.
2. If any of the parameters were changed, click the "Reset" button. Otherwise, continue to step 3.
3. Click the "Start" button.
