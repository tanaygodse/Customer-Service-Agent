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
    ├── ...
    ├── app                         # Directory containing all the code
    │   ├── agent.py                # Contains LangGraph code
    │   ├── main.py                 # FastAPI Server
    │   ├── config.json             # JSON file containing product, component and team details
    │   ├── config.py               # Code to load config
    │   ├── nodes/                  # Directory containing all the code for each of the nodes
    │   │   ├── bug_report.py       # File containing code for generating bug_report response
    │   │   ├── classification.py   # File containing code for classifying the message
    │   │   ├── feature_request.py  # File containing code for generating feature_request response
    │   │   ├── general_inquiry.py  # File containing code for generating general_inquiry response
    │   ├── utils/                  # Directory containing utility functions
    │   │   ├── LLM.py              # File containing code for LLMClient class
    │   ├── tests/                  # Directory containing test files
    │   │   ├── unit_tests.py       # File containing code for testing
    ├── Dockerfile                  # Docker Image to build the application
    ├── docker-compose.yml          # Docker Compose file to build the application along with passing in the .env file
    ├── pytest.ini                  # Set the PYTHONPATH to root directory for pytest
    ├── requirements.txt            # File containing all the dependencies of this application

# LangGraph Graph 
                                  +-----------+                                      
                                  | __start__ |                                      
                                  +-----------+                                      
                                         *                                           
                                         *                                           
                                         *                                           
                                +----------------+                                   
                                | classify_input |                                   
                            ....+----------------+.....                              
                       .....             .             .....                         
                 ......                 .                   ......                   
              ...                       .                         ...                
+----------------+           +--------------------+           +--------------------+ 
| bug_extraction |           | feature_extraction |           | inquiry_extraction | 
+----------------+*****      +--------------------+         **+--------------------+ 
                       *****            *              *****                         
                            ******       *       ******                              
                                  ***    *    ***                                    
                                    +---------+                                      
                                    | __end__ |                                      
                                    +---------+

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

