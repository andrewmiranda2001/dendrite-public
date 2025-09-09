from typing import Optional, Union
from dendrite.interface.interface import Interface, NoteEdit
from dendrite.interface.components import Scaffolding
from dendrite.interface.types import Note, Node
from dendrite.mcp.base_mcp import InterfaceMCP
from dendrite.db.io import DatabaseType

def dress_mcp_write(mcp: InterfaceMCP, interface: Interface) -> None:

    @mcp.tool()
    def create_note(name: str, content: str, references: list[str]) -> None:
        """
        Create a new note for later retrieval. This note will be marked as ADDED in the interface.

        Args:
            name (str): The name of the new note
            content (str): The content of the new note
            references (list[str]): A list of node paths this note should be categorized under
            conversation_reference (tuple[int, int]): The start and end line numbers of the conversation content you are taking notes on for this creation.
        """
        return interface.create_note(name, content, references)

    @mcp.tool()
    def edit_note(edit: NoteEdit) -> None:
        """
        Modify an existing note's content, name, and/or references. The note will be marked as MODIFIED.
        Can perform multiple operations in a single call - update content (replace or append), 
        change the note name, and/or update which nodes the note references.

        Args:
            edit (NoteEdit): Note modification parameters including:
                - path_to_note (str): Full path to the note including note ID (e.g., /root/personality/risk_tolerance/123456)
                - content_update (ContentUpdate, optional): New content to replace or append
                - updated_references (list[str], optional): New list of node paths this note should appear in  
                - updated_name (str, optional): New name for the note
        """
        return interface.edit_note(edit)

    @mcp.tool()
    def generate_scaffolding(parent_path: str, scaffolding: Scaffolding) -> None:
        """
        Generate new node structure under the specified parent node. New nodes will be marked as ADDED.

        Args:
            parent_path (str): The path to the parent node under which the scaffolding will be created
            scaffolding (dict): Nested structure like:
                {
                    "personality": {
                        "risk_tolerance": {},
                        "decision_making": {}
                    },
                    "relationships": {
                        "family": {},
                        "romantic": {},
                        "friendships": {}
                    }
                }
        """
        return interface.generate_scaffolding(parent_path, scaffolding)
    

example_paths = {
    DatabaseType.CONCEPTUAL: DatabaseType.CONCEPTUAL.value + '/personality/risk_tolerance',
    DatabaseType.CONCRETE: DatabaseType.CONCRETE.value + '/relationships/family/mother',
    DatabaseType.TEMPORAL: DatabaseType.TEMPORAL.value + '/2024/06/15',
}

tie_permissions: dict[DatabaseType, tuple[Optional[Union[Note, Node]], Optional[Union[Note, Node]]]] = {
    DatabaseType.CONCEPTUAL: (None, None),
    DatabaseType.CONCRETE: (Note, Note),
    DatabaseType.TEMPORAL: (Node, Note),
}

def dress_mcp_write_tied(mcp: InterfaceMCP, interface: Interface, tie_interface: Interface) -> None:
    permission1, permission2 = tie_permissions[interface.db_type]
    type1, type2 = interface.db_type, tie_interface.db_type
    if not permission1 or not permission2:
        raise ValueError(f"Tied writing not supported for {interface.db_type.value} interfaces.")
    if interface.db_type == tie_interface.db_type:
        raise ValueError("Cannot tie an interface to another interface of the same type.")
    
    example_note_id = '123456'
    note_condition = 'Note ID'
    node_condition = 'Path to node'
    if permission1 == Note:
        example_1 += example_note_id
        condition_1 = note_condition
    else:
        example_1 = example_paths[type1]
        condition_1 = node_condition
    
    if permission2 == Note:
        example_2 += example_note_id
        condition_2 = note_condition
    else:
        example_2 = example_paths[type2]
        condition_2 = node_condition


    @mcp.tool()
    def create_cross_reference(ref1: str, ref2: str) -> None:
        f"""
        Create a cross-reference between a {permission1} from the {type1} database and a {permission2} from the {type2} database.

        Args:
            ref1 (str): {condition_1} (e.g., {example_1})
            ref2 (str): {condition_2} (e.g., {example_2})
        """
        if permission1 == Note:
            interface.add_cross_reference(permission2, ref1, ref2)
        if permission2 == Note:
            if not ref2.endswith(example_note_id):
                raise ValueError(f"Path to {permission2} must include note ID. Example: {example_2}")
            interface.add_cross_reference(permission1, ref2.split('/')[-1], ref1)


