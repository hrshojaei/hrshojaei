#!/bin/bash
# Setup script for AI Calling Agent

set -e  # Exit on error

echo "🚀 AI Calling Agent - Setup Script"
echo "===================================="
echo ""

# Check Python version
echo "1️⃣  Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Python $PYTHON_VERSION found"
echo ""

# Create virtual environment
echo "2️⃣  Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Skipping."
else
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "3️⃣  Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Install dependencies
echo "4️⃣  Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Create .env file
echo "5️⃣  Setting up configuration..."
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists. Skipping."
else
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file with your credentials:"
    echo "   - TWILIO_ACCOUNT_SID"
    echo "   - TWILIO_AUTH_TOKEN"
    echo "   - TWILIO_PHONE_NUMBER"
    echo "   - ANTHROPIC_API_KEY or OPENAI_API_KEY"
    echo "   - PUBLIC_URL (set after starting ngrok)"
fi
echo ""

# Create directories
echo "6️⃣  Creating directories..."
mkdir -p data
mkdir -p logs
mkdir -p scripts
echo "✅ Directories created"
echo ""

# Initialize database
echo "7️⃣  Initializing database..."
python -m src.candidate_manager init
echo "✅ Database initialized"
echo ""

# Make scripts executable
echo "8️⃣  Making scripts executable..."
chmod +x scripts/*.py scripts/*.sh 2>/dev/null || true
echo "✅ Scripts made executable"
echo ""

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "==========="
echo ""
echo "1. Edit .env file with your API credentials:"
echo "   nano .env"
echo ""
echo "2. Install ngrok (if not already installed):"
echo "   https://ngrok.com/download"
echo ""
echo "3. Start ngrok in a separate terminal:"
echo "   ngrok http 8000"
echo ""
echo "4. Copy ngrok URL and set PUBLIC_URL in .env:"
echo "   PUBLIC_URL=https://your-ngrok-url.ngrok.io"
echo ""
echo "5. Start the server:"
echo "   source venv/bin/activate"
echo "   python -m src.main server"
echo ""
echo "6. Make a test call:"
echo "   python -m src.main call +4915112345678"
echo ""
echo "📚 For detailed instructions, see QUICKSTART.md"
echo ""
