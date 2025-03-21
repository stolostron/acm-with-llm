import asyncio
import sys
from typing import Literal
from dataclasses import dataclass

from agents import (
    Agent,
    Runner,
    RunConfig,
    RunContextWrapper,
    TResponseInputItem,
    trace,
    ItemHelpers,
    RunResult,
)

from dotenv import load_dotenv
from litemcp.manager import MCPServerManager
from framework.openai.grc.grc_hook import (
    EvaluationFeedback,
    GrcAgentHooks,
    yaml_applier_validator,
)
from framework.openai.grc.grc_prompt import (
    GRC_AUTHOR_PROMPT,
    GRC_CRITIC_PROMPT,
    KUBERNETES_ENGINEER_PROMPT,
)


load_dotenv()


async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_mcp_server>")
        sys.exit(1)

    async with MCPServerManager(sys.argv[1]) as server_manager:
        server_manager.register_validator("yaml_applier", yaml_applier_validator)

        mcp_server_tools = await server_manager.agent_sdk_tools()

        engineer = Agent(
            name="Kubernetes Engineer",
            handoff_description="I am the Engineer can apply your policy into the environment",
            instructions=KUBERNETES_ENGINEER_PROMPT,
            tools=mcp_server_tools,
            hooks=GrcAgentHooks("Engineer"),
        )

        critic = Agent(
            name="Critic",
            instructions=GRC_CRITIC_PROMPT,
            output_type=EvaluationFeedback,
            hooks=GrcAgentHooks("Critic"),
        )

        author = Agent(
            name="Author",
            instructions=GRC_AUTHOR_PROMPT,
            hooks=GrcAgentHooks("Author"),
        )
        print()
        msg = input("What kind of policy would you like? \n \n")
        input_items: list[TResponseInputItem] = [{"content": msg, "role": "user"}]
        latest_grc: str | None = None

        while True:
            # generate the policy
            grc_result: RunResult = await Runner.run(
                author, input_items, run_config=RunConfig(tracing_disabled=True)
            )

            input_items = grc_result.to_input_list()
            latest_grc = ItemHelpers.text_message_outputs(grc_result.new_items)

            # evaluate
            evaluator_result = await Runner.run(
                critic, input_items, run_config=RunConfig(tracing_disabled=True)
            )
            result: EvaluationFeedback = evaluator_result.final_output

            if result.score == "pass":
                break

            # feedback
            input_items.append(
                {"content": f"Feedback: {result.feedback}", "role": "user"}
            )

        # apply the grc
        msg = f"Please apply the following Policy into the kubernetes cluster: \n {latest_grc}"
        input_items: list[TResponseInputItem] = [{"content": msg, "role": "user"}]

        engineer_result = ""
        while True:
            engineer_result = await Runner.run(
                engineer, input_items, run_config=RunConfig(tracing_disabled=True)
            )
            input_items = engineer_result.to_input_list()

            input_items.append(
                {"content": f"{engineer_result.new_items}", "role": "user"}
            )
            print()
            user_input = input(" Continue? (yes/no): ").strip().lower()

            if user_input in ["no", "n"]:
                break
            if user_input in ["yes", "y"]:
                continue
            input_items.append({"content": f"User Input: {user_input}", "role": "user"})


if __name__ == "__main__":
    asyncio.run(main())

"""
$ python -m framework.openai.grc.grc_chat framework/openai/grc/mcp-config.json
"""
