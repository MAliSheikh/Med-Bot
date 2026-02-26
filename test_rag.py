#!/usr/bin/env python
"""
Test script for RAG QA system — run from project root:
  python test_rag.py
"""
import os
import sys
import asyncio
import signal
from datetime import datetime


# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Patch signal for Windows to avoid AttributeError
if sys.platform == 'win32':
    if not hasattr(signal, 'SIGALRM'):
        signal.SIGALRM = 14  # Dummy value
    if not hasattr(signal, 'alarm'):
        signal.alarm = lambda x: None
    
    # Patch signal.signal to ignore SIGALRM on Windows
    _original_signal = signal.signal
    def _signal_wrapper(sig, handler):
        if sig == signal.SIGALRM:
            return None
        return _original_signal(sig, handler)
    signal.signal = _signal_wrapper

from services.rag.qa import answer_query
from db.conn import users_collection
from api.func.reports.reports import create_report

async def test_rag():
    print("Testing RAG QA system...")
    
    # Create dummy user
    user_data = {
        "name": "Test Patient",
        "age": 45,
        "gender": "Male",
        "allergies": ["Penicillin"],
        "email": "test_rag_user@example.com"
    }
    
    # Clean up existing test user if any
    await users_collection.delete_many({"email": "test_rag_user@example.com"})
    
    insert_result = await users_collection.insert_one(user_data)
    user_id = str(insert_result.inserted_id)
    print(f"Created test user: {user_id}")

    try:
        # Create dummy report
        report_doc = {
            "user_id": user_id,
            "filename": "test_report.pdf",
            "uploaded_at": datetime.now(),
            "report_data": {
                "summary": "Blood pressure normal, glucose slightly elevated",
                "report_date": "2026-02-01"
            }
        }
        await create_report(report_doc)
        print("Created test report")
        
        question = "What are common causes of fever in adults?"
        print(f"\nQuestion: {question}")
        print(f"User ID: {user_id}")
        
        response = await answer_query(question, user_id=user_id, top_k=5)
        
        print("\n--- Response ---")
        # The response object from the OpenAI client is not a dict. Access content directly.
        print(response.choices[0].message.content.strip())
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        print("Cleaning up...")
        await users_collection.delete_one({"_id": insert_result.inserted_id})

if __name__ == "__main__":
    asyncio.run(test_rag())
