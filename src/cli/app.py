import argparse
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from src.core.agent import AgentRouter
from src.knowledge.vector_store import VectorStore
from src.knowledge.graph_store import GraphStore
from src.ingest.extractor import GraphExtractor
from src.memory.semantic import SemanticMemory
from src.memory.episodic import EpisodicMemory

console = Console()

class CLIApp:
    def __init__(self):
        self.vector_store = VectorStore()
        self.graph_store = GraphStore()
        self.semantic_memory = SemanticMemory()
        self.episodic_memory = EpisodicMemory()
        self.agent = AgentRouter(
            self.vector_store,
            self.graph_store,
            self.semantic_memory,
            self.episodic_memory
        )

    def print_banner(self):
        banner_text = "[bold blue]CyberSamantha - Your Cyber Second Brain[/bold blue]"
        console.print(Panel(banner_text, expand=False))

    def interactive_chat(self):
        self.print_banner()
        console.print("[yellow]Type /help for commands, or 'quit' to exit.[/yellow]\n")

        while True:
            try:
                question = console.input("[bold green]You:[/bold green] ").strip()
                if not question:
                    continue
                
                if question.lower() in ['quit', 'exit', 'q']:
                    console.print("[blue]Goodbye![/blue]")
                    break
                
                if question.startswith('/help'):
                    console.print("Commands:")
                    console.print("  [cyan]/wiki <topic>[/cyan] - Get a knowledge graph wiki summary")
                    console.print("  [cyan]search <query>[/cyan] - Web search for threat intel")
                    console.print("  [cyan]run <command>[/cyan] - Execute safe terminal command")
                    console.print("  [cyan]read <file>[/cyan] - Read local file")
                    console.print("  [cyan]think[/cyan] - Show chain-of-thought reasoning")
                    console.print("  [cyan]remember that <fact>[/cyan] - Teach the assistant a fact")
                    console.print("  [cyan]quit[/cyan] - Exit")
                    continue
                
                show_thoughts = question.lower() == "think"
                if show_thoughts:
                    question = self.episodic_memory.get_history_string().split("\n")[-1] if self.episodic_memory.get_history_string() else ""
                    if not question:
                        console.print("[yellow]No previous question to show thoughts for.[/yellow]")
                        continue
                    answer = self.agent.query(question, show_thoughts=True)
                    console.print("\n[bold purple]Samantha:[/bold purple]")
                    console.print(Markdown(answer))
                    console.print("-" * 50)
                    continue
                
                mode = "auto"
                if question.startswith('/wiki '):
                    mode = "wiki"
                    question = question[6:].strip()

                console.print("[dim]Thinking...[/dim]")
                answer = self.agent.query(question, mode=mode)
                
                console.print("\n[bold purple]Samantha:[/bold purple]")
                console.print(Markdown(answer))
                console.print("-" * 50)
                
            except KeyboardInterrupt:
                console.print("\n[blue]Goodbye![/blue]")
                break
            except Exception as e:
                console.print(f"[bold red]Error:[/bold red] {str(e)}")

    def run(self):
        parser = argparse.ArgumentParser(description="CyberSamantha Second Brain")
        parser.add_argument("--index", action="store_true", help="Index documents")
        parser.add_argument("--force", action="store_true", help="Force reindex")
        parser.add_argument("--question", type=str, help="Ask a question")
        
        args = parser.parse_args()

        if args.index or args.force:
            console.print("[yellow]Starting index and graph extraction...[/yellow]")
            extractor = GraphExtractor(self.graph_store)
            self.vector_store.index_documents(
                force_reindex=args.force, 
                extraction_callback=extractor.extract_from_text
            )
            
        if args.question:
            answer = self.agent.query(args.question)
            console.print(Markdown(answer))
        elif not args.index:
            self.interactive_chat()

if __name__ == "__main__":
    app = CLIApp()
    app.run()
