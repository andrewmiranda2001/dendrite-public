from __future__ import annotations
import dendrite.interface.types as types
from dendrite.utils.file import write_to_file, read_file


import json
import os
from typing import cast, List
from pydantic import BaseModel
from enum import Enum


"""
Read utilities
"""

db_json = dict[str, 'db_json']

class note_json(BaseModel):
    id: int
    name: str
    node_references: list[str]
    note_references: list[str]
    read_only: bool = False

class DatabaseType(Enum):
    CONCEPTUAL = "conceptual"
    CONCRETE = "concrete"
    TEMPORAL = "temporal"
    

DatabaseSet = dict[DatabaseType, types.Node]

ROOT = os.getenv("DB_ROOT")
node_path = os.path.join(ROOT, 'nodes.json')
note_path = os.path.join(ROOT, 'notes', 'notes.json')
content_folder = os.path.join(ROOT, 'notes', 'content')

def load_db_into_memory() -> DatabaseSet:
    dbs: DatabaseSet = {}
    notes_by_path: dict[str, list[types.Note]] = {}
    notes = cast(List[note_json], json.loads(read_file(note_path)))
    for read_note in notes:
        content_path = os.path.join(content_folder, f'{read_note['id']}.md')
        content = read_file(content_path)
        read_note = types.Note(
            id=read_note['id'],
            read_only=read_note['read_only'],
            name=read_note['name'],
            content=[types.Content(text=content, status=types.ContentStatus.STAGED)],
            node_references=read_note['node_references'],
            note_references=read_note['note_references'],
            status=types.GitStatus.STAGED
        )
        for ref in read_note.node_references:
            if ref not in notes_by_path:
                notes_by_path[ref] = []
            notes_by_path[ref].append(read_note)
    read_dbs = cast(db_json, json.loads(read_file(node_path)))
    if not all(type_.value in read_dbs for type_ in DatabaseType):
        raise ValueError(f"Database root at {ROOT} is missing one of the required database types: {[type_.value for type_ in DatabaseType]}")
    for type_ in DatabaseType:
        db = traverse_node(read_dbs[type_.value], notes_by_path, type_.value)
        if not len(db) == 1:
            raise ValueError(f"Database of type {type_.value} does not have a single root node.")
        dbs[type_] = db[0]
    return dbs

def traverse_node(db: db_json, notes_by_path: dict[str, list[types.Note]], current_path: str) -> list[types.Node]:
    nodes = []
    for name, child_json in db.items():
        node = types.Node(
            name=name,
            notes=[
                note for note in notes_by_path.get(os.path.join(current_path, name), [])
            ],
            children=[traverse_node(val, notes_by_path, os.path.join(current_path, name)) for val in child_json.values()],
            status=types.GitStatus.STAGED
        )
        nodes.append(node)
    return nodes

DB_SET = load_db_into_memory()

"""
Write utilities
"""

def add_note(note: types.Note):
    # read in current notes json
    notes = cast(List[note_json], json.loads(read_file(note_path)))
    # add note in memory
    notes.append({
        'id': note.id,
        'name': note.name,
        'references': note.node_references
    })
    # write updated notes json back to file
    write_to_file(note_path, json.dumps(notes, indent=4))
    # write actual content file
    write_to_file(
        os.path.join(content_folder, f'{note.id}.md'),
        note.to_storage_string()
    )

def update_note_content(note_id: int, content: str):
    content_path = os.path.join(content_folder, f'{note_id}.md')
    write_to_file(content_path, content)

def save_session_changes(root_node: types.Node):
    _save_all_notes(root_node)
    _save_nodes_structure(root_node)

def _save_all_notes(node: types.Node):
    for note in node.notes:
        if note.status in [types.GitStatus.ADDED, types.GitStatus.MODIFIED]:
            if note.status == types.GitStatus.ADDED:
                add_note(note)
            else:
                update_note_content(note.id, note.to_storage_string())
                if note.name != note.original_name or note.node_references != note.og_note_references:
                    _update_note_metadata(note)
    
    for child in node.children:
        _save_all_notes(child)

def _update_note_metadata(note: types.Note):
    from dendrite.utils.file import write_to_file, read_file
    notes = cast(List[note_json], json.loads(read_file(note_path)))
    for i, note_data in enumerate(notes):
        if note_data['id'] == note.id:
            notes[i]['name'] = note.name
            notes[i]['references'] = note.node_references
            break

    write_to_file(note_path, json.dumps(notes, indent=4))

def _save_nodes_structure(root_node: types.Node):
    """Save the node structure to nodes.json"""
    nodes_json = _node_to_json(root_node)
    write_to_file(
        node_path,
        json.dumps(nodes_json, indent=4)
    )

def _node_to_json(node: types.Node, include_root=False) -> db_json:
    """Recursively convert Node tree back to JSON format"""
    result = {}
    children_to_process = node.children if include_root else node.children
    
    for child in children_to_process:
        result[child.name] = {
            "children": _node_to_json(child, include_root=True)
        }
    return result