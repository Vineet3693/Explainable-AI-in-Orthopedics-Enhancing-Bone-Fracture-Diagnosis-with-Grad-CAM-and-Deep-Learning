"""
Generate Report Script

PURPOSE:
    Standalone script to generate radiology reports from X-ray images.

USAGE:
    python scripts/generate_report.py --image path/to/xray.jpg --output report.txt
"""

import argparse
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.llm_integration.gemini_client import GeminiClient
from src.prompts.gemini.report_generation import generate_radiology_report_prompt
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description='Generate radiology report')
    parser.add_argument('--image', required=True, help='Path to X-ray image')
    parser.add_argument('--output', default='report.txt', help='Output file')
    parser.add_argument('--prediction', default='fracture', help='AI prediction')
    parser.add_argument('--confidence', type=float, default=0.95, help='Confidence')
    parser.add_argument('--anatomy', default='wrist', help='Anatomy')
    
    args = parser.parse_args()
    
    # Generate prompt
    prompt = generate_radiology_report_prompt(
        prediction=args.prediction,
        confidence=args.confidence,
        anatomy=args.anatomy,
        image_quality=85
    )
    
    # Generate report
    client = GeminiClient()
    report = client.generate_text(prompt)
    
    # Save report
    with open(args.output, 'w') as f:
        f.write(report)
    
    print(f"Report generated: {args.output}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
