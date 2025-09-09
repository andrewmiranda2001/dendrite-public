from typing import Optional

from dendrite.interface.interface import Interface
from dendrite.db.io import DatabaseType
from ..base_mcp import InterfaceMCP
from ..read.dressing import dress_mcp_read
from .dressing import dress_mcp_write, dress_mcp_write_tied

class WriteMCP(InterfaceMCP):
    """
    Dressed with both read and write tools. Read is needed for navigation.
    """
    def __init__(self, db_type: DatabaseType, tie_interface: Optional[Interface]) -> None:
        super().__init__('write', db_type, tie_interface)
        dress_mcp_read(self, self.interface)
        if tie_interface:
            dress_mcp_write_tied(self, self.interface, tie_interface)
        else:
            dress_mcp_write(self, self.interface)