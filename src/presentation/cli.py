import typer
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from rich.console import Console

from src.application.session_manager import SessionManager

app = typer.Typer(help="Alethe - Context-Aware Offline AI CLI")
console = Console()


@app.command()
def chat(
    ctx: typer.Context,
    model: str = typer.Option(
        "ollama", "--model", "-m", help="Set the active LLM provider"
    ),
):
    # Retrieve injected Application Service
    session_manager: SessionManager = ctx.obj
    session_manager.switch_model(model)

    console.print(
        f"[bold green]Session initialized.[/bold green] Active model: [bold cyan]{session_manager.state.active_model}[/bold cyan]"
    )
    console.print(
        "Type [bold yellow]/switch <model>[/bold yellow] to change providers or [bold red]/exit[/bold red] to quit.\n"
    )

    prompt_session = PromptSession(history=FileHistory(".cli_history"))

    while True:
        try:
            # Use domain state for active model display
            user_input = prompt_session.prompt(
                f"User ({session_manager.state.active_model}) > "
            )

            if not user_input.strip():
                continue

            command = user_input.strip().lower()
            if command in ["/exit", "/quit"]:
                console.print("[bold red]Terminating session...[/bold red]")
                break

            if command.startswith("/switch"):
                parts = command.split()
                if len(parts) > 1:
                    session_manager.switch_model(parts[1])
                    console.print(
                        f"[bold green]Switched active model to:[/bold green] [bold cyan]{session_manager.state.active_model}[/bold cyan]"
                    )
                else:
                    console.print(
                        "[bold red]Please specify a model. Usage: /switch <model>[/bold red]"
                    )
                continue

            console.print(
                f"[italic dim]System: Routing prompt to {session_manager.state.active_model}...[/italic dim]"
            )

            # Delegate all processing to the Application Service
            response = session_manager.process_input(user_input)
            console.print(f"{response}\n")

        except (KeyboardInterrupt, EOFError):
            console.print(
                "\n[bold red]Session terminated by user. Exiting... [/bold red]"
            )
            break
