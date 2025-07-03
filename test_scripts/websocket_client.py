import asyncio
import websockets

async def listen():
    """Connects to the WebSocket and listens for messages."""
    uri = "ws://localhost:8000/jobs/stream"
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"Successfully connected to {uri}")
            while True:
                try:
                    message = await websocket.recv()
                    print(f"< Received: {message}")
                except websockets.ConnectionClosed:
                    print("Connection closed by the server.")
                    break
    except Exception as e:
        print(f"Failed to connect to {uri}. Is the server running?")
        print(f"Error: {e}")


if __name__ == "__main__":
    print("--- Starting WebSocket Client ---")
    asyncio.run(listen())