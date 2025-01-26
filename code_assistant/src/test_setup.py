from dotenv import load_dotenv
from assistant import initialize_client, create_code_assistant

def test_environment():
    # Test environment variables
    load_dotenv()
    client = initialize_client()
    
    # Test assistant creation
    assistant_id = create_code_assistant(client)
    print(f"Successfully created assistant with ID: {assistant_id}")

if __name__ == "__main__":
    test_environment()