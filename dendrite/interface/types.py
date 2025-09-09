from pydantic import BaseModel
from typing import List
from enum import Enum
from dendrite.db.io import DatabaseType
from dendrite.utils.constants import TAB

class GitStatus(str, Enum):
    STAGED = "staged"           # Loaded from DB (committed)
    ADDED = "added"             # New this session
    MODIFIED = "modified"       # Changed this session

class ContentStatus(str, Enum):
    STAGED = "staged"           # Original content from DB
    ADDED = "added"             # New content added this session
    DELETED = "deleted"         # Content removed this session

class Content(BaseModel):
    text: str
    status: ContentStatus = ContentStatus.STAGED
    
    def to_interface_lines(self, indent: str = "") -> List[str]:
        prefix = "+" if self.status == ContentStatus.ADDED else " "
        lines = []
        for i, line in enumerate(self.text.split('\n')):
            lines.append(f"{indent}{i + 1}: {prefix} {line}")
        return lines

class Note:
    def __init__(
        self,
        #db_type: DatabaseType, TODO: get rid of all references to db_type since notes can now exist in multiple dbs
        id: int,
        read_only: bool,
        name: str,
        content: List[Content],
        node_references: List['Node'],
        note_references: List['Note'],
        status: GitStatus = GitStatus.STAGED,
    ):
        self.id = id
        self.read_only = read_only
        self.name = name
        self.content = content
        self.node_references = node_references
        self.note_references = note_references
        self.status = status
        self.original_name = name
        self.og_note_references = [node.name for node in self.node_references]
        self.og_node_references = [note.name for note in self.note_references]

    def add_content(self, text: str):
        if self.status == GitStatus.STAGED:
            self.status = GitStatus.MODIFIED
        self.content.append(Content(text=text, status=ContentStatus.ADDED))
    
    def change_name(self, new_name: str):
        if self.status == GitStatus.STAGED:
            self.status = GitStatus.MODIFIED
        self.name = new_name
    
    def change_references(self, new_references: List[str]):
        if self.status == GitStatus.STAGED:
            self.status = GitStatus.MODIFIED
        self.node_references = new_references

    def to_interface_string(self, indent: str = "", tie_interface: bool = False) -> str:
        status_prefix = {
            GitStatus.STAGED: " ",
            GitStatus.ADDED: "+",
            GitStatus.MODIFIED: "~",
        }[self.status]
        
        lines = []
        
        lines.append(f"{indent}{status_prefix} <note id=\"{self.id}\" name=\"{self.name}\">")
        suffix = f"{indent}{status_prefix} </note>"


        content = [content.to_interface_lines(indent + TAB) for content in self.content]
        if not self.status == GitStatus.MODIFIED:
            return "\n".join(lines + content + [suffix])

        
        if self.original_name != self.name:
            lines.append(f"{indent}  {'-' if not tie_interface else ''} name: {self.original_name}")
            lines.append(f"{indent}  {'+' if not tie_interface else ''} name: {self.name}")


        lines.extend(self._ref_comparison_string(self.og_note_references, [node.name for node in self.node_references], indent))
        if tie_interface:
            lines.extend(self._ref_comparison_string(self.og_node_references, [note.name for note in self.note_references], indent))

        lines.append(suffix)
        return "\n".join(lines)

    def _ref_comparison_string(self, og: list[str], current: list[str], indent: str = "") -> list[str]:
        if og == current:
            return [f'{indent}  - refs: {og}']
        lines = []
        for ref in og:
            if ref not in current:
                lines.append(f"{indent}  - ref: {ref}")
        for ref in current:
            if ref not in og:
                lines.append(f"{indent}  + ref: {ref}")
            lines.append(f"{indent}    ref: {ref}")
        return lines

    def to_storage_string(self) -> str:
        from dendrite.interface.utils.diff import content_list_to_storage_string
        return content_list_to_storage_string(self.content)

class Node(BaseModel):
    
    def __init__(self,
                 db_type: str,
                 name: str,
                 notes: List[Note],
                 children: List["Node"],
                 status: GitStatus = GitStatus.STAGED
        ):
        self.db_type = db_type
        self.name = name
        self.notes = notes
        self.children = children
        self.status = status
        self.original_name = self.name
    
    def change_name(self, new_name: str):
        """Change node name"""
        if self.status == GitStatus.STAGED:
            self.status = GitStatus.MODIFIED
        self.name = new_name

    def to_interface_string(self, indent: str = "", show_notes_summary: bool = True) -> str:
        """Return git-style diff for interface display"""
        status_prefix = {
            GitStatus.STAGED: " ",
            GitStatus.ADDED: "+", 
            GitStatus.MODIFIED: "~",
        }[self.status]
        
        lines = []
        
        # Node header with name change if applicable
        if self.status == GitStatus.MODIFIED and self.original_name != self.name:
            lines.append(f"{indent}~ <node name=\"{self.name}\" original=\"{self.original_name}\">")
        else:
            lines.append(f"{indent}{status_prefix} <node name=\"{self.name}\">")
        
        # Show child nodes recursively (for schema section)
        for child in self.children:
            lines.append(child.to_interface_string(indent + "  ", show_notes_summary=False))
        
        lines.append(f"{indent}{status_prefix} </node>")
        return "\n".join(lines)
    
    def to_current_node_string(self, indent: str = "") -> str:
        """Return detailed view of current node with notes and immediate children"""
        status_prefix = {
            GitStatus.STAGED: " ",
            GitStatus.ADDED: "+", 
            GitStatus.MODIFIED: "~",
        }[self.status]
        
        lines = []
        
        # Node header
        if self.status == GitStatus.MODIFIED and self.original_name != self.name:
            lines.append(f"{indent}~ <node name=\"{self.name}\" original=\"{self.original_name}\">")
        else:
            lines.append(f"{indent}{status_prefix} <node name=\"{self.name}\">")
        
        # Show immediate child nodes (collapsed)
        for child in self.children:
            child_prefix = {
                GitStatus.STAGED: " ",
                GitStatus.ADDED: "+",
                GitStatus.MODIFIED: "~",
            }[child.status]
            
            if child.status == GitStatus.MODIFIED and child.original_name != child.name:
                lines.append(f"{indent}  ~ <node name=\"{child.name}\" original=\"{child.original_name}\"></node>")
            else:
                lines.append(f"{indent}  {child_prefix} <node name=\"{child.name}\"></node>")
        
        # Show all notes in this node with full detail
        for note in self.notes:
            note_prefix = {
                GitStatus.STAGED: " ",
                GitStatus.ADDED: "+",
                GitStatus.MODIFIED: "~",
            }[note.status]
            
            note_line = f"{indent}  {note_prefix} <note id=\"{note.id}\" name=\"{note.name}\""
            
            # Show modifications
            if note.status == GitStatus.MODIFIED:
                modifications = []
                if note.original_name != note.name:
                    modifications.append(f"name_changed=\"{note.original_name}\"")
                if note.og_note_references != note.node_references:
                    modifications.append("refs_changed=\"true\"")
                if modifications:
                    note_line += f" {' '.join(modifications)}"
            
            note_line += "></note>"
            lines.append(note_line)
        
        lines.append(f"{indent}{status_prefix} </node>")
        return "\n".join(lines)