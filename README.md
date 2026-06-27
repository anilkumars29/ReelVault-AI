# 🎬 ReelVault AI: Multimodal Knowledge Engine

An asynchronous, local Retrieval-Augmented Generation (RAG) loop that allows users to wirelessly index, transcribe, analyze, and query educational short-form videos via a Telegram chat interface.

## 🚀 Key Architectural Features
* **Multimodal Data Processing:** Splits incoming video streams to run Speech-to-Text via Whisper AI and Computer Vision via EasyOCR.
* **Edge Intelligence:** Powered entirely locally using `Ollama` and an optimized `Llama 3.2` model on consumer hardware.
* **Hybrid Storage Topology:** Synchronizes structured analytical summaries to a cloud Notion workspace while capturing semantic coordinates inside a local vector space (ChromaDB).
* **Asynchronous Concurrency:** Multi-threaded execution structure ensures non-blocking query responsiveness.

## 📐 System Architecture Design
[We will drop a clean text-based flowchart or diagram here later!]

## 🛠️ Tech Stack
* **Language:** Python 3.12
* **AI Frameworks:** Ollama (Llama 3.2), OpenAI Whisper, EasyOCR, OpenCV
* **Databases:** ChromaDB (Vector Store), Notion API
* **Interfaces:** Telegram Bot API, Streamlit

## 📐 System Architecture & Data Flow

```mermaid
graph TD
    %% Define Node Aesthetics
    classDef mobile fill:#FFD700,stroke:#333,stroke-width:2px,color:#000;
    classDef telegram fill:#0088cc,stroke:#333,stroke-width:2px,color:#fff;
    classDef engine fill:#1E1E1E,stroke:#333,stroke-width:2px,color:#fff;
    classDef pipeline fill:#FF4500,stroke:#333,stroke-width:2px,color:#fff;
    classDef database fill:#1E90FF,stroke:#333,stroke-width:2px,color:#fff;

    %% Data Transversal Vectors
    UserPhone["📱 Mobile Phone: User Action"]
    TGCloud["☁️ Telegram Cloud Servers"]
    BotEngine["🤖 telegram_bot.py Server Node"]
    
    subgraph "Ingestion Router & Worker Threading Matrix"
        BotEngine --> IntentRouter{"Intent Router"}
        IntentRouter -->|1. Delete Intent| DeleteHandler["🗑️ Deletion Purge Filter"]
        IntentRouter -->|2. Query Intent| RAGEngine["🧠 ChromaDB Vector Lookup"]
        IntentRouter -->|3. New Asset Ingestion| DuplicateCheck{"Idempotency Pre-Check"}
        
        DuplicateCheck -->|Matches Existing Metadata| SkipNotify["🧠 Duplicate Alert Dispatched"]
        DuplicateCheck -->|Unique Asset URL| ThreadSpawn["🧵 Background Worker Thread Spawned"]
    end
    
    subgraph "Multi-Modal Ingestion Pipeline"
        ThreadSpawn --> Pipeline["pipeline.py Engine"]
        Pipeline --> YTDLP["🎬 yt-dlp Video/Audio Splitter"]
        YTDLP -->|Audio Track .mp3| Whisper["🗣️ OpenAI Whisper AI: Speech-to-Text"]
        YTDLP -->|Video Frames .mp4| EasyOCR["👁️ EasyOCR Engine: Computer Vision Frame Scan"]
    end

    subgraph "Dual-Topology Hybrid Database Sync"
        Whisper --> ContextCompiler["🧩 Context Compiler Matrix"]
        EasyOCR --> ContextCompiler
        
        ContextCompiler --> Chroma["🗄️ Local ChromaDB Vector Store"]
        ContextCompiler --> Notion["📝 Notion Workspace Cloud Database"]
    end
    
    subgraph "Edge Inference Execution"
        RAGEngine --> DistanceShield{"Distance Threshold Shield"}
        DistanceShield -->|Score > 1.3| ShieldHalt["🤷‍♂️ Irrelevant Query Block Dispatch"]
        DistanceShield -->|Score <= 1.3| Ollama["🦙 Ollama: llama3.2 Inference Engine"]
        Ollama --> TargetResponse["📱 Dispatched to Phone Screen"]
    end

    subgraph "UI Control Center Layer"
        Chroma --> Streamlit["📊 app.py Streamlit UI Center"]
    end

    %% Network Connections
    UserPhone --> TGCloud
    TGCloud --> BotEngine
    DeleteHandler --> Chroma

    %% Assign Styles Legibly at the Base
    class UserPhone mobile;
    class TGCloud telegram;
    class BotEngine engine;
    class Pipeline pipeline;
    class Chroma database;
    class Notion database;
    class Streamlit mobile;