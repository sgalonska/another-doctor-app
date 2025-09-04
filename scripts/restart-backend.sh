#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔄 Restarting Another Doctor Backend${NC}"
echo "========================================"

# Function to check if backend is running
check_backend_running() {
    # Check if port 8000 is in use
    if lsof -ti:8000 >/dev/null 2>&1; then
        return 0  # Backend is running
    fi
    
    # Check for uvicorn processes
    if ps aux | grep "uvicorn.*app.main:app" | grep -v grep >/dev/null 2>&1; then
        return 0  # Backend is running
    fi
    
    # Check for python backend processes
    if ps aux | grep "python.*app/main.py\|python.*main:app" | grep -v grep >/dev/null 2>&1; then
        return 0  # Backend is running
    fi
    
    return 1  # Backend is not running
}

# Function to find and kill backend processes
kill_backend_processes() {
    echo -e "${YELLOW}🔍 Looking for existing backend processes...${NC}"
    
    # Find processes running on port 8000
    PORT_PIDS=$(lsof -ti:8000 2>/dev/null || true)
    
    # Find uvicorn processes
    UVICORN_PIDS=$(ps aux | grep "uvicorn.*app.main:app" | grep -v grep | awk '{print $2}' || true)
    
    # Find python processes running the backend
    PYTHON_PIDS=$(ps aux | grep "python.*app/main.py\|python.*main:app" | grep -v grep | awk '{print $2}' || true)
    
    # Combine all PIDs and remove duplicates
    ALL_PIDS=$(echo "$PORT_PIDS $UVICORN_PIDS $PYTHON_PIDS" | tr ' ' '\n' | sort -u | grep -v '^$' || true)
    
    if [ -n "$ALL_PIDS" ]; then
        echo -e "${YELLOW}📋 Found processes: $ALL_PIDS${NC}"
        
        for PID in $ALL_PIDS; do
            if kill -0 "$PID" 2>/dev/null; then
                echo -e "${YELLOW}🛑 Killing process $PID...${NC}"
                kill -TERM "$PID" 2>/dev/null || true
                
                # Give it a moment to gracefully shut down
                sleep 2
                
                # Force kill if still running
                if kill -0 "$PID" 2>/dev/null; then
                    echo -e "${RED}⚡ Force killing process $PID...${NC}"
                    kill -KILL "$PID" 2>/dev/null || true
                fi
            fi
        done
        
        echo -e "${GREEN}✅ All backend processes stopped${NC}"
    else
        echo -e "${GREEN}✅ No existing backend processes found${NC}"
    fi
}

# Function to wait for port to be free
wait_for_port_free() {
    echo -e "${YELLOW}⏳ Waiting for port 8000 to be free...${NC}"
    
    # Wait up to 10 seconds for port to be free
    for i in {1..10}; do
        if ! lsof -ti:8000 >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Port 8000 is free${NC}"
            return 0
        fi
        sleep 1
        echo -n "."
    done
    
    echo -e "${RED}❌ Port 8000 is still busy after 10 seconds${NC}"
    echo -e "${YELLOW}🔍 Processes still using port 8000:${NC}"
    lsof -i:8000 || true
    return 1
}

# Check if backend is already running
if check_backend_running; then
    echo -e "${YELLOW}⚠️  Backend is currently running - stopping existing processes${NC}"
    # Kill existing processes
    kill_backend_processes
    
    # Wait for port to be free
    wait_for_port_free
else
    echo -e "${GREEN}✅ No backend processes running - starting fresh${NC}"
fi

# Start the backend
echo -e "${BLUE}🚀 Starting new backend instance...${NC}"

# Change to backend directory
cd "$(dirname "$0")/../apps/backend"

# Check if we should run the existing script or start directly
if [ -f "./scripts/run-backend-local.sh" ]; then
    echo -e "${GREEN}📝 Using existing startup script${NC}"
    exec ./scripts/run-backend-local.sh
else
    echo -e "${YELLOW}📝 Starting backend directly${NC}"
    
    # Ensure virtual environment exists
    if [ ! -d "venv" ]; then
        echo -e "${BLUE}🐍 Creating virtual environment...${NC}"
        python3 -m venv venv
    fi
    
    # Activate virtual environment and start
    source venv/bin/activate
    
    echo -e "${BLUE}📦 Installing dependencies...${NC}"
    pip install -r requirements.txt
    
    echo -e "${BLUE}🗄️  Running migrations...${NC}"
    alembic upgrade head || true
    
    echo -e "${GREEN}🎉 Starting uvicorn server...${NC}"
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
fi