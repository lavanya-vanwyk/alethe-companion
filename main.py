# import typer
# from rich.console import Console
# from prompt_toolkit import PromptSession
# from prompt_toolkit.history import FileHistory

# app = typer.Typer(help="Alethe - Offline AI CLI")
# console = Console()


# @app.command()
# def chat(
#     model: str = typer.Option(
#         "ollama",
#         "--model",
#         "-m",
#         help="Set the active LLM provider (e.g., ollama, gpt, claude, gemini)",
#     )
# ):
#     """
#     Starts the interactive chat session, maintaining the prompt loop.
#     """
#     console.print(
#         f"[bold green]Session initialized.[/bold green] Active model: [bold cyan]{model}[/bold cyan]"
#     )
#     console.print(
#         "Type [bold yellow]/switch <model>[/bold yellow] to change providers or [bold red]/exit[/bold red] to quit.\n"
#     )

#     active_model = model
#     session = PromptSession(history=FileHistory(".cli_history"))

#     while True:
#         try:
#             user_input = session.ask(f"[bold blue]User ({active_model})[/bold blue]")

#             if not user_input.strip():
#                 continue

#             if user_input.strip().lower() in ["/exit", "/quit"]:
#                 console.print("[bold red]Terminating session...[/bold red]")
#                 break

#             if user_input.strip().lower().startswith("/switch"):
#                 parts = user_input.split()
#                 if len(parts) > 1:
#                     active_model = parts[1]
#                     console.print(
#                         f"[bold green]Switched active model to:[/bold green] [bold cyan]{active_model}[/bold cyan]"
#                     )
#                 else:
#                     console.print(
#                         "[bold red]Please specify a model. Usage: /switch <model>[/bold red]"
#                     )
#                 continue

#             console.print(f"[italic dim]System: Routing prompt to {active_model}...\n")

#         except (KeyboardInterrupt, EOFError):
#             console.print(
#                 "\n[bold red]Session terminated by user. Exiting... [/bold red]"
#             )
#             break


# if __name__ == "__main__":
#     app()
