#!/usr/bin/env python3
"""
Health Check Utility

Quick endpoint health checks for incident response.
Usage: python check_health.py <url> [--timeout 10]
"""

import argparse
import socket
import ssl
import sys
import time
from urllib.parse import urlparse
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError


def parse_args():
    parser = argparse.ArgumentParser(
        description='Check endpoint health and connectivity'
    )
    parser.add_argument(
        'url',
        help='URL to check (e.g., https://api.example.com/health)'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=10,
        help='Timeout in seconds (default: 10)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed output'
    )
    parser.add_argument(
        '--no-verify-ssl',
        action='store_true',
        help='Skip SSL certificate verification'
    )
    return parser.parse_args()


def check_dns(hostname):
    """Check DNS resolution for hostname."""
    try:
        start = time.time()
        ip = socket.gethostbyname(hostname)
        elapsed = (time.time() - start) * 1000
        return {
            'success': True,
            'ip': ip,
            'time_ms': round(elapsed, 2)
        }
    except socket.gaierror as e:
        return {
            'success': False,
            'error': str(e)
        }


def check_port(hostname, port, timeout):
    """Check TCP connectivity to host:port."""
    try:
        start = time.time()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((hostname, port))
        elapsed = (time.time() - start) * 1000
        sock.close()
        
        if result == 0:
            return {
                'success': True,
                'port': port,
                'time_ms': round(elapsed, 2)
            }
        else:
            return {
                'success': False,
                'port': port,
                'error': f'Connection refused (code: {result})'
            }
    except socket.timeout:
        return {
            'success': False,
            'port': port,
            'error': 'Connection timeout'
        }
    except Exception as e:
        return {
            'success': False,
            'port': port,
            'error': str(e)
        }


def check_http(url, timeout, verify_ssl=True):
    """Check HTTP endpoint."""
    try:
        start = time.time()
        
        # Create request with user agent
        req = Request(
            url, 
            headers={'User-Agent': 'HealthCheck/1.0'}
        )
        
        # Handle SSL verification
        context = None
        if not verify_ssl:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
        
        response = urlopen(req, timeout=timeout, context=context)
        elapsed = (time.time() - start) * 1000
        
        return {
            'success': True,
            'status_code': response.getcode(),
            'time_ms': round(elapsed, 2),
            'headers': dict(response.headers)
        }
        
    except HTTPError as e:
        elapsed = (time.time() - start) * 1000
        return {
            'success': False,
            'status_code': e.code,
            'time_ms': round(elapsed, 2),
            'error': str(e.reason)
        }
    except URLError as e:
        return {
            'success': False,
            'error': str(e.reason)
        }
    except socket.timeout:
        return {
            'success': False,
            'error': 'Request timeout'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def format_result(check_name, result, verbose=False):
    """Format check result for display."""
    if result['success']:
        status = "[PASS]"
    else:
        status = "[FAIL]"
    
    output = [f"{status} {check_name}"]
    
    if verbose or not result['success']:
        for key, value in result.items():
            if key in ['success']:
                continue
            if key == 'headers' and not verbose:
                continue
            output.append(f"    {key}: {value}")
    elif result['success']:
        if 'time_ms' in result:
            output[0] += f" ({result['time_ms']}ms)"
        if 'status_code' in result:
            output[0] += f" [HTTP {result['status_code']}]"
    
    return '\n'.join(output)


def main():
    args = parse_args()
    
    # Parse URL
    parsed = urlparse(args.url)
    if not parsed.scheme:
        # Assume https if no scheme provided
        args.url = f'https://{args.url}'
        parsed = urlparse(args.url)
    
    hostname = parsed.hostname
    port = parsed.port or (443 if parsed.scheme == 'https' else 80)
    
    print(f"Health Check: {args.url}")
    print("=" * 50)
    
    all_passed = True
    
    # DNS Check
    print("\n[1/3] DNS Resolution")
    dns_result = check_dns(hostname)
    print(format_result(f"DNS lookup for {hostname}", dns_result, args.verbose))
    if not dns_result['success']:
        all_passed = False
        print("\n⚠ DNS resolution failed. Cannot proceed with further checks.")
        sys.exit(1)
    
    # TCP Port Check
    print("\n[2/3] TCP Connectivity")
    port_result = check_port(hostname, port, args.timeout)
    print(format_result(f"TCP port {port}", port_result, args.verbose))
    if not port_result['success']:
        all_passed = False
    
    # HTTP Check
    print("\n[3/3] HTTP Request")
    http_result = check_http(
        args.url, 
        args.timeout, 
        verify_ssl=not args.no_verify_ssl
    )
    print(format_result(f"HTTP {parsed.scheme.upper()}", http_result, args.verbose))
    if not http_result['success']:
        all_passed = False
    
    # Summary
    print("\n" + "=" * 50)
    if all_passed:
        print("[OK] All checks passed - Endpoint is healthy")
        sys.exit(0)
    else:
        print("[ERROR] Some checks failed - Endpoint may have issues")
        sys.exit(1)


if __name__ == '__main__':
    main()
