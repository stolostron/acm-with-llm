## Motivation

This repo intends to build a set of agents (experimental stage) that can simplify interaction with Red Hat Advanced Cluster Management leveraging LLM capabilities. These require subscription to OpenAI as explained below. 

### On ACM Search Data
ACM Search data is stored in PostgreSQL DB. A sample database content file is included [here](./data/search_load.sql).
1. Create a database in PostgreSQL. This should be created locally. We can easily expand this to allow for non local database.
1. Populate the database by importing [here](./data/search_load.sql) or running the SQLs manually.
1. Follow the steps mentioned below to get the LLM to run.

## What do you need to run
### Prereq
1. Clone this repo
1. Setup venv.
    - `cd to the repo dir`
    - run: 
        ```
        python -m venv .venv
        source .venv/bin/activate
        pip install -r requirements.txt
        ```
    - run :`which python` and this show that python is being used from the venv directory
    - after all work is done, to exit the venv, just run: `deactivate`
1. Copy `env-sample` to `.env` and edit the new file.
1. Obtain an API Key token from openai.com and update the value for the `OPENAI_API_KEY` variable in `.env`. **NOTE** This requires you purchase a Tier 1 rate from openai.com because the gpt-4 model is being used.  See [Open AI Rate Limits](https://platform.openai.com/docs/guides/rate-limits/usage-tiers?context=tier-one) for more details.
1. ACM Search data is stored in PostgreSQL DB. A sample database content file is included [here](./data/search_load.sql).
Create a database in PostgreSQL. A remote database will work as well as long as the DB credentials are available.
Populate the database by importing from [here](./data/search_load.sql) or running the SQLs manually.
1. Update your DB credentials in the `.env`.
1. Run (replace python3 with python if appropriate)
    ```
    python3 src/acm_chat.py
    ```
---

## Using Ollama for Local LLM Iteration

> 💡 **Note:** If Ollama is not installed or running, the chatbot will fall back to a base model.

You can alternate between OpenAI and local LLMs (like Llama3) using [Ollama](https://ollama.com/).

1. **Install Ollama**
    - On macOS:
      ```bash
      brew install ollama
      ```
    - Or follow [Ollama install instructions](https://ollama.com/download).

2. **Start a model**
    ```bash
    ollama run llama3
    ```
    - Ollama should run on port **11434** by default.

3. **Change Ollama model (optional)**
    - Get model name
      ```
      curl http://localhost:11434/api/tags
      ```
    - Edit `.env`:
      ```
      OLLAMA_MODEL=mistral
      ```

---
## 🛠️ How to Fix Your Uploaded ACM Policy using LLM

1. Place your ACM policy YAML file in the `./load_files` directory.
2. Ask the ACM LLM to review and fix it.  
   **Example prompt:**  
   `"Can you fix my uploaded policy?"`
