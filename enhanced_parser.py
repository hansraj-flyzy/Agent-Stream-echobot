#!/usr/bin/env python3
"""
Enhanced Log Parser for AgentStream Dashboard
==========================================
Handles multiline logs and proper timestamp/digit extraction
"""

import re
from datetime import datetime, timezone
from collections import deque

class EnhancedLogParser:
    def __init__(self):
        self.log_buffer = deque(maxlen=10)  # Keep last 10 lines for multiline parsing
        
    def parse_multiline_log(self, lines):
        """Parse multiple log lines together to handle multiline events"""
        events = []
        
        for i, line in enumerate(lines):
            if line.strip():
                self.log_buffer.append(line.strip())
                
                # Try to parse this line as an event
                event = self.parse_single_line(line.strip(), list(self.log_buffer))
                if event:
                    events.append(event)
                    
        return events
    
    def parse_single_line(self, line, context_lines):
        """Parse a single line with context from surrounding lines"""
        try:
            # Extract timestamp with timezone awareness
            timestamp_match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})', line)
            if not timestamp_match:
                return None
                
            timestamp_str = timestamp_match.group(1)
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f').replace(tzinfo=timezone.utc)
            
            # Extract connection ID
            connection_match = re.search(r'(conn_\w+)', line)
            connection_id = connection_match.group(1) if connection_match else 'unknown'
            
            # Extract stream SID and call SID from context
            stream_sid = self.extract_from_context(context_lines, r'Stream SID: ([^\s,\n]+)')
            call_sid = self.extract_from_context(context_lines, r'Call SID: ([^\s,\n]+)')
            
            # Parse different event types
            if '🎉 CONNECTED EVENT' in line:
                return {
                    'timestamp': timestamp,
                    'timestamp_str': timestamp_str,
                    'type': 'connected',
                    'event': 'CONNECTED',
                    'description': 'New call connected',
                    'icon': '🎉',
                    'connection_id': connection_id,
                    'stream_sid': stream_sid,
                    'call_sid': call_sid,
                    'severity': 'success'
                }
            
            elif '🚀 START EVENT' in line:
                return {
                    'timestamp': timestamp,
                    'timestamp_str': timestamp_str,
                    'type': 'start',
                    'event': 'START',
                    'description': 'Stream started',
                    'icon': '🚀',
                    'connection_id': connection_id,
                    'stream_sid': stream_sid,
                    'call_sid': call_sid,
                    'severity': 'info'
                }
            
            elif '🎵 MEDIA EVENT' in line:
                chunk = self.extract_from_context(context_lines, r'Chunk: (\d+)')
                size = self.extract_from_context(context_lines, r'size: (\d+) bytes')
                sequence = self.extract_from_context(context_lines, r'Sequence: (\d+)')
                
                return {
                    'timestamp': timestamp,
                    'timestamp_str': timestamp_str,
                    'type': 'media',
                    'event': 'MEDIA',
                    'description': f"Audio chunk {chunk or 'N/A'} ({size or 'N/A'} bytes)",
                    'icon': '🎵',
                    'connection_id': connection_id,
                    'stream_sid': stream_sid,
                    'call_sid': call_sid,
                    'chunk': chunk,
                    'size': size,
                    'sequence': sequence,
                    'severity': 'primary'
                }
            
            elif '🔢 DTMF EVENT' in line:
                # Extract digit and duration from context lines
                digit = self.extract_from_context(context_lines, r'🎹 Digit: ([^\s\n]+)')
                duration = self.extract_from_context(context_lines, r'⏱️\s+Duration: ([^\s\n]+)ms')
                
                return {
                    'timestamp': timestamp,
                    'timestamp_str': timestamp_str,
                    'type': 'dtmf',
                    'event': 'DTMF',
                    'description': f"Key pressed: {digit or 'Unknown'}",
                    'icon': '🔢',
                    'connection_id': connection_id,
                    'stream_sid': stream_sid,
                    'call_sid': call_sid,
                    'digit': digit,
                    'duration': duration,
                    'severity': 'info'
                }
            
            elif '🔢 DTMF RESPONSE' in line:
                digit = self.extract_from_context([line], r"Acknowledged digit '([^']+)'")
                return {
                    'timestamp': timestamp,
                    'timestamp_str': timestamp_str,
                    'type': 'dtmf_response',
                    'event': 'DTMF_ACK',
                    'description': f"DTMF acknowledged: {digit or 'Unknown'}",
                    'icon': '✅',
                    'connection_id': connection_id,
                    'stream_sid': stream_sid,
                    'call_sid': call_sid,
                    'digit': digit,
                    'severity': 'success'
                }
            
            elif '📍 MARK EVENT' in line:
                mark_name = self.extract_from_context(context_lines, r'🏷️\s+Mark Name: ([^\s\n]+)')
                return {
                    'timestamp': timestamp,
                    'timestamp_str': timestamp_str,
                    'type': 'mark',
                    'event': 'MARK',
                    'description': f"Mark: {mark_name or 'Unknown'}",
                    'icon': '📍',
                    'connection_id': connection_id,
                    'stream_sid': stream_sid,
                    'call_sid': call_sid,
                    'mark_name': mark_name,
                    'severity': 'warning'
                }
            
            elif '📍 MARK RESPONSE' in line:
                mark_name = self.extract_from_context([line], r"Acknowledged mark '([^']+)'")
                return {
                    'timestamp': timestamp,
                    'timestamp_str': timestamp_str,
                    'type': 'mark_response',
                    'event': 'MARK_ACK',
                    'description': f"Mark acknowledged: {mark_name or 'Unknown'}",
                    'icon': '✅',
                    'connection_id': connection_id,
                    'stream_sid': stream_sid,
                    'call_sid': call_sid,
                    'mark_name': mark_name,
                    'severity': 'success'
                }
            
            elif '🧹 CLEAR EVENT' in line:
                return {
                    'timestamp': timestamp,
                    'timestamp_str': timestamp_str,
                    'type': 'clear',
                    'event': 'CLEAR',
                    'description': 'Clear command received',
                    'icon': '🧹',
                    'connection_id': connection_id,
                    'stream_sid': stream_sid,
                    'call_sid': call_sid,
                    'severity': 'warning'
                }
            
            elif '🧹 CLEAR RESPONSE' in line:
                return {
                    'timestamp': timestamp,
                    'timestamp_str': timestamp_str,
                    'type': 'clear_response',
                    'event': 'CLEAR_ACK',
                    'description': 'Clear command acknowledged',
                    'icon': '✅',
                    'connection_id': connection_id,
                    'stream_sid': stream_sid,
                    'call_sid': call_sid,
                    'severity': 'success'
                }
            
            elif '🛑 STOP EVENT' in line:
                reason = self.extract_from_context(context_lines, r'🔚 Reason: ([^\s\n]+)')
                return {
                    'timestamp': timestamp,
                    'timestamp_str': timestamp_str,
                    'type': 'stop',
                    'event': 'STOP',
                    'description': f"Call ended: {reason or 'Unknown'}",
                    'icon': '🛑',
                    'connection_id': connection_id,
                    'stream_sid': stream_sid,
                    'call_sid': call_sid,
                    'reason': reason,
                    'severity': 'danger'
                }
                
        except Exception as e:
            print(f"Error parsing log line: {e}")
        
        return None
    
    def extract_from_context(self, lines, pattern):
        """Extract a value from context lines using regex pattern"""
        for line in lines:
            match = re.search(pattern, line)
            if match:
                return match.group(1).strip()
        return None

# Test the enhanced parser
if __name__ == '__main__':
    parser = EnhancedLogParser()
    
    # Test with sample log lines
    test_lines = [
        "2025-07-31 16:44:58,855 - INFO - 🔢 DTMF EVENT - Key press from conn_1753960498855",
        "2025-07-31 16:44:58,855 - INFO -    🎹 Digit: 8",
        "2025-07-31 16:44:58,855 - INFO -    ⏱️  Duration: 250ms",
        "2025-07-31 16:44:58,856 - INFO -    📊 Sequence: 1",
        "2025-07-31 16:44:58,856 - INFO -    📊 Full DTMF data: {",
        '  "digit": "8",',
        '  "duration": "250"',
        "}"
    ]
    
    events = parser.parse_multiline_log(test_lines)
    for event in events:
        print(f"✅ Parsed: {event['event']} - {event['description']} (digit: {event.get('digit', 'N/A')})") 