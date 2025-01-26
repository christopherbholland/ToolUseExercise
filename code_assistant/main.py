# main.py

import asyncio
from pathlib import Path
from src.security import create_security_context
from src.assistant import initialize_client, create_code_assistant
from src.tools import file_writer
import os
from dotenv import load_dotenv
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))


class CodeAssistantApp:
    def __init__(self):
        """
        Initialize the application with all necessary components:
        - OpenAI client and assistant
        - Security validator
        - Directory structure
        """
        # Set up the OpenAI client and assistant
        self.client = initialize_client()
        self.assistant_id = create_code_assistant(self.client)
        
        # Initialize security context
        self.security = create_security_context()
        
        # Ensure output directory exists
        os.makedirs('output', exist_ok=True)

    async def generate_code(self, description: str, filename: str) -> str:
        """
        Generate code using the OpenAI assistant based on a description.
        
        Args:
            description: What the code should do
            filename: Where to save the generated code
            
        Returns:
            str: Status message about the operation
        """
        # Create a conversation thread
        thread = self.client.beta.threads.create()
        
        # Add the user's request to the thread
        self.client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=f"Write Python code that does the following: {description}\n"
                    f"Make sure the code is secure and well-documented."
        )
        
        # Run the assistant
        run = self.client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=self.assistant_id
        )
        
        # Wait for completion
        while True:
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            if run.status == "completed":
                break
            elif run.status == "failed":
                return "Error: Assistant failed to generate code"
            await asyncio.sleep(1)

        # Get the assistant's response
        messages = self.client.beta.threads.messages.list(
            thread_id=thread.id
        )
        
        # Process the response
        for msg in messages:
            if msg.role == "assistant":
                content = msg.content[0].text.value
                # Find the Python code block
                code_start = content.find("```python")
                if code_start == -1:
                    code_start = content.find("```")
                code_end = content.find("```", code_start + 3)
                
                if code_start != -1 and code_end != -1:
                    # Extract the code, removing the markdown backticks
                    if code_start == content.find("```python"):
                        code = content[code_start + 8:code_end].strip()
                    else:
                        code = content[code_start + 3:code_end].strip()
                    
                    return await self.save_code(code, filename)
                    
        return "No code was found in the assistant's response"

    async def save_code(self, code: str, filename: str) -> str:
        """
        Securely save the generated code to a file.
        
        Args:
            code: The code to save
            filename: Name of the file to create
            
        Returns:
            str: Status message about the save operation
        """
        # Construct the full file path
        file_path = f"output/{filename}"
        
        try:
            # Validate the file path
            if not self.security.validate_file_path(file_path):
                return "Error: Invalid file path or name"
            
            # Scan code for security concerns
            concerns = self.security.scan_file_content(code)
            if concerns:
                return f"Security concerns found: {', '.join(concerns)}"
            
            # Write the code to file
            result = await file_writer({
                "file_path": file_path,
                "content": code
            })
            
            if result["status"] == "success":
                # Compute and log the file hash
                file_hash = self.security.compute_file_hash(file_path)
                self.security.log_security_event(
                    "FILE_CREATION",
                    f"Created {filename} with hash {file_hash}"
                )
                return f"Code successfully saved to {file_path}"
            else:
                return f"Error saving code: {result['message']}"
                
        except Exception as e:
            return f"Error: {str(e)}"

async def main():
    """
    Main function to demonstrate the code assistant's capabilities.
    """
    app = CodeAssistantApp()
    
    # Example code generation tasks
    tasks = [
        {
            "description": "Create a function that calculates the factorial of a number recursively",
            "filename": "factorial.py"
        },
        {
            "description": "Create a secure password generator function",
            "filename": "password_gen.py"
        }
    ]
    
    # Process each task
    for task in tasks:
        print(f"\nGenerating code for: {task['description']}")
        result = await app.generate_code(
            task['description'],
            task['filename']
        )
        print(result)
        
        # If file was created, verify its size
        file_path = f"output/{task['filename']}"
        if Path(file_path).exists():
            if app.security.verify_file_size(file_path):
                print("File size check passed")
            else:
                print("Warning: File size exceeds limits")

if __name__ == "__main__":
    asyncio.run(main())