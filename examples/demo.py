"""
Demo script showing how to use the BlockIAM library

This example demonstrates all major features of the library including
device registration, access control, logging, and caching.
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Add parent directory to path to import blockiam
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from iot_iam import IAMClient, logger
from rich import print as rprint
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


def print_section(title: str) -> None:
    """Print a formatted section header"""
    rprint(f"\n[bold yellow]{'═' * 60}[/bold yellow]")
    rprint(f"[bold yellow]{title}[/bold yellow]")
    rprint(f"[bold yellow]{'═' * 60}[/bold yellow]\n")


def print_result(result: dict, success_msg: str = None) -> None:
    """Print formatted result"""
    if result['status'] == 'success':
        msg = success_msg or "Operation completed successfully"
        rprint(f"[green]✓[/green] {msg}")
        if 'tx_hash' in result:
            rprint(f"  [dim]Transaction: {result['tx_hash']}[/dim]")
        if 'gas_used' in result:
            rprint(f"  [dim]Gas used: {result['gas_used']}[/dim]")
    else:
        rprint(f"[red]✗[/red] Failed: {result.get('message', 'Unknown error')}")
    rprint()


def main():
    """Demonstrate IAMClient functionality"""
    
    # Print banner
    console.print(Panel.fit(
        "[bold cyan]BlockIAM - Professional Demo[/bold cyan]\n"
        "[dim]Blockchain-based Device Identity & Access Management[/dim]",
        border_style="cyan"
    ))
    
    # Initialize client
    print_section("Step 1: Initialize IAMClient")
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            progress.add_task(description="Connecting to blockchain...", total=None)
            client = IAMClient()
        
        rprint("[green]✓[/green] Client initialized successfully\n")
    except Exception as e:
        rprint(f"[red]✗ Error initializing client: {e}[/red]")
        return 1
    
    # Example device address (replace with actual address from Ganache)
    device_address = "0x1234567890123456789012345678901234567890"
    
    # Register a device
    print_section("Step 2: Register IoT Device")
    rprint(f"[cyan]Device Address:[/cyan] {device_address}")
    rprint(f"[cyan]Device Name:[/cyan] Smart Thermostat")
    rprint(f"[cyan]Device Role:[/cyan] sensor\n")
    
    result = client.register_device(
        address=device_address,
        name="Smart Thermostat",
        role="sensor",
        metadata="Location: Building A, Floor 3"
    )
    print_result(result, "Device registered successfully")
    
    # Grant access
    print_section("Step 3: Grant Device Access")
    result = client.grant_access(device_address, expiry=0)
    print_result(result, "Access granted successfully")
    
    # Check access
    print_section("Step 4: Verify Access Status")
    result = client.check_access(device_address)
    if result['status'] == 'success':
        has_access = result['has_access']
        status = "[green]GRANTED ✓[/green]" if has_access else "[red]DENIED ✗[/red]"
        rprint(f"Access status: {status}\n")
    
    # Log access
    print_section("Step 5: Log Access Event")
    result = client.log_access("Temperature reading request")
    print_result(result, "Access event logged")
    
    # Get device info
    print_section("Step 6: Retrieve Device Information")
    result = client.get_device_info(device_address)
    if result['status'] == 'success':
        data = result['data']
        table = Table(title="Device Information", show_header=False, border_style="cyan")
        table.add_column("Field", style="cyan bold", width=15)
        table.add_column("Value", style="white")
        
        table.add_row("Address", data['address'])
        table.add_row("Name", data['name'])
        table.add_row("Role", data['role'])
        table.add_row("Metadata", data['metadata'] or '(none)')
        table.add_row("Registered", str(datetime.fromtimestamp(data['registered_at'])))
        table.add_row("Status", "[green]Active[/green]" if data['is_registered'] else "[red]Inactive[/red]")
        
        console.print(table)
    rprint()
    
    # Fetch logs from blockchain
    print_section("Step 7: Fetch Blockchain Access Logs")
    result = client.get_logs()
    if result['status'] == 'success' and result['count'] > 0:
        logs = result['data'][:5]  # Show last 5 logs
        
        table = Table(title=f"Recent Access Logs ({result['count']} total)", border_style="cyan")
        table.add_column("Device", style="cyan", no_wrap=True)
        table.add_column("Status", style="green", justify="center")
        table.add_column("Reason", style="yellow")
        table.add_column("Timestamp", style="magenta")
        
        for log in logs:
            table.add_row(
                log['device'][:12] + "...",
                "[green]✓[/green]" if log['success'] else "[red]✗[/red]",
                log['reason'],
                str(datetime.fromtimestamp(log['timestamp']))
            )
        
        console.print(table)
    else:
        rprint("[yellow]No logs found yet[/yellow]")
    rprint()
    
    # Sync to local cache
    print_section("Step 8: Sync to Local SQLite Cache")
    result = client.sync_cache()
    print_result(result, "Cache synced successfully")
    
    # Read from cache
    print_section("Step 9: Read from Local Cache")
    result = client.get_cached_logs(limit=5)
    if result['status'] == 'success' and len(result['data']) > 0:
        rprint(f"[green]✓[/green] Retrieved {len(result['data'])} logs from cache\n")
        
        # Show cache stats
        stats = client._cache_manager.get_stats()
        info_table = Table(show_header=False, box=None)
        info_table.add_column(style="cyan bold")
        info_table.add_column(style="white")
        info_table.add_row("Total Devices Cached", str(stats['total_devices']))
        info_table.add_row("Total Logs Cached", str(stats['total_logs']))
        console.print(info_table)
    else:
        rprint("[yellow]No cached logs available[/yellow]")
    
    # Success summary
    rprint()
    console.print(Panel.fit(
        "[bold green]✓ Demo completed successfully![/bold green]\n\n"
        "[dim]All features demonstrated:[/dim]\n"
        "  • Device registration\n"
        "  • Access control (grant/check)\n"
        "  • Access logging\n"
        "  • Blockchain querying\n"
        "  • Local cache synchronization",
        border_style="green"
    ))
    
    # Cleanup
    client.close()
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        rprint("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        rprint(f"\n[red]Unexpected error: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)
