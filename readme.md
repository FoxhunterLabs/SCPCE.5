________________________________________
SCPCE — Persistent Context Engine
A deterministic, auditable memory subsystem for long-running reasoning workflows.
________________________________________
🚧 Overview
SCPCE is a dependency-free Python engine that maintains reasoning continuity across sessions.
It stores compressed interaction frames, retrieves them using deterministic rules, and reconstructs a stable “reasoning state” for any project — without ML, embeddings, or probabilistic behavior.
Designed for autonomy, robotics, infra-tech, and operational engineering where reliability, traceability, and reproducibility matter.
________________________________________
✨ Features
Deterministic Memory Pipeline
•	Rule-based keyword extraction
•	Sentence deduplication + compression
•	Stable, predictable scoring
•	No randomness, no embeddings
Append-Only, Auditable Storage
•	JSONL memory log (./memory/context.jsonl)
•	Each frame is hash-verified for integrity
•	Optional snapshot generation
•	Automatic pruning (last 300 frames)
Structured Memory Types
•	SemanticMemory — concepts, definitions
•	ProceduralMemory — workflows, how-to logic
•	ProjectState — summary, constraints, tasks
•	Preferences — style, tone, user constraints
•	RecapFrame — timestamped interaction snapshot
Context Reconstruction
Builds a unified ContextBundle containing:
•	Project summary
•	Active workstream
•	User preferences
•	Known constraints
•	Recommended next steps
________________________________________
📁 Project Structure
SCPE/
│
├── app.py                     # SCPCE.5 enhanced CLI
│
└── pce/
    ├── __init__.py
    ├── api.py                 # Public interface
    ├── compression.py         # Deterministic text compressor
    ├── schema.py              # Dataclasses for structured memory
    ├── storage.py             # Append-only JSONL engine
    └── retrieval.py           # Rule-based search + reconstruction
________________________________________
🚀 Usage
Start CLI
python app.py
Save a new interaction
python app.py save
Enter user and assistant messages, ending each with . on its own line.
Load reconstructed state
python app.py load
Search memory
python app.py search <keyword>
Show recent frames
python app.py tail 5
Inspect a specific frame
python app.py frame 12
Verify integrity (hash validation)
python app.py verify
Create a deterministic snapshot
python app.py snapshot
Interactive shell
python app.py shell
________________________________________
🧠 How It Works
1. Interaction → RecapFrame
Messages are distilled into:
•	key topics
•	compressed intent + output
•	semantic + procedural notes
•	project-state hints
•	user preferences
•	integrity hash
2. Deterministic Compression
•	stopword removal
•	keyword frequencies
•	whitespace + sentence dedupe
•	max length enforcement
3. Append-Only Storage
Frames written as JSON objects, one per line.
Automatic pruning keeps the most recent 300.
4. Retrieval
Matches keywords deterministically and applies recency weighting.
Stable-sorted for reproducibility.
5. Reconstruction
Merges multiple frames into a consistent context bundle used for the next session.
________________________________________
🔒 Design Principles
•	Deterministic: same input → same output
•	Auditable: all memory readable as JSON
•	Reversible: snapshots and integrity checks
•	Small: pure stdlib, zero dependencies
•	Safe: write-blocks on corruption
SCPCE is not an AI memory gimmick — it is a reliability layer.
________________________________________
📦 Requirements
None.
requirements.txt intentionally empty.
________________________________________
📜 License
MIT 
________________________________________
