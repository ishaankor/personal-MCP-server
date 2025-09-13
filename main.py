from mcp.server.fastmcp import FastMCP
import os

mcp = FastMCP(
    name="RemoteMCP",
    host="0.0.0.0",
    port=8050,
    # stateless_http=True
)

@mcp.resource(uri="resource://about_me", name="Information for Ishaan Koradia", description="Helps the user learn about Ishaan Koradia!")
def about_me_resource():
    path = os.path.join(os.path.dirname(__file__), "about_me.txt")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
    

if __name__ == "__main__":
    mcp.run(transport="streamable-http")