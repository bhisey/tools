#!/usr/bin/env python3
import os
import re
import glob
import sys
import argparse

def check_high_await_times(filepath, threshold):
    """Parse iostat files and find lines with high await times"""
    with open(filepath, 'r') as file:
        lines = file.readlines()
    
    high_await_lines = []
    current_timestamp = ""
    line_number = 0
    
    for i, line in enumerate(lines):
        line_number = i + 1
        original_line = line.strip()
        
        # Clean line - remove line numbers if present
        if '|' in line and line.split('|')[0].isdigit():
            clean_line = '|'.join(line.split('|')[1:])
        else:
            clean_line = line
        
        clean_line = clean_line.strip()
        
        # Check for timestamp
        if re.match(r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2} [APM]{2}', clean_line):
            current_timestamp = clean_line
            continue
        
        # Check for device data lines (skip header)
        if clean_line and not clean_line.startswith('Device') and not clean_line.startswith('avg-cpu'):
            parts = clean_line.split()
            
            # Check if this looks like a device statistics line
            if len(parts) >= 16 and parts[0] not in ['Linux', '']:
                try:
                    device = parts[0]
                    r_await = float(parts[9])  # r_await column (corrected)
                    w_await = float(parts[10])  # w_await column (corrected)
                    
                    if r_await > threshold or w_await > threshold:
                        result = {
                            'filename': os.path.basename(filepath),
                            'full_filepath': filepath,
                            'line_number': line_number,
                            'original_line': original_line,
                            'timestamp': current_timestamp,
                            'device': device,
                            'r_await': r_await,
                            'w_await': w_await,
                            'clean_line': clean_line,
                            'all_parts': parts
                        }
                        high_await_lines.append(result)
                        
                except (ValueError, IndexError):
                    # Skip lines that don't match expected format
                    continue
    
    return high_await_lines

def get_severity_emoji(max_await):
    """Return emoji based on severity level"""
    if max_await >= 5000:
        return "💀"  # Skull for catastrophic
    elif max_await >= 1000:
        return "🔥"  # Fire for critical
    elif max_await >= 500:
        return "⚠️ "  # Warning for extreme
    elif max_await >= 250:
        return "🔴"  # Red circle for very high
    elif max_await >= 200:
        return "🟠"  # Orange circle for severe
    elif max_await >= 100:
        return "🟡"  # Yellow circle for medium high
    else:
        return "🟤"  # Brown circle for slow

def get_severity_text(max_await):
    """Return severity text with color"""
    if max_await >= 5000:
        return "\033[91m\033[1mCATASTROPHIC\033[0m"  # Bold red
    elif max_await >= 1000:
        return "\033[91m\033[1mCRITICAL\033[0m"  # Bold red
    elif max_await >= 500:
        return "\033[91mEXTREME\033[0m"  # Red
    elif max_await >= 250:
        return "\033[93mVERY HIGH\033[0m"  # Yellow
    elif max_await >= 200:
        return "\033[35mSEVERE\033[0m"  # Magenta
    elif max_await >= 100:
        return "\033[33mMEDIUM HIGH\033[0m"  # Orange
    else:
        return "\033[33mSLOW\033[0m"  # Brown

def print_detailed_entry(entry, index):
    """Print detailed information for a single entry"""
    max_await = max(entry['r_await'], entry['w_await'])
    server = entry['filename'].split('-')[1]
    emoji = get_severity_emoji(max_await)
    severity = get_severity_text(max_await)
    
    print(f"\n{'='*85}")
    print(f"{emoji} Entry #{index + 1} - {severity}")
    print(f"{'='*85}")
    print(f"🖥️  Server IP: \033[1m{server}\033[0m")
    print(f"📁 Source File: {entry['filename']}")
    print(f"📍 Full Path: {entry['full_filepath']}")
    print(f"📏 Line Number: \033[1m{entry['line_number']}\033[0m")
    print(f"⏰ Timestamp: {entry['timestamp']}")
    print(f"💾 Device: \033[1m{entry['device']}\033[0m")
    print(f"📖 Read Await: {entry['r_await']:.2f} ms")
    print(f"✍️  Write Await: \033[1m{entry['w_await']:.2f} ms\033[0m")
    print(f"📊 Max Await: \033[1m{max_await:.2f} ms\033[0m")
    print(f"\n📄 Original Line from File:")
    print(f"   {entry['original_line']}")
    print(f"\n🔧 Cleaned/Parsed Line:")
    print(f"   {entry['clean_line']}")
    print(f"\n📋 Parsed Fields:")
    headers = ['Device', 'r/s', 'w/s', 'rkB/s', 'wkB/s', 'rrqm/s', 'wrqm/s', '%rrqm', '%wrqm', 'r_await', 'w_await', 'aqu-sz', 'rareq-sz', 'wareq-sz', 'svctm', '%util']
    for i, (header, value) in enumerate(zip(headers, entry['all_parts'])):
        if header == 'r_await' and float(value) > 100:
            marker = " \033[91m<-- HIGH READ\033[0m"
        elif header == 'w_await' and float(value) > 100:
            marker = " \033[91m<-- HIGH WRITE\033[0m"
        else:
            marker = ""
        print(f"   {i:2d}. {header:10s}: {value:>12s}{marker}")

def main():
    """Main function to process all iostat files"""
    parser = argparse.ArgumentParser(description='Analyze iostat files for high await times')
    parser.add_argument('threshold', type=float, nargs='?', default=100.0,
                       help='Threshold for await times in milliseconds (default: 100.0)')
    parser.add_argument('--detailed', '-d', action='store_true',
                       help='Show detailed information for each entry')
    parser.add_argument('--limit', '-l', type=int, default=None,
                       help='Limit number of detailed entries to show (default: show all)')
    parser.add_argument('--extreme-only', '-e', action='store_true',
                       help='Show only critical entries (>=1000ms)')
    
    args = parser.parse_args()
    threshold = args.threshold
    
    if args.extreme_only:
        threshold = 1000.0
        print(f"Showing only CRITICAL entries (>= 1000ms)")
    else:
        print(f"Analyzing for await times >= {threshold}ms")
    
    iostat_files = glob.glob("iostat-*.output")
    
    if not iostat_files:
        print("No iostat-*.output files found in current directory")
        return
    
    print(f"Found {len(iostat_files)} iostat files to analyze")
    print("="*80)
    
    all_results = []
    
    for filepath in sorted(iostat_files):
        print(f"Processing: {filepath}")
        results = check_high_await_times(filepath, threshold)
        all_results.extend(results)
    
    if not all_results:
        print(f"\nNo r_await or w_await times found greater than {threshold}ms")
        return
    
    # Sort results by await time (highest first)
    all_results.sort(key=lambda x: max(x['r_await'], x['w_await']), reverse=True)
    
    print(f"\n\n🎯 FOUND {len(all_results)} entries with await times >= {threshold}ms")
    print("═"*85)
    
    # Summary by server
    by_server = {}
    for result in all_results:
        server = result['filename'].split('-')[1]
        if server not in by_server:
            by_server[server] = []
        by_server[server].append(result)
    
    print(f"\n🖥️  SUMMARY BY SERVER:")
    print("═"*85)
    for server, entries in sorted(by_server.items()):
        max_await = max([max(e['r_await'], e['w_await']) for e in entries])
        emoji = get_severity_emoji(max_await)
        severity = get_severity_text(max_await)
        print(f"{emoji} Server {server}: {len(entries):3d} entries, max await: \033[1m{max_await:8.2f}ms\033[0m ({severity})")
    
    # Summary table
    print(f"\n\n📊 SUMMARY TABLE - Top entries >= {threshold}ms:")
    print("═"*140)
    print(f"{'#':<4} {'🔥':<2} {'Server IP':<15} {'📁 File':<38} {'📏Line':<6} {'💾Dev':<8} {'📖r_await':<10} {'✍️w_await':<10} {'📊Max':<10} {'⏰ Timestamp':<20}")
    print("═"*140)
    
    display_limit = args.limit if args.limit else len(all_results)
    
    for i, result in enumerate(all_results[:display_limit]):
        server = result['filename'].split('-')[1]
        max_await = max(result['r_await'], result['w_await'])
        emoji = get_severity_emoji(max_await)
        
        # Color code the max await value
        if max_await >= 5000:
            max_color = f"\033[91m\033[1m{max_await:8.2f}\033[0m"  # Bold red for catastrophic
        elif max_await >= 1000:
            max_color = f"\033[91m{max_await:8.2f}\033[0m"  # Red for critical
        elif max_await >= 500:
            max_color = f"\033[93m{max_await:8.2f}\033[0m"  # Yellow for extreme
        elif max_await >= 250:
            max_color = f"\033[35m{max_await:8.2f}\033[0m"  # Magenta for very high
        elif max_await >= 200:
            max_color = f"\033[33m{max_await:8.2f}\033[0m"  # Orange for severe
        elif max_await >= 100:
            max_color = f"\033[33m{max_await:8.2f}\033[0m"  # Orange for medium high
        else:
            max_color = f"{max_await:8.2f}"
            
        # Color code w_await if it's the high value
        if result['w_await'] == max_await and result['w_await'] >= 100:
            w_await_color = f"\033[91m{result['w_await']:8.2f}\033[0m"  # Red
        else:
            w_await_color = f"{result['w_await']:8.2f}"
            
        # Color code r_await if it's the high value
        if result['r_await'] == max_await and result['r_await'] >= 100:
            r_await_color = f"\033[91m{result['r_await']:8.2f}\033[0m"  # Red
        else:
            r_await_color = f"{result['r_await']:8.2f}"
        
        print(f"{i+1:<4} {emoji:<2} {server:<15} {result['filename']:<38} {result['line_number']:<6} {result['device']:<8} "
              f"{r_await_color:<10} {w_await_color:<10} {max_color:<10} {result['timestamp']:<20}")
    
    # Detailed entries if requested
    if args.detailed:
        print(f"\n\nDETAILED ENTRIES:")
        entries_to_show = all_results[:display_limit] if display_limit else all_results
        
        for i, entry in enumerate(entries_to_show):
            print_detailed_entry(entry, i)
    
    # Severity breakdown
    catastrophic = [r for r in all_results if max(r['r_await'], r['w_await']) >= 5000]
    critical = [r for r in all_results if 1000 <= max(r['r_await'], r['w_await']) < 5000]
    extreme = [r for r in all_results if 500 <= max(r['r_await'], r['w_await']) < 1000]
    very_high = [r for r in all_results if 250 <= max(r['r_await'], r['w_await']) < 500]
    severe = [r for r in all_results if 200 <= max(r['r_await'], r['w_await']) < 250]
    medium_high = [r for r in all_results if 100 <= max(r['r_await'], r['w_await']) < 200]
    normal = [r for r in all_results if threshold <= max(r['r_await'], r['w_await']) < 100]
    
    print(f"\n\n📈 SEVERITY BREAKDOWN:")
    print("═"*85)
    print(f"💀 Catastrophic (>=5000ms):      \033[91m\033[1m{len(catastrophic):3d} entries\033[0m")
    print(f"🔥 Critical (1000-4999ms):       \033[91m\033[1m{len(critical):3d} entries\033[0m")
    print(f"⚠️  Extreme (500-999ms):         \033[91m{len(extreme):3d} entries\033[0m")
    print(f"🔴 Very High (250-499ms):        \033[93m{len(very_high):3d} entries\033[0m")
    print(f"🟠 Severe (200-249ms):           \033[35m{len(severe):3d} entries\033[0m")
    print(f"🟡 Medium High (100-199ms):      \033[33m{len(medium_high):3d} entries\033[0m")
    if normal:
        print(f"🟤 Slow ({threshold:.0f}-99ms):            \033[33m{len(normal):3d} entries\033[0m")
    
    print(f"\n\n💡 USAGE EXAMPLES:")
    print("═"*85)
    print(f"📋 python3 {sys.argv[0]} 50          # Show entries >= 50ms")
    print(f"📋 python3 {sys.argv[0]} 100 -d      # Show entries >= 100ms with details")
    print(f"📋 python3 {sys.argv[0]} 200 -d -l 5 # Show top 5 entries >= 200ms with details")
    print(f"📋 python3 {sys.argv[0]} -e -d       # Show only critical entries (>=1000ms) with details")

if __name__ == "__main__":
    main()
