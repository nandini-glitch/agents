# Voice Agents Examples

This directory contains a comprehensive collection of voice-based agent examples demonstrating various capabilities and integrations with the LiveKit Agents framework.

## 📋 Table of Contents

### 🚀 Getting Started

- [`basic_agent.py`](./basic_agent.py) - A fundamental voice agent with metrics collection

### 🛠️ Tool Integration & Function Calling

- [`annotated_tool_args.py`](./annotated_tool_args.py) - Using Python type annotations for tool arguments
- [`dynamic_tool_creation.py`](./dynamic_tool_creation.py) - Creating and registering tools dynamically at runtime
- [`raw_function_description.py`](./raw_function_description.py) - Using raw JSON schema definitions for tool descriptions
- [`silent_function_call.py`](./silent_function_call.py) - Executing function calls without verbal responses to user
- [`long_running_function.py`](./long_running_function.py) - Handling long running function calls with interruption support

### ⚡ Real-time Models

- [`weather_agent.py`](./weather_agent.py) - OpenAI Realtime API with function calls for weather information
- [`realtime_video_agent.py`](./realtime_video_agent.py) - Google Gemini with multimodal video and voice capabilities
- [`realtime_joke_teller.py`](./realtime_joke_teller.py) - Amazon Nova Sonic real-time model with function calls
- [`realtime_load_chat_history.py`](./realtime_load_chat_history.py) - Loading previous chat history into real-time models
- [`realtime_turn_detector.py`](./realtime_turn_detector.py) - Using LiveKit's turn detection with real-time models
- [`realtime_with_tts.py`](./realtime_with_tts.py) - Combining external TTS providers with real-time models

### 🎯 Pipeline Nodes & Hooks

- [`fast-preresponse.py`](./fast-preresponse.py) - Generating quick responses using the `on_user_turn_completed` node
- [`flush_llm_node.py`](./flush_llm_node.py) - Flushing partial LLM output to TTS in `llm_node`
- [`structured_output.py`](./structured_output.py) - Structured data and JSON outputs from agent responses
- [`speedup_output_audio.py`](./speedup_output_audio.py) - Dynamically adjusting agent audio playback speed
- [`timed_agent_transcript.py`](./timed_agent_transcript.py) - Reading timestamped transcripts from `transcription_node`
- [`inactive_user.py`](./inactive_user.py) - Handling inactive users with the `user_state_changed` event hook
- [`resume_interrupted_agent.py`](./resume_interrupted_agent.py) - Resuming agent speech after false interruption detection
- [`toggle_io.py`](./toggle_io.py) - Dynamically toggling audio input/output during conversations

### 🤖 Multi-agent & AgentTask Use Cases

- [`restaurant_agent.py`](./restaurant_agent.py) - Multi-agent system for restaurant ordering and reservation management
- [`multi_agent.py`](./multi_agent.py) - Collaborative storytelling with multiple specialized agents
- [`email_example.py`](./email_example.py) - Using AgentTask to collect and validate email addresses

### 🔗 MCP & External Integrations

- [`web_search.py`](./web_search.py) - Integrating web search capabilities into voice agents
- [`langgraph_agent.py`](./langgraph_agent.py) - LangGraph integration
- [`mcp/`](./mcp/) - Model Context Protocol (MCP) integration examples
  - [`mcp-agent.py`](./mcp/mcp-agent.py) - MCP agent integration
  - [`server.py`](./mcp/server.py) - MCP server example
- [`zapier_mcp_integration.py`](./zapier_mcp_integration.py) - Automating workflows with Zapier through MCP

### 💾 RAG & Knowledge Management

- [`llamaindex-rag/`](./llamaindex-rag/) - Complete RAG implementation with LlamaIndex
  - [`chat_engine.py`](./llamaindex-rag/chat_engine.py) - Chat engine integration
  - [`query_engine.py`](./llamaindex-rag/query_engine.py) - Query engine used in a function tool
  - [`retrieval.py`](./llamaindex-rag/retrieval.py) - Document retrieval

### 🎵 Specialized Use Cases

- [`background_audio.py`](./background_audio.py) - Playing background audio or ambient sounds during conversations
- [`push_to_talk.py`](./push_to_talk.py) - Push-to-talk interaction
- [`tts_text_pacing.py`](./tts_text_pacing.py) - Pacing control for TTS requests
- [`speaker_id_multi_speaker.py`](./speaker_id_multi_speaker.py) - Multi-speaker identification

### 📊 Tracing & Error Handling

- [`langfuse_trace.py`](./langfuse_trace.py) - LangFuse integration for conversation tracing
- [`error_callback.py`](./error_callback.py) - Error handling callback
- [`session_close_callback.py`](./session_close_callback.py) - Session lifecycle management

## 📖 Additional Resources

- [LiveKit Agents Documentation](https://docs.livekit.io/agents/)
- [Agents Starter Example](https://github.com/livekit-examples/agent-starter-python)
- [More Agents Examples](https://github.com/livekit-examples/python-agents-examples)

# Intelligent Voice Interruption Filter for LiveKit Agents

**Student Name**: Nandini Sharma  
**University**: Netaji Subhas University of Technology  
**Branch**: `feature/livekit-interrupt-handler-nandini`  
**Date**: November 18, 2025

---

## Problem Statement

LiveKit's Voice Activity Detection (VAD) treats all user speech as valid interruptions, including filler sounds like "uh", "umm", and "hmm". This causes the agent to stop speaking unnecessarily, breaking conversational flow.

**Goal**: Create an intelligent filter that distinguishes meaningful interruptions from irrelevant fillers while maintaining real-time responsiveness.

---

## What Changed

I implemented a three-layer filtering system that sits on top of LiveKit without modifying the core SDK.

### New Files Created

#### 1. `config.py` (Configuration Layer)
**Purpose**: Manages all filter settings and loads them from environment variables.

**What it contains**:
- `InterruptionConfig` class using Python dataclass
- List of ignored filler words (configurable via .env)
- Confidence threshold setting (0.0-1.0 scale)
- Debug mode toggle
- Multi-language support structure

**Key features**:
- Loads from .env file using `from_env()` classmethod
- Supports runtime updates to ignored word list
- Default filler words: uh, um, umm, hmm, haan, mhm, aha, err, ah

**Code structure**:
```python
@dataclass
class InterruptionConfig:
    ignored_words: List[str] = None
    confidence_threshold: float = 0.6
    debug_mode: bool = False
    language_fillers: Dict[str, List[str]] = None
```

#### 2. `interruption_handler.py` (Brain/Logic Layer)
**Purpose**: The core decision-making engine that analyzes speech and decides whether to allow interruptions.

**What it contains**:
- `IntelligentInterruptionHandler` class
- Four-rule filtering system
- Event logging for debugging
- Thread-safe state management using `asyncio.Lock`

**The Four Rules** :

1. **Agent Quiet Rule**: If agent isn't speaking, allow ALL speech (even fillers)
   - Rationale: User might be thinking; "hmm" is natural when pondering
   
2. **Confidence Rule**: Ignore low-confidence transcriptions (< 0.6 by default)
   - Rationale: Prevents false positives from background noise
   
3. **Filler-Only Rule**: If speech contains ONLY filler words, ignore it
   - Rationale: Pure fillers shouldn't interrupt the agent
   
4. **Real Speech Rule**: If any non-filler words present, allow interruption
   - Rationale: User wants to actually say something

**Key design decisions**:
- Used `Set` instead of `List` for O(1) word lookup (fast performance)
- Async/await for non-blocking operation
- Lock mechanism prevents race conditions in concurrent access

#### 3. `interruption_filter_wrapper.py` (Integration Layer)
**Purpose**: Connects the filter logic to LiveKit's AgentSession without modifying core SDK.

**What it contains**:
- `InterruptionFilterWrapper` class
- Simple API for the main agent code
- Agent state tracking (speaking/quiet)

**Why this wrapper exists**: 
- Keeps the handler independent of LiveKit internals
- Makes integration clean and modular
- Easy to add/remove without breaking existing code

### Modified Files

#### `basic_agent.py`
**Lines added**: ~15 lines | **Lines modified**: 0 lines (only additions)

**Changes made**:
```python
# Lines 16-18: Import our custom modules
from interruption_filter_wrapper import InterruptionFilterWrapper
from config import InterruptionConfig

# Lines 76-78: Initialize the filter after creating session
config = InterruptionConfig.from_env()
filter_wrapper = InterruptionFilterWrapper(session, config)
logger.info(f"Interruption filter initialized with words: {config.ignored_words}")

# Lines 98-105: Track agent speaking state
@session.on("agent_started_speaking")
def on_agent_started():
    asyncio.create_task(filter_wrapper.set_agent_speaking(True))

@session.on("agent_stopped_speaking")
def on_agent_stopped():
    asyncio.create_task(filter_wrapper.set_agent_speaking(False))
```

**Why `asyncio.create_task()`?**  
LiveKit's `.on()` decorator doesn't support async functions directly. The wrapper function is synchronous but schedules the async task to run without blocking.

### Configuration Parameters Added

Added to `.env` file:
```bash
# Interruption Filter Configuration
IGNORED_WORDS=uh,um,umm,hmm,haan,mhm,aha,err,ah
CONFIDENCE_THRESHOLD=0.6
DEBUG_MODE=true
```

**Parameter explanations**:
- `IGNORED_WORDS`: Comma-separated list of words to filter out
- `CONFIDENCE_THRESHOLD`: Minimum speech recognition confidence (0-1)
- `DEBUG_MODE`: Enable detailed console logging


---

## Steps to Test My Implementation

### Prerequisites

- **Python**: Version 3.9 or higher
- **Operating System**: macOS, Linux, or Windows
- **LiveKit Account**: Free cloud account from https://cloud.livekit.io
- **API Keys Required**:
  - OpenAI (for LLM)
  - Deepgram (for Speech-to-Text)
  - Cartesia (for Text-to-Speech)

### Installation Steps
```bash
# 1. Clone the forked repository
git clone https://github.com/[YOUR-GITHUB-USERNAME]/agents.git
cd agents

# 2. Checkout my feature branch
git checkout feature/livekit-interrupt-handler-nandini

# 3. Navigate to the voice agents directory
cd examples/voice_agents

# 4. Create Python virtual environment
python3 -m venv venv

# 5. Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows Command Prompt:
venv\Scripts\activate.bat
# On Windows PowerShell:
venv\Scripts\Activate.ps1

# 6. Install dependencies
pip install --upgrade pip
pip install livekit-agents
pip install livekit-plugins-silero
pip install livekit-plugins-deepgram
pip install livekit-plugins-openai
pip install livekit-plugins-cartesia
pip install python-dotenv
pip install livekit
pip install aiofiles==25.1.0
pip install aiohappyeyeballs==2.6.1
pip install aiohttp==3.13.2
pip install aiosignal==1.4.0
pip install annotated-types==0.7.0
pip install anyio==4.11.0
pip install async-timeout==5.0.1
pip install attrs==25.4.0
pip install av==15.1.0
pip install backports.asyncio.runner==1.2.0
pip install certifi==2025.11.12
pip install cffi==2.0.0
pip install charset-normalizer==3.4.4
pip install click==8.1.8
pip install colorama==0.4.6
pip install distro==1.9.0
pip install docstring_parser==0.17.0
pip install val_type_backport==0.3.0
pip install exceptiongroup==1.3.0
fpip install rozenlist==1.8.0
pip install googleapis-common-protos==1.72.0
pip install grpcio==1.76.0
pip install h11==0.16.0
pip install httpcore==1.0.9
pip install httpx==0.28.1
pip install idna==3.11
pip install importlib_metadata==8.7.0
pip install iniconfig==2.1.0
pip install jiter==0.12.0
pip install livekit==1.0.19
pip install livekit-agents==1.3.2
pip install livekit-api==1.0.7
pip install livekit-blingfire==1.0.0
pip install livekit-plugins-openai==1.3.2
pip install livekit-protocol==1.1.0
pip install markdown-it-py==3.0.0
pip install mdurl==0.1.2
pip install multidict==6.7.0
pip install nest-asyncio==1.6.0
pip install numpy==2.0.2
pip install openai==2.8.0
pip install opentelemetry-api==1.38.0
pip install opentelemetry-exporter-otlp==1.38.0
pip install opentelemetry-exporter-otlp-proto-common==1.38.0
pip install opentelemetry-exporter-otlp-proto-grpc==1.38.0
pip install opentelemetry-exporter-otlp-proto-http==1.38.0
opip install pentelemetry-proto==1.38.0
pip install opentelemetry-sdk==1.38.0
pip install opentelemetry-semantic-conventions==0.59b0
pip install packaging==25.0
pip install pillow==11.3.0
pip install pluggy==1.6.0
pip install prometheus_client==0.23.1
pip install ropcache==0.4.1
pip install protobuf==6.33.1
pip install psutil==7.1.3
pip install pycparser==2.23
pip install pydantic==2.12.4
pip install pydantic_core==2.41.5
pip install Pygments==2.19.2
pip install PyJWT==2.10.1
pip install pytest==8.4.2
pip install pytest-asyncio==1.2.0
pip install python-dotenv==1.2.1
pip install requests==2.32.5
pip install rich==14.2.0
pip install shellingham==1.5.4
pip install sniffio==1.3.1
pip install sounddevice==0.5.3
pip install tomli==2.3.0
pip install tqdm==4.67.1
pip install typer==0.20.0
tpip install ypes-protobuf==6.32.1.20251105
pip install typing-inspection==0.4.2
pip install typing_extensions==4.15.0
pip install urllib3==2.5.0
pip install watchfiles==1.1.1
pip install websockets==15.0.1
pip install yarl==1.22.0
pip install zipp==3.23.0


# 7. Create environment file
touch .env
```

### Configure Environment Variables

Edit the `.env` file and add the following configuration:
```bash
# ============================================
# INTERRUPTION FILTER CONFIGURATION
# ============================================
IGNORED_WORDS=uh,um,umm,hmm,haan,mhm,aha,err,ah
CONFIDENCE_THRESHOLD=0.6
DEBUG_MODE=true

# ============================================
# LIVEKIT CONFIGURATION
# ============================================
# Get these from https://cloud.livekit.io (Settings → Keys)
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=APIxxxxxxxxxxxxxxxxxxxxxxx
LIVEKIT_API_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxx

# ============================================
# AI SERVICE API KEYS
# ============================================
# OpenAI: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxx

# Deepgram: https://console.deepgram.com/
DEEPGRAM_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxx

# Cartesia: https://play.cartesia.ai/
CARTESIA_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxx
```

### Running the Agent
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # or appropriate command for your OS

# Start the agent in development mode
python basic_agent.py dev

# Expected output:
# INFO   livekit.agents   starting worker
# INFO   livekit.agents   registered worker
# INFO   basic-agent      Interruption filter initialized with words: ['uh', 'um', ...]
```

**If you see this, the agent is running successfully!** Leave this terminal window open.

### Connecting as a Test User

Open a **new terminal** and generate an access token:
```bash
# Navigate to project directory
cd ~/agents/examples/voice_agents
source venv/bin/activate

# Generate token
python -c "
from livekit import api
import os
from dotenv import load_dotenv
load_dotenv()

token = api.AccessToken(
    os.getenv('LIVEKIT_API_KEY'),
    os.getenv('LIVEKIT_API_SECRET')
).with_identity('test-user').with_name('Test User').with_grants(
    api.VideoGrants(room_join=True, room='test-room')
)
print('\n=== COPY THIS TOKEN ===')
print(token.to_jwt())
print('=' * 50 + '\n')
"
```

**Copy the generated token**, then:

1. Open browser and go to: **https://meet.livekit.io/custom**
2. Fill in the form:
   - **LiveKit Server URL**: Your LIVEKIT_URL from .env (the wss:// URL)
   - **Token**: Paste the token you just copied
   - **Room Name**: `test-room`
3. Click **"Connect"**
4. **Allow microphone access** when prompted
5. Wait 5-10 seconds for agent "Kelly" to join

### Verification Checklist

Once connected, verify the filter is working:

- [ ] Agent Kelly joins and greets you
- [ ] Terminal shows: "Interruption filter initialized"
- [ ] Say "umm" while agent speaks → Agent continues
- [ ] Terminal logs: ` Filtered filler: 'umm'`
- [ ] Say "wait" while agent speaks → Agent stops
- [ ] Terminal logs: `✓ Allowed speech: 'wait'`
- [ ] Say "hmm" when agent is quiet → Registered as speech
- [ ] Terminal logs: `✓ Registered: 'hmm' (agent quiet)`

### Troubleshooting

**Agent doesn't start**:
- Check all API keys are correct in .env
- Verify LIVEKIT_URL starts with `wss://`
- Check Python version: `python --version` (must be 3.9+)

**Can't connect to room**:
- Regenerate token (they expire after 6 hours by default)
- Check LIVEKIT_URL matches what you used in token generation
- Try refreshing the browser page

**No filter logs appearing**:
- Make sure `DEBUG_MODE=true` in .env
- Restart the agent after changing .env

---

## Environment Details

### Development Environment

- **Python Version**: 3.9.16
- **Operating System**: macOS Ventura 13.x
- **IDE/Editor**: Visual Studio Code / Terminal
- **Virtual Environment**: venv

### Dependencies

**Core Framework**:
```
livekit-agents >= 0.9.0
```

**LiveKit Plugins**:
```
livekit-plugins-silero >= 0.6.0
livekit-plugins-deepgram >= 0.6.0
livekit-plugins-openai >= 0.6.0
livekit-plugins-cartesia >= 0.1.0
```

**Utilities**:
```
python-dotenv >= 1.0.0
livekit >= 0.11.0
```

### Python Standard Library Modules Used

- `asyncio` - Asynchronous I/O and task management
- `logging` - Event logging and debugging
- `os` - Environment variable access
- `datetime` - Timestamp generation for events
- `typing` - Type hints for better code documentation
- `dataclasses` - Simplified data class creation

### Tested On

- **Primary**: macOS Ventura 13.x with Python 3.9.16
- **Virtual Environment**: venv (Python's built-in)
- **Terminal**: macOS Terminal / iTerm2

---

## Implementation Approach

### Design Principles

1. **Non-Invasive Architecture**: Extension layer over LiveKit, not modification
2. **Performance First**: Used Set (O(1) lookup) instead of List (O(n) lookup)
3. **Thread Safety**: Async locks to prevent race conditions
4. **Configurability**: All settings in .env for easy adjustment
5. **Debuggability**: Comprehensive logging for every decision

### Why These Choices?

**Set vs List for Word Matching**:
- Set lookup: O(1) constant time
- List lookup: O(n) linear time
- With 10+ words, Set is significantly faster
- Example: Checking if "umm" is in 100 words takes same time as 1 word with Set

**Async/Await Pattern**:
- Non-blocking operations
- Doesn't freeze the agent while processing
- Essential for real-time voice applications

**Four-Rule System**:
- Clear decision tree
- Easy to test each rule independently
- Easy to add new rules without breaking existing ones
- Rules ordered by priority (fastest checks first)

### Alternative Approaches Considered

**Machine Learning Classifier**:
- Pros: Could learn user-specific patterns
- Cons: Overkill for this problem, needs training data, adds latency
- Decision: Rule-based is sufficient and more transparent

**Regex Pattern Matching**:
- Pros: Flexible pattern detection
- Cons: Slower than Set lookup, harder to configure
- Decision: Simple word matching is faster and clearer

---

## What I Learned

### Technical Skills

- **Async Python**: Understanding `asyncio.Lock`, `create_task()`, and when to use `await`
- **Performance Optimization**: Why data structures matter (Set vs List)
- **LiveKit Integration**: How to extend frameworks without modifying core code
- **Event-Driven Programming**: Using callbacks and event listeners effectively

### Challenges Overcome

1. **Async/Sync Mismatch**: 
   - Problem: LiveKit's `.on()` doesn't support async functions
   - Solution: Learned to wrap async calls in `asyncio.create_task()`

2. **State Management**:
   - Problem: Agent speaking state could be accessed from multiple places
   - Solution: Used `asyncio.Lock` for thread-safe updates

3. **Testing Real-Time Systems**:
   - Problem: Hard to create reproducible test cases with speech
   - Solution: Manual testing with detailed logging

### What I'm Proud Of

- Clean, modular code structure
- Comprehensive documentation
- No modifications to LiveKit core 
- Works in real-time with no noticeable latency

### Future Improvements

Given more time, I would add:

1. **Adaptive Learning**: Track user's speech patterns and adjust filters
2. **Multi-Language**: Better support for Hindi + English code-switching
3. **Context Awareness**: Consider conversation history in decisions
4. **Analytics Dashboard**: Web UI showing filter statistics
5. **Unit Tests**: Automated test suite for each filtering rule


---

## Submission Details

**Repository**: https://github.com/[nandini-glitch]/agents  
**Branch**: `feature/livekit-interrupt-handler-nandini`  
**Contact**: [nandinisharma.mail20@gmail.com]

---