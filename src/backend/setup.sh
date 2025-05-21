
#!/bin/bash

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Print instructions
echo ""
echo "Setup complete! To run the UXAgent backend:"
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Set your OpenAI API key:"
echo "   export OPENAI_API_KEY=your-api-key"
echo ""
echo "3. Start the API server:"
echo "   python api.py"
echo ""
echo "The API will be available at: http://localhost:8000"
