import re
import os
from collections import Counter, defaultdict
from datetime import datetime
import json

class LogAnalyzer:
    def __init__(self, filepath):
        self.filepath = filepath
    
    def analyze(self):
        """Perform comprehensive log analysis - optimized for large files"""
        results = {
            'filename': os.path.basename(self.filepath),
            'total_lines': 0,
            'total_size': self.get_file_size(),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error_count': 0,
            'warning_count': 0,
            'info_count': 0,
            'error_types': Counter(),
            'ip_addresses': Counter(),
            'urls': [],
            'status_codes': Counter(),
            'top_errors': [],
            'timeline': [],
            'unique_ips': set(),
            'file_type': None
        }
        
        # Read first few lines for file type detection
        sample_lines = []
        try:
            with open(self.filepath, 'r', encoding='utf-8', errors='ignore') as f:
                for i, line in enumerate(f):
                    if i < 10:
                        sample_lines.append(line)
                    if i >= 10:
                        break
        except Exception as e:
            raise Exception(f"Error reading file: {str(e)}")
        
        if not sample_lines:
            return {
                'total_lines': 0,
                'error': 'File is empty or could not be read'
            }
        
        # Detect file type from sample
        results['file_type'] = self.detect_file_type(sample_lines)
        
        # Process file line by line (memory efficient for large files)
        try:
            with open(self.filepath, 'r', encoding='utf-8', errors='ignore') as f:
                line_num = 0
                timeline_limit = 100  # Limit timeline entries to prevent memory issues
                
                for line in f:
                    line_num += 1
                    line_lower = line.lower()
                    
                    # Count log levels
                    if any(keyword in line_lower for keyword in ['error', 'exception', 'failed', 'fatal']):
                        results['error_count'] += 1
                        results['error_types'][self.extract_error_type(line)] += 1
                    elif any(keyword in line_lower for keyword in ['warning', 'warn']):
                        results['warning_count'] += 1
                    elif any(keyword in line_lower for keyword in ['info', 'information']):
                        results['info_count'] += 1
                    
                    # Extract IP addresses
                    ips = self.extract_ip_addresses(line)
                    for ip in ips:
                        results['ip_addresses'][ip] += 1
                        results['unique_ips'].add(ip)
                    
                    # Extract URLs (limit to prevent memory issues)
                    if len(results['urls']) < 1000:
                        urls = self.extract_urls(line)
                        results['urls'].extend(urls)
                    
                    # Extract HTTP status codes
                    status_codes = self.extract_status_codes(line)
                    for code in status_codes:
                        results['status_codes'][code] += 1
                    
                    # Extract timestamps (limit entries)
                    if len(results['timeline']) < timeline_limit:
                        timestamp = self.extract_timestamp(line)
                        if timestamp:
                            results['timeline'].append({
                                'line': line_num,
                                'timestamp': timestamp,
                                'content': line.strip()[:100]
                            })
                
                results['total_lines'] = line_num
        except Exception as e:
            raise Exception(f"Error processing file: {str(e)}")
        
        # Process results
        results['top_errors'] = results['error_types'].most_common(10)
        results['top_ips'] = results['ip_addresses'].most_common(10)
        results['unique_ip_count'] = len(results['unique_ips'])
        results['unique_ips'] = list(results['unique_ips'])[:20]  # Convert to list for JSON serialization
        results['top_status_codes'] = results['status_codes'].most_common(10)
        results['unique_urls'] = list(set(results['urls']))[:20]
        
        # Calculate statistics
        results['error_rate'] = (results['error_count'] / results['total_lines'] * 100) if results['total_lines'] > 0 else 0
        results['warning_rate'] = (results['warning_count'] / results['total_lines'] * 100) if results['total_lines'] > 0 else 0
        
        return results
    
    def get_file_size(self):
        """Get file size in appropriate unit"""
        size = os.path.getsize(self.filepath)
        if size < 1024:
            return f"{size:.2f} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.2f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.2f} MB"
        else:
            return f"{size / (1024 * 1024 * 1024):.2f} GB"
    
    def detect_file_type(self, sample_lines):
        """Detect the type of log file from sample lines"""
        if not sample_lines:
            return "Unknown"
        
        sample = ' '.join(sample_lines).lower()
        
        if 'apache' in sample or 'httpd' in sample:
            return "Apache"
        elif 'nginx' in sample:
            return "Nginx"
        elif 'iis' in sample or 'w3svc' in sample:
            return "IIS"
        elif any(keyword in sample for keyword in ['[info]', '[error]', '[warn]', '[debug]']):
            return "Application Log"
        else:
            return "Generic Log"
    
    def extract_ip_addresses(self, line):
        """Extract IP addresses from a line"""
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        return re.findall(ip_pattern, line)
    
    def extract_urls(self, line):
        """Extract URLs from a line"""
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        return re.findall(url_pattern, line, re.IGNORECASE)
    
    def extract_status_codes(self, line):
        """Extract HTTP status codes"""
        status_pattern = r'\b(?:1\d{2}|2\d{2}|3\d{2}|4\d{2}|5\d{2})\b'
        return re.findall(status_pattern, line)
    
    def extract_timestamp(self, line):
        """Extract timestamp from a line"""
        # Common timestamp patterns
        patterns = [
            r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',
            r'\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}',
            r'\[\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}',
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                return match.group(0)
        return None
    
    def extract_error_type(self, line):
        """Extract error type from a line"""
        error_keywords = {
            'timeout': 'Timeout',
            'connection': 'Connection Error',
            'permission': 'Permission Error',
            'not found': 'Not Found',
            'unauthorized': 'Unauthorized',
            'forbidden': 'Forbidden',
            'server error': 'Server Error',
            'database': 'Database Error',
            'memory': 'Memory Error',
            'exception': 'Exception'
        }
        
        line_lower = line.lower()
        for keyword, error_type in error_keywords.items():
            if keyword in line_lower:
                return error_type
        
        return 'General Error'

