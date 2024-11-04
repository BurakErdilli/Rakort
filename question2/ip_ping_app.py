from fastapi import FastAPI
import asyncio
import httpx
import signal
import sys

app = FastAPI()

# List to store unreachable IP addresses
unreachable_ips = []

# IP addresses to ping (from 192.168.1.1 to 192.168.1.255)
ip_addresses = [f"192.168.1.{i}" for i in range(1, 256)]  # Valid IP addresses

# Global variable to control the running state of the ping operation
running = True


async def ping_ip(ip: str):
    """Pings the specified IP address and checks its reachability.

    Args:
        ip (str): The IP address to ping.
    """
    async with httpx.AsyncClient() as client:
        try:
            # Send an HTTP request to the IP address
            response = await client.get(f"http://{ip}", timeout=2.0)
            if response.status_code == 200:
                return  # Only return if reachable, do nothing
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            # Print only if the IP is unreachable
            print(f"{ip} is unreachable: {e}")
            unreachable_ips.append(ip)


async def ping_all_ips():
    """Pings all specified IP addresses in a loop.

    This function continuously pings the IP addresses in the ip_addresses list.
    It collects the unreachable IPs every 5 seconds.
    """
    while running:  # Continue pinging while running is True
        tasks = [ping_ip(ip) for ip in ip_addresses]  # Ping all IP addresses
        await asyncio.gather(*tasks)  # Run all ping tasks concurrently
        print("Skipped pinging for 5 seconds, preparing for the next cycle...")
        await asyncio.sleep(5)  # Wait for 5 seconds before the next ping


@app.on_event("startup")
async def startup_event():
    """Starts the pinging process when the application starts."""
    asyncio.create_task(ping_all_ips())  # Start pinging in the background


@app.on_event("shutdown")
async def shutdown_event():
    """Handles the application shutdown event."""
    global running
    running = False  # Stop the pinging loop


def signal_handler(sig, frame):
    """Handles the termination signal for graceful shutdown."""
    print("Received exit signal, shutting down...")
    asyncio.run(shutdown_event())
    sys.exit(0)


# Register signal handler for Ctrl+C (SIGINT)
signal.signal(signal.SIGINT, signal_handler)


@app.get("/unreachable/")
async def get_unreachable_ips():
    """Retrieves the list of unreachable IP addresses.

    Returns:
        dict: A dictionary containing the list of unreachable IP addresses.
    """
    return {"unreachable_ips": unreachable_ips}
