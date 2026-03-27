#!/bin/bash
# Quick setup script for Ghost DB

echo "🚀 Ghost DB Setup"
echo "================="
echo ""

# Add ghost to PATH
export PATH="/Users/atin5551/.local/bin:${PATH}"

echo "Step 1: Login to Ghost"
echo "----------------------"
echo "Running: ghost login"
echo ""
ghost login

echo ""
echo "Step 2: Create Database"
echo "----------------------"
echo "Running: ghost create --name research-agent-db"
echo ""
ghost create --name research-agent-db --wait

echo ""
echo "Step 3: Get Connection String"
echo "----------------------------"
echo "Running: ghost list"
echo ""
DB_ID=$(ghost list --json | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)

if [ -n "$DB_ID" ]; then
    echo "Database ID: $DB_ID"
    echo ""
    echo "Getting connection string..."
    CONN_STRING=$(ghost connect $DB_ID)
    
    echo ""
    echo "✅ Success! Add this to your .env file:"
    echo ""
    echo "MASTER_DATABASE_URL=$CONN_STRING"
    echo ""
else
    echo "❌ Could not find database ID. Run 'ghost list' to see your databases."
fi

echo ""
echo "Step 4: Initialize Schema"
echo "------------------------"
if [ -n "$CONN_STRING" ]; then
    echo "Running schema scripts..."
    psql "$CONN_STRING" < db/master_schema.sql
    psql "$CONN_STRING" < db/job_schema.sql
    echo "✅ Schema initialized!"
else
    echo "⚠️  Run these manually after getting connection string:"
    echo "  psql \$MASTER_DATABASE_URL < db/master_schema.sql"
    echo "  psql \$MASTER_DATABASE_URL < db/job_schema.sql"
fi

echo ""
echo "🎉 Setup complete! Now run:"
echo "  cd agents/research"
echo "  pip install -r requirements.txt"
echo "  python example.py"
