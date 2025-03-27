#!/usr/bin/env python3
"""
infodump+ - System Information Diagnostic Tool
Originally written in Bash by Joseph Fleet | Rewritten in Python with AI assistance
Enhanced further using additional prompting.
"""

import os
import platform
import socket
import psutil
import subprocess
import argparse
from datetime import datetime

# Attempt to import rich for fancy output; fallback gracefully if not available.
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
except ImportError:
    Console = None

def get_console():
    """Returns a Console instance if rich is available."""
    return Console() if Console is not None else None

def header(title, console=None):
    """Prints a section header using rich or plain text."""
    if console:
        console.print(Panel(title, style="bold cyan"))
    else:
        print(f"\n{'=' * 20} {title} {'=' * 20}")

def get_basic_info(console=None):
    """Displays basic system information."""
    header("SYSTEM INFO", console)
    info = [
        f"Current Directory: {os.getcwd()}",
        f"Username: {os.getlogin()}",
        f"Hostname: {socket.gethostname()}",
        f"Kernel: {platform.release()}",
        f"OS: {platform.system()} {platform.version()}",
        f"Language: {os.environ.get('LANG', 'Unknown')}",
        f"Time: {datetime.now()}"
    ]
    for line in info:
        if console:
            console.print(line)
        else:
            print(line)

def check_network(console=None):
    """Checks network connectivity by pinging 1.1.1.1."""
    header("NETWORK", console)
    try:
        subprocess.check_call(
            ['ping', '-c', '1', '1.1.1.1'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        message = "✅ Outbound connection successful."
    except subprocess.CalledProcessError:
        message = "❌ Outbound connection FAILED."
    
    if console:
        console.print(message)
    else:
        print(message)

    if console:
        console.print("\nInterfaces:")
    else:
        print("\nInterfaces:")
    for iface in psutil.net_if_addrs().keys():
        if console:
            console.print(f" - {iface}")
        else:
            print(f" - {iface}")

def show_memory(console=None):
    """Displays memory usage."""
    header("MEMORY", console)
    mem = psutil.virtual_memory()
    lines = [
        f"Total: {mem.total / (1024 ** 3):.2f} GB",
        f"Available: {mem.available / (1024 ** 3):.2f} GB",
        f"Used: {mem.used / (1024 ** 3):.2f} GB ({mem.percent}%)"
    ]
    for line in lines:
        if console:
            console.print(line)
        else:
            print(line)

def show_disks(console=None):
    """Displays disk usage information."""
    header("DISK USAGE", console)
    partitions = psutil.disk_partitions()
    for p in partitions:
        try:
            usage = psutil.disk_usage(p.mountpoint)
            line = f"{p.device} ({p.mountpoint}): {usage.percent}% used"
        except PermissionError:
            line = f"{p.device} ({p.mountpoint}): Permission Denied"
        if console:
            console.print(line)
        else:
            print(line)

def largest_files(path="/home", count=3, console=None):
    """
    Finds and displays the largest files in the specified path.
    
    Args:
        path (str): Directory path to search.
        count (int): Number of largest files to display.
        console: Optional rich Console instance.
    """
    header(f"{count} LARGEST FILES in {path}", console)
    try:
        files = []
        for root, dirs, filenames in os.walk(path):
            for fname in filenames:
                fpath = os.path.join(root, fname)
                try:
                    size = os.path.getsize(fpath)
                    files.append((size, fpath))
                except OSError:
                    continue
        for size, f in sorted(files, reverse=True)[:count]:
            # Format size: use GB if the file is 1GB or larger, else MB.
            if size >= 1024 ** 3:  # 1GB = 1024^3 bytes
                formatted_size = f"{size / (1024 ** 3):.2f} GB"
            else:
                formatted_size = f"{size / (1024 ** 2):.2f} MB"
            line = f"{formatted_size} - {f}"
            if console:
                console.print(line)
            else:
                print(line)
    except Exception as e:
        error_message = f"Error: {e}"
        if console:
            console.print(error_message, style="bold red")
        else:
            print(error_message)

def top_cpu_processes(n=3, console=None):
    """
    Displays the top CPU consuming processes.
    
    Args:
        n (int): Number of processes to display.
        console: Optional rich Console instance.
    """
    header(f"TOP {n} CPU PROCESSES", console)
    processes = sorted(
        psutil.process_iter(['pid', 'name', 'cpu_percent']),
        key=lambda p: p.info.get('cpu_percent', 0),
        reverse=True
    )
    for p in processes[:n]:
        line = f"{p.info['pid']} - {p.info['name']} ({p.info['cpu_percent']}% CPU)"
        if console:
            console.print(line)
        else:
            print(line)

def show_temperatures(console=None):
    """
    Displays system temperature readings using lm-sensors.
    """
    header("SYSTEM TEMPERATURES", console)
    try:
        sensors_output = subprocess.check_output(["sensors"], universal_newlines=True)
        if console:
            console.print(sensors_output)
        else:
            print(sensors_output)
    except subprocess.CalledProcessError as e:
        error_message = f"Error executing lm-sensors: {e}"
        if console:
            console.print(error_message, style="bold red")
        else:
            print(error_message)
    except FileNotFoundError:
        error_message = "lm-sensors command not found. Please install lm-sensors."
        if console:
            console.print(error_message, style="bold red")
        else:
            print(error_message)

def show_nvidia_temperature(console=None):
    """
    Checks for an Nvidia GPU using nvidia-smi and displays its temperature.
    """
    try:
        nvidia_smi_list = subprocess.check_output(
            ["nvidia-smi", "-L"], universal_newlines=True
        ).strip()
        if not nvidia_smi_list:
            message = "No Nvidia GPU detected."
            if console:
                console.print(message, style="yellow")
            else:
                print(message)
            return
        
        temps_output = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=temperature.gpu", "--format=csv,noheader,nounits"],
            universal_newlines=True
        ).strip()
        temperatures = temps_output.splitlines()
        
        if temperatures:
            for idx, temp in enumerate(temperatures):
                message = f"GPU {idx}: {temp.strip()}°C"
                if console:
                    console.print(message)
                else:
                    print(message)
        else:
            message = "Unable to retrieve Nvidia GPU temperature."
            if console:
                console.print(message, style="bold red")
            else:
                print(message)
    except FileNotFoundError:
        message = "nvidia-smi not found. Nvidia drivers may not be installed."
        if console:
            console.print(message, style="bold red")
        else:
            print(message)
    except subprocess.CalledProcessError as e:
        message = f"Error calling nvidia-smi: {e}"
        if console:
            console.print(message, style="bold red")
        else:
            print(message)

def main():
    """Main function to execute the diagnostic tool."""
    parser = argparse.ArgumentParser(
        description="infodump+ - System Information Diagnostic Tool"
    )
    parser.add_argument("--path", default="/home", help="Path to search for largest files")
    parser.add_argument("--largest", type=int, default=3, help="Number of largest files to display")
    parser.add_argument("--cpu", type=int, default=3, help="Number of top CPU processes to display")
    parser.add_argument("--no-color", action="store_true", help="Disable colorful output")
    parser.add_argument("--no-temp", action="store_true", help="Disable lm-sensors temperature output")
    parser.add_argument("--no-nvidia", action="store_true", help="Disable Nvidia GPU temperature output")
    args = parser.parse_args()

    console = None
    if not args.no_color and Console is not None:
        console = get_console()

    get_basic_info(console)
    check_network(console)
    show_memory(console)
    show_disks(console)
    largest_files(path=args.path, count=args.largest, console=console)
    top_cpu_processes(n=args.cpu, console=console)
    if not args.no_temp:
        show_temperatures(console)
    if not args.no_nvidia:
        show_nvidia_temperature(console)

if __name__ == "__main__":
    main()
