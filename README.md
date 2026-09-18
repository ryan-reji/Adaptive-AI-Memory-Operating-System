# Adaptive-AI-Memory-Operating-System

Privacy-preserving AI Memory Assistant with activity capture, relevance-aware memory creation, smart forgetting, and information retrieval using RAG.

## Overview

The Adaptive AI Memory Operating System is a privacy-preserving personal memory assistant designed to continuously capture permitted user activity, identify information that may be useful as long-term memory, store it in a structured memory system, and make it available for semantic retrieval through RAG.

The system is designed around a modular architecture where activity monitoring, memory management, AI processing, and user interaction are separated into independent components.

The current system supports:

- File, Browser and VS Code activity monitoring
- Activity evidence collection and storage
- AI-based activity relevance classification
- Relevance-aware memory creation
- Persistent memory storage using SQLite
- Memory ingestion into ChromaDB
- Embedding generation
- RAG-based memory retrieval
- Privacy and permission controls

Smart Forgetting is part of the project architecture and is planned as a later memory-management component.
