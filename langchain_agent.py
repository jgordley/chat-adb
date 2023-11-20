from langchain.agents import AgentExecutor
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools.render import format_tool_to_openai_function
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import AgentAction

from asyncio import Queue

from typing import Dict, Any

from adb_tools import (
    ListDevicesTool,
    GetDeviceBatteryLevelTool,
    GetDeviceInfoTool,
    SearchDeviceFilesTool,
    ListInstalledAppsTool,
    ListRunningProcessesTool,
    get_tool_metadata_from_name,
)


class MyCustomHandlerOne(BaseCallbackHandler):
    def __init__(self, queue: Queue):
        self.queue = queue

    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> Any:
        """Run on agent action."""

        # Get the metadata for this tool
        metadata = get_tool_metadata_from_name(action.tool)
        self.queue.put_nowait(metadata)


def run_agent_executor(input, openai_api_key, model, queue: Queue):
    if not openai_api_key:
        return "Please enter your OpenAI API Key in the sidebar, I can't function without it :("

    # Options
    llm = ChatOpenAI(temperature=0, model=model, api_key=openai_api_key)
    tools = [
        ListDevicesTool(),
        GetDeviceBatteryLevelTool(),
        GetDeviceInfoTool(),
        SearchDeviceFilesTool(),
        ListInstalledAppsTool(),
        ListRunningProcessesTool(),
    ]

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful assistant"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    functions = [format_tool_to_openai_function(t) for t in tools]

    llm_with_tools = llm.bind(functions=functions)

    agent = (
        {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_to_openai_function_messages(
                x["intermediate_steps"]
            ),
        }
        | prompt
        | llm_with_tools
        | OpenAIFunctionsAgentOutputParser()
    )

    handler = MyCustomHandlerOne(queue=queue)

    agent_executor = AgentExecutor(
        agent=agent, tools=tools, verbose=True, callbacks=[handler]
    )
    result = agent_executor.invoke({"input": input})

    # Put the result in the queue
    queue.put_nowait(result.get("output"))

    queue.put_nowait("[DONE]")
