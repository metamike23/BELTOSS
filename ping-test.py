import subprocess
import platform
import re
import sys

import requests

def get_gateway_ip():
    try:
        # Check if a network connection is active
        response = requests.get("https://www.google.com", timeout=5)
        if response.status_code != 200:
            raise Exception("No network connection detected")

        # Get the default gateway based on the OS
        system_platform = platform.system()
        if system_platform == "Windows":
            result = subprocess.run("route print | findstr 0.0.0.0", shell=True, capture_output=True, text=True)
        elif system_platform in ["Linux", "Darwin"]:
            result = subprocess.run("ip route | grep default", shell=True, capture_output=True, text=True)
        else:
            raise Exception(f"Unsupported platform: {system_platform}")

        if result.returncode != 0:
            raise Exception("Could not detect default gateway")

        # Extract the gateway IP
        gateway_ip = result.stdout.split()[2]
        return gateway_ip
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def ping_device(ip):
    """Ping a device and return average ping statistics."""
    try:
        # Define the ping command based on the OS
        if platform.system().lower() == "windows":
            cmd = ["ping", "-n", "4", ip]  # Windows-specific ping command
        else:
            cmd = ["ping", "-c", "4", ip]  # Linux/macOS ping command

        # Execute the ping command
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            return f"Ping failed for {ip}: {result.stderr.strip()}"

        # Parse the average ping time from the output
        if platform.system().lower() == "windows":
            match = re.search(r"Average = (\d+)ms", result.stdout)
        else:
            match = re.search(r"min/avg/max/(?:stddev|mdev) = [\d.]+/([\d.]+)/[\d.]+/[\d.]+ ms", result.stdout)

        if match:
            avg_ping = float(match.group(1)) if platform.system().lower() != "windows" else float(match.group(1))
            return avg_ping
        else:
            return "No average ping data available"

    except Exception as e:
        return f"Error pinging {ip}: {e}"

def get_devices_from_gateway(gateway_ip):
    """Get a list of active devices from the gateway using Nmap."""
    try:
        cmd = ["nmap", "-sn", gateway_ip + "/24"]  # Ping scan
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            raise Exception(f"Nmap scan failed: {result.stderr.strip()}")

        # Extract active device IPs from the Nmap output
        devices = []
        for line in result.stdout.splitlines():
            match = re.search(r"Nmap scan report for (\S+)", line)
            if match:
                devices.append(match.group(1))

        return devices
    except Exception as e:
        print(f"Error during Nmap scan: {e}")
        return []

def save_ping_statistics_to_file(ping_results, filename):
    """Save the ping statistics to a file."""
    try:
        with open(filename, "w") as file:
            for ip, stats in ping_results.items():
                file.write(f"{ip}: {stats}\n")
        print(f"Ping statistics saved to {filename}")
    except Exception as e:
        print(f"Error saving results: {e}")

if __name__ == "__main__":
    # Specify the gateway IP (e.g., "192.168.1.1")
    gateway_ip = get_gateway_ip()

    # Step 1: Get the list of devices from the gateway
    devices = get_devices_from_gateway(gateway_ip)

    # Step 2: Ping each device and collect average ping statistics
    ping_results = {}
    for device in devices:
        print(f"Pinging device: {device}")
        ping_results[device] = ping_device(device)

    # Step 3: Save the ping statistics to a file
    save_ping_statistics_to_file(ping_results, "ping_statistics.txt")

    print("Ping scan and statistics collection completed.")
