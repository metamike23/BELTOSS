import sys
import nmap
import subprocess
import platform
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

def scan_network(gateway_ip):
    try:
        # Initialize nmap scanner
        nm = nmap.PortScanner()

        # Scan the entire subnet
        network = gateway_ip + "/24"
        print(f"Scanning network: {network}")
        nm.scan(hosts=network, arguments="-O -sV -p-")

        # Parse scan results
        results = {}
        for host in nm.all_hosts():
            raw_output = nm[host]
            results[host] = raw_output

        return results
    except Exception as e:
        print(f"Error during scan: {e}")
        sys.exit(1)

def save_raw_results_to_file(results, filename):
    try:
        with open(filename, "w") as file:
            for ip, raw_output in results.items():
                file.write(f"--- Device: {ip} ---\n")
                file.write(f"{raw_output}\n")
                file.write(f"--- End of Device: {ip} ---\n\n")
        print(f"Raw results saved to {filename}")
    except Exception as e:
        print(f"Error saving results: {e}")
        sys.exit(1)


def print_ascii_art():
    art = r"""
  ___      _ _       ___ ___ 
 | _ ) ___| | |_ ___/ __/ __|
 | _ \/ -_) |  _/ _ \__ \__ \
 |___/\___|_|\__\___/___/___/

version 1.0
    """
    print(art)

if __name__ == "__main__":


    print_ascii_art()
    # Step 1: Get the gateway IP
    gateway_ip = get_gateway_ip()
    print(f"Detected Gateway IP: {gateway_ip}")

    # Step 2: Perform the network scan
    scan_results = scan_network(gateway_ip)

    # Step 3: Save the raw scan results to a file
    save_raw_results_to_file(scan_results, "raw_scan_results.txt")

    print("Network scan completed and raw results saved.")
