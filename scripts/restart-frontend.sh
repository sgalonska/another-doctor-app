#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔄 Restarting Another Doctor Frontend${NC}"
echo "========================================"

# Function to check if frontend is running
check_frontend_running() {
    # Check if port 3000 is in use
    if lsof -ti:3000 >/dev/null 2>&1; then
        return 0  # Frontend is running
    fi
    
    # Check for next.js/npm processes
    if ps aux | grep "next\|npm.*run.*dev\|npm.*start" | grep -v grep >/dev/null 2>&1; then
        return 0  # Frontend is running
    fi
    
    # Check for node frontend processes
    if ps aux | grep "node.*3000\|node.*next\|node.*frontend" | grep -v grep >/dev/null 2>&1; then
        return 0  # Frontend is running
    fi
    
    return 1  # Frontend is not running
}

# Function to find and kill frontend processes
kill_frontend_processes() {
    echo -e "${YELLOW}🔍 Looking for existing frontend processes...${NC}"
    
    # Find processes running on port 3000
    PORT_PIDS=$(lsof -ti:3000 2>/dev/null || true)
    
    # Find next.js/npm processes
    NEXT_PIDS=$(ps aux | grep "next\|npm.*run.*dev\|npm.*start" | grep -v grep | awk '{print $2}' || true)
    
    # Find node processes that might be the frontend
    NODE_PIDS=$(ps aux | grep "node.*3000\|node.*next\|node.*frontend" | grep -v grep | awk '{print $2}' || true)
    
    # Combine all PIDs and remove duplicates
    ALL_PIDS=$(echo "$PORT_PIDS $NEXT_PIDS $NODE_PIDS" | tr ' ' '\n' | sort -u | grep -v '^$' || true)
    
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
        
        echo -e "${GREEN}✅ All frontend processes stopped${NC}"
    else
        echo -e "${GREEN}✅ No existing frontend processes found${NC}"
    fi
}

# Function to wait for port to be free
wait_for_port_free() {
    echo -e "${YELLOW}⏳ Waiting for port 3000 to be free...${NC}"
    
    # Wait up to 10 seconds for port to be free
    for i in {1..10}; do
        if ! lsof -ti:3000 >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Port 3000 is free${NC}"
            return 0
        fi
        sleep 1
        echo -n "."
    done
    
    echo -e "${RED}❌ Port 3000 is still busy after 10 seconds${NC}"
    echo -e "${YELLOW}🔍 Processes still using port 3000:${NC}"
    lsof -i:3000 || true
    return 1
}

# Check if frontend is already running
if check_frontend_running; then
    echo -e "${YELLOW}⚠️  Frontend is currently running - stopping existing processes${NC}"
    # Kill existing processes
    kill_frontend_processes
    
    # Wait for port to be free
    wait_for_port_free
else
    echo -e "${GREEN}✅ No frontend processes running - starting fresh${NC}"
fi

# Start the frontend
echo -e "${BLUE}🚀 Starting new frontend instance...${NC}"

# Change to frontend directory
cd "$(dirname "$0")/../apps/frontend"

# Check if we should run the existing script or start directly
if [ -f "./scripts/run-frontend-local.sh" ]; then
    echo -e "${GREEN}📝 Using existing startup script${NC}"
    exec ./scripts/run-frontend-local.sh
elif [ -f "../scripts/run-frontend-local.sh" ]; then
    echo -e "${GREEN}📝 Using parent startup script${NC}"
    exec ../scripts/run-frontend-local.sh
else
    echo -e "${YELLOW}📝 Starting frontend directly${NC}"
    
    # Check for package.json
    if [ ! -f "package.json" ]; then
        echo -e "${RED}❌ No package.json found in frontend directory${NC}"
        echo -e "${YELLOW}📁 Current directory: $(pwd)${NC}"
        echo -e "${YELLOW}📁 Contents:${NC}"
        ls -la
        exit 1
    fi
    
    echo -e "${BLUE}📦 Installing dependencies...${NC}"
    npm install
    
    echo -e "${GREEN}🎉 Starting development server...${NC}"
    exec npm run dev
fi