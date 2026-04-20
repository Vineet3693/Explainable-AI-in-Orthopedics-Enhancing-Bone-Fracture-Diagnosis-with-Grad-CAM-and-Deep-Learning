"""
Test Q&A System - Tests for Question Answering

PURPOSE:
    Tests Q&A system components including classifier and generator.

USAGE:
    pytest tests/test_qa_system.py -v
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.qa_system.question_classifier import QuestionClassifier
from src.qa_system.knowledge_base import KnowledgeBase


class TestQuestionClassifier:
    """Test question classification"""
    
    @pytest.fixture
    def classifier(self):
        return QuestionClassifier()
    
    def test_treatment_question(self, classifier):
        """Test treatment question classification"""
        category = classifier.classify("What is the treatment for fractures?")
        assert category == 'treatment'
    
    def test_recovery_question(self, classifier):
        """Test recovery question classification"""
        category = classifier.classify("How long will recovery take?")
        assert category == 'recovery'


class TestKnowledgeBase:
    """Test knowledge base"""
    
    @pytest.fixture
    def kb(self):
        return KnowledgeBase()
    
    def test_exact_match(self, kb):
        """Test exact question match"""
        answer = kb.get_answer("what is a fracture")
        assert answer is not None
        assert 'break' in answer['answer'].lower()
    
    def test_fuzzy_match(self, kb):
        """Test fuzzy question matching"""
        answer = kb.get_answer("what's a fracture")
        assert answer is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
