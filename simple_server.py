#!/usr/bin/env python3
"""
Simple WebSocket Echo Server for Exotel Voice Streaming
======================================================

A minimal WebSocket server that echoes audio packets back to Exotel,
perfect for testing bidirectional voice streaming functionality.

Features:
- Handles all Exotel WebSocket events (connected, start, media, dtmf, stop)
- Echoes media packets back for bidirectional testing
- Comprehensive logging with timestamps
- Connection tracking and error handling
- Ready for production deployment

Usage:
    python3 simple_server.py

Requirements:
    - websockets>=12.0
    - Python 3.8+
"""

import asyncio
import websockets
import json
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

# Add file handler for persistent logging
file_handler = logging.FileHandler('logs/voice_bot_echo.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

async def handle_websocket(websocket, path):
    """
    Handle incoming WebSocket connections from Exotel.
    
    This function processes all Exotel voice streaming events and echoes
    media packets back for bidirectional testing.
    """
    connection_id = f"conn_{int(datetime.now().timestamp() * 1000)}"
    logger.info(f"🔗 New WebSocket connection established: {connection_id} on path: {path}")
    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                event_type = data.get('event', 'unknown')
                logger.info(f"📨 Received event from {connection_id}: {event_type}")
                
                # Handle different Exotel events
                if event_type == 'connected':
                    logger.info(f"🎉 Call connected for {connection_id}")
                    # Log call details for debugging
                    with open('logs/calls.log', 'a') as f:
                        f.write(json.dumps({
                            'timestamp': datetime.now().isoformat(),
                            'connection_id': connection_id,
                            'event': 'connected',
                            'data': data
                        }) + '\n')
                
                elif event_type == 'start':
                    logger.info(f"🚀 Stream started for {connection_id}")
                    logger.info(f"📋 Stream details: Call SID: {data.get('start', {}).get('call_sid', 'N/A')}")
                
                elif event_type == 'media':
                    # Echo back media packets for bidirectional testing
                    payload_size = len(data.get('media', {}).get('payload', ''))
                    logger.info(f"🎵 Media packet received from {connection_id}: size={payload_size} bytes")
                    
                    # Echo the media packet back to Exotel
                    echo_response = {
                        'event': 'media',
                        'stream_sid': data.get('stream_sid'),
                        'media': data.get('media')
                    }
                    
                    await websocket.send(json.dumps(echo_response))
                    logger.info(f"🔊 Media packet echoed back to {connection_id}")
                
                elif event_type == 'dtmf':
                    digit = data.get('dtmf', {}).get('digit', 'unknown')
                    logger.info(f"🔢 DTMF digit received from {connection_id}: {digit}")
                
                elif event_type == 'stop':
                    reason = data.get('stop', {}).get('reason', 'unknown')
                    logger.info(f"🛑 Stream stopped for {connection_id}: {reason}")
                
                elif event_type == 'mark':
                    mark_name = data.get('mark', {}).get('name', 'unknown')
                    logger.info(f"📍 Mark event received from {connection_id}: {mark_name}")
                
                elif event_type == 'clear':
                    logger.info(f"🧹 Clear event received from {connection_id}")
                
                else:
                    logger.warning(f"❓ Unknown event type from {connection_id}: {event_type}")
                    
            except json.JSONDecodeError as e:
                logger.error(f"❌ Invalid JSON from {connection_id}: {e}")
            except Exception as e:
                logger.error(f"❌ Error processing message from {connection_id}: {e}")
                
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"👋 Connection closed normally: {connection_id}")
    except Exception as e:
        logger.error(f"❌ Connection error for {connection_id}: {str(e)}")
    finally:
        logger.info(f"🔚 Connection ended: {connection_id}")

async def main():
    """
    Main server function that starts the WebSocket server.
    """
    port = 5000
    host = "0.0.0.0"
    
    logger.info(f"🚀 Starting Voice Bot Echo Server...")
    logger.info(f"📡 Server will listen on {host}:{port}")
    logger.info(f"🌐 WebSocket endpoint: ws://{host}:{port}")
    logger.info(f"📝 Logs will be saved to: logs/voice_bot_echo.log")
    
    server = await websockets.serve(
        handle_websocket,
        host,
        port,
        ping_interval=30,  # Send ping every 30 seconds
        ping_timeout=10    # Wait 10 seconds for pong response
    )
    
    logger.info(f"✅ Voice Bot Echo Server running at ws://{host}:{port}")
    logger.info(f"🎯 Ready to receive Exotel voice streaming connections!")
    
    try:
        await server.wait_closed()
    except KeyboardInterrupt:
        logger.info("🛑 Server shutdown requested by user")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Voice Bot Echo Server shutting down...")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}") 