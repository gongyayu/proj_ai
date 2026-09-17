import asyncio
import json
from contextlib import AsyncExitStack
from multiprocessing.util import debug
from typing import Any, Dict, List, Optional
from urllib import response
from urllib import response

import nest_asyncio
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import AsyncOpenAI
import streamlit as st


# Apply nest_asyncio to allow nested event loops (needed for Jupyter/IPython)
#nest_asyncio.apply()

# Load environment variables
load_dotenv("../.env")


class MCPOpenAIClient:
    """Client for interacting with OpenAI models using MCP tools."""

    def __init__(self, model: str ):
        """Initialize the OpenAI MCP client.

        Args:
            model: The OpenAI model to use.
        """
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        #self.openai_client = AsyncOpenAI()
        self.openai_client = AsyncOpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama"
        )
        self.model = model
        #self.model = "gpt-oss:latest"
        self.stdio: Optional[Any] = None
        self.write: Optional[Any] = None

    async def connect_to_server(self, server_script_path: str, debug: str):
        """Connect to an MCP server.
        Args:
            server_script_path: Path to the server script.
        """
        # Server configuration
        server_params = StdioServerParameters(
            command="python",
            args=[server_script_path]
        )
        if debug == 'Yes':
            st.write(f'Debug info: To connect to MCP server: {server_script_path}')
        # Connect to the server
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )
        # Initialize the connection
        await self.session.initialize()

        # List available tools
        tools_result = await self.session.list_tools()
        if debug == 'Yes':
            st.write(f'Debug info: List tools after the session is initialized -> {tools_result}')

        for tool in tools_result.tools:
            print(f"  - {tool.name}: {tool.description}")

    async def get_mcp_tools(self, debug: str) -> List[Dict[str, Any]]:
        """Get available tools from the MCP server in OpenAI format.

        Returns:
            A list of tools in OpenAI format.
        """
        tools_result = await self.session.list_tools()
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema,
                },
            }
            for tool in tools_result.tools
        ]

    async def process_query(self, query: str, debug: str) -> tuple[str,str]:
        """Process a query using OpenAI and available MCP tools.

        Args:
            query: The user query.

        Returns:
            The response from OpenAI.
        """

        debug_info = ''
        if debug == 'Yes':
            debug_info += f"Query: {query}\n\n"
        # Get available tools
        tools = await self.get_mcp_tools(debug)
        if debug == 'Yes':
            debug_info += f'Debug info: Retrieve tools from the client -> {tools}\n\n'

        # Initial OpenAI API call
        response = await self.openai_client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": query}],
            tools=tools,
            tool_choice="auto",
        )
        if debug == 'Yes':
            debug_info += f'Debug info: To get the response from initial OpenAI API call-> {response}\n\n'

        # Get assistant's response
        assistant_message = response.choices[0].message
        if debug == 'Yes':
            debug_info += f"Debug info: To get the assistant's response -> {response}\n\n"

        # Initialize conversation with user query and assistant response
        messages = [
            {"role": "user", "content": query},
            assistant_message,
        ]
        if debug == 'Yes':
            debug_info = f'Debug info: To get the messages via initialize conversation with user and assistance response -> {messages}\n\n'

        # Handle tool calls if present
        if assistant_message.tool_calls:
            # Process each tool call
            for tool_call in assistant_message.tool_calls:
                # Execute tool call
                result = await self.session.call_tool(
                    tool_call.function.name,
                    arguments=json.loads(tool_call.function.arguments),
                )

                # Add tool response to conversation
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result.content[0].text,
                    }
                )

            # Get final response from OpenAI with tool results
            final_response = await self.openai_client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="none",  # Don't allow more tool calls
            )
            if debug == 'Yes':
                debug_info += f'Debug info: To get the final response from OpenAI with tool -> {final_response}\n\n'
            return final_response.choices[0].message.content, debug_info

        # No tool calls, just return the direct response
        if debug == 'Yes':
            debug_info += f'Debug info: To get the final response with no tool calls -> {assistant_message.content}\n\n'
        return assistant_message.content, debug_info

    async def cleanup(self):
        """Clean up resources."""
        await self.exit_stack.aclose()

async def ask_mcp(prompt: str,llm,debug: str): 
    debug_list = []
    if debug == 'Yes':
        debug_list.append(f'Debug info: To initialize an client instance\n')  
    client = MCPOpenAIClient(llm)
    server_script_path = "ai_mod/mcp_server_mod.py"

    try:
        await client.connect_to_server(server_script_path,debug)

        if debug == 'Yes':
            debug_list.append(f'Debug info: To process the query: {prompt}\n')
        response, debug_info  = await client.process_query(prompt, debug)

        if debug == 'Yes':
            debug_list.append(f"Query process: {debug_info}")
            debug_list.append(f'Debug info: To return the final response: {response}\n')
        return response, debug_list
    finally:
        await client.cleanup()
#
# the following main is only for cli, not used in streamlit
#
async def main():
    """Main entry point for the client."""
    client = MCPOpenAIClient()
    try:
        await client.connect_to_server("mcp_server_mod.py")

        # Example: Ask about company vacation policy
        query = "What is our company's vacation policy?"
        print(f"\nQuery: {query}")

        response = await client.process_query(query)
        print(f"\nResponse: {response}")
    finally:
        await client.cleanup()


#if __name__ == "__main__":
#    asyncio.run(main())