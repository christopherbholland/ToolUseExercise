# ToolUseExercise
## Code Assistant with OpenAI

A secure Python application for generating code using OpenAI's Assistant API.

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Unix
venv\Scripts\activate     # Windows
```

2. Install dependencies:
```bash
pip install openai python-dotenv
```

3. Configure environment:
- Create `.env` file in project root
- Add OpenAI API key:
```
OPENAI_API_KEY=your-key-here
```

## Project Structure
```
project_root/
├── config/
│   └── tasks.json       # Code generation tasks
├── src/
│   ├── assistant.py     # OpenAI integration
│   ├── security.py      # Security validation
│   └── tools.py         # File operations
├── output/              # Generated code
└── main.py             # Application entry
```

## Usage

1. Define tasks in `config/tasks.json`:
```json
{
    "tasks": [
        {
            "description": "Task description",
            "filename": "output_file.py"
        }
    ]
}
```

2. Run application:
```bash
python main.py
```

Generated code appears in `output/` directory.

## Security Features

- File path validation
- Code content scanning
- Size limit enforcement
- Operation logging
- Atomic file writes

## Best Practices

- Keep API key secure
- Review generated code
- Check security logs
- Monitor file sizes

## License

MIT
