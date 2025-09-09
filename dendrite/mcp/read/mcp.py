from mcp.server.fastmcp import FastMCP
from dendrite.interface.interface import Interface
from dendrite.databases.io import DatabaseType
from .dressing import dress_mcp_read

class ReadMCP(FastMCP):
    def __init__(self, db_type: DatabaseType) -> None:
        super().__init__('read')
        self.interface = Interface(db_type)
        dress_mcp_read(self, self.interface)