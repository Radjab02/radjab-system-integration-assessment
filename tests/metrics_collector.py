#!/usr/bin/env python3
"""
Metrics Collector
Collects real-time metrics from all system components
"""
import requests
import time
import json
from datetime import datetime
from typing import Dict, Any
import sys


class MetricsCollector:
    """Collect metrics from system components"""
    
    def __init__(self):
        self.mock_api_url = "http://localhost:8081"
        self.java_producer_url = "http://localhost:8082"
        self.kafka_ui_url = "http://localhost:8090"
        
        self.metrics_history = []
    
    def collect_java_producer_metrics(self) -> Dict[str, Any]:
        """Collect metrics from Java Producers"""
        try:
            # Get sync status
            response = requests.get(
                f"{self.java_producer_url}/api/sync/status",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'customer': {
                        'total_synced': data.get('customer', {}).get('totalRecordsSynced', 0),
                        'last_sync_count': data.get('customer', {}).get('lastSyncRecordCount', 0),
                        'last_sync_time': data.get('customer', {}).get('lastSyncTime', 'N/A')
                    },
                    'inventory': {
                        'total_synced': data.get('inventory', {}).get('totalRecordsSynced', 0),
                        'last_sync_count': data.get('inventory', {}).get('lastSyncRecordCount', 0),
                        'last_sync_time': data.get('inventory', {}).get('lastSyncTime', 'N/A')
                    }
                }
        except Exception as e:
            return {'error': str(e)}
    
    def collect_mock_api_metrics(self) -> Dict[str, Any]:
        """Collect metrics from Mock APIs"""
        try:
            # Get actuator health
            response = requests.get(
                f"{self.mock_api_url}/actuator/health",
                timeout=5
            )
            
            return {
                'status': response.json().get('status', 'UNKNOWN'),
                'response_time_ms': response.elapsed.total_seconds() * 1000
            }
        except Exception as e:
            return {'error': str(e)}
    
    def collect_all_metrics(self) -> Dict[str, Any]:
        """Collect all system metrics"""
        timestamp = datetime.now().isoformat()
        
        metrics = {
            'timestamp': timestamp,
            'java_producers': self.collect_java_producer_metrics(),
            'mock_api': self.collect_mock_api_metrics()
        }
        
        self.metrics_history.append(metrics)
        return metrics
    
    def monitor(self, duration_seconds=300, interval_seconds=10):
        """
        Monitor system continuously
        
        Args:
            duration_seconds: How long to monitor
            interval_seconds: Sampling interval
        """
        print("=" * 80)
        print("SYSTEM MONITORING")
        print("=" * 80)
        print(f"Duration: {duration_seconds} seconds")
        print(f"Interval: {interval_seconds} seconds")
        print("=" * 80)
        print()
        
        start_time = time.time()
        
        while (time.time() - start_time) < duration_seconds:
            metrics = self.collect_all_metrics()
            
            # Print current metrics
            elapsed = time.time() - start_time
            print(f"\n[{elapsed:.1f}s] Metrics:")
            print(f"  Mock API: {metrics['mock_api'].get('status', 'ERROR')}")
            
            java_metrics = metrics.get('java_producers', {})
            if 'error' not in java_metrics:
                customer = java_metrics.get('customer', {})
                inventory = java_metrics.get('inventory', {})
                print(f"  Java Producers:")
                print(f"    Customers: {customer.get('total_synced', 0)} total, "
                      f"{customer.get('last_sync_count', 0)} last sync")
                print(f"    Inventory: {inventory.get('total_synced', 0)} total, "
                      f"{inventory.get('last_sync_count', 0)} last sync")
            
            time.sleep(interval_seconds)
        
        self._save_metrics()
        self._print_summary()
    
    def _save_metrics(self):
        """Save metrics to file"""
        filename = f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.metrics_history, f, indent=2)
        
        print(f"\n\nMetrics saved to: {filename}")
    
    def _print_summary(self):
        """Print metrics summary"""
        if not self.metrics_history:
            return
        
        print("\n" + "=" * 80)
        print("METRICS SUMMARY")
        print("=" * 80)
        
        # Calculate totals
        total_customers = 0
        total_inventory = 0
        
        for metric in self.metrics_history:
            java_metrics = metric.get('java_producers', {})
            if 'error' not in java_metrics:
                customer = java_metrics.get('customer', {})
                inventory = java_metrics.get('inventory', {})
                
                total_customers = max(total_customers, customer.get('total_synced', 0))
                total_inventory = max(total_inventory, inventory.get('total_synced', 0))
        
        print(f"Total Customers Synced: {total_customers}")
        print(f"Total Inventory Synced: {total_inventory}")
        print(f"Total Records: {total_customers + total_inventory}")
        print("=" * 80)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='System Metrics Collector')
    parser.add_argument('--duration', type=int, default=300,
                       help='Monitoring duration in seconds (default: 300)')
    parser.add_argument('--interval', type=int, default=10,
                       help='Sampling interval in seconds (default: 10)')
    
    args = parser.parse_args()
    
    collector = MetricsCollector()
    
    try:
        collector.monitor(
            duration_seconds=args.duration,
            interval_seconds=args.interval
        )
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user")
        collector._save_metrics()
        collector._print_summary()


if __name__ == "__main__":
    main()
