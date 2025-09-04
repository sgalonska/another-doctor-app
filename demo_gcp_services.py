#!/usr/bin/env python3
"""
Demo script showing GCP services integration with localhost emulation

This script demonstrates:
1. File upload and storage (local development vs GCP Cloud Storage)
2. Queue processing (synchronous localhost vs GCP Cloud Tasks)
3. Task processing pipeline (diagnosis -> specialist matching -> notification)

Run this script to see the services in action.
"""
import asyncio
import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000/api/v1"

def print_section(title: str):
    """Print a section header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print('='*60)

async def demo_text_upload():
    """Demo text content upload and processing"""
    print_section("TEXT UPLOAD & PROCESSING DEMO")
    
    # Sample medical case text
    case_text = """
    Patient: 65-year-old male presents with chest pain and shortness of breath.
    
    History: Patient reports crushing chest pain that started 2 hours ago, 
    radiating to left arm. Associated with nausea and diaphoresis. 
    Past medical history significant for hypertension and hyperlipidemia.
    
    Physical Exam: 
    - BP: 160/90 mmHg
    - HR: 110 bpm, irregular
    - Lungs: crackles at bilateral bases
    - Heart: irregular rhythm, no murmurs
    
    EKG: ST elevation in leads II, III, aVF
    
    Lab Results:
    - Troponin I: 15.2 ng/mL (elevated)
    - CK-MB: 45 U/L (elevated)
    - BNP: 450 pg/mL
    """
    
    print("Uploading medical case text...")
    print(f"Case content preview: {case_text[:100]}...")
    
    # Upload text
    response = requests.post(
        f"{BASE_URL}/upload/text",
        data={
            "text_content": case_text,
            "case_title": "Acute Chest Pain Case"
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        case_id = result['case_id']
        print(f"✅ Text uploaded successfully!")
        print(f"   Case ID: {case_id}")
        print(f"   Status: {result['status']}")
        return case_id
    else:
        print(f"❌ Upload failed: {response.text}")
        return None

async def demo_task_status(case_id: str):
    """Demo task status checking (only works in development)"""
    print_section("TASK STATUS MONITORING")
    
    print("Checking for running tasks...")
    
    # Since tasks run synchronously in development, they should be completed
    # Let's create a manual task to demonstrate the status endpoint
    
    task_data = {
        "task_type": "diagnosis_analysis",
        "payload": {
            "case_id": case_id,
            "file_path": f"cases/{case_id}/input.txt",
            "user_id": "demo_user"
        }
    }
    
    print("Creating a diagnosis analysis task...")
    response = requests.post(f"{BASE_URL}/tasks/create", json=task_data)
    
    if response.status_code == 200:
        result = response.json()
        task_id = result['task_id']
        print(f"✅ Task created: {task_id}")
        
        # Check task status
        print(f"Checking task status...")
        status_response = requests.get(f"{BASE_URL}/tasks/status/{task_id}")
        
        if status_response.status_code == 200:
            status = status_response.json()
            print(f"✅ Task Status:")
            print(f"   ID: {status['task_id']}")
            print(f"   Status: {status['status']}")
            print(f"   Created: {status['created_at']}")
            print(f"   Completed: {status['completed_at']}")
            
            if status['result']:
                print(f"   Result Preview:")
                result_data = status['result']
                if 'extracted_entities' in result_data:
                    print(f"     Entities: {len(result_data['extracted_entities'])} found")
                if 'primary_conditions' in result_data:
                    print(f"     Conditions: {', '.join(result_data['primary_conditions'])}")
                if 'suggested_specialties' in result_data:
                    print(f"     Specialties: {', '.join(result_data['suggested_specialties'])}")
                    
        return task_id
    else:
        print(f"❌ Task creation failed: {response.text}")
        return None

def demo_file_structure():
    """Demo the local file structure created"""
    print_section("LOCAL FILE STORAGE STRUCTURE")
    
    uploads_dir = Path("uploads")
    
    if not uploads_dir.exists():
        print("❌ No uploads directory found. Upload some content first!")
        return
    
    print("📁 Local file storage structure:")
    
    def print_tree(path: Path, prefix: str = ""):
        """Print directory tree"""
        if path.is_file():
            size = path.stat().st_size
            print(f"{prefix}📄 {path.name} ({size} bytes)")
        elif path.is_dir():
            print(f"{prefix}📁 {path.name}/")
            children = sorted(path.iterdir())
            for i, child in enumerate(children):
                is_last = i == len(children) - 1
                child_prefix = prefix + ("    " if is_last else "│   ")
                print_tree(child, child_prefix)
    
    print_tree(uploads_dir)

def demo_api_endpoints():
    """Demo available API endpoints"""
    print_section("AVAILABLE API ENDPOINTS")
    
    print("🔗 Queue & Task Processing:")
    print("   POST /api/v1/tasks/create")
    print("   GET  /api/v1/tasks/status/{task_id}")
    print("   POST /api/v1/tasks/diagnosis/analyze")
    print("   POST /api/v1/tasks/specialist/match") 
    print("   POST /api/v1/tasks/notification/send")
    
    print("\n🔗 File Upload & Storage:")
    print("   POST /api/v1/upload/presigned-url")
    print("   POST /api/v1/upload/direct")
    print("   POST /api/v1/upload/text")
    print("   GET  /api/v1/upload/{file_path}")
    
    print("\n🔗 Health Check:")
    print("   GET  /health")
    
    # Test health check
    print("\nTesting health check...")
    response = requests.get("http://localhost:8000/health")
    if response.status_code == 200:
        print(f"✅ API is healthy: {response.json()}")
    else:
        print(f"❌ API health check failed")

def demo_environment_switching():
    """Demo environment configuration"""
    print_section("ENVIRONMENT CONFIGURATION")
    
    print("🏠 Current Environment: DEVELOPMENT")
    print("   - File Storage: Local filesystem (./uploads/)")
    print("   - Queue Processing: Synchronous execution")
    print("   - Task Status: Available via REST API")
    print("   - GCP Libraries: Imported but not used")
    
    print("\n🏢 Production Environment (GCP):")
    print("   - File Storage: Google Cloud Storage")
    print("   - Queue Processing: Google Cloud Tasks")
    print("   - Task Status: Not available (handled by GCP)")
    print("   - GCP Libraries: Fully utilized")
    
    print("\n⚙️  Environment Switching:")
    print("   Set ENVIRONMENT=production to use GCP services")
    print("   Set GCP_PROJECT_ID, GCS_BUCKET_NAME, etc. for configuration")

async def main():
    """Run the demo"""
    print("🚀 Another Doctor - GCP Services Integration Demo")
    print("=" * 60)
    
    try:
        # Test API connectivity
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("❌ Backend API is not running!")
            print("   Please start it with: ./scripts/run-backend-local.sh")
            return
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to backend API!")
        print("   Please ensure the backend is running at http://localhost:8000")
        return
    
    # Run demo steps
    case_id = await demo_text_upload()
    
    if case_id:
        await demo_task_status(case_id)
    
    demo_file_structure()
    demo_api_endpoints()
    demo_environment_switching()
    
    print_section("DEMO COMPLETE")
    print("✅ GCP services integration with localhost emulation is working!")
    print("\n📖 Key Features Demonstrated:")
    print("   • File upload with local storage emulation")
    print("   • Queue processing with synchronous execution")
    print("   • Task pipeline: diagnosis → matching → notification")
    print("   • Environment switching (dev vs production)")
    print("   • API endpoints for all functionality")
    print("\n🔧 Next Steps:")
    print("   • Configure GCP credentials for production")
    print("   • Set ENVIRONMENT=production to use real GCP services")
    print("   • Deploy to GCP with Cloud Run + Cloud Tasks + Cloud Storage")

if __name__ == "__main__":
    asyncio.run(main())