# Customer Service Agent

This repository contains the code for a customer service agent that can classify the user message into one of three categories: 'bug_report', 'feature_request' or 'general_inquiry'

## Overview

This project showcases a system built using LangGraph and OpenAI API:
- **LangGraph-Based Workflows:**
  Utilizes LangGraph to create nodes for each class, each node follow a different workflow to generate a response with a different format.

- **JSON-Based Configuration:**
  Utilizes JSON-Based configurations of products and their components.

- **Environment-Based Configuration:**  
  Manages API keys and sensitive configurations through environment variables loaded from a `.env` file.

## Prerequisites

Before running this project, ensure you have the following:
- **Environment Variables:**
    - A valid API key for OpenAI. Obtain your API Key [here](https://platform.openai.com/api-keys).

    Create a `.env` file in the project directory with the following keys:
    `OPENAI_API_KEY=<openai-api_key>`

- Docker:
    - Ensure you have `docker` installed. For more information click [here](https://docs.docker.com).

## Project Structure
  .
  |- app
  |-- agent.py
  |-- main.py
  |-- config.json
  |-- config.py
  |-- nodes/
  |--- bug_report.py
  |--- classification.py
  |--- feature_request.py
  |--- general_inquiry.py
  |-- utils/
  |--- LLM.py
  |-- tests/
  |--- unit_tests.py
  |- Dockerfile
  |- docker-compose.yml
  |- pytest.ini
  |- requirements.txt

# Running the System

__1. Run the docker compose command:__

```bash
docker-compose up --build
```

# Troubleshooting

1. **Environment Variables**

Ensure that `OPENAI_API_KEY` is correctly defined in your `.env` file.

Missing or incorrect API keys will lead to errors.

2. API Connectivity

Verify that the OpenAI API endpoint (https://api.openai.com/v1/chat/completions) is accessible.

# Debugging
Review the console output to diagnose any problems during execution.

