# AI Agent (Python + Ollama)

> 🚧 **Work in progress.** This project is built step by step and this README is updated as new features are added.

A command-line AI agent built from scratch in Python. It talks to a locally hosted LLM through the OpenAI-compatible API, can call tools, and streams its answers.

## Progress

- [x] OpenAI-compatible client with a local LLM (Ollama)
- [x] `.env` configuration
- [x] Chat loop with conversation memory
- [x] System prompt
- [x] Tool calling with parameters
- [x] Chained tool calling (agent loop) with `MAX_STEPS` and error handling
- [x] Debug logging and modular code
- [x] Streaming responses and streamed tool calls
- [x] Graceful Ctrl+C handling
- [ ] RAG
- [ ] MCP
- [ ] Persistent memory
- [ ] Multi-agent workflows
- [ ] LangChain / LangGraph
- [ ] Deployment

## Tech stack

- Python 3
- [Ollama](https://ollama.com) (local LLM, default model: `qwen3:4b`)
- `openai` SDK (used against Ollama's OpenAI-compatible API)
- `python-dotenv`, `requests`

## Project structure

```
.
├── simple_ai_assistant.py   # chat loop, agent loop, streaming
├── tools.py                 # tools, tool schemas, run_tool()
├── Utilities/
│   └── utilities.py         # debug logging
├── .env                     # local config (not committed)
└── README.md
```

## Getting started

### 1. Start Ollama
```bash
ollama pull qwen3:4b
ollama serve        # skip if the Ollama app is already running
```

### 2. Set up the project
```bash
python3 -m venv .venv
source .venv/bin/activate      # macOS / Linux
# .venv\Scripts\activate       # Windows

pip install openai python-dotenv requests
```

### 3. Create a `.env` file
```dotenv
BASE_URL=http://127.0.0.1:11434/v1
API_KEY=dummy_key
MODEL=qwen3:4b
DEBUG=False
```

| Variable | Description |
|---|---|
| `BASE_URL` | OpenAI-compatible endpoint (Ollama default shown above) |
| `API_KEY` | Any placeholder works for Ollama |
| `MODEL` | Model name as known by the server |
| `DEBUG` | Set to `True` to print debug logs |

### 4. Run
```bash
python3 simple_ai_assistant.py
```
Type `exit`, `quit`, `bye` or `goodbye` to leave. Press `Ctrl+C` while an answer is streaming to stop it.

## Available tools

| Tool | Parameters | Description |
|---|---|---|
| `get_current_time` | none | Returns the current date and time |
| `get_city_weather` | `city` | Returns the current weather for a city |

