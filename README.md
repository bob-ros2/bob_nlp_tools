# ROS Package [bob_nlp_tools](https://github.com/bob-ros2/bob_nlp_tools)
[![ROS 2 CI](https://github.com/bob-ros2/bob_nlp_tools/actions/workflows/ros2_ci.yml/badge.svg)](https://github.com/bob-ros2/bob_nlp_tools/actions/workflows/ros2_ci.yml)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

This ROS Package is part of Bob's NLP and LLM tools. It provides high-level semantic analysis and routing capabilities using OpenAI-compatible APIs (OpenAI, LM Studio, Ollama, LocalAI).

## NlpSemanticDriver (Library)
The package includes a standalone, ROS-free Python library `NlpSemanticDriver` that encapsulates the communication with the LLM API. It provides high-level methods for:
- **Semantic Routing**: Matching content to a key based on descriptions.
- **Semantic Filtering**: Boolean pass/fail based on a criterion.
- **Summarization**: Context-aware text compression.
- **Normalization**: Structured data extraction.

## ROS Node Semantic Router
The `semantic_router` node uses the LLM to categorize incoming text messages and routes them to specialized output topics based on their intent.

### Usage
```bash
# Start router with custom targets
ros2 run bob_nlp_tools router --ros-args \
  -p targets:='{"MOV": "Movement commands", "SPE": "Speech requests"}' \
  -p base_url:="http://192.168.1.9:8000/v1"
```

### Parameters

| Name | Type | Description |
|---|---|---|
| `api_key` | string | API key for the provider. Can also be set via environment variable `NLP_API_KEY`. Default: `not-set`. |
| `base_url` | string | Base URL for the OpenAI-compatible API. Can also be set via environment variable `NLP_BASE_URL`. Default: `http://localhost:1234/v1`. |
| `model` | string | Model name to use for routing. Can also be set via environment variable `NLP_MODEL`. Default: `gpt-3.5-turbo`. |
| `targets` | string (JSON) | JSON dictionary mapping topic suffixes to intent descriptions: `{"key": "Description"}`. |
| `default_target` | string | Suffix used for unrouted messages. Default: `unrouted`. |

### Topics

| Name | Type | Description |
|---|---|---|
| `topic_in` | `std_msgs/String` | Input topic for messages to be routed. |
| `~/out/<key>` | `std_msgs/String` | Dynamically created output topics for each target key. |
| `~/out/<default_target>` | `std_msgs/String` | Fallback topic for messages that couldn't be routed. |

## Installation
Ensure you have the `requests` library installed:
```bash
pip3 install requests
```
