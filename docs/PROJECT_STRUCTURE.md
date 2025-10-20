# 📁 Project Structure

## 🏗️ Organized Directory Layout

```
cs6300_a5/
├── src/                                    # Core RAG system components
│   ├── __init__.py
│   ├── arxiv_fetcher.py                   # ArXiv API integration
│   ├── chat_manager.py                    # Chat session management
│   ├── config.py                          # Configuration management
│   ├── llm_client.py                      # LM Studio client
│   ├── rag_engine.py                      # RAG logic and caching
│   └── vector_db_populator.py             # Vector database operations
├── data/                                   # Data storage directory
│   ├── vector_db/                         # ChromaDB vector database files
│   ├── chat_history/                      # Saved chat sessions
│   │   ├── 129b5df7-5c65-4bef-b2bb-4169b419322f.json
│   │   ├── 49947c8c-69ee-4518-ab99-fa4a3b4154af.json
│   │   ├── c739af2b-b2c9-48d1-adf6-90f6ef8cb7a0.json
│   │   └── e45bbcbd-229c-4618-b2fc-4f5f5633558e.json
│   ├── models/                            # Sentence transformer model cache
│   │   └── models--sentence-transformers--all-MiniLM-L6-v2/
│   └── reports/                           # Test reports and metrics
│       ├── targeted_rag_test_report_neural_networks.json
│       └── rag_system_test_summary.json
├── scripts/                               # Executable scripts
│   ├── chat_viewer_gui.py                # GUI for viewing chat histories
│   ├── demo_pipeline.py                  # Main demo script
│   ├── generate_test_summary.py          # Test results summary
│   ├── populate_arxiv.py                 # ArXiv paper fetcher
│   ├── rag_chat.py                       # Interactive RAG chat
│   └── targeted_rag_test.py              # Targeted test with 12 papers
├── docs/                                  # Documentation
│   ├── README.md
│   ├── FINAL_SUMMARY.md
│   ├── WORKSPACE_CLEAN.md
│   └── PROJECT_STRUCTURE.md
└── requirements.txt                       # Python dependencies
```

## 📂 Directory Purposes

### `src/` - Core System Components
- **Purpose**: Contains all the core RAG system logic
- **Files**: Modular components for arXiv, LLM, RAG, vector DB, chat management
- **Usage**: Imported by scripts, not run directly

### `data/` - Data Storage
- **`data/vector_db/`**: ChromaDB vector database files
- **`data/chat_history/`**: JSON files of saved chat sessions
- **`data/models/`**: Cached sentence transformer models
- **`data/reports/`**: Test reports, metrics, and analysis results

### `scripts/` - Executable Scripts
- **Purpose**: Main entry points for running the RAG system
- **Files**: Demo scripts, test scripts, GUI applications
- **Usage**: Run directly with `python3 script_name.py`

### `docs/` - Documentation
- **Purpose**: All project documentation and summaries
- **Files**: README, guides, summaries, structure documentation

## 🎯 Key Benefits of This Organization

### 1. **Separation of Concerns**
- Core logic (`src/`) separate from executables (`scripts/`)
- Data storage (`data/`) separate from code
- Documentation (`docs/`) centralized

### 2. **Clean Workspace**
- No clutter in root directory
- Logical grouping of related files
- Easy to find what you need

### 3. **Scalability**
- Easy to add new components to `src/`
- Easy to add new scripts to `scripts/`
- Data grows in organized `data/` subdirectories

### 4. **Maintenance**
- Clear where to put new files
- Easy to backup data separately from code
- Documentation stays organized

## 🚀 Quick Start Commands

### Run Main Demo
```bash
python3 scripts/demo_pipeline.py --topic "your topic" --max-papers 12
```

### Run Targeted Test
```bash
python3 scripts/targeted_rag_test.py --topic "neural networks" --max-papers 12
```

### View Chat Histories
```bash
python3 scripts/chat_viewer_gui.py
```

### Generate Test Summary
```bash
python3 scripts/generate_test_summary.py
```

## 📊 Data Flow

1. **ArXiv Papers** → `data/vector_db/` (via ChromaDB)
2. **Chat Sessions** → `data/chat_history/` (JSON files)
3. **Model Cache** → `data/models/` (sentence transformers)
4. **Test Reports** → `data/reports/` (metrics and analysis)

## 🧹 Maintenance

### Adding New Components
- **Core logic**: Add to `src/`
- **New scripts**: Add to `scripts/`
- **Documentation**: Add to `docs/`

### Data Management
- **Vector DBs**: Automatically stored in `data/vector_db/`
- **Chat histories**: Automatically saved to `data/chat_history/`
- **Reports**: Generated in `data/reports/`

This organization makes the project professional, maintainable, and easy to understand! 🎯
