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
    classDef worker fill:#4B0082,stroke:#333,stroke-width:2px,color:#fff;
    classDef pipeline fill:#FF4500,stroke:#333,stroke-width:2px,color:#fff;
    classDef database fill:#1E90FF,stroke:#333,stroke-width:2px,color:#fff;

    %% Data Transversal Vectors
    UserPhone[📱 Mobile Phone: User Action] :::mobile
    TGCloud[☁️ Telegram Cloud Servers] :::telegram
    BotEngine[🤖 telegram_bot.py Server Node] :::engine
    
    subgraph "Ingestion Router & Worker Threading Matrix"
        BotEngine -->|Parser Check| IntentRouter{Intent Router}
        IntentRouter -->|1. Delete Intent| DeleteHandler[🗑️ Deletion Purge Filter]
        IntentRouter -->|2. Query Intent| RAGEngine[🧠 ChromaDB Vector Lookup]
        IntentRouter -->|3. New Asset Ingestion| DuplicateCheck{Idempotency Pre-Check}
        
        DuplicateCheck -->|Matches Existing Metadata| SkipNotify[🧠 Duplicate Alert Dispatched]
        DuplicateCheck -->|Unique Asset URL| ThreadSpawn[🧵 Background Worker Thread Spawned]
    end
    
    subgraph "Multi-Modal Ingestion Pipeline"
        ThreadSpawn -->|Async Handshake| Pipeline[pipeline.py Engine] :::pipeline
        Pipeline -->|🍪 Session cookies.txt Auth| YTDLP[🎬 yt-dlp Video/Audio Splitter]
        YTDLP -->|Audio Track .mp3| Whisper[🗣️ OpenAI Whisper AI: Speech-to-Text]
        YTDLP -->|Video Frames .mp4| EasyOCR[👁️ EasyOCR Engine: Computer Vision Frame Scan]
    end

    subgraph "Dual-Topology Hybrid Database Sync"
        Whisper -->|Synthesized Raw Metadata text| ContextCompiler[🧩 Context Compiler Matrix]
        EasyOCR -->|Extracted Text Data layers| ContextCompiler
        
        ContextCompiler -->|Vector Embeddings generation| Chroma[🗄️ Local ChromaDB Vector Store] :::database
        ContextCompiler -->|Structured Analytical Summary JSON| Notion[📝 Notion Workspace Cloud Database] :::database
    end
    
    subgraph "Edge Inference Execution"
        RAGEngine -->|Extracted Relevant Context Coordinates| DistanceShield{Distance Threshold Shield}
        DistanceShield -->|Score > 1.3: Insufficient Context| ShieldHalt[🤷‍♂️ Irrelevant Query Block Dispatch]
        DistanceShield -->|Score <= 1.3: Safe Node Context| Ollama[🦙 Ollama: llama3.2 Inference Engine]
        Ollama -->|Refined Plain-English Executive Answer| TargetResponse[📱 Dispatched to Phone Screen]
    end

    subgraph "UI Control Center Layer"
        Chroma -->|Live Local Storage Coordinates Read| Streamlit[📊 app.py Streamlit UI Center] :::mobile
    end

    %% Network Connections
    UserPhone -->|Sends Link / Query| TGCloud
    TGCloud -->|Long Polling Matrix Catch| BotEngine
    DeleteHandler -->|Drop Coordinate Indexes| Chroma