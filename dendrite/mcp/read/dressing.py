from dendrite.mcp.base_mcp import InterfaceMCP
from dendrite.interface.interface import Interface

def dress_mcp_read(mcp: InterfaceMCP, interface: Interface):
    @mcp.tool()
    def open_note(path_to_note: str):
        """
        Open a note by its path. After calling this tool, you will see the full contents of the note appear in the "opened" section of the interface.

        CRITICAL: The path must end with the note ID (the number), NOT the note name.
        Look at the interface XML to find the correct ID.

        Args:
            path_to_note (str): Absolute or relative path to the note to open.

        """
        return interface.open_note(path_to_note)

    @mcp.tool()
    def open_node(path_to_node: str):
        """
        Open a node by its path. After calling this tool, you will see the "explorer" in the interface updated with the node expanded.
        Args:
            path_to_node (str): Absolute or relative path to the node to open.
        """
        return interface.open_node(path_to_node)