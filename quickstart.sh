#!/bin/bash

echo "🚀 Yield Curves Project - Quick Start"
echo "======================================"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env with your production database credentials"
    echo "   For local development, the defaults should work fine."
fi

# Start local services
echo "🐳 Starting local services (PostgreSQL + Redis)..."
make services-up

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 5

# Run initial migrations
echo "🔄 Running initial migrations on local database..."
make migrate-local

echo ""
echo "✅ Setup complete! Here are your next steps:"
echo ""
echo "🎯 Quick Commands:"
echo "  make run-local      # Start local development server"
echo "  make shell-local    # Open Django shell (local DB)"
echo "  make shell-admin    # Open Django shell (production DB, admin user)"
echo ""
echo "📖 See all available commands:"
echo "  make help"
echo ""
echo "🏃‍♂️ Start developing:"
echo "  make run-local"
