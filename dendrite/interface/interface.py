import dendrite.interface.components as components
from dendrite.interface.types import Note, Node
from dendrite.utils.constants import TAB, MAX_INTERFACE_LENGTH
from dendrite.db.io import DB_SET, DatabaseType
from pydantic import BaseModel
from typing import Optional

class ContentUpdate(BaseModel):
    content: str = None
    append: bool = False

class NoteEdit(BaseModel):
    path_to_note: str
    content_update: Optional[ContentUpdate]
    updated_references: Optional[list[str]] = None
    updated_name: Optional[str] = None

class Interface:
    def __init__(self, db_type: DatabaseType, base_indent: int = 0):
        self.db_type = db_type
        self.base_indent = base_indent
        self.db = DB_SET[db_type]
        self.explorer = components.Explorer(self.db, base_indent=base_indent + 2)
        # put in read only manifest at root of db if it exists
        self.opened = components.Notes([self.db.notes[0]] if self.db.notes and self.db.notes[0].read_only else [], base_indent=base_indent + 2)
        self.notifications = components.Notifications(base_indent=base_indent + 2)
        self.current_node = self.db.model_copy()
        self.current_path = ""

    def __str__(self, tie_interface: bool = False):
        tab = TAB * self.base_indent
        component_names = ["explorer", "opened", "notifications", "conversation_coverage"] if tie_interface else ["opened"]

        room_left = MAX_INTERFACE_LENGTH

        prefix = f'{tab}<interface>\n'
        for name in component_names:
            comp: components.Component = getattr(self, name)
            comp.set_max_length(room_left)
            if tie_interface and isinstance(comp, components.Notes):
                comp_str = str(comp, show_diff=False)
            else:
                comp_str = str(comp)
            prefix += f'{tab}{TAB}<{name}>\n{comp_str + chr(10) if comp_str else ""}{tab}{TAB}</{name}>\n'

        return f"{prefix}{tab}</interface>"

    def open_node(self, node_path: str):
        self.explorer.open_node(node_path)
        # with git diff showing most edit history, we can just notify write model about paths its explored
        self.notifications.add_notification(f"Opened node: {node_path}")

    def open_note(self, note_path: str):
        self.opened.open_note(note_path, self.current_node)
    
    def create_note(self, name: str, content: str, references: list[str]):
        if not references:
            raise ValueError("References cannot be empty")
        new_note = self.explorer.create_note(name, content, node_references=references, note_references=[])
        id = new_note.id
        ref = references[0]
        note_path = f"{ref}/{id}"
        self.opened.open_note(note_path, self.current_node)

    def edit_note(self, note_edit: NoteEdit):
        if note_edit.content_update:
            self.explorer.edit_note(note_edit.path_to_note, note_edit.content_update.content, append=note_edit.content_update.append)
            self.opened.open_note(note_edit.path_to_note, self.current_node)
        if note_edit.updated_name:
            self.explorer.change_note_name(note_edit.path_to_note, note_edit.updated_name)
        if note_edit.updated_references:
            self.explorer.change_note_references(note_edit.path_to_note, note_edit.updated_references)

    def add_cross_reference(self, tie_type: type[Note] | type[Node], note_id: str, tie_interface: 'Interface', tie_ref: str):
        corresponding_primary_note = [note for note in self.opened.open_notes if note.id == note_id]
        if len(corresponding_primary_note) != 1:
            raise ValueError(f"Expected to find exactly one note with ID {note_id} in opened notes, found {len(corresponding_primary_note)} instead.")
        corresponding_primary_note = corresponding_primary_note[0]
        
        if tie_type == Note:
            corresponding_tie_note = [note for note in tie_interface.opened.open_notes if note.id == tie_ref]
            if len(corresponding_tie_note) != 1:
                raise ValueError(f"Expected to find exactly one note with ID {tie_ref} in tie interface opened notes, found {len(corresponding_tie_note)} instead.")
            corresponding_tie_note = corresponding_tie_note[0]
            corresponding_primary_note.note_references.append(corresponding_tie_note)
            corresponding_tie_note.note_references.append(corresponding_primary_note)
        elif tie_type == Node:
            tie_interface.explorer.open_node(tie_ref)
            corresponding_tie_node = tie_interface.explorer.node
            corresponding_primary_note.node_references.append(corresponding_tie_node)

    def generate_scaffolding(self, parent_path: str, scaffolding: components.Scaffolding):
        self.explorer.generate_scaffolding(parent_path, scaffolding)