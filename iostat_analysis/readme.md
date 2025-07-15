# detailed_await_analysis.py

A comprehensive Python script for analyzing iostat output files to identify and analyze high I/O await times in Cassandra cluster environments.

## 📋 Description

This script parses iostat output files and provides detailed analysis of I/O await times, helping identify performance bottlenecks in storage systems. It offers color-coded output, severity classification, and comprehensive reporting capabilities.

## 🎯 Features

- **Threshold-based Analysis**: Configurable await time thresholds
- **Color-coded Output**: Visual severity indicators with emojis
- **Detailed Reporting**: Comprehensive breakdowns by server and severity
- **Flexible Display Options**: Summary tables and detailed entry views
- **Critical Filtering**: Focus on extreme performance issues
- **Multi-file Processing**: Analyzes all iostat files in directory

## 🚀 Usage

### Basic Syntax
```bash
python3 detailed_await_analysis.py [threshold] [options]
```

### Command Line Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `threshold` | float | 100.0 | Threshold for await times in milliseconds |
| `--detailed` / `-d` | flag | False | Show detailed information for each entry |
| `--limit` / `-l` | int | None | Limit number of detailed entries to show |
| `--extreme-only` / `-e` | flag | False | Show only critical entries (≥1000ms) |

### Examples

#### 1. Basic Analysis (50ms threshold)
```bash
python3 detailed_await_analysis.py 50
```

**Output:**
```
Analyzing for await times >= 50ms
Found 10 iostat files to analyze
================================================================================
Processing: iostat-10.xx.56.xxx-2025-07-09--22_35_40.output
Processing: iostat-10.xx.56.yyy-2025-07-09--22_35_40.output
...

🎯 FOUND 2,341 entries with await times >= 50ms
═════════════════════════════════════════════════════════════════════════════════

🖥️  SUMMARY BY SERVER:
═════════════════════════════════════════════════════════════════════════════════
🔥 Server 10.xx.56.xxx: 234 entries, max await: 2,847.50ms (CRITICAL)
🟠 Server 10.xx.56.yyy: 187 entries, max await:   285.30ms (SEVERE)
🟡 Server 10.xx.56.zzz: 156 entries, max await:   145.20ms (MEDIUM HIGH)
```

#### 2. Detailed Analysis with 100ms threshold
```bash
python3 detailed_await_analysis.py 100 --detailed
```

**Output:**
```
═════════════════════════════════════════════════════════════════════════════════
🔥 Entry #1 - CRITICAL
═════════════════════════════════════════════════════════════════════════════════
🖥️  Server IP: 10.xx.56.xxx
📁 Source File: iostat-10.xx.56.xxx-2025-07-09--22_35_40.output
📍 Full Path: /path/to/iostat-10.xx.56.xxx-2025-07-09--22_35_40.output
📏 Line Number: 1247
⏰ Timestamp: 07/09/2025 10:35:42 PM
💾 Device: dm-2
📖 Read Await: 125.50 ms
✍️  Write Await: 2847.50 ms
📊 Max Await: 2847.50 ms

📄 Original Line from File:
   dm-2    45.2   127.8   1024.5   3584.2     0.0     2.1     0.00     1.62   125.50  2847.50     3.45   22.68   28.04   15.20   98.75

🔧 Cleaned/Parsed Line:
   dm-2    45.2   127.8   1024.5   3584.2     0.0     2.1     0.00     1.62   125.50  2847.50     3.45   22.68   28.04   15.20   98.75

📋 Parsed Fields:
    0. Device    :         dm-2
    1. r/s       :         45.2
    2. w/s       :        127.8
    3. rkB/s     :       1024.5
    4. wkB/s     :       3584.2
    5. rrqm/s    :          0.0
    6. wrqm/s    :          2.1
    7. %rrqm     :         0.00
    8. %wrqm     :         1.62
    9. r_await   :       125.50
   10. w_await   :      2847.50 <-- HIGH WRITE
   11. aqu-sz    :         3.45
   12. rareq-sz  :        22.68
   13. wareq-sz  :        28.04
   14. svctm     :        15.20
   15. %util     :        98.75
```

#### 3. Top 5 High-Impact Entries
```bash
python3 detailed_await_analysis.py 200 --detailed --limit 5
```

#### 4. Critical Issues Only
```bash
python3 detailed_await_analysis.py --extreme-only --detailed
```

**Output:**
```
Showing only CRITICAL entries (>= 1000ms)
Found 10 iostat files to analyze
================================================================================

🎯 FOUND 15 entries with await times >= 1000ms
═════════════════════════════════════════════════════════════════════════════════

💀 Catastrophic (>=5000ms):        2 entries
🔥 Critical (1000-4999ms):        13 entries
⚠️  Extreme (500-999ms):           0 entries
🔴 Very High (250-499ms):          0 entries
🟠 Severe (200-249ms):             0 entries
🟡 Medium High (100-199ms):        0 entries
```

#### 5. Quick Summary (25ms threshold)
```bash
python3 detailed_await_analysis.py 25
```

## 📊 Output Interpretation

### Severity Levels

| Emoji | Level | Threshold | Color | Description |
|-------|-------|-----------|-------|-------------|
| 💀 | Catastrophic | ≥5000ms | Bold Red | System nearly unusable |
| 🔥 | Critical | 1000-4999ms | Red | Severe performance impact |
| ⚠️ | Extreme | 500-999ms | Red | High performance impact |
| 🔴 | Very High | 250-499ms | Yellow | Notable performance impact |
| 🟠 | Severe | 200-249ms | Magenta | Moderate performance impact |
| 🟡 | Medium High | 100-199ms | Orange | Low performance impact |
| 🟤 | Slow | threshold-99ms | Orange | Above threshold |

### Key Metrics Explained

- **r_await**: Average time for read requests to be served (milliseconds)
- **w_await**: Average time for write requests to be served (milliseconds)
- **Max Await**: Higher of r_await or w_await values
- **Device**: Storage device identifier (e.g., dm-2, sda1)
- **%util**: Percentage of CPU time during I/O requests

## 📈 Sample Output Sections

### 1. Server Summary
```
🖥️  SUMMARY BY SERVER:
═════════════════════════════════════════════════════════════════════════════════
🔥 Server 10.xx.56.xxx: 234 entries, max await: 2,847.50ms (CRITICAL)
🟠 Server 10.xx.56.yyy: 187 entries, max await:   285.30ms (SEVERE)
🟡 Server 10.xx.56.zzz: 156 entries, max await:   145.20ms (MEDIUM HIGH)
```

### 2. Summary Table
```
📊 SUMMARY TABLE - Top entries >= 50ms:
════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
#    🔥 Server IP        📁 File                                📏Line 💾Dev    📖r_await  ✍️w_await  📊Max      ⏰ Timestamp        
════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
1    🔥 10.73.56.xxx     iostat-10.xx.56.xxx-2025-07-09--22_35_40.output  1247   dm-2     125.50     2847.50    2847.50    07/09/2025 10:35:42 PM
2    ⚠️  10.73.56.yyy     iostat-10.xx.56.yyy-2025-07-09--22_35_40.output  2156   sda1     542.30     125.20     542.30     07/09/2025 10:42:15 PM
```

### 3. Severity Breakdown
```
📈 SEVERITY BREAKDOWN:
═════════════════════════════════════════════════════════════════════════════════
💀 Catastrophic (>=5000ms):        2 entries
🔥 Critical (1000-4999ms):        13 entries
⚠️  Extreme (500-999ms):          45 entries
🔴 Very High (250-499ms):        123 entries
🟠 Severe (200-249ms):           234 entries
🟡 Medium High (100-199ms):      567 entries
🟤 Slow (50-99ms):             1,357 entries
```

## 🔧 Technical Details

### File Processing
- Automatically finds all `iostat-*.output` files in current directory
- Parses iostat extended format output
- Handles timestamped entries
- Extracts device-specific I/O statistics

### Data Extraction
- Parses r_await (column 9) and w_await (column 10) values
- Associates timestamps with data entries
- Extracts server IP from filename
- Maintains line number references

### Performance Considerations
- Processes files sequentially
- Sorts results by maximum await time
- Memory-efficient for large datasets
- Handles malformed lines gracefully

## 📁 Input File Format

Expected iostat output format:
```
07/09/2025 10:35:40 PM
Device            r/s     w/s     rkB/s     wkB/s   rrqm/s   wrqm/s  %rrqm  %wrqm r_await w_await aqu-sz rareq-sz wareq-sz  svctm  %util
dm-2             45.2   127.8    1024.5    3584.2     0.0     2.1   0.00   1.62  125.50 2847.50   3.45    22.68    28.04  15.20  98.75
sda1             23.1    87.4     512.3    2048.7     0.0     1.5   0.00   1.69   67.20  234.80   2.18    22.15    23.45  12.30  87.50
```

## 🛠️ Error Handling

- Gracefully handles missing files
- Skips malformed lines
- Continues processing if individual entries fail
- Provides informative error messages

## 💡 Usage Tips

1. **Start with lower thresholds** (25-50ms) for comprehensive analysis
2. **Use --detailed for troubleshooting** specific performance issues
3. **Focus on critical entries** with --extreme-only for urgent issues
4. **Limit output** with --limit for manageable reports
5. **Compare across servers** using server summary section

## 🔍 Troubleshooting

### Common Issues

1. **No files found**: Ensure iostat-*.output files exist in current directory
2. **No results**: Lower the threshold or check file format
3. **Parsing errors**: Verify iostat output format matches expected structure
4. **Memory issues**: Use --limit to reduce output size

### File Requirements

- Files must be named: `iostat-[IP]-[timestamp].output`
- Must contain extended iostat output format
- Timestamps should be in MM/DD/YYYY HH:MM:SS AM/PM format

## 📞 Support

For issues or questions regarding this script, refer to:
- ACI Worldwide ticket #00102987
- System administration team
- Performance engineering team

---

**Note**: This script is designed for analyzing Cassandra cluster performance data and should be used in conjunction with other monitoring tools for comprehensive system analysis.
