import os
from typing import Dict, Any, Tuple
try:
    import google.generativeai as genai
except ImportError as e:
    print(f"❌ Missing required package: {e}")

from src.knowledge.vector_store import VectorStore
from src.knowledge.graph_store import GraphStore
from src.memory.semantic import SemanticMemory
from src.memory.episodic import EpisodicMemory

class AgentRouter:
    def __init__(self, vector_store: VectorStore, graph_store: GraphStore, 
                 semantic_memory: SemanticMemory, episodic_memory: EpisodicMemory):
        self.vector_store = vector_store
        self.graph_store = graph_store
        self.semantic_memory = semantic_memory
        self.episodic_memory = episodic_memory
        self.genai_model = None
        self._setup_gemini()

    def _setup_gemini(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("⚠️  GEMINI_API_KEY not found - running in embedding-only mode")
            return
            
        try:
            genai.configure(api_key=api_key)
            self.genai_model = genai.GenerativeModel('gemini-2.0-flash')
        except Exception as e:
            print(f"⚠️  Failed to configure Gemini API: {e}")

    def query(self, question: str, mode: str = "auto") -> str:
        """
        Main entry point for agent queries.
        mode can be: "auto", "rag", "wiki"
        """
        self.episodic_memory.add_interaction("user", question)
        
        # In 'auto' mode, a full implementation would use an LLM call to classify the intent.
        # For simplicity and speed, we will route based on the mode provided or default to RAG.
        if mode == "wiki":
            answer = self._handle_wiki_query(question)
        else:
            answer = self._handle_rag_query(question)
            
        self.episodic_memory.add_interaction("assistant", answer)
        
        # Opportunistic memory update (extracting simple facts from user statements)
        if question.lower().startswith("remember that"):
            fact = question[13:].strip()
            # Simplistic key generation
            self.semantic_memory.add_fact(f"fact_{len(self.semantic_memory.get_all_facts())}", fact)
            
        return answer

    def _handle_rag_query(self, question: str) -> str:
        search_results = self.vector_store.search(question, n_results=5)
        
        if not search_results:
            return "❌ No relevant information found in the knowledge base."
            
        context_parts = []
        sources = []
        for i, result in enumerate(search_results, 1):
            source_file = result["metadata"]["file_path"]
            relevance = result['score']
            context_parts.append(f"[Document {i}: {source_file}]\n{result['content']}")
            sources.append(f"  {i}. {source_file} (relevance: {relevance:.2%})")
            
        context = "\n\n".join(context_parts)
        
        if self.genai_model is None:
            return "🤖 Answer Generation Disabled (No Gemini Key). Sources found:\n" + "\n".join(sources)
            
        prompt = f"""Based on the cybersecurity documentation and conversation history, answer the question accurately.

CONVERSATION HISTORY:
{self.episodic_memory.get_history_string()}

CONTEXT:
{context}

USER FACTS:
{self.semantic_memory.get_all_facts()}

QUESTION: {question}

Provide a clear, actionable answer based strictly on the context."""

        try:
            response = self.genai_model.generate_content(
                prompt,
                generation_config={'temperature': 0.7, 'max_output_tokens': 1024}
            )
            return response.text + "\n\n📚 **Sources:**\n" + "\n".join(sources)
        except Exception as e:
            return f"❌ Error generating AI response: {str(e)}"

    def _handle_wiki_query(self, topic: str) -> str:
        """Query knowledge graph and generate a wiki-style summary"""
        entities = self.graph_store.search_entities(topic)
        if not entities:
            # Fallback to RAG if not found in graph
            return self._handle_rag_query(topic)
            
        context_data = self.graph_store.get_entity_context(entities[0], depth=2)
        
        if self.genai_model is None:
            return f"Found entity in graph: {entities[0]}"
            
        prompt = f"""You are a cybersecurity wiki system. Generate a comprehensive summary about the following topic based on the knowledge graph data provided.
        
TOPIC: {topic}
GRAPH DATA:
{context_data}

Provide a structured, markdown-formatted wiki page."""

        try:
            response = self.genai_model.generate_content(
                prompt,
                generation_config={'temperature': 0.2, 'max_output_tokens': 2048}
            )
            return response.text
        except Exception as e:
            return f"❌ Error generating Wiki response: {str(e)}"
