### **AI-Driven Policy Creation**  

This project enables AI-assisted policy creation, inspired by [acm-with-llm](https://github.com/stolostron/acm-with-llm/tree/main/src).  

#### **Features**  
- **Built with `openai-agent-sdk`** for intelligent automation.  
- **Three specialized AI agents** collaborate:  
  - **Author** – Drafts the policy.  
  - **Critic** – Reviews and refines it.  
  - **Engineer** – Implements the policy in Kubernetes.  
- **Kubernetes integration** via `multicluster-mcp-server` (custom implementation, as `agent-sdk` lacks native support). [More details](https://github.com/openai/openai-agents-python/issues/23).  
- **Live demo**
  <a href="https://asciinema.org/a/709075">
    <img src="https://asciinema.org/a/709075.svg" width="600">
  </a>