import argparse
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table

from src.core.agent import AgentRouter
from src.core.llm_provider import LLMProvider
from src.knowledge.vector_store import VectorStore
from src.knowledge.reality_graph import RealityGraph
from src.ingest.extractor import GraphExtractor
from src.ingest.daemon import IngestionDaemon
from src.memory.semantic import SemanticMemory
from src.memory.episodic import EpisodicMemory
from src.memory.meta_memory import MetaMemory
from src.skills.genome_engine import GenomeEngine
from src.core.thought_router import ThoughtRouter
from src.core.curiosity_daemon import CuriosityDaemon
from src.skills.loader import SkillLoader
from src.agents.base import BaseAgent

console = Console()

class CLIApp:
    def __init__(self):
        self.vector_store = VectorStore()
        self.graph_store = RealityGraph()
        self.semantic_memory = SemanticMemory()
        self.episodic_memory = EpisodicMemory()
        self.meta_memory = MetaMemory()
        self.genome_engine = GenomeEngine()
        self.thought_router = ThoughtRouter(meta_memory=self.meta_memory)
        self.agent = AgentRouter(
            self.vector_store,
            self.graph_store,
            self.semantic_memory,
            self.episodic_memory,
            self.meta_memory,
            self.thought_router
        )
        
        self.curiosity_daemon = CuriosityDaemon(reality_graph=self.graph_store, agent_router=self.agent)
        # Background ingestion daemon (shares stores with the agent)
        self.daemon = IngestionDaemon(
            vector_store=self.vector_store,
            graph_store=self.graph_store,
            on_ingest=self._on_file_ingested,
        )

    def _on_file_ingested(self, file_path: str, chunk_count: int):
        """Callback when the daemon auto-ingests a new file."""
        import os
        fname = os.path.basename(file_path)
        console.print(f"\n[bold green]📥 Auto-ingested:[/bold green] {fname} ({chunk_count} chunks)")

    def print_banner(self):
        ascii_art = r"""                                       
 ▄▄▄▄  ▄▄▄  ▄▄   ▄▄  ▄▄▄  ▄▄  ▄▄ ▄▄▄▄▄▄ ▄▄ ▄▄  ▄▄▄  
███▄▄ ██▀██ ██▀▄▀██ ██▀██ ███▄██   ██   ██▄██ ██▀██ 
▄▄██▀ ██▀██ ██   ██ ██▀██ ██ ▀██   ██   ██ ██ ██▀██ 
                                                    
        """
        llm_status = self.agent.llm.provider_name
        banner_text = (
            f"[bold cyan]{ascii_art}[/bold cyan]\n\n"
            "[bold blue]CyberSamantha — Your Cyber Second Brain[/bold blue]\n"
            f"[dim]LLM: {llm_status}[/dim]"
        )
        console.print(Panel(banner_text, expand=False))

    def _print_status(self):
        """Print system status table."""
        table = Table(title="System Status", show_header=True, header_style="bold cyan")
        table.add_column("Component", style="bold")
        table.add_column("Status")

        # LLM Provider
        llm_info = self.agent.llm.get_status()
        table.add_row("LLM Provider", llm_info["display_name"])

        # Vector Store
        try:
            stats = self.vector_store.get_stats()
            table.add_row("Vector Store", f"✅ {stats.get('total_chunks', 0)} chunks indexed")
        except Exception:
            table.add_row("Vector Store", "❌ Error")

        # Graph Store
        node_count = len(self.graph_store.graph.nodes())
        edge_count = len(self.graph_store.graph.edges())
        table.add_row("Knowledge Graph", f"✅ {node_count} entities, {edge_count} relationships")

        # Semantic Memory
        fact_count = len(self.semantic_memory.get_all_facts())
        table.add_row("Semantic Memory", f"✅ {fact_count} facts stored")

        # Episodic Memory
        hist_count = len(self.episodic_memory.history)
        table.add_row("Episodic Memory", f"✅ {hist_count} messages in session")

        # Daemon
        daemon_status = "🟢 Running" if self.daemon.is_running else "⚪ Stopped"
        table.add_row("Ingestion Daemon", f"{daemon_status} ({self.daemon.watch_dir})")

        # Skills
        skill_loader = BaseAgent.get_skill_loader()
        md_count = len(skill_loader.get_all_md_skills())
        py_count = len(skill_loader.get_all_py_skills())
        table.add_row("Skills", f"✅ {md_count} playbooks, {py_count} tool modules")

        console.print(table)

    def interactive_chat(self):
        self.print_banner()
        console.print("[yellow]Type /help for commands, or 'quit' to exit.[/yellow]\n")

        while True:
            try:
                question = console.input("[bold green]You:[/bold green] ").strip()
                if not question:
                    continue
                
                if question.lower() in ['quit', 'exit', 'q']:
                    self.daemon.stop()
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
                    console.print("  [cyan]/status[/cyan] - Show system status")
                    console.print("  [cyan]/daemon start[/cyan] - Start background file watcher")
                    console.print("  [cyan]/daemon stop[/cyan] - Stop background file watcher")
                    console.print("  [cyan]/daemon log[/cyan] - Show recent auto-ingested files")
                    console.print("  [cyan]/provider[/cyan] - Show active LLM provider info")
                    console.print("  [cyan]/skills[/cyan] - List all loaded skills")
                    console.print("  [cyan]/skills enable <name>[/cyan] - Enable a skill")
                    console.print("  [cyan]/skills disable <name>[/cyan] - Disable a skill")
                    console.print("  [cyan]quit[/cyan] - Exit")
                    continue

                # ── New commands ──────────────────────────────────────
                if question.startswith('/status'):
                    self._print_status()
                    continue

                if question.startswith('/provider'):
                    info = self.agent.llm.get_status()
                    console.print(Panel(
                        f"[bold]Provider:[/bold] {info['display_name']}\n"
                        f"[bold]Model:[/bold] {info['model']}\n"
                        f"[bold]Available:[/bold] {'✅ Yes' if info['available'] else '❌ No'}",
                        title="LLM Provider",
                        expand=False,
                    ))
                    continue

                if question.startswith('/daemon'):
                    parts = question.split()
                    sub = parts[1] if len(parts) > 1 else "start"

                    if sub == "start":
                        self.daemon.start()
                    elif sub == "stop":
                        self.daemon.stop()
                    elif sub == "log":
                        log = self.daemon.get_log()
                        if not log:
                            console.print("[dim]No files auto-ingested yet.[/dim]")
                        else:
                            for entry in log[-10:]:
                                console.print(f"  📄 {entry['file']} — {entry['chunks']} chunks @ {entry['timestamp']}")
                    else:
                        console.print("[yellow]Usage: /daemon start | stop | log[/yellow]")
                    continue

                if question.startswith('/skills'):
                    parts = question.split()
                    skill_loader = BaseAgent.get_skill_loader()

                    if len(parts) == 1:
                        # List all skills
                        summary = skill_loader.get_summary()
                        if not summary:
                            console.print("[dim]No skills found. Add .md files to the skills/ folder.[/dim]")
                        else:
                            table = Table(title="Loaded Skills", show_header=True, header_style="bold cyan")
                            table.add_column("Name", style="bold")
                            table.add_column("Type")
                            table.add_column("Agent")
                            table.add_column("Tags")
                            table.add_column("Status")
                            for s in summary:
                                status = "🟢" if s.get("enabled", True) else "⚪"
                                agent = s.get("agent", ", ".join(s.get("compatible_agents", ["all"])))
                                table.add_row(
                                    s["name"],
                                    s.get("type", "python"),
                                    str(agent),
                                    ", ".join(s.get("tags", [])),
                                    status,
                                )
                            console.print(table)
                    elif len(parts) >= 3 and parts[1] == "enable":
                        name = parts[2]
                        if skill_loader.enable(name):
                            console.print(f"[green]✅ Skill '{name}' enabled.[/green]")
                        else:
                            console.print(f"[red]Skill '{name}' not found.[/red]")
                    elif len(parts) >= 3 and parts[1] == "disable":
                        name = parts[2]
                        if skill_loader.disable(name):
                            console.print(f"[yellow]⚪ Skill '{name}' disabled.[/yellow]")
                        else:
                            console.print(f"[red]Skill '{name}' not found.[/red]")
                    else:
                        console.print("[yellow]Usage: /skills | /skills enable <name> | /skills disable <name>[/yellow]")
                    continue

                # ── Existing commands ─────────────────────────────────
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
                self.daemon.stop()
                console.print("\n[blue]Goodbye![/blue]")
                break
            except Exception as e:
                console.print(f"[bold red]Error:[/bold red] {str(e)}")

    def run(self):
        parser = argparse.ArgumentParser(description="CyberSamantha Second Brain")
        parser.add_argument("--index", action="store_true", help="Index documents")
        parser.add_argument("--force", action="store_true", help="Force reindex")
        parser.add_argument("--question", type=str, help="Ask a question")
        parser.add_argument("--daemon", action="store_true", help="Start background ingestion daemon")
        
        args = parser.parse_args()

        if args.index or args.force:
            console.print("[yellow]Starting index and graph extraction...[/yellow]")
            extractor = GraphExtractor(self.graph_store)
            self.vector_store.index_documents(
                force_reindex=args.force, 
                extraction_callback=extractor.extract_from_text
            )

        if args.daemon:
            self.daemon.ingest_existing()
            self.daemon.start()
            
        if args.question:
            answer = self.agent.query(args.question)
            console.print(Markdown(answer))
        elif not args.index:
            self.interactive_chat()

if __name__ == "__main__":
    app = CLIApp()
    app.run()
