import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def initialize_client():
    """
    Initialize the OpenAI client with proper error handling.
    
    Returns:
        OpenAI: Configured OpenAI client
    
    Raises:
        ValueError: If API key is not found
        Exception: For other initialization errors
    """
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError(
            "OpenAI API key not found. "
            "Make sure you have created a .env file with your API key."
        )
    
    try:
        return OpenAI(api_key=api_key)
    except Exception as e:
        raise Exception(f"Failed to initialize OpenAI client: {str(e)}")

def create_code_assistant(client: OpenAI) -> str:
    """
    Creates a new assistant specialized for code writing and explanation.
    
    Args:
        client: Initialized OpenAI client
        
    Returns:
        str: The ID of the created assistant
    """
    tools = [
        {
            "type": "function",
            "function": {
                "name": "file_writer",
                "description": "Writes code to a file in the specified path",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "The path where the code should be written"
                        },
                        "content": {
                            "type": "string",
                            "description": "The code content to write to the file"
                        }
                    },
                    "required": ["file_path", "content"]
                }
            }
        }
    ]
    
    try:
        assistant = client.beta.assistants.create(
            name="code_assistant",
            instructions="""You are a specialized coding assistant that can write and explain code.
            When writing code, place it in fenced code blocks (```).
            You can write code to files using the file_writer tool.
            Always explain your code thoroughly and consider security implications.""",
            model="gpt-4-0125-preview",
            tools=tools
        )
        return assistant.id
    except Exception as e:
        raise Exception(f"Failed to create assistant: {str(e)}")