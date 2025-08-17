#!/usr/bin/env python3
"""
Integration test script for Enhanced Amundsen Search
Tests all the new features and configurations
"""
import requests
import time
import json
import sys
import os
from typing import Dict, Any, List

class AmundsenSearchTester:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.base_url = f"http://{config['host']}:{config['port']}"
        self.es_url = f"{config['es_scheme']}://{config['es_host']}:{config['es_port']}"
        self.results = []
    
    def log_result(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        status = "PASS" if success else "FAIL"
        self.results.append({
            'test': test_name,
            'status': status,
            'message': message
        })
        print(f"[{status}] {test_name}: {message}")
    
    def test_basic_connectivity(self) -> bool:
        """Test basic service connectivity"""
        try:
            response = requests.get(f"{self.base_url}/healthcheck", timeout=10)
            success = response.status_code in [200, 503]
            self.log_result("Basic Connectivity", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_result("Basic Connectivity", False, str(e))
            return False
    
    def test_elasticsearch_connectivity(self) -> bool:
        """Test Elasticsearch connectivity"""
        try:
            response = requests.get(f"{self.es_url}/_cluster/health", timeout=10)
            success = response.status_code == 200
            if success:
                health = response.json()
                cluster_status = health.get('status', 'unknown')
                self.log_result("Elasticsearch Connectivity", True, f"Cluster status: {cluster_status}")
            else:
                self.log_result("Elasticsearch Connectivity", False, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_result("Elasticsearch Connectivity", False, str(e))
            return False
    
    def test_metrics_endpoint(self) -> bool:
        """Test Prometheus metrics endpoint if enabled"""
        if not self.config.get('metrics_enabled', False):
            self.log_result("Metrics Endpoint", True, "Metrics disabled - skipping")
            return True
        
        try:
            metrics_url = f"http://{self.config['host']}:{self.config['metrics_port']}/metrics"
            response = requests.get(metrics_url, timeout=10)
            success = response.status_code == 200
            if success:
                metrics_count = len([line for line in response.text.split('\n') if line.startswith('amundsen_')])
                self.log_result("Metrics Endpoint", True, f"Found {metrics_count} Amundsen metrics")
            else:
                self.log_result("Metrics Endpoint", False, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_result("Metrics Endpoint", False, str(e))
            return False
    
    def test_authentication(self) -> bool:
        """Test authentication if enabled"""
        if not self.config.get('auth_enabled', False):
            self.log_result("Authentication", True, "Authentication disabled - skipping")
            return True
        
        # Test without auth (should fail)
        try:
            response = requests.get(f"{self.base_url}/search", timeout=10)
            if response.status_code == 401:
                self.log_result("Authentication", True, "Properly rejecting unauthenticated requests")
                return True
            else:
                self.log_result("Authentication", False, f"Expected 401, got {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Authentication", False, str(e))
            return False
    
    def test_tls_configuration(self) -> bool:
        """Test TLS configuration if enabled"""
        if not self.config.get('tls_enabled', False):
            self.log_result("TLS Configuration", True, "TLS disabled - skipping")
            return True
        
        try:
            https_url = f"https://{self.config['host']}:{self.config['port']}/healthcheck"
            response = requests.get(https_url, timeout=10, verify=False)
            success = response.status_code in [200, 503]
            self.log_result("TLS Configuration", success, f"HTTPS Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_result("TLS Configuration", False, str(e))
            return False
    
    def test_search_functionality(self) -> bool:
        """Test basic search functionality"""
        try:
            search_data = {
                "query": {
                    "match_all": {}
                },
                "size": 5
            }
            
            headers = {'Content-Type': 'application/json'}
            response = requests.post(f"{self.base_url}/search", json=search_data, headers=headers, timeout=10)
            
            success = response.status_code in [200, 404]  # 404 is OK if no data indexed yet
            if success:
                if response.status_code == 200:
                    results = response.json()
                    result_count = len(results.get('hits', {}).get('hits', []))
                    self.log_result("Search Functionality", True, f"Search returned {result_count} results")
                else:
                    self.log_result("Search Functionality", True, "Search endpoint responding (no data indexed)")
            else:
                self.log_result("Search Functionality", False, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_result("Search Functionality", False, str(e))
            return False
    
    def test_logging_configuration(self) -> bool:
        """Test logging configuration"""
        log_files = [
            "/var/log/amundsen/search.log",
            "/var/log/amundsen/search_access.log"
        ]
        
        found_logs = []
        for log_file in log_files:
            if os.path.exists(log_file):
                found_logs.append(log_file)
        
        success = len(found_logs) > 0
        self.log_result("Logging Configuration", success, f"Found log files: {found_logs}")
        return success
    
    def test_systemd_service(self) -> bool:
        """Test systemd service status"""
        try:
            import subprocess
            result = subprocess.run(['systemctl', 'is-active', 'amundsen-search'], 
                                  capture_output=True, text=True)
            
            active = result.stdout.strip() == 'active'
            self.log_result("Systemd Service", active, f"Service status: {result.stdout.strip()}")
            return active
        except Exception as e:
            self.log_result("Systemd Service", False, str(e))
            return False
    
    def test_health_check_scripts(self) -> bool:
        """Test health check scripts"""
        health_script = "/opt/amundsen/search/venv/health_check.py"
        
        if not os.path.exists(health_script):
            self.log_result("Health Check Scripts", False, "Health check script not found")
            return False
        
        try:
            import subprocess
            result = subprocess.run(['python3', health_script, '--startup-check'], 
                                  capture_output=True, text=True, timeout=30)
            
            success = result.returncode == 0
            self.log_result("Health Check Scripts", success, f"Health check exit code: {result.returncode}")
            return success
        except Exception as e:
            self.log_result("Health Check Scripts", False, str(e))
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return summary"""
        print("=" * 60)
        print("AMUNDSEN SEARCH ENHANCED FEATURES TEST SUITE")
        print("=" * 60)
        
        tests = [
            self.test_basic_connectivity,
            self.test_elasticsearch_connectivity,
            self.test_systemd_service,
            self.test_search_functionality,
            self.test_metrics_endpoint,
            self.test_authentication,
            self.test_tls_configuration,
            self.test_logging_configuration,
            self.test_health_check_scripts
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            if test():
                passed += 1
            else:
                failed += 1
        
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {passed + failed}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed / (passed + failed) * 100):.1f}%")
        
        return {
            'total': passed + failed,
            'passed': passed,
            'failed': failed,
            'success_rate': passed / (passed + failed) * 100,
            'results': self.results
        }

def main():
    # Configuration - adjust these values for your environment
    config = {
        'host': 'localhost',
        'port': 5001,
        'es_host': 'localhost',
        'es_port': 9200,
        'es_scheme': 'http',
        'metrics_enabled': True,
        'metrics_port': 9090,
        'auth_enabled': False,
        'tls_enabled': False
    }
    
    tester = AmundsenSearchTester(config)
    summary = tester.run_all_tests()
    
    # Exit with error code if any tests failed
    sys.exit(0 if summary['failed'] == 0 else 1)

if __name__ == '__main__':
    main()
