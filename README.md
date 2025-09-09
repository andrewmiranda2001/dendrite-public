# Dendrite 🧠

**Intelligent memory architecture for AI that understands psychology, not just keywords.**

Dendrite creates AI systems with genuine memory - tracking psychological patterns, relationship dynamics, and behavioral insights across conversations. Instead of simple vector search, it builds interconnected knowledge graphs that mirror how human memory actually works.

## 🎯 The Problem

Current AI memory is fundamentally broken:
- **Shallow retrieval**: Vector similarity misses psychological connections
- **No learning**: Can't identify patterns in your behavior over time  
- **Context gaps**: Work stress doesn't connect to relationship patterns
- **Static knowledge**: Just glorified search over chat logs

## 🧩 The Architecture

### Three-Layer Memory System

**🔮 Conceptual Layer**: Psychological patterns and behavioral frameworks that explain *why* things happen

**🏗️ Concrete Layer**: Specific people, places, events, and conversations from your life

**⏰ Temporal Layer**: Session summaries with intelligent cross-references linking moments to insights

### The Magic: Cross-Layer Intelligence
When you mention relationship anxiety, Dendrite connects:
- **Concrete**: Previous conversations about this person
- **Conceptual**: Your attachment patterns and triggers  
- **Temporal**: What helped last time you felt this way

## 🔧 Technical Innovation

### Asymmetric Retrieval
- **Concrete side**: Proximity-weighted embeddings with spatial decay
- **Conceptual side**: Model-driven psychological reasoning
- **Cross-database bridges**: Semantic pathways through psychological understanding

### Intelligent Writing
Models create psychological insights, not conversation dumps:
- **Pattern recognition**: Identifies recurring behavioral themes
- **Strategic categorization**: Builds psychological frameworks automatically
- **Cross-reference creation**: Links insights across life domains

### Technical Stack
- **MCP Integration**: Modular tools for different AI providers
- **Provider Agnostic**: OpenAI, Anthropic, others via simple config
- **Git-Style Tracking**: Visual diff system for all memory changes
- **Efficient Storage**: SQLite + embeddings for fast proximity computation

## 🚀 Current Status (MVP)

**~2,000 lines of clean, modular code**:
- ✅ Three-layer database architecture with cross-references
- ✅ Git-style interface with change tracking
- ✅ MCP tool system for write operations
- ✅ Provider-agnostic client architecture
- 🔄 Proximity-weighted embedding system
- 🔄 CLI interface (targeting 5,000 total lines)

## 🎯 Next Steps

**Phase 1: Core System**
- Complete embedding implementation for concrete layer
- Fine-tuned head placement model (4-5 node selection)
- Working CLI with conversation processing

**Phase 2: Intelligence**
- Specialized conceptual navigation model
- Advanced psychological pattern recognition
- Recency bias and temporal optimization

**Phase 3: Production**
- Web interface for anyone to be able test out Dendrite!

## 💡 Why This Matters

As AI becomes personal, memory architecture becomes critical. Current systems feel like talking to someone with amnesia - they can't learn your patterns or grow with you.

Dendrite enables AI that actually *knows* you:
- **Therapeutic applications**: Understanding triggers and coping mechanisms
- **Personal growth tracking**: Psychological development over time  
- **Relationship insights**: Patterns across all your connections
- **Contextual wisdom**: Advice based on your psychological profile

## 🛠️ Getting Started

```bash
# Install
pip install -e .

# Configure
export CONFIG_PATH=./config.json
export CONFIG=openai_write
export DB_ROOT=./dendrite/db/storage

# Run write pass
python -c "from dendrite.utils.config import run_write_pass; run_write_pass('./dendrite/data/prompts/write/relationships.json')"
```
# Note: This is an early-stage research prototype. 
# The core architecture is functional but not yet production-ready.

## 🔬 Beyond Current Solutions

**vs. mem0**: Psychological modeling instead of entity extraction  
**vs. LangChain**: Structured insights, not conversation logs  
**vs. Vector DBs**: Semantic pathways through psychological understanding  
**vs. Knowledge Graphs**: Single-person psychological ecosystem

## 📈 Vision

The future of AI is personalization through psychological understanding. Dendrite provides the memory architecture to make truly personal AI possible - systems that learn, adapt, and provide meaningful support based on deep understanding of who you are.
