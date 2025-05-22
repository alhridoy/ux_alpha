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

# Install Playwright browsers
echo "Installing Playwright browsers..."
python -m playwright install

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOL
# API Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
BROWSERBASE_API_KEY=your_browserbase_api_key_here
BROWSERBASE_PROJECT_ID=your_browserbase_project_id_here

# Configuration
USE_BROWSERBASE=false
HEADLESS=false
DEFAULT_MODEL=gpt-4o
EOL
    echo ".env file created. Please update it with your API keys."
fi

# Print instructions
echo ""
echo "Setup complete! To run the UX Agent Simulator:"
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Update your API keys in the .env file"
echo ""
echo "3. Start the API server:"
echo "   python src/backend/api.py"
echo ""
echo "The API will be available at: http://localhost:8000"
