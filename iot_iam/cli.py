"""
Command-line interface for BlockIAM library
"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from . import IAMClient, __version__
from .logger import setup_logger
from .utils import format_timestamp, truncate_address


console = Console()


@click.group()
@click.version_option(version=__version__)
@click.option('--debug', is_flag=True, help='Enable debug logging')
@click.pass_context
def cli(ctx, debug):
    """BlockIAM - Blockchain-based IoT device identity and access management"""
    ctx.ensure_object(dict)
    
    if debug:
        import logging
        setup_logger(level=logging.DEBUG)
    
    try:
        ctx.obj['client'] = IAMClient()
    except Exception as e:
        rprint(f"[red]Error initializing client: {e}[/red]")
        ctx.exit(1)


@cli.command()
@click.argument('address')
@click.argument('name')
@click.argument('role')
@click.option('--metadata', default='', help='Additional metadata')
@click.pass_context
def register(ctx, address, name, role, metadata):
    """Register a new IoT device"""
    client = ctx.obj['client']
    
    with console.status(f"[cyan]Registering device {name}..."):
        result = client.register_device(address, name, role, metadata)
    
    if result['status'] == 'success':
        rprint(f"[green]✓[/green] Device registered successfully!")
        rprint(f"[dim]Transaction: {result['tx_hash']}[/dim]")
    else:
        rprint(f"[red]✗[/red] Failed: {result.get('message', 'Unknown error')}")


@cli.command()
@click.argument('address')
@click.option('--expiry', default=0, help='Access expiry timestamp')
@click.pass_context
def grant(ctx, address, expiry):
    """Grant access to a device"""
    client = ctx.obj['client']
    
    with console.status(f"[cyan]Granting access..."):
        result = client.grant_access(address, expiry)
    
    if result['status'] == 'success':
        rprint(f"[green]✓[/green] Access granted successfully!")
        rprint(f"[dim]Transaction: {result['tx_hash']}[/dim]")
    else:
        rprint(f"[red]✗[/red] Failed: {result.get('message', 'Unknown error')}")


@cli.command()
@click.argument('address')
@click.pass_context
def revoke(ctx, address):
    """Revoke access from a device"""
    client = ctx.obj['client']
    
    with console.status(f"[cyan]Revoking access..."):
        result = client.revoke_access(address)
    
    if result['status'] == 'success':
        rprint(f"[green]✓[/green] Access revoked successfully!")
        rprint(f"[dim]Transaction: {result['tx_hash']}[/dim]")
    else:
        rprint(f"[red]✗[/red] Failed: {result.get('message', 'Unknown error')}")


@cli.command()
@click.argument('address')
@click.pass_context
def check(ctx, address):
    """Check device access status"""
    client = ctx.obj['client']
    
    result = client.check_access(address)
    
    if result['status'] == 'success':
        has_access = result['has_access']
        status = "[green]GRANTED[/green]" if has_access else "[red]DENIED[/red]"
        rprint(f"Access status for {truncate_address(address)}: {status}")
    else:
        rprint(f"[red]✗[/red] Failed: {result.get('message', 'Unknown error')}")


@cli.command()
@click.argument('address')
@click.pass_context
def info(ctx, address):
    """Get device information"""
    client = ctx.obj['client']
    
    result = client.get_device_info(address)
    
    if result['status'] == 'success':
        data = result['data']
        
        table = Table(title="Device Information", show_header=False)
        table.add_column("Field", style="cyan bold")
        table.add_column("Value", style="white")
        
        table.add_row("Address", data['address'])
        table.add_row("Name", data['name'])
        table.add_row("Role", data['role'])
        table.add_row("Metadata", data['metadata'] or '(none)')
        table.add_row("Registered", format_timestamp(data['registered_at']))
        table.add_row("Status", "Active" if data['is_registered'] else "Inactive")
        
        console.print(table)
    else:
        rprint(f"[red]✗[/red] Failed: {result.get('message', 'Unknown error')}")


@cli.command()
@click.argument('reason')
@click.pass_context
def log(ctx, reason):
    """Log an access event"""
    client = ctx.obj['client']
    
    with console.status(f"[cyan]Logging access..."):
        result = client.log_access(reason)
    
    if result['status'] == 'success':
        rprint(f"[green]✓[/green] Access logged successfully!")
        rprint(f"[dim]Transaction: {result['tx_hash']}[/dim]")
    else:
        rprint(f"[red]✗[/red] Failed: {result.get('message', 'Unknown error')}")


@cli.command()
@click.option('--limit', default=10, help='Number of logs to display')
@click.option('--from-block', default=0, help='Starting block number')
@click.pass_context
def logs(ctx, limit, from_block):
    """Fetch access logs from blockchain"""
    client = ctx.obj['client']
    
    with console.status("[cyan]Fetching logs..."):
        result = client.get_logs(from_block=from_block)
    
    if result['status'] == 'success' and result['count'] > 0:
        logs = result['data'][:limit]
        
        table = Table(title=f"Access Logs (showing {len(logs)} of {result['count']})")
        table.add_column("Device", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Reason", style="yellow")
        table.add_column("Timestamp", style="magenta")
        table.add_column("TX Hash", style="dim")
        
        for log in logs:
            table.add_row(
                truncate_address(log['device']),
                "✓" if log['success'] else "✗",
                log['reason'][:30] + ("..." if len(log['reason']) > 30 else ""),
                format_timestamp(log['timestamp']),
                truncate_address(log['tx_hash'])
            )
        
        console.print(table)
    elif result['status'] == 'success':
        rprint("[yellow]No logs found[/yellow]")
    else:
        rprint(f"[red]✗[/red] Failed: {result.get('message', 'Unknown error')}")


@cli.command()
@click.pass_context
def sync(ctx):
    """Sync blockchain data to local cache"""
    client = ctx.obj['client']
    
    with console.status("[cyan]Syncing to cache..."):
        result = client.sync_cache()
    
    if result['status'] == 'success':
        rprint(f"[green]✓[/green] Cache synced successfully!")
    else:
        rprint(f"[red]✗[/red] Failed: {result.get('message', 'Unknown error')}")


@cli.command()
@click.option('--limit', default=10, help='Number of logs to display')
@click.pass_context
def cache(ctx, limit):
    """View cached logs"""
    client = ctx.obj['client']
    
    result = client.get_cached_logs(limit=limit)
    
    if result['status'] == 'success' and len(result['data']) > 0:
        logs = result['data']
        
        table = Table(title=f"Cached Logs (showing {len(logs)})")
        table.add_column("ID", style="cyan")
        table.add_column("Device", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Reason", style="yellow")
        table.add_column("Timestamp", style="magenta")
        
        for log in logs:
            table.add_row(
                str(log['id']),
                truncate_address(log['device']),
                "✓" if log['success'] else "✗",
                log['reason'][:30] + ("..." if len(log['reason']) > 30 else ""),
                format_timestamp(log['timestamp'])
            )
        
        console.print(table)
    elif result['status'] == 'success':
        rprint("[yellow]No cached logs found[/yellow]")
    else:
        rprint(f"[red]✗[/red] Failed: {result.get('message', 'Unknown error')}")


def main():
    """Main CLI entry point"""
    cli(obj={})


if __name__ == '__main__':
    main()
