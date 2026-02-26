#!/usr/bin/env python
"""
Test script for RAG QA system — run from project root:
  python test_rag.py
"""
import os
import sys


# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.rag.qa import answer_query

def test_rag():
    print("Testing RAG QA system...")
    try:
        user_info = {
            "user_id": "test-user",
            "name": "Test Patient",
            "age": 45,
            "gender": "Male",
            "allergies": ["Penicillin"]
        }
        past_reports = [
            {"report_date": "2026-02-01", "summary": "Blood pressure normal, glucose slightly elevated"}
        ]
        
        question = "What are common causes of fever in adults?"
        print(f"\nQuestion: {question}")
        print(f"User: {user_info.get('name')}")
        print(f"Past reports: {len(past_reports)}")
        
        response = answer_query(question, user_info=user_info, past_reports=past_reports, top_k=5)
        
        print("\n--- Response ---")
        if isinstance(response, dict):
            if "choices" in response:
                print(response["choices"][0]["message"]["content"])
            else:
                print(response)
        else:
            print(response)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_rag()
