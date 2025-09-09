from mcp.server.fastmcp import FastMCP
from typing import Optional

from dendrite.interface.interface import Interface
from dendrite.db.io import DatabaseType

class InterfaceMCP(FastMCP):
    """
    Dressed with both read and write tools. Read is needed for navigation.
    """
    def __init__(self, name: str, db_type: DatabaseType, tie_interface: Optional[Interface]) -> None:
        super().__init__(name)
        self.interface = Interface(db_type)
        if tie_interface:
            tie_interface = tie_interface.copy()
        self.tie_interface = tie_interface