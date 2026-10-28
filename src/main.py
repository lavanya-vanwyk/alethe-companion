from src.application.pii_gateway import PIIGateway
from src.application.session_manager import SessionManager
from src.infrastructure.git_tracker import ASTGitTracker
from src.infrastructure.redis_vault import RedisTokenVault
from src.presentation.cli import app as cli_app


def main():

    # Instantiate services
    git_tracker = ASTGitTracker()
    redis_vault = RedisTokenVault()
    pii_gateway = PIIGateway(vault=redis_vault)

    session_manager = SessionManager(
        pii_gateway=pii_gateway, git_tracker=git_tracker, default_model="ollama"
    )

    # pass dependencies into the CLI via Typer's context object
    cli_app(obj=session_manager)


if __name__ == "__main__":
    main()
