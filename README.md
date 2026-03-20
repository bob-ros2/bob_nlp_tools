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

## ROS Nodes
The package provides several ROS 2 nodes that leverage the semantic driver for high-level NLP tasks:

### 1. Semantic Router (`router`)
Categorizes incoming text messages and routes them to specialized output topics based on their intent.

**Example:**
```bash
ros2 run bob_nlp_tools router --ros-args \
  -p targets:='{"MOV": "Movement commands", "SPE": "Speech requests"}' \
  -p base_url:="http://localhost:1234/v1"
```

### 2. Semantic Filter (`filter`)
Filters incoming messages based on a natural language criterion. Messages meeting the criterion are published to `topic_out`, others to `topic_rejected`.

**Example:**
```bash
ros2 run bob_nlp_tools filter --ros-args \
  -p criterion:='Handelt es sich um eine Frage zu Bobs Status?' \
  -p base_url:="http://localhost:1234/v1"
```

### 3. Summarizer (`summarizer`)
Generates concise summaries of incoming messages based on a provided context.

**Example:**
```bash
ros2 run bob_nlp_tools summarizer --ros-args \
  -p context:='Zusammenfassung der letzten Fehlermeldungen' \
  -p max_words:=20
```

### 4. Normalizer (`normalizer`)
Transforms unstructured input text into a structured format (e.g., JSON) based on descriptive instructions.

**Example:**
```bash
ros2 run bob_nlp_tools normalizer --ros-args \
  -p instructions:='Extrahiere Name und Alter als JSON: {"name": "", "age": 0}'
```

## Configuration

### Parameters

| Name | Type | Nodes | Description |
|---|---|---|---|
| `api_key` | string | all | API key for the provider. Can also be set via environment variable `NLP_API_KEY`. |
| `base_url` | string | all | Base URL for the OpenAI-compatible API. Default: `http://localhost:1234/v1`. |
| `model` | string | all | Model name to use. Default: `gpt-3.5-turbo`. |
| `targets` | string (JSON) | router | JSON dict mapping topic suffixes to intent descriptions: `{"key": "Description"}`. |
| `default_target` | string | router | Suffix used for unrouted messages. Default: `unrouted`. |
| `criterion` | string | filter | Natural language condition for the filter. |
| `context` | string | summarizer | Context for the summarization task. |
| `max_words` | int | summarizer | Word limit for the summary. Default: 50. |
| `instructions` | string | normalizer | Descriptive instructions for the normalization task. |

### Topics

| Name | Type | Nodes | Description |
|---|---|---|---|
| `topic_in` | `std_msgs/String` | all | Input topic for messages to be processed. |
| `topic_out` | `std_msgs/String` | filter, summarizer, normalizer | Output topic for processed messages. |
| `topic_rejected` | `std_msgs/String` | filter | Output topic for messages that did not meet the criterion. |
| `~/out/<key>` | `std_msgs/String` | router | Dynamically created output topics for each target key. |
| `~/out/<default_target>` | `std_msgs/String` | router | Fallback topic for messages that couldn't be routed. |

## Installation
Ensure you have the `requests` library installed:
```bash
pip3 install requests
```
