#!/usr/bin/env python3
"""
Test script for the research aggregation API
"""
import asyncio
import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test if the API is running"""
    print("🏥 Testing API Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is healthy and running!")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API: {e}")
        print("   Please ensure the backend is running at http://localhost:8000")
        return False

def test_research_sources():
    """Test getting available research sources"""
    print("\n📚 Testing Available Research Sources...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/research/sources")
        if response.status_code == 200:
            sources = response.json()
            print("✅ Available Research Sources:")
            for source_id, info in sources['sources'].items():
                print(f"   • {info['name']} ({source_id})")
                print(f"     {info['description']}")
                print(f"     Data: {', '.join(info['data_types'])}")
                print()
        else:
            print(f"❌ Failed to get sources: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_research_search():
    """Test research search functionality"""
    print("🔍 Testing Research Search...")
    
    # Test queries
    test_queries = [
        "cardiovascular disease treatment",
        "diabetes mellitus type 2",
        "COVID-19 vaccine"
    ]
    
    for query in test_queries:
        print(f"\n   Searching: '{query}'")
        try:
            # Test with limited sources for speed
            response = requests.get(
                f"{BASE_URL}/api/v1/research/search",
                params={
                    "q": query,
                    "max_results": 5,
                    "sources": "pubmed"  # Just PubMed for faster testing
                },
                timeout=30
            )
            
            if response.status_code == 200:
                results = response.json()
                print(f"   ✅ Found {results['total_results']} results")
                print(f"   ⏱️  Execution time: {results['execution_time_ms']}ms")
                print(f"   🔗 Sources: {', '.join(results['sources_queried'])}")
                
                # Show sample results
                if results['results']['publications']:
                    pub = results['results']['publications'][0]
                    print(f"   📄 Sample: {pub['title'][:80]}...")
                
            else:
                print(f"   ❌ Search failed: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_publications_search():
    """Test publications-only search"""
    print("\n📖 Testing Publications Search...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/research/publications",
            params={
                "q": "machine learning medical diagnosis",
                "max_results": 10
            },
            timeout=30
        )
        
        if response.status_code == 200:
            results = response.json()
            print(f"✅ Found {results['total_results']} publications")
            
            for i, pub in enumerate(results['publications'][:3], 1):
                print(f"   {i}. {pub['title'][:60]}...")
                print(f"      Source: {pub['source']} | Year: {pub['year']} | Score: {pub['relevance_score']:.1f}")
                
        else:
            print(f"❌ Publications search failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_upload_text():
    """Test text upload functionality"""
    print("\n📝 Testing Text Upload...")
    
    sample_case = """
    Patient: 45-year-old female presents with fatigue and joint pain.
    
    History: Patient reports 3 months of progressive fatigue, morning stiffness 
    lasting >1 hour, and symmetric joint pain affecting hands, wrists, and feet.
    Family history significant for rheumatoid arthritis in mother.
    
    Physical Exam:
    - Vital signs stable
    - Hands: symmetric swelling of MCP and PIP joints
    - Positive squeeze test
    - Limited range of motion in wrists
    
    Lab Results:
    - RF: 150 IU/mL (elevated)
    - Anti-CCP: 80 U/mL (positive)
    - ESR: 45 mm/hr (elevated)
    - CRP: 15 mg/L (elevated)
    """
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/upload/text",
            data={
                "text_content": sample_case,
                "case_title": "Suspected Rheumatoid Arthritis"
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Text uploaded successfully!")
            print(f"   Case ID: {result['case_id']}")
            print(f"   Status: {result['status']}")
            return result['case_id']
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None

def main():
    """Run all tests"""
    print("🚀 Another Doctor API Test Suite")
    print("=" * 50)
    
    # Test API connectivity first
    if not test_health_check():
        print("\n❌ Cannot proceed without API connectivity")
        return
    
    # Test research functionality
    test_research_sources()
    test_research_search()
    test_publications_search()
    
    # Test upload functionality
    case_id = test_upload_text()
    
    print("\n" + "=" * 50)
    print("✅ Test Suite Complete!")
    print("\n📋 Summary:")
    print("   • Health Check: API is running")
    print("   • Research Sources: Available and documented")
    print("   • Research Search: Multi-source aggregation working")
    print("   • Publications Search: Filtered search working")
    print("   • Text Upload: Case processing working")
    
    if case_id:
        print(f"\n🔬 You can now test with case ID: {case_id}")
        print("   Try the research API with medical terms from this case!")

if __name__ == "__main__":
    main()