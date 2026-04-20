"""
Interactive Q&A Script

PURPOSE:
    Interactive command-line Q&A session about fractures.

USAGE:
    python scripts/interactive_qa.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.qa_system.answer_generator import AnswerGenerator
import logging

logging.basicConfig(level=logging.INFO)


def main():
    print("=== Fracture Detection AI - Interactive Q&A ===")
    print("Ask questions about fractures. Type 'quit' to exit.\n")
    
    generator = AnswerGenerator()
    
    while True:
        question = input("Your question: ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not question:
            continue
        
        # Generate answer
        answer = generator.generate_answer(question)
        print(f"\nAnswer: {answer}\n")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
