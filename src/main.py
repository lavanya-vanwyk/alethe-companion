import typer
from src.presentation.cli import app as cli_app
from src.application.session_manager import SessionManager
from src.infrastructure.redis_vault import RedisTokenVault

def main():
    
    # Instantiate valut
    redis_vault = RedisTokenVault()
    session_manager = SessionManager(default_model="ollama")
    
    # pass dependencies into the CLI via Typer's context object
    cli_app(obj=session_manager)

if __name__ == "__main__":
    main()