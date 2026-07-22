from mcp.server.fastmcp import FastMCP
mcp = FastMCP("test")
@mcp.tool()
def hello(name: str) -> str:
    return f"Hello {name}"
print(type(mcp.run))
