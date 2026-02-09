#!/usr/bin/env python3
"""
Performance Test Data Generator
Generates test data to simulate high-volume scenarios
"""
import requests
import time
import random
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import json

# Configuration
MOCK_API_BASE_URL = "http://localhost:8081"
CUSTOMER_ENDPOINT = f"{MOCK_API_BASE_URL}/api/customers"

# Test parameters
TARGET_RECORDS_PER_HOUR = 10000
TEST_DURATION_MINUTES = 5
BATCH_SIZE = 100
CONCURRENT_REQUESTS = 10


class DataGenerator:
    """Generate realistic test data"""
    
    FIRST_NAMES = ["John", "Jane", "Michael", "Sarah", "David", "Emma", "Robert", "Lisa", 
                   "James", "Mary", "William", "Patricia", "Richard", "Jennifer", "Thomas"]
    
    LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
                  "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Wilson"]
    
    CITIES = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia",
              "San Antonio", "San Diego", "Dallas", "San Jose"]
    
    STATES = ["NY", "CA", "IL", "TX", "AZ", "PA", "TX", "CA", "TX", "CA"]
    
    @staticmethod
    def generate_customer():
        """Generate a random customer"""
        first_name = random.choice(DataGenerator.FIRST_NAMES)
        last_name = random.choice(DataGenerator.LAST_NAMES)
        city_idx = random.randint(0, len(DataGenerator.CITIES) - 1)
        
        return {
            "name": f"{first_name} {last_name}",
            "email": f"{first_name.lower()}.{last_name.lower()}.{uuid.uuid4().hex[:6]}@testmail.com",
            "phone": f"+1{random.randint(1000000000, 9999999999)}",
            "address": f"{random.randint(100, 9999)} {random.choice(['Main', 'Oak', 'Maple', 'Cedar'])} St, {DataGenerator.CITIES[city_idx]}, {DataGenerator.STATES[city_idx]} {random.randint(10000, 99999)}"
        }


class PerformanceTester:
    """Performance testing orchestrator"""
    
    def __init__(self):
        self.results = {
            'total_requests': 0,
            'successful': 0,
            'failed': 0,
            'start_time': None,
            'end_time': None,
            'response_times': [],
            'errors': []
        }
    
    def send_customer(self, customer_data):
        """Send a single customer to API"""
        start = time.time()
        try:
            response = requests.post(
                CUSTOMER_ENDPOINT,
                json=customer_data,
                timeout=10
            )
            elapsed = time.time() - start
            
            if response.status_code in [200, 201]:
                return {'success': True, 'time': elapsed, 'status': response.status_code}
            else:
                return {'success': False, 'time': elapsed, 'status': response.status_code, 
                       'error': response.text}
        except Exception as e:
            elapsed = time.time() - start
            return {'success': False, 'time': elapsed, 'error': str(e)}
    
    def run_batch(self, batch_size, concurrent=False):
        """Run a batch of requests"""
        customers = [DataGenerator.generate_customer() for _ in range(batch_size)]
        
        if concurrent:
            return self._run_concurrent(customers)
        else:
            return self._run_sequential(customers)
    
    def _run_sequential(self, customers):
        """Run requests sequentially"""
        results = []
        for customer in customers:
            result = self.send_customer(customer)
            results.append(result)
            self._update_results(result)
        return results
    
    def _run_concurrent(self, customers):
        """Run requests concurrently"""
        results = []
        with ThreadPoolExecutor(max_workers=CONCURRENT_REQUESTS) as executor:
            futures = [executor.submit(self.send_customer, customer) for customer in customers]
            
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                self._update_results(result)
        
        return results
    
    def _update_results(self, result):
        """Update test results"""
        self.results['total_requests'] += 1
        
        if result['success']:
            self.results['successful'] += 1
        else:
            self.results['failed'] += 1
            self.results['errors'].append(result.get('error', 'Unknown error'))
        
        self.results['response_times'].append(result['time'])
    
    def run_throughput_test(self, target_per_hour=10000, duration_minutes=5):
        """
        Test if system can handle target throughput
        
        Args:
            target_per_hour: Target records per hour
            duration_minutes: Test duration in minutes
        """
        print("=" * 80)
        print("THROUGHPUT TEST")
        print("=" * 80)
        print(f"Target: {target_per_hour} records/hour")
        print(f"Duration: {duration_minutes} minutes")
        print(f"Expected records: {int(target_per_hour * duration_minutes / 60)}")
        print("=" * 80)
        
        self.results['start_time'] = datetime.now()
        
        target_per_minute = target_per_hour / 60
        target_per_second = target_per_hour / 3600
        
        duration_seconds = duration_minutes * 60
        interval = 1.0 / target_per_second if target_per_second > 0 else 0.1
        
        print(f"\nSending ~{target_per_second:.2f} requests/second")
        print(f"Interval: {interval:.3f} seconds\n")
        
        start = time.time()
        
        while (time.time() - start) < duration_seconds:
            batch_start = time.time()
            
            # Send batch
            customer = DataGenerator.generate_customer()
            result = self.send_customer(customer)
            self._update_results(result)
            
            # Progress update every 10 seconds
            if self.results['total_requests'] % int(target_per_second * 10) == 0:
                elapsed = time.time() - start
                rate = self.results['total_requests'] / elapsed if elapsed > 0 else 0
                print(f"Progress: {self.results['total_requests']} requests "
                      f"in {elapsed:.1f}s ({rate:.2f} req/s) - "
                      f"Success: {self.results['successful']}, Failed: {self.results['failed']}")
            
            # Wait for next interval
            elapsed_batch = time.time() - batch_start
            if elapsed_batch < interval:
                time.sleep(interval - elapsed_batch)
        
        self.results['end_time'] = datetime.now()
        self._print_results()
    
    def run_burst_test(self, total_records=1000, concurrent=True):
        """
        Test burst capacity (send as fast as possible)
        
        Args:
            total_records: Total records to send
            concurrent: Use concurrent requests
        """
        print("=" * 80)
        print("BURST TEST (Maximum Throughput)")
        print("=" * 80)
        print(f"Total records: {total_records}")
        print(f"Concurrent: {concurrent}")
        print(f"Batch size: {BATCH_SIZE}")
        print("=" * 80)
        
        self.results['start_time'] = datetime.now()
        
        batches = total_records // BATCH_SIZE
        remainder = total_records % BATCH_SIZE
        
        for i in range(batches):
            print(f"\nBatch {i+1}/{batches}")
            self.run_batch(BATCH_SIZE, concurrent=concurrent)
        
        if remainder > 0:
            print(f"\nFinal batch ({remainder} records)")
            self.run_batch(remainder, concurrent=concurrent)
        
        self.results['end_time'] = datetime.now()
        self._print_results()
    
    def _print_results(self):
        """Print test results"""
        duration = (self.results['end_time'] - self.results['start_time']).total_seconds()
        
        print("\n" + "=" * 80)
        print("TEST RESULTS")
        print("=" * 80)
        print(f"Duration: {duration:.2f} seconds")
        print(f"Total Requests: {self.results['total_requests']}")
        print(f"Successful: {self.results['successful']}")
        print(f"Failed: {self.results['failed']}")
        print(f"Success Rate: {(self.results['successful']/self.results['total_requests']*100):.2f}%")
        
        if self.results['response_times']:
            avg_response = sum(self.results['response_times']) / len(self.results['response_times'])
            min_response = min(self.results['response_times'])
            max_response = max(self.results['response_times'])
            
            print(f"\nResponse Times:")
            print(f"  Average: {avg_response*1000:.2f} ms")
            print(f"  Min: {min_response*1000:.2f} ms")
            print(f"  Max: {max_response*1000:.2f} ms")
        
        throughput = self.results['total_requests'] / duration if duration > 0 else 0
        throughput_per_hour = throughput * 3600
        
        print(f"\nThroughput:")
        print(f"  {throughput:.2f} requests/second")
        print(f"  {throughput * 60:.2f} requests/minute")
        print(f"  {throughput_per_hour:.2f} requests/hour")
        
        if throughput_per_hour >= TARGET_RECORDS_PER_HOUR:
            print(f"\n✅ SUCCESS: Exceeds target of {TARGET_RECORDS_PER_HOUR} records/hour")
        else:
            shortfall = TARGET_RECORDS_PER_HOUR - throughput_per_hour
            print(f"\n❌ BELOW TARGET: {shortfall:.0f} records/hour short of {TARGET_RECORDS_PER_HOUR}")
        
        if self.results['failed'] > 0:
            print(f"\nErrors (showing first 5):")
            for error in self.results['errors'][:5]:
                print(f"  - {error}")
        
        print("=" * 80)
        
        # Save results to file
        self._save_results()
    
    def _save_results(self):
        """Save results to JSON file"""
        filename = f"performance_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        results_data = {
            'test_config': {
                'target_records_per_hour': TARGET_RECORDS_PER_HOUR,
                'test_duration_minutes': TEST_DURATION_MINUTES,
                'batch_size': BATCH_SIZE,
                'concurrent_requests': CONCURRENT_REQUESTS
            },
            'results': {
                'start_time': self.results['start_time'].isoformat(),
                'end_time': self.results['end_time'].isoformat(),
                'duration_seconds': (self.results['end_time'] - self.results['start_time']).total_seconds(),
                'total_requests': self.results['total_requests'],
                'successful': self.results['successful'],
                'failed': self.results['failed'],
                'success_rate': (self.results['successful']/self.results['total_requests']*100) if self.results['total_requests'] > 0 else 0,
                'avg_response_time_ms': (sum(self.results['response_times']) / len(self.results['response_times']) * 1000) if self.results['response_times'] else 0,
                'throughput_per_second': self.results['total_requests'] / (self.results['end_time'] - self.results['start_time']).total_seconds() if (self.results['end_time'] - self.results['start_time']).total_seconds() > 0 else 0
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"\nResults saved to: {filename}")


def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Performance Testing Tool')
    parser.add_argument('--mode', choices=['throughput', 'burst', 'both'], 
                       default='both', help='Test mode')
    parser.add_argument('--records', type=int, default=1000,
                       help='Number of records for burst test')
    parser.add_argument('--duration', type=int, default=5,
                       help='Duration in minutes for throughput test')
    parser.add_argument('--target', type=int, default=10000,
                       help='Target records per hour')
    
    args = parser.parse_args()
    
    global TARGET_RECORDS_PER_HOUR, TEST_DURATION_MINUTES
    TARGET_RECORDS_PER_HOUR = args.target
    TEST_DURATION_MINUTES = args.duration
    
    tester = PerformanceTester()
    
    if args.mode in ['throughput', 'both']:
        tester.run_throughput_test(
            target_per_hour=args.target,
            duration_minutes=args.duration
        )
        
        if args.mode == 'both':
            print("\n\nWaiting 10 seconds before burst test...\n")
            time.sleep(10)
            tester = PerformanceTester()  # Reset
    
    if args.mode in ['burst', 'both']:
        tester.run_burst_test(
            total_records=args.records,
            concurrent=True
        )


if __name__ == "__main__":
    main()
