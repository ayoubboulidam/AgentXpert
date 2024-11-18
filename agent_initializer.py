import os
from typing import Any, Optional

from dotenv import load_dotenv
from langchain import hub
from langchain_core.tools import Tool
from langchain.agents import create_react_agent, AgentExecutor
from langchain_experimental.tools import PythonREPLTool
from langchain_experimental.agents.agent_toolkits import create_csv_agent
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()


def initialize_grand_agent(csv_file_path: Optional[str] = None) -> AgentExecutor:
    """
    Initializes and returns a grand agent executor, optionally configured for CSV file analysis.
    """
    instructions = (
        "You are an agent designed to execute Python code, analyze CSV files, perform complex calculations, "
        "and handle various tasks using Python libraries. "
        "If unsure about an answer, respond with 'I don't know.'"
    )

    base_prompt = hub.pull("langchain-ai/react-agent-template")
    prompt = base_prompt.partial(instructions=instructions)

    # Tools for agents
    tools = [PythonREPLTool()]

    # Python Agent
    python_agent = create_react_agent(
        prompt=prompt,
        llm=ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0),
        tools=tools,
    )
    python_executor = AgentExecutor(agent=python_agent, tools=tools, verbose=True)

    # CSV Agent
    csv_executor = None
    if csv_file_path:
        csv_executor = create_csv_agent(
            llm=ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0),
            path=csv_file_path,
            verbose=True,
            allow_dangerous_code=True,
        )

    # Mathematical Agent
    def math_agent_func(prompt: str) -> dict[str, Any]:
        try:
            # Evaluate mathematical expressions
            result = {"output": str(eval(prompt))}
        except Exception as e:
            result = {"output": f"Math error: {str(e)}"}
        return result

    # Wrapper functions
    def python_executor_wrapper(prompt: str) -> dict[str, Any]:
        return python_executor.invoke({"input": prompt})

    def csv_executor_wrapper(prompt: str) -> dict[str, Any]:
        if csv_executor:
            return csv_executor.invoke({"input": prompt})
        return {"output": "No CSV file provided for analysis."}

    # Define tools for the grand agent
    grand_tools = [
        Tool(
            name="Python Agent",
            func=python_executor_wrapper,
            description="Executes Python code for advanced tasks.",
        ),
        Tool(
            name="CSV Agent",
            func=csv_executor_wrapper,
            description="Analyzes CSV files using pandas.",
        ),
        Tool(
            name="Math Agent",
            func=math_agent_func,
            description="Solves mathematical problems. Input the equation or problem directly.",
        ),
    ]

    # Grand Agent
    grand_agent = create_react_agent(
        prompt=prompt,
        llm=ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0),
        tools=grand_tools,
    )

    return AgentExecutor(agent=grand_agent, tools=grand_tools, verbose=True)
