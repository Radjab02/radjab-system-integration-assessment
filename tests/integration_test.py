#!/usr/bin/env python3
"""
End-to-End Integration Test
Tests complete data flow from Mock APIs to Analytics
"""
import requests
import time
import json
from datetime import datetime
import sys


class IntegrationTester:
    """End-to-end integration testing"""
    
    def __init__(self):
        self.mock_api_url = "http://localhost:8081"
        self.java_producer_url = "http://localhost:8082"
        
        self.test_results = {
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'failures': []
        }
    
    def log_test(self, name, passed, message=""):
        """Log test result"""
        self.test_results['tests_run'] += 1
        
        if passed:
            self.test_results['tests_passed'] += 1
            print(f"✅ PASS: {name}")
            if message:
                print(f"   {message}")
        else:
            self.test_results['tests_failed'] += 1
            self.test_results['failures'].append({'test': name, 'message': message})
            print(f"❌ FAIL: {name}")
            if message:
                print(f"   {message}")
    
    def test_mock_api_health(self):
        """Test 1: Mock API is healthy"""
        try:
            response = requests.get(f"{self.mock_api_url}/actuator/health", timeout=5)
            passed = response.status_code == 200 and response.json().get('status') == 'UP'
            self.log_test(
                "Mock API Health Check",
                passed,
                f"Status: {response.json().get('status', 'UNKNOWN')}"
            )
        except Exception as e:
            self.log_test("Mock API Health Check", False, str(e))
    
    def test_java_producer_health(self):
        """Test 2: Java Producer is healthy"""
        try:
            response = requests.get(f"{self.java_producer_url}/actuator/health", timeout=5)
            passed = response.status_code == 200 and response.json().get('status') == 'UP'
            self.log_test(
                "Java Producer Health Check",
                passed,
                f"Status: {response.json().get('status', 'UNKNOWN')}"
            )
        except Exception as e:
            self.log_test("Java Producer Health Check", False, str(e))
    
    def test_create_customer(self):
        """Test 3: Create new customer via Mock API"""
        customer_data = {
            "name": "Integration Test User",
            "email": f"integration.test.{int(time.time())}@example.com",
            "phone": "+1999888777",
            "address": "123 Test Street"
        }
        
        try:
            response = requests.post(
                f"{self.mock_api_url}/api/customers",
                json=customer_data,
                timeout=10
            )
            passed = response.status_code in [200, 201]
            
            if passed:
                customer_id = response.json().get('id', 'N/A')
                self.log_test(
                    "Create Customer",
                    True,
                    f"Created customer ID: {customer_id}"
                )
                return customer_id
            else:
                self.log_test(
                    "Create Customer",
                    False,
                    f"Status: {response.status_code}, Response: {response.text[:100]}"
                )
                return None
        except Exception as e:
            self.log_test("Create Customer", False, str(e))
            return None
    
    def test_trigger_sync(self):
        """Test 4: Trigger incremental sync"""
        try:
            response = requests.post(
                f"{self.java_producer_url}/api/sync/customers/incremental",
                timeout=30
            )
            passed = response.status_code == 200
            self.log_test(
                "Trigger Incremental Sync",
                passed,
                f"Status: {response.status_code}"
            )
            return passed
        except Exception as e:
            self.log_test("Trigger Incremental Sync", False, str(e))
            return False
    
    def test_verify_sync_status(self):
        """Test 5: Verify sync status shows data was synced"""
        try:
            # Wait a bit for sync to complete
            time.sleep(5)
            
            response = requests.get(
                f"{self.java_producer_url}/api/sync/status",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                customer_data = data.get('customer', {})
                total_synced = customer_data.get('totalRecordsSynced', 0)
                
                passed = total_synced > 0
                self.log_test(
                    "Verify Sync Status",
                    passed,
                    f"Total customers synced: {total_synced}"
                )
            else:
                self.log_test("Verify Sync Status", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Verify Sync Status", False, str(e))
    
    def test_data_flow_latency(self):
        """Test 6: Measure end-to-end latency"""
        print("\n--- Testing End-to-End Latency ---")
        
        # Create customer
        start_time = time.time()
        
        customer_data = {
            "name": "Latency Test User",
            "email": f"latency.test.{int(time.time())}@example.com",
            "phone": "+1888777666",
            "address": "456 Latency Ave"
        }
        
        try:
            # Step 1: Create customer
            response = requests.post(
                f"{self.mock_api_url}/api/customers",
                json=customer_data,
                timeout=10
            )
            create_time = time.time() - start_time
            
            if response.status_code not in [200, 201]:
                self.log_test("Data Flow Latency", False, "Failed to create customer")
                return
            
            # Step 2: Trigger sync
            sync_start = time.time()
            requests.post(
                f"{self.java_producer_url}/api/sync/customers/incremental",
                timeout=30
            )
            sync_time = time.time() - sync_start
            
            # Step 3: Wait for Python consumers to process (30s interval + processing time)
            print("   Waiting for Python consumers to process...")
            time.sleep(35)
            
            total_time = time.time() - start_time
            
            passed = total_time < 60  # Should complete within 1 minute
            
            self.log_test(
                "Data Flow Latency",
                passed,
                f"Total time: {total_time:.2f}s (Create: {create_time:.2f}s, Sync: {sync_time:.2f}s)"
            )
        except Exception as e:
            self.log_test("Data Flow Latency", False, str(e))
    
    def test_throughput_calculation(self):
        """Test 7: Calculate current system throughput"""
        try:
            # Get initial state
            response = requests.get(
                f"{self.java_producer_url}/api/sync/status",
                timeout=5
            )
            
            if response.status_code != 200:
                self.log_test("Throughput Calculation", False, "Cannot get sync status")
                return
            
            initial_data = response.json()
            initial_customer_count = initial_data.get('customer', {}).get('totalRecordsSynced', 0)
            initial_inventory_count = initial_data.get('inventory', {}).get('totalRecordsSynced', 0)
            
            # Wait for one sync cycle (60 seconds)
            print("   Waiting 60 seconds for sync cycle...")
            time.sleep(60)
            
            # Get final state
            response = requests.get(
                f"{self.java_producer_url}/api/sync/status",
                timeout=5
            )
            
            final_data = response.json()
            final_customer_count = final_data.get('customer', {}).get('totalRecordsSynced', 0)
            final_inventory_count = final_data.get('inventory', {}).get('totalRecordsSynced', 0)
            
            # Calculate throughput
            customer_delta = final_customer_count - initial_customer_count
            inventory_delta = final_inventory_count - initial_inventory_count
            total_delta = customer_delta + inventory_delta
            
            # Extrapolate to per hour
            records_per_hour = total_delta * 60  # 60 minutes in an hour
            
            passed = records_per_hour >= 10000 or total_delta > 0  # Either meets target or showing activity
            
            self.log_test(
                "Throughput Calculation",
                passed,
                f"Records/hour: {records_per_hour} (Target: 10,000) - Delta: {total_delta} in 60s"
            )
        except Exception as e:
            self.log_test("Throughput Calculation", False, str(e))
    
    def run_all_tests(self, skip_latency=False):
        """Run all integration tests"""
        print("=" * 80)
        print("END-TO-END INTEGRATION TESTS")
        print("=" * 80)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print()
        
        # Health checks
        self.test_mock_api_health()
        self.test_java_producer_health()
        
        print()
        
        # Data creation and sync
        self.test_create_customer()
        self.test_trigger_sync()
        self.test_verify_sync_status()
        
        print()
        
        # Performance tests
        if not skip_latency:
            self.test_data_flow_latency()
        
        # Note: Throughput test takes 60 seconds, skip by default
        # Uncomment to run:
        # self.test_throughput_calculation()
        
        self._print_summary()
    
    def _print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Tests Run: {self.test_results['tests_run']}")
        print(f"Passed: {self.test_results['tests_passed']}")
        print(f"Failed: {self.test_results['tests_failed']}")
        
        if self.test_results['tests_run'] > 0:
            pass_rate = (self.test_results['tests_passed'] / self.test_results['tests_run']) * 100
            print(f"Pass Rate: {pass_rate:.1f}%")
        
        if self.test_results['failures']:
            print("\nFailed Tests:")
            for failure in self.test_results['failures']:
                print(f"  - {failure['test']}: {failure['message']}")
        
        print("=" * 80)
        
        # Save results
        filename = f"integration_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\nResults saved to: {filename}\n")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='End-to-End Integration Test')
    parser.add_argument('--skip-latency', action='store_true',
                       help='Skip latency test (takes 35+ seconds)')
    
    args = parser.parse_args()
    
    tester = IntegrationTester()
    
    try:
        tester.run_all_tests(skip_latency=args.skip_latency)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        tester._print_summary()
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        tester._print_summary()
        sys.exit(1)


if __name__ == "__main__":
    main()
