### **AI-Driven Policy Creation**  

This project enables AI-assisted policy creation, inspired by [acm-with-llm](https://github.com/stolostron/acm-with-llm/tree/main/src).  

#### **Key Features**  

- **Built with `openai-agent-sdk`** for automation.  
- **Three AI agents** collaborate:  
  - **Author** – Drafts policies.  
  - **Critic** – Reviews and refines.  
  - **Engineer** – Implements in Kubernetes. 
- **MCP Server** via [multicluster-mcp-server](https://github.com/yanmxa/multicluster-mcp-server), MCP Adaptor/Client - [litemcp](https://github.com/yanmxa/litemcp)

#### Tool Call Validator(Optional)

You can add a **custom validation function** to control MCP tool calls. This helps prevent server tools from directly accessing your system without permission—such as integrating a **human-in-the-loop** step.

##### 1. Define the Validator

```python
def applier_validator(func_args) -> Optional[str]:
    """
    Return:
    - None: allow the tool call
    - str : block the tool call and return message instead
    """
    user_input = console.input(
        f"  🛠  Cluster - [yellow]{cluster}[/yellow] ⎈ Proceed with this YAML? (yes/no): "
    ).strip().lower()

    if user_input in {"yes", "y"}:
        return None
    if user_input in {"no", "n"}:
        console.print("[red]Exiting process.[/red]")
        sys.exit(0)
    return user_input
```

##### 2. Register the Validator with MCP Server

```python
async with MCPServerManager(sys.argv[1]) as server_manager:
    server_manager.register_validator("yaml_applier", applier_validator)

    mcp_server_tools = await server_manager.agent_sdk_tools()

    engineer = Agent(...)
```

#### **Live demo**

  <a href="https://asciinema.org/a/709075">
    <img src="https://asciinema.org/a/709075.svg" width="600">
  </a>