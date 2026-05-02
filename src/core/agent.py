import os
from typing import Dict, Any, Tuple, List
try:
    import google.generativeai as genai
except ImportError as e:
    print(f"Missing required package: {e}")

from src.knowledge.vector_store import VectorStore
from src.knowledge.graph_store import GraphStore
from src.memory.semantic import SemanticMemory
from src.memory.episodic import EpisodicMemory
from src.tools import WebSearchTool, TerminalTool, FileReaderTool
from src.tools.base import ToolResult

class AgentRouter:
    def __init__(self, vector_store: VectorStore, graph_store: GraphStore, 
                 semantic_memory: SemanticMemory, episodic_memory: EpisodicMemory):
        self.vector_store = vector_store
        self.graph_store = graph_store
        self.semantic_memory = semantic_memory
        self.episodic_memory = episodic_memory
        self.genai_model = None
        self.thought_chain: List[str] = []
        self.tools = {
            "web_search": WebSearchTool(),
            "terminal": TerminalTool(),
            "file_reader": FileReaderTool()
        }
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

    def query(self, question: str, mode: str = "auto", show_thoughts: bool = False) -> str:
        """
        Main entry point for agent queries.
        mode can be: "auto", "rag", "wiki", "web", "terminal", "file"
        """
        self.thought_chain = []
        self.episodic_memory.add_interaction("user", question)
        
        if question.lower().startswith("search ") or question.lower().startswith("web "):
            tool_name = "web_search"
            query = question[6:].strip() if question.lower().startswith("search ") else question[4:].strip()
            self._add_thought(f"Action: Searching web for '{query}'...")
            result = self.tools[tool_name].execute(query=query)
            self._add_thought(f"Result: Found {result.metadata.get('results_count', 0)} results")
            self.episodic_memory.add_interaction("assistant", result.output)
            return result.output
        
        if question.lower().startswith("run "):
            parts = question[4:].strip().split(" ", 1)
            cmd, args = parts[0], parts[1] if len(parts) > 1 else ""
            self._add_thought(f"Action: Executing terminal command '{cmd}'...")
            result = self.tools["terminal"].execute(command=cmd, args=args)
            self._add_thought(f"Result: Return code {result.metadata.get('return_code', 'N/A')}")
            self.episodic_memory.add_interaction("assistant", result.output)
            return result.output
        
        if question.lower().startswith("read "):
            file_path = question[5:].strip()
            self._add_thought(f"Action: Reading file '{file_path}'...")
            result = self.tools["file_reader"].execute(file_path=file_path)
            self._add_thought(f"Result: Read {result.metadata.get('lines', 0)} lines")
            self.episodic_memory.add_interaction("assistant", result.output)
            return result.output
        
        if mode == "web":
            self._add_thought("Action: Searching web...")
            result = self.tools["web_search"].execute(query=question)
            answer = result.output if result.success else result.error
        elif mode == "terminal":
            self._add_thought("Action: Executing terminal command...")
            answer = "Terminal mode requires 'run <command>' syntax"
        elif mode == "wiki":
            answer = self._handle_wiki_query(question)
        elif mode == "auto":
            answer = self._handle_auto_query(question)
        else:
            answer = self._handle_rag_query(question)
            
        self.episodic_memory.add_interaction("assistant", answer)
        
        if question.lower().startswith("remember that"):
            fact = question[13:].strip()
            self.semantic_memory.add_fact(f"fact_{len(self.semantic_memory.get_all_facts())}", fact)
        
        if show_thoughts:
            return "🧠 **Chain of Thought:**\n" + "\n".join(f"  → {t}" for t in self.thought_chain) + "\n\n" + answer
        
        return answer
    
    def _add_thought(self, thought: str):
        self.thought_chain.append(thought)

    def _handle_auto_query(self, question: str) -> str:
        """Autonomous mode that decides which tools to use and how to answer."""
        if self.genai_model is None:
            self._add_thought("Warning: No Gemini key, falling back to RAG.")
            return self._handle_rag_query(question)

        max_iterations = 5
        
        system_prompt = f"""You are CyberSamantha, an autonomous cybersecurity AI agent.
You have access to the following tools:
1. web_search: Search the web for recent information. Usage: Action: web_search\nAction Input: <query>
2. terminal: Run local shell commands. Usage: Action: terminal\nAction Input: <command>
3. file_reader: Read a local file. Usage: Action: file_reader\nAction Input: <path>
4. rag_query: Query the local vector knowledge base. Usage: Action: rag_query\nAction Input: <query>
5. wiki_query: Query the local knowledge graph. Usage: Action: wiki_query\nAction Input: <topic>

Use the following format:
Thought: you should always think about what to do
Action: the action to take, should be one of [web_search, terminal, file_reader, rag_query, wiki_query]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!
Question: {question}"""

        history = system_prompt
        
        for i in range(max_iterations):
            try:
                response = self.genai_model.generate_content(
                    history,
                    generation_config={{'temperature': 0.2, 'stop_sequences': ['Observation:']}}
                )
                response_text = response.text
                
                history += f"\n{response_text}"
                
                # Check for Final Answer
                if "Final Answer:" in response_text:
                    final_answer = response_text.split("Final Answer:", 1)[1].strip()
                    self._add_thought("Found final answer.")
                    return final_answer
                
                # Extract Action and Action Input
                action = None
                action_input = None
                
                for line in response_text.split('\n'):
                    if line.startswith("Thought:"):
                        self._add_thought(line[8:].strip())
                    elif line.startswith("Action:"):
                        action = line[7:].strip()
                    elif line.startswith("Action Input:"):
                        action_input = line[13:].strip()
                        
                if not action or not action_input:
                    # Model didn't format correctly
                    self._add_thought("Model failed to specify action. Ending loop.")
                    return response_text.replace("Final Answer:", "").strip()
                    
                self._add_thought(f"Action: {action}('{action_input}')")
                
                # Execute action
                observation = ""
                if action == "web_search":
                    res = self.tools["web_search"].execute(query=action_input)
                    observation = res.output if res.success else res.error
                elif action == "terminal":
                    res = self.tools["terminal"].execute(command=action_input)
                    observation = res.output if res.success else res.error
                elif action == "file_reader":
                    res = self.tools["file_reader"].execute(file_path=action_input)
                    observation = res.output if res.success else res.error
                elif action == "rag_query":
                    observation = self._handle_rag_query(action_input)
                elif action == "wiki_query":
                    observation = self._handle_wiki_query(action_input)
                else:
                    observation = f"Unknown action: {action}"
                    
                history += f"\nObservation: {observation}"
                self._add_thought(f"Observation completed ({len(observation)} chars)")
                
            except Exception as e:
                self._add_thought(f"Error during autonomous loop: {str(e)}")
                return f"Agent encountered an error: {str(e)}"
                
        return "Agent reached maximum iterations without finding a final answer."

    def _handle_rag_query(self, question: str) -> str:
        search_results = self.vector_store.search(question, n_results=5)
        
        if not search_results:
            return "Error: No relevant information found in the knowledge base."
            
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
            return f"Error generating AI response: {str(e)}"

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
            return f"Error generating Wiki response: {str(e)}"
