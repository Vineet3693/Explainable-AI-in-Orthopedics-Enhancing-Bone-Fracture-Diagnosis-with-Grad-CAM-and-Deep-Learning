"""
Export Metrics Script

PURPOSE:
    Exports metrics to various formats (CSV, JSON) for analysis.
    Useful for reporting and data analysis.

USAGE:
    python scripts/export_metrics.py --format csv --output metrics.csv
"""

import argparse
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
import csv
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def export_to_csv(metrics: list, output_file: str):
    """Export metrics to CSV"""
    logger.info(f"Exporting to CSV: {output_file}")
    
    with open(output_file, 'w', newline='') as f:
        if metrics:
            writer = csv.DictWriter(f, fieldnames=metrics[0].keys())
            writer.writeheader()
            writer.writerows(metrics)
    
    logger.info(f"  ✓ Exported {len(metrics)} metrics")


def export_to_json(metrics: list, output_file: str):
    """Export metrics to JSON"""
    logger.info(f"Exporting to JSON: {output_file}")
    
    with open(output_file, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    logger.info(f"  ✓ Exported {len(metrics)} metrics")


def main():
    parser = argparse.ArgumentParser(description='Export metrics')
    parser.add_argument('--format', choices=['csv', 'json'], default='csv')
    parser.add_argument('--output', required=True, help='Output file')
    
    args = parser.parse_args()
    
    # Sample metrics (in production, would fetch from Prometheus)
    metrics = [
        {'timestamp': datetime.now().isoformat(), 'metric': 'api_latency', 'value': 1.5},
        {'timestamp': datetime.now().isoformat(), 'metric': 'predictions_total', 'value': 100},
    ]
    
    if args.format == 'csv':
        export_to_csv(metrics, args.output)
    else:
        export_to_json(metrics, args.output)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
