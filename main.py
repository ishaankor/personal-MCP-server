from fastmcp import FastMCP
import os

mcp = FastMCP("RemoteMCP")

@mcp.resource(uri="resource://about_me", name="Information for Ishaan Koradia", description="Helps the user learn about Ishaan Koradia!")
def about_me_resource():
    path = os.path.join(os.path.dirname(__file__), "about_me.txt")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
    
    
if __name__ == "__main__":
    mcp.run(transport="streamable-http")