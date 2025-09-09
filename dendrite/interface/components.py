from __future__ import annotations
from abc import ABC, abstractmethod
import dendrite.interface.types as types
from dendrite.utils.constants import TAB
from dendrite.db.io import DB_SET
import dendrite.db.io as io
from typing import Dict, Any, Tuple, Optional
from pydantic import BaseModel

Scaffolding = Dict[str, Any]

def _parse_path(path: str, current_node: types.Node, last_node_is_note: bool = False) -> Tuple[types.Node, int]:
    """
    Parse a path and return (target_node, note_id_or_empty).
    
    Returns:
        - For node paths: (target_node, "")
        - For note paths: (parent_node, note_id)
    """
    path = path.strip().strip('/')
    if not path:
        raise ValueError("Path cannot be empty")
    skip = 1
    temp_node = None
    
    path_parts = path.split('/')
    if path_parts[0] == '.':
        if path_parts[1] != current_node.name:
            raise ValueError(f"Relative path must still include the current node '{current_node.name}'")
        skip = 2
        temp_node = current_node.model_copy()
    else:
        if path_parts[0] not in [db.db_type for db in DB_SET.values()]:
            raise ValueError(f"Absolute path must start with a valid database type: {[db.db_type for db in DB_SET.values()]}")
        temp_node = DB_SET[types.DatabaseType(path_parts[0])]
    
    note_id = None
    if last_node_is_note:
        note_id = int(path_parts[-1])
        node_path = path_parts[skip:-1]
    else:
        node_path = path_parts[skip:]
    
    for dir_name in node_path:
        found = False
        for child in temp_node.children:
            if child.name == dir_name:
                temp_node = child
                found = True
                break
        if not found:
            raise ValueError(f"Node '{dir_name}' not found in path '{path_parts}'")
    
    return temp_node, note_id

class Component(ABC):
    def __init__(self, base_indent: int = 0):
        self.base_indent = base_indent
        self.max_length = 0

    def set_max_length(self, max_length: int):
        self.max_length = max_length

    @abstractmethod
    def __str__(self):
        raise NotImplementedError("Subclasses must implement __str__ method")

class Explorer(Component):
    def __init__(self, node: types.Node, base_indent: int = 0):
        super().__init__(base_indent)
        self.node: types.Node = node
        self.db = node
        self.current_path: list[str] = [node.db_type]
        self.SCHEMA_PRIORITY = 0.7

    def __str__(self):
        tab = TAB * self.base_indent
        path_str = "/".join(self.current_path) if hasattr(self, 'current_path') and self.current_path else "/root"
        
        total_available = self.max_length
        header_size = len(f'{tab}<current_path>{path_str}</current_path>\n')
        
        schema_budget = int((total_available - header_size) * self.SCHEMA_PRIORITY)
        current_node_budget = total_available - header_size - schema_budget
        
        result = f'{tab}<current_path>{path_str}</current_path>\n'
        
        # Full schema section (collapsed view with git status)
        schema_section = f'{tab}<schema>\n'
        schema_content = self.db.to_interface_string(tab + TAB)  # Use DB root for full schema

        if len(schema_content) > schema_budget:
            schema_section += f"{tab + TAB}<schema truncated=\"true\">...</schema>\n"
        else:
            schema_section += schema_content + '\n'
        schema_section += f'{tab}</schema>\n'
        
        # Current node detail section
        current_section = f'{tab}<current_node>\n'
        current_content = self.node.to_current_node_string(tab + TAB)
        
        if len(current_content) > current_node_budget:
            current_section += f"{tab + TAB}<current_node truncated=\"true\">...</current_node>\n"
        else:
            current_section += current_content + '\n'
        current_section += f'{tab}</current_node>\n'
        
        return result + schema_section + current_section
    
    def open_node(self, node_path: str):
        target_node, _ = _parse_path(node_path, self.node, False)
        self.node = target_node
        self.current_path = [p for p in node_path.split('/') if p]

    # only for use by write passers, not tiers
    def create_note(self, name: str, content: str, node_references: list[str], note_references: list[str]) -> types.Note:
        new_note = types.Note(
            id=abs(hash(name + content)),
            name=name,
            content=[types.Content(text=content, status=types.ContentStatus.ADDED)],
            node_references=node_references,
            note_references=note_references,
            status=types.GitStatus.ADDED
        )
        return self.create_note_direct(new_note)
    
    # only for use by tiers, not write passers
    def create_note_direct(self, note: types.Note) -> types.Note:
        og_node = self.node
        for ref in note.node_references:
            target_node, _ = _parse_path(ref, self.node, False)
            if target_node.name == self.node.db_type:
                raise ValueError("Cannot add note to root node")
            target_node.notes.append(note)
        self.node = og_node
        io.add_note(note)
        return note        

    def edit_note(self, path_to_note: str, content: str, append: bool = False):
        og_node = self.node
        
        try:
            target_node, note_id = _parse_path(path_to_note, self.node, True)
            if target_node.name == target_node.db_type:
                raise ValueError("Cannot edit note in root node")
            if not note_id:
                raise ValueError(f"Path '{path_to_note}' does not end with a note ID")
            
            found = False
            for note in target_node.notes:
                if note.id == note_id:
                    if append:
                        note.add_content(content)
                    else:
                        from dendrite.interface.utils.diff import apply_content_diff
                        new_content, has_changes = apply_content_diff(note.content, content)
                        
                        if has_changes:
                            note.content = new_content
                            if note.status == types.GitStatus.STAGED:
                                note.status = types.GitStatus.MODIFIED
                    found = True
                    break
            
            if not found:
                raise ValueError(f"Note with ID {note_id} not found in target node")

        finally:
            self.node = og_node

    def change_note_name(self, path_to_note: str, new_name: str):
        og_node = self.node
        
        try:
            target_node, note_id = _parse_path(path_to_note, self.node, True)
            
            for note in target_node.notes:
                if note.id == note_id:
                    note.change_name(new_name)
                    break
        finally:
            self.node = og_node

    def change_note_references(self, path_to_note: str, new_references: list[str]):
        og_node = self.node
        
        try:
            target_node, note_id = _parse_path(path_to_note, self.node, True)
            
            for note in target_node.notes:
                if note.id == note_id:
                    note.change_references(new_references)
                    break
        finally:
            self.node = og_node

    def generate_scaffolding(self, parent_path: str, scaffolding: Scaffolding):
        og_node = self.node
        try:
            target_node, _ = _parse_path(parent_path, self.node, False)
            self._add_scaffolding(target_node, scaffolding)
        finally:
            self.node = og_node

    def _add_scaffolding(self, node: types.Node, scaffolding: Scaffolding):
        for name, child in scaffolding.items():
            new_node = types.Node(
                name=name, 
                notes=[], 
                children=[],
                status=types.GitStatus.ADDED
            )
            node.children.append(new_node)
            self._add_scaffolding(new_node, child)

class Notes(Component):
    def __init__(self, open_notes: list[types.Note], base_indent: int = 0):
        super().__init__(base_indent)
        self.open_notes = open_notes

    def __str__(self, tie_interface: bool = False):
        if not self.open_notes:
            return ""
        
        tab = TAB * self.base_indent
        lines = []
        
        for note in self.open_notes:
            note_str = note.to_interface_string(tab, tie_interface=tie_interface)
            if len("\n".join(lines + [note_str])) > self.max_length:
                lines.append(f"{tab}<note truncated=\"true\">...</note>")
                break
            lines.append(note_str)
        
        return "\n".join(lines)

    def open_note(self, note_path: str, current_node: types.Node) -> str:
        target_node, note_id = _parse_path(note_path, current_node, True)
        if not note_id:
            raise ValueError(f"Path '{note_path}' does not end with a note ID")

        if note_id in [note.id for note in self.open_notes]:
            return str(self)
        
        for note in target_node.notes:
            if note.id == note_id:
                self.open_notes.append(note)
                return str(self)

        raise ValueError(f"Note with ID {note_id} not found in target node")

class Notifications(Component):
    def __init__(self, notifications: list[str] = [], base_indent: int = 0):
        super().__init__(base_indent)
        self.notifications = notifications

    def add_notification(self, message: str) -> None:
        self.notifications.append(message)

    def __str__(self):
        tab = f'\n{TAB * self.base_indent}'
        if not self.notifications:
            return ""
        
        notifications_content = ""
        for note in self.notifications:
            if len(notifications_content) >= self.max_length:
                notifications_content += f'{TAB * self.base_indent}<notification truncated="true">...</notification>'
                break
            notifications_content += f'{TAB * self.base_indent}<notification content="{tab + TAB}{note.replace("\n", tab + TAB)}{tab}">{tab}</notification>'

        return notifications_content