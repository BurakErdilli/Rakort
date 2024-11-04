from fastapi import FastAPI
import asyncio
import httpx
import paramiko

app = FastAPI()

# List to store unreachable IP addresses
unreachable_ips = []

# Network prefix for scanning
network_prefix = "172.29."

# Global variable to control the running state of the scanning operation
running = True


async def check_ip(ip: str):
    """Checks if the specified IP address is reachable and attempts to establish an SSH connection.

    Args:
        ip (str): The IP address to check.
    """
    async with httpx.AsyncClient() as client:
        try:
            # Ping the IP address using HTTP request
            response = await client.get(f"http://{ip}", timeout=2.0)
            if response.status_code == 200:
                print(f"{ip} is reachable.")
                # Attempt SSH connection
                await ssh_connect(ip)
            else:
                print(
                    f"{ip} is unreachable (HTTP status code: {response.status_code}).")
                unreachable_ips.append(ip)
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            print(f"{ip} is unreachable: {e}")
            unreachable_ips.append(ip)


async def ssh_connect(ip: str):
    """Attempts to establish an SSH connection to the specified IP address.

    Args:
        ip (str): The IP address to connect to.
    """
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Attempt to connect to the IP (replace 'username' and 'password' as needed)
        client.connect(ip, username='username', password='password', timeout=2)
        print(f"SSH connection established to {ip}.")
        client.close()
    except Exception as e:
        print(f"Error connecting to {ip} via SSH: {e}")
        unreachable_ips.append(ip)


async def scan_network():
    """Scan the specified network for active IP addresses."""
    tasks = []
    for i in range(0, 256):  # Scan from 172.29.0.0 to 172.29.255.255
        for j in range(1, 255):  # Start from 1 to 254 for hosts
            ip = f"{network_prefix}{i}.{j}"
            tasks.append(check_ip(ip))

    await asyncio.gather(*tasks)  # Run all tasks concurrently


@app.on_event("startup")
async def startup_event():
    """Starts the scanning process when the application starts."""
    asyncio.create_task(scan_network())  # Start scanning in the background


@app.on_event("shutdown")
async def shutdown_event():
    """Handles the application shutdown event."""
    global running
    running = False  # Stop the scanning loop


@app.get("/unreachable/")
async def get_unreachable_ips():
    """Retrieves the list of unreachable IP addresses.

    Returns:
        dict: A dictionary containing the list of unreachable IP addresses.
    """
    return {"unreachable_ips": unreachable_ips}


@app.get("/scan/")
async def scan():
    """Initiates the network scan.

    Returns:
        dict: A message indicating that the scan has started.
    """
    if running:
        return {"message": "Network scan in progress..."}
    else:
        return {"message": "Network scan has been stopped."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
