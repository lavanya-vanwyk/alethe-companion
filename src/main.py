import typer
from src.presentation.cli import app as cli_app
from src.application.session_manager import SessionManager

def main():
    
    session_manager = SessionManager(default_model="ollama")
    
    # pass dependencies into the CLI via Typer's context object
    cli_app(obj=session_manager)

if __name__ == "__main__":
    main()