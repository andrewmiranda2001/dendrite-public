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

**Concrete/Temporal System**:  Uses model-controlled semantic chunking to extract targeted conversation segments as input embeddings for graph traversal from intelligently placed search heads. Traversal decisions are made using semantic similarity scores between the input embedding and proximity-weighted embeddings of neighboring nodes, or direct embeddings of notes at the current node. Instead of noisy full-conversation vectors or arbitrary chunking, the system gets precise queries like "mom's criticism about career choices" directed to specific knowledge domains.

**Conceptual System**: Employs fine-tuned models for all traversal decisions to ensure psychological subtext and emotional patterns drive navigation rather than surface-level keyword matching. This system understands that "I'm fine" might signal distress based on conversational context and historical patterns.

**The Intersection Magic**: When both retrieval systems converge on related psychological territory - concrete events that exemplify conceptual patterns - the system provides rich, multi-layered context. A current work stress discussion connects to specific past conversations (concrete) while simultaneously surfacing underlying perfectionism patterns (conceptual), creating genuinely insightful dialogue.

This dual-system approach solves traditional RAG's fundamental limitation: the inability to understand subtextual connections that aren't semantically obvious. The retrieval magic happens at the convergence points where lived experience meets psychological insight.

### Sequential Write Passes
**Two-Phase Architecture**: Writing and tying are separate passes with distinct system prompts and MCP tools.

**Phase 1 - Writing**: 
- **Conceptual Writer**: Creates psychological frameworks with internal node references only
- **Concrete Writer**: Documents specific people, places, and events with internal node references
- **Temporal Summarizer**: Generates session summaries with temporal node reference to the session time

**Phase 2 - Tie Consolidation**:
- **Concrete Tie Consolidator**: Creates note-to-note connections between concrete and conceptual notes
- **Temporal Tie Consolidator**: Adds node-to-note temporal node tags to concrete notes from the session

**Git-Style Change Tracking**: Models see granular edit history through diff visualization - which nodes were added/modified, note content changes, reference updates - enabling contextual understanding of session evolution without cognitive overload.

This separation ensures clean cognitive focus - writers concentrate on their domain expertise without cross-database complexity, then specialized tie consolidators create the cross-layer connections that enable intersection magic during retrieval.

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

## 🔬 Beyond Current Solutions

**vs. mem0**: Psychological modeling instead of entity extraction  
**vs. LangChain**: Structured insights, not conversation logs  
**vs. Vector DBs**: Semantic pathways through psychological understanding  
**vs. Knowledge Graphs**: Single-person psychological ecosystem

## 📈 Vision

The future of AI is personalization through psychological understanding. Dendrite provides the memory architecture to make truly personal AI possible - systems that learn, adapt, and provide meaningful support based on deep understanding of who you are.
