#!/usr/bin/env python3
"""
Molecule Test Runner for pfSense Role

This script provides utilities for running comprehensive tests
against the pfSense Ansible role.
"""

import os
import sys
import subprocess
import argparse
import yaml
from pathlib import Path

class PfSenseTestRunner:
    """Main test runner class for pfSense role testing."""
    
    def __init__(self):
        self.role_path = Path(__file__).parent.parent
        self.scenarios = [
            'default',
            'basic_config', 
            'enterprise',
            'vpn_config'
        ]
    
    def run_scenario(self, scenario, destroy=True):
        """Run a specific test scenario."""
        print(f"Running Molecule scenario: {scenario}")
        
        cmd = ['molecule', 'test', '-s', scenario]
        if not destroy:
            cmd.append('--destroy=never')
            
        try:
            result = subprocess.run(
                cmd,
                cwd=self.role_path,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minute timeout
            )
            
            if result.returncode == 0:
                print(f"✅ Scenario {scenario} passed")
                return True
            else:
                print(f"❌ Scenario {scenario} failed")
                print(f"STDOUT: {result.stdout}")
                print(f"STDERR: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"⏰ Scenario {scenario} timed out")
            return False
        except Exception as e:
            print(f"💥 Scenario {scenario} error: {e}")
            return False
    
    def run_all_scenarios(self, destroy=True):
        """Run all test scenarios."""
        results = {}
        
        for scenario in self.scenarios:
            results[scenario] = self.run_scenario(scenario, destroy)
        
        # Print summary
        print("\n" + "="*50)
        print("TEST SUMMARY")
        print("="*50)
        
        passed = 0
        failed = 0
        
        for scenario, result in results.items():
            status = "PASS" if result else "FAIL"
            print(f"{scenario:20} {status}")
            
            if result:
                passed += 1
            else:
                failed += 1
        
        print(f"\nTotal: {len(results)} | Passed: {passed} | Failed: {failed}")
        
        return failed == 0
    
    def lint_role(self):
        """Run linting on the role."""
        print("Running role linting...")
        
        try:
            # Run ansible-lint
            result = subprocess.run(
                ['ansible-lint', '.'],
                cwd=self.role_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ Linting passed")
                return True
            else:
                print("❌ Linting failed")
                print(result.stdout)
                return False
                
        except FileNotFoundError:
            print("⚠️  ansible-lint not found, skipping linting")
            return True
    
    def check_syntax(self):
        """Check Ansible syntax."""
        print("Checking Ansible syntax...")
        
        try:
            result = subprocess.run(
                ['ansible-playbook', '--syntax-check', 'molecule/default/converge.yml'],
                cwd=self.role_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ Syntax check passed")
                return True
            else:
                print("❌ Syntax check failed")
                print(result.stdout)
                return False
                
        except Exception as e:
            print(f"💥 Syntax check error: {e}")
            return False
    
    def validate_test_config(self):
        """Validate test configuration files."""
        print("Validating test configuration...")
        
        config_files = [
            'molecule/test_config.yml',
            'molecule/requirements.yml'
        ]
        
        for config_file in config_files:
            config_path = self.role_path / config_file
            
            if not config_path.exists():
                print(f"❌ Missing config file: {config_file}")
                return False
            
            try:
                with open(config_path, 'r') as f:
                    yaml.safe_load(f)
                print(f"✅ Valid YAML: {config_file}")
            except yaml.YAMLError as e:
                print(f"❌ Invalid YAML in {config_file}: {e}")
                return False
        
        return True

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='pfSense Role Test Runner')
    parser.add_argument(
        '--scenario', 
        choices=['default', 'basic_config', 'enterprise', 'vpn_config'],
        help='Run specific scenario'
    )
    parser.add_argument(
        '--no-destroy',
        action='store_true',
        help='Do not destroy test instances after testing'
    )
    parser.add_argument(
        '--lint-only',
        action='store_true',
        help='Only run linting and syntax checks'
    )
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate test configuration'
    )
    
    args = parser.parse_args()
    
    runner = PfSenseTestRunner()
    
    # Validate configuration
    if not runner.validate_test_config():
        sys.exit(1)
    
    if args.validate_only:
        print("✅ Configuration validation complete")
        sys.exit(0)
    
    # Run linting and syntax checks
    if not runner.lint_role() or not runner.check_syntax():
        if args.lint_only:
            sys.exit(1)
        print("⚠️  Continuing with tests despite linting/syntax issues...")
    
    if args.lint_only:
        print("✅ Linting and syntax checks complete")
        sys.exit(0)
    
    # Run tests
    destroy = not args.no_destroy
    
    if args.scenario:
        success = runner.run_scenario(args.scenario, destroy)
    else:
        success = runner.run_all_scenarios(destroy)
    
    if success:
        print("🎉 All tests completed successfully!")
        sys.exit(0)
    else:
        print("💥 Some tests failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
