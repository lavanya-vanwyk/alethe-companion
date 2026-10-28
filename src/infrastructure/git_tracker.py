import subprocess
from collections import defaultdict
from typing import Dict, List, Optional
from tree_sitter import Language, Parser, Node
import tree_sitter_python

from src.domain.ports import GitTrackerPort
from src.domain.entities import CodeChangeDelta

class ASTGitTracker(GitTrackerPort):
    """Infrastructure implementation for version control and AST monitoring."""

    def __init__(self):
        self.py_language = Language(tree_sitter_python.language())
        self.parser = Parser(self.py_language)

    def _get_changed_lines(self) -> Dict[str, List[int]]:
        """Executes git diff and extracts modified lines per file."""
        
        # Fetches changes currently staged in git
        result = subprocess.run(["git", "diff", "--cached", "-U0"], capture_output=True, text=True)
        changes = defaultdict(list)
        current_file = None
        
        for line in result.stdout.splitlines():
            if line.startswith("+++ b/"):
                current_file = line[6:]
            elif line.startswith("@@"):
                parts = line.split(" ")
                try:
                    # Extract the starting line number from the diff chunk
                    start_line = int(parts[2].split(",")[0].replace("+", ""))
                    changes[current_file].append(start_line)
                except (IndexError, ValueError):
                    continue
                    
        return dict(changes)

    def _find_enclosing_node(self, node: Node, line_number: int, target_types=("function_definition", "class_definition")) -> Optional[Node]:
        """Recursively traverses the AST to find the structural boundary enclosing a line[cite: 1]."""
        enclosing = None
        
        # tree-sitter uses 0-indexed rows; adjust from 1-indexed git lines
        row = line_number - 1 
        
        if node.start_point[0] <= row <= node.end_point[0]:
            if node.type in target_types:
                enclosing = node
            for child in node.children:
                child_enclosing = self._find_enclosing_node(child, line_number, target_types)
                if child_enclosing:
                    enclosing = child_enclosing
        return enclosing

    def get_structural_diffs(self) -> List[CodeChangeDelta]:
        """Satisfies the GitTrackerPort, converting raw diffs to AST summaries."""
        changed_files = self._get_changed_lines()
        deltas = []

        for file_path, lines in changed_files.items():
            
            #(MVP) restrict AST parsing to Python files
            if not file_path.endswith(".py"):
                continue
                
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    source_code = f.read()
            except FileNotFoundError:
                continue

            tree = self.parser.parse(bytes(source_code, "utf8"))
            root_node = tree.root_node
            
            affected_structures = set()
            for line in lines:
                enclosing = self._find_enclosing_node(root_node, line)
                if enclosing:
                    
                    # Extract the identifier of the function/class
                    node_name = "unknown"
                    for child in enclosing.children:
                        if child.type == "identifier":
                            node_name = child.text.decode("utf8")
                            break
                    affected_structures.add(f"{enclosing.type.replace('_', ' ').title()}: '{node_name}'")

            # Semantic summary
            summary = "Modified at root scope/imports."
            if affected_structures:
                summary = "Modified structures: " + ", ".join(affected_structures)

            # Return Domain entities
            deltas.append(CodeChangeDelta(
                file_path=file_path,
                changed_lines=lines,
                structural_summary=summary
            ))

        return deltas