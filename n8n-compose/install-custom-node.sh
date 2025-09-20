#!/bin/bash

echo "🔧 Installing Job Text Splitter custom n8n node..."

# Navigate to the custom node directory
cd /Users/gareth/cyber/n8n_selfhost/n8n-compose/custom-nodes/n8n-nodes-job-text-splitter

# Check if node modules exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install --production
else
    echo "✅ Dependencies already installed"
fi

# Build the node
echo "🏗️ Building the node..."
npm run build

echo "✅ Job Text Splitter node installed successfully!"
echo ""
echo "Next steps:"
echo "1. Restart n8n: cd /Users/gareth/cyber/n8n_selfhost/n8n-compose && docker-compose restart n8n"
echo "2. Look for 'Job Text Splitter' in the Transform category"
echo "3. Connect it after your Lambda function node"