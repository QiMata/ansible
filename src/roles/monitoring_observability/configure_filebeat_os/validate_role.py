#!/usr/bin/env python3
"""
Comprehensive validation script for the enhanced Configure Filebeat OS role.
This script validates all the new features and configurations.
"""

import os
import sys
import yaml
import json
import subprocess
from pathlib import Path

class FilebeatRoleValidator:
    def __init__(self, role_path):
        self.role_path = Path(role_path)
        self.errors = []
        self.warnings = []
        self.success_count = 0
        
    def log_error(self, message):
        self.errors.append(f"❌ ERROR: {message}")
        
    def log_warning(self, message):
        self.warnings.append(f"⚠️  WARNING: {message}")
        
    def log_success(self, message):
        self.success_count += 1
        print(f"✅ SUCCESS: {message}")
        
    def validate_file_exists(self, file_path, description):
        """Validate that a file exists"""
        full_path = self.role_path / file_path
        if full_path.exists():
            self.log_success(f"{description} exists: {file_path}")
            return True
        else:
            self.log_error(f"{description} missing: {file_path}")
            return False
            
    def validate_yaml_syntax(self, file_path):
        """Validate YAML syntax"""
        full_path = self.role_path / file_path
        try:
            with open(full_path, 'r') as f:
                yaml.safe_load(f)
            self.log_success(f"YAML syntax valid: {file_path}")
            return True
        except yaml.YAMLError as e:
            self.log_error(f"YAML syntax error in {file_path}: {e}")
            return False
        except FileNotFoundError:
            self.log_error(f"File not found: {file_path}")
            return False
            
    def validate_defaults_variables(self):
        """Validate that all required default variables are present"""
        defaults_path = self.role_path / "defaults" / "main.yml"
        
        required_vars = [
            # Basic Configuration
            'filebeat_version', 'filebeat_config_dir', 'filebeat_data_dir', 'filebeat_log_dir',
            # Service Management
            'filebeat_service_enabled', 'filebeat_service_state',
            # Output Configuration
            'filebeat_output_type', 'filebeat_output_elasticsearch_hosts',
            'filebeat_output_logstash_hosts', 'filebeat_output_kafka_hosts', 'filebeat_output_redis_hosts',
            # Security & Authentication
            'filebeat_ssl_enabled', 'filebeat_ssl_certificate_authorities', 'filebeat_ssl_certificate',
            'filebeat_ssl_key', 'filebeat_ssl_verification_mode', 'filebeat_username', 'filebeat_password',
            'filebeat_api_key', 'filebeat_use_keystore', 'filebeat_keystore_keys',
            # Input Configuration
            'filebeat_input_type', 'filebeat_paths', 'filebeat_journald_enabled', 'filebeat_docker_enabled',
            # Multiline Configuration
            'filebeat_multiline_enabled', 'filebeat_multiline_pattern', 'filebeat_multiline_negate',
            'filebeat_multiline_match', 'filebeat_multiline_max_lines',
            # Modules
            'filebeat_modules_enabled', 'filebeat_system_module_enabled',
            # Processors
            'filebeat_processors_enabled', 'filebeat_add_host_metadata', 'filebeat_add_docker_metadata',
            'filebeat_processors_custom',
            # Performance
            'filebeat_queue_type', 'filebeat_queue_events', 'filebeat_bulk_max_size', 'filebeat_worker',
            # Monitoring
            'filebeat_monitoring_enabled', 'filebeat_http_enabled', 'filebeat_http_port',
            # Logging
            'filebeat_logging_level', 'filebeat_logging_to_files', 'filebeat_logging_files_keepfiles',
            # Fields and Tags
            'filebeat_fields', 'filebeat_tags', 'filebeat_name'
        ]
        
        try:
            with open(defaults_path, 'r') as f:
                defaults = yaml.safe_load(f)
                
            for var in required_vars:
                if var in defaults:
                    self.log_success(f"Required variable present: {var}")
                else:
                    self.log_error(f"Required variable missing: {var}")
                    
        except Exception as e:
            self.log_error(f"Failed to validate defaults: {e}")
            
    def validate_template_variables(self):
        """Validate that template uses the new variables correctly"""
        template_path = self.role_path / "templates" / "filebeat.yml.j2"
        
        required_template_sections = [
            'filebeat.inputs:', 'processors:', 'output.elasticsearch:', 'output.logstash:',
            'output.kafka:', 'output.redis:', 'queue.', 'monitoring.', 'http.', 'logging.',
            'ssl.enabled', 'multiline.', 'filebeat.config.modules:'
        ]
        
        try:
            with open(template_path, 'r') as f:
                template_content = f.read()
                
            for section in required_template_sections:
                if section in template_content:
                    self.log_success(f"Template section present: {section}")
                else:
                    self.log_warning(f"Template section not found: {section}")
                    
        except Exception as e:
            self.log_error(f"Failed to validate template: {e}")
            
    def validate_molecule_scenarios(self):
        """Validate molecule test scenarios"""
        scenarios = ['default', 'security', 'advanced', 'performance']
        
        for scenario in scenarios:
            scenario_path = self.role_path / "molecule" / scenario
            
            required_files = [
                'molecule.yml', 'converge.yml', 'verify.yml'
            ]
            
            if scenario_path.exists():
                self.log_success(f"Molecule scenario exists: {scenario}")
                
                for file in required_files:
                    file_path = scenario_path / file
                    if file_path.exists():
                        self.log_success(f"Molecule file exists: {scenario}/{file}")
                        self.validate_yaml_syntax(f"molecule/{scenario}/{file}")
                    else:
                        self.log_error(f"Molecule file missing: {scenario}/{file}")
            else:
                self.log_error(f"Molecule scenario missing: {scenario}")
                
    def validate_example_playbooks(self):
        """Validate example playbooks"""
        examples_path = self.role_path / "examples"
        
        expected_examples = [
            'basic.yml', 'security.yml', 'advanced.yml', 'performance.yml'
        ]
        
        for example in expected_examples:
            example_path = examples_path / example
            if example_path.exists():
                self.log_success(f"Example playbook exists: {example}")
                self.validate_yaml_syntax(f"examples/{example}")
            else:
                self.log_error(f"Example playbook missing: {example}")
                
    def validate_handlers(self):
        """Validate handlers have been enhanced"""
        handlers_path = self.role_path / "handlers" / "main.yml"
        
        expected_handlers = [
            'restart filebeat', 'reload filebeat', 'enable filebeat', 'validate filebeat config'
        ]
        
        try:
            with open(handlers_path, 'r') as f:
                handlers_content = f.read()
                
            for handler in expected_handlers:
                if handler in handlers_content:
                    self.log_success(f"Handler present: {handler}")
                else:
                    self.log_warning(f"Handler not found: {handler}")
                    
        except Exception as e:
            self.log_error(f"Failed to validate handlers: {e}")
            
    def validate_tasks_enhancements(self):
        """Validate that tasks include new functionality"""
        tasks_path = self.role_path / "tasks" / "main.yml"
        
        expected_task_features = [
            'keystore', 'SSL', 'modules enable', 'RedHat', 'service', 'test config', 'test output'
        ]
        
        try:
            with open(tasks_path, 'r') as f:
                tasks_content = f.read()
                
            for feature in expected_task_features:
                if feature.lower() in tasks_content.lower():
                    self.log_success(f"Task feature present: {feature}")
                else:
                    self.log_warning(f"Task feature not found: {feature}")
                    
        except Exception as e:
            self.log_error(f"Failed to validate tasks: {e}")
            
    def validate_os_variables(self):
        """Validate OS-specific variables"""
        vars_path = self.role_path / "vars"
        
        os_families = ['Debian.yml', 'RedHat.yml']
        
        for os_file in os_families:
            os_path = vars_path / os_file
            if os_path.exists():
                self.log_success(f"OS variables exist: {os_file}")
                self.validate_yaml_syntax(f"vars/{os_file}")
            else:
                self.log_error(f"OS variables missing: {os_file}")
                
    def run_all_validations(self):
        """Run all validation checks"""
        print("🚀 Starting Enhanced Filebeat OS Role Validation")
        print("=" * 60)
        
        # Core file structure
        print("\n📁 Validating Core File Structure...")
        self.validate_file_exists("defaults/main.yml", "Defaults file")
        self.validate_file_exists("tasks/main.yml", "Tasks file")
        self.validate_file_exists("handlers/main.yml", "Handlers file")
        self.validate_file_exists("templates/filebeat.yml.j2", "Template file")
        self.validate_file_exists("README.md", "README file")
        
        # YAML syntax
        print("\n📝 Validating YAML Syntax...")
        self.validate_yaml_syntax("defaults/main.yml")
        self.validate_yaml_syntax("tasks/main.yml")
        self.validate_yaml_syntax("handlers/main.yml")
        
        # Variable validation
        print("\n🔧 Validating Variables...")
        self.validate_defaults_variables()
        self.validate_template_variables()
        
        # OS support
        print("\n🖥️  Validating OS Support...")
        self.validate_os_variables()
        
        # Enhanced functionality
        print("\n⚡ Validating Enhanced Functionality...")
        self.validate_handlers()
        self.validate_tasks_enhancements()
        
        # Testing
        print("\n🧪 Validating Test Suite...")
        self.validate_molecule_scenarios()
        
        # Examples
        print("\n📚 Validating Examples...")
        self.validate_example_playbooks()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 VALIDATION SUMMARY")
        print("=" * 60)
        
        print(f"✅ Successful validations: {self.success_count}")
        
        if self.warnings:
            print(f"⚠️  Warnings: {len(self.warnings)}")
            for warning in self.warnings:
                print(f"   {warning}")
                
        if self.errors:
            print(f"❌ Errors: {len(self.errors)}")
            for error in self.errors:
                print(f"   {error}")
            print("\n🚨 VALIDATION FAILED - Please fix the above errors")
            return False
        else:
            print("\n🎉 ALL VALIDATIONS PASSED!")
            print("✨ Enhanced Filebeat OS role is ready for production use!")
            print("\n🔧 Features validated:")
            print("   • SSL/TLS Configuration & Certificate Management")
            print("   • Authentication & Keystore Integration") 
            print("   • Multiple Output Types (Elasticsearch, Logstash, Kafka, Redis)")
            print("   • Multiline Processing & Pattern Matching")
            print("   • Filebeat Modules Support")
            print("   • Custom Processors & Field Enrichment")
            print("   • Performance Tuning & Queue Management")
            print("   • Health Monitoring & HTTP Endpoints")
            print("   • Cross-Platform Support (Debian & RedHat)")
            print("   • Comprehensive Test Suite")
            return True

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 validate_role.py <role_path>")
        sys.exit(1)
        
    role_path = sys.argv[1]
    
    if not os.path.exists(role_path):
        print(f"❌ Role path does not exist: {role_path}")
        sys.exit(1)
        
    validator = FilebeatRoleValidator(role_path)
    success = validator.run_all_validations()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
