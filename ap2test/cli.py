"""
CLI interface for AP2Test

Provides command-line interface for testing AP2 payment flows.
"""

import click
import json
from typing import List

from .harness import AP2TestHarness
from .mandates import CartItem, PaymentMethod


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """
    AP2Test - Agent Payments Protocol Testing CLI
    
    Test your AI agent payment implementations with cryptographic mandates.
    """
    pass


@cli.command()
def run():
    """Run complete test scenarios with multiple flows"""
    click.echo("\n" + "=" * 60)
    click.echo("AP2 PAYMENT PROTOCOL - TEST SUITE")
    click.echo("=" * 60)
    
    harness = AP2TestHarness()
    
    # Scenario 1: Standard Purchase
    click.echo("\n--- SCENARIO 1: Standard Human-Present Purchase ---\n")
    
    intent = harness.create_intent_mandate(
        max_amount=500.00,
        currency="USD",
        merchant_whitelist=["amazon", "bestbuy"],
        categories=["electronics", "books"]
    )
    click.echo(f"✓ Intent Mandate Created")
    click.echo(f"  Max Amount: ${intent.max_amount}")
    click.echo(f"  Merchants: {', '.join(intent.merchant_whitelist)}")
    click.echo(f"  Signature: {intent.signature[:16]}...")
    
    cart_items = [
        CartItem("Wireless Keyboard", 79.99, 1, "amazon"),
        CartItem("USB-C Cable", 15.99, 2, "amazon")
    ]
    
    cart = harness.create_cart_mandate(
        items=cart_items,
        merchant_id="amazon"
    )
    
    if cart:
        click.echo(f"\n✓ Cart Mandate Created")
        click.echo(f"  Total: ${cart.total_amount:.2f}")
        click.echo(f"  Items: {len(cart_items)}")
        click.echo(f"  Signature: {cart.signature[:16]}...")
        
        payment = harness.execute_payment(payment_method=PaymentMethod.CARD)
        click.echo(f"\n✓ Payment Executed")
        click.echo(f"  Transaction ID: {payment.transaction_id}")
        click.echo(f"  Method: {payment.payment_method.value}")
        click.echo(f"  Amount: ${payment.amount:.2f}")
    
    # Scenario 2: Autonomous Agent Purchase
    click.echo("\n--- SCENARIO 2: Autonomous Agent Purchase ---\n")
    
    sub_items = [CartItem("Cloud Storage Subscription", 9.99, 1, "amazon")]
    sub_cart = harness.create_cart_mandate(items=sub_items, merchant_id="amazon")
    
    if sub_cart:
        click.echo(f"✓ Cart Mandate: ${sub_cart.total_amount:.2f}")
        payment = harness.execute_payment(
            cart_mandate=sub_cart,
            payment_method=PaymentMethod.BANK_TRANSFER,
            human_present=False
        )
        click.echo(f"✓ Autonomous Payment Executed")
        click.echo(f"  Transaction ID: {payment.transaction_id}")
        click.echo(f"  Human Present: {payment.human_present}")
    
    # Scenario 3: Intent Violation
    click.echo("\n--- SCENARIO 3: Intent Violation Test ---\n")
    
    expensive = [CartItem("4K Monitor", 599.99, 1, "amazon")]
    failed = harness.create_cart_mandate(items=expensive, merchant_id="amazon")
    
    if failed is None:
        click.echo("✗ Cart Mandate REJECTED")
        click.echo("  Reason: Exceeds maximum amount ($500.00)")
    
    # Scenario 4: Unauthorized Merchant
    click.echo("\n--- SCENARIO 4: Unauthorized Merchant Test ---\n")
    
    unauthorized = [CartItem("Book", 19.99, 1, "unauthorized_store")]
    failed2 = harness.create_cart_mandate(items=unauthorized, merchant_id="unauthorized_store")
    
    if failed2 is None:
        click.echo("✗ Cart Mandate REJECTED")
        click.echo("  Reason: Merchant not in whitelist")
    
    # Summary
    click.echo("\n" + "=" * 60)
    click.echo("TEST SUMMARY")
    click.echo("=" * 60)
    
    audit = harness.audit_trail()
    click.echo(f"✓ Intent Mandates: {audit['summary']['intent_mandates']}")
    click.echo(f"✓ Cart Mandates: {audit['summary']['cart_mandates']}")
    click.echo(f"✓ Successful Payments: {audit['summary']['payments']}")
    click.echo(f"✓ Total Spent: ${audit['summary']['total_spent']:.2f}")
    click.echo(f"✓ Autonomous Transactions: {audit['summary']['autonomous_transactions']}")


@cli.command()
@click.option('--amount', required=True, type=float, help='Maximum amount the agent can spend')
@click.option('--currency', default='USD', help='Currency code (e.g., USD, EUR)')
@click.option('--hours', default=24, type=int, help='Validity period in hours')
@click.option('--merchant', multiple=True, help='Whitelisted merchant ID (can be used multiple times)')
@click.option('--category', multiple=True, help='Allowed product category (can be used multiple times)')
def create_intent(amount, currency, hours, merchant, category):
    """Create an Intent Mandate to authorize agent shopping"""
    harness = AP2TestHarness()
    
    mandate = harness.create_intent_mandate(
        max_amount=amount,
        currency=currency,
        valid_hours=hours,
        merchant_whitelist=list(merchant) if merchant else None,
        categories=list(category) if category else None
    )
    
    click.echo("✓ Intent Mandate Created Successfully")
    click.echo(f"\n  User ID: {mandate.user_id}")
    click.echo(f"  Agent ID: {mandate.agent_id}")
    click.echo(f"  Max Amount: {currency} {amount}")
    click.echo(f"  Valid Until: {mandate.valid_until}")
    click.echo(f"  Merchants: {', '.join(mandate.merchant_whitelist)}")
    click.echo(f"  Categories: {', '.join(mandate.categories)}")
    click.echo(f"  Signature: {mandate.signature[:16]}...")


@cli.command()
@click.option('--items', required=True, help='Items as name:price:qty,name:price:qty')
@click.option('--merchant', required=True, help='Merchant ID')
def create_cart(items, merchant):
    """Create a Cart Mandate with specific items to purchase"""
    harness = AP2TestHarness()
    
    # Parse items
    cart_items = []
    try:
        for item_str in items.split(','):
            parts = item_str.split(':')
            if len(parts) != 3:
                raise ValueError(f"Invalid item format: {item_str}")
            name, price, qty = parts
            cart_items.append(CartItem(name.strip(), float(price), int(qty), merchant))
    except Exception as e:
        click.echo(f"✗ Error parsing items: {e}", err=True)
        click.echo("\nFormat: name:price:quantity,name:price:quantity")
        click.echo("Example: Keyboard:79.99:1,Mouse:29.99:1")
        return
    
    # Create cart mandate
    cart = harness.create_cart_mandate(items=cart_items, merchant_id=merchant)
    
    if cart:
        click.echo("✓ Cart Mandate Created Successfully")
        click.echo(f"\n  Merchant: {cart.merchant_id}")
        click.echo(f"  Total Amount: {cart.currency} {cart.total_amount:.2f}")
        click.echo(f"  Number of Items: {len(cart_items)}")
        click.echo(f"  Items:")
        for item in cart_items:
            click.echo(f"    - {item.name}: {item.quantity} x ${item.price:.2f} = ${item.total_price():.2f}")
        click.echo(f"  Signature: {cart.signature[:16]}...")
    else:
        click.echo("✗ Cart Mandate REJECTED", err=True)
        click.echo("\nPossible reasons:")
        click.echo("  - Total exceeds maximum amount in Intent Mandate")
        click.echo("  - Merchant not in whitelist")
        click.echo("  - Currency mismatch")
        intent = harness.get_latest_intent_mandate()
        if intent:
            click.echo(f"\nCurrent Intent Mandate limits:")
            click.echo(f"  Max Amount: {intent.currency} {intent.max_amount}")
            click.echo(f"  Allowed Merchants: {', '.join(intent.merchant_whitelist)}")


@cli.command()
@click.option(
    '--method',
    type=click.Choice(['card', 'bank_transfer', 'stablecoin', 'crypto']),
    default='card',
    help='Payment method to use'
)
@click.option(
    '--human-present/--no-human-present',
    default=True,
    help='Whether a human is present for this transaction'
)
def execute_payment(method, human_present):
    """Execute a payment transaction"""
    harness = AP2TestHarness()
    
    try:
        payment_method = PaymentMethod(method)
        payment = harness.execute_payment(
            payment_method=payment_method,
            human_present=human_present
        )
        
        click.echo("✓ Payment Executed Successfully")
        click.echo(f"\n  Transaction ID: {payment.transaction_id}")
        click.echo(f"  Payment Method: {payment.payment_method.value}")
        click.echo(f"  Amount: {payment.currency} {payment.amount:.2f}")
        click.echo(f"  Agent Present: {payment.agent_present}")
        click.echo(f"  Human Present: {payment.human_present}")
        click.echo(f"  Timestamp: {payment.timestamp}")
        
        if payment.is_autonomous():
            click.echo(f"\n  ⚠️  This was an AUTONOMOUS transaction (no human present)")
    
    except ValueError as e:
        click.echo(f"✗ Error: {e}", err=True)
        click.echo("\nCreate a cart mandate first with: ap2test create-cart")


@cli.command()
@click.option('--format', type=click.Choice(['json', 'text']), default='text', help='Output format')
def audit(format):
    """View complete audit trail of all transactions"""
    harness = AP2TestHarness()
    audit_data = harness.audit_trail()
    
    if format == 'json':
        click.echo(json.dumps(audit_data, indent=2))
    else:
        click.echo("\n" + "=" * 60)
        click.echo("AUDIT TRAIL")
        click.echo("=" * 60)
        
        click.echo(f"\nUser ID: {audit_data['user_id']}")
        click.echo(f"Agent ID: {audit_data['agent_id']}")
        
        click.echo("\n--- Summary ---")
        summary = audit_data['summary']
        click.echo(f"Intent Mandates: {summary['intent_mandates']}")
        click.echo(f"Cart Mandates: {summary['cart_mandates']}")
        click.echo(f"Payments: {summary['payments']}")
        click.echo(f"Total Spent: ${summary['total_spent']:.2f}")
        click.echo(f"Autonomous Transactions: {summary['autonomous_transactions']}")
        
        if audit_data['transactions']:
            click.echo("\n--- Transaction History ---")
            for i, tx in enumerate(audit_data['transactions'], 1):
                click.echo(f"\n{i}. Transaction {tx['transaction_id']}")
                click.echo(f"   Amount: {tx['currency']} {tx['amount']:.2f}")
                click.echo(f"   Method: {tx['payment_method']}")
                click.echo(f"   Autonomous: {tx['autonomous']}")
                click.echo(f"   Timestamp: {tx['timestamp']}")
        else:
            click.echo("\nNo transactions recorded yet.")


@cli.command()
@click.confirmation_option(prompt='Are you sure you want to clear all test data?')
def reset():
    """Clear all test data (requires confirmation)"""
    harness = AP2TestHarness()
    harness.reset()
    click.echo("✓ All test data has been cleared")
    click.echo(f"  Removed: ~/.ap2test_data.json")


@cli.command()
def status():
    """Show current test data status"""
    harness = AP2TestHarness()
    stats = harness.get_statistics()
    
    click.echo("\n" + "=" * 60)
    click.echo("AP2TEST STATUS")
    click.echo("=" * 60)
    
    click.echo(f"\nIntent Mandates: {stats['intent_mandates']}")
    click.echo(f"Cart Mandates: {stats['cart_mandates']}")
    click.echo(f"Payments: {stats['payments']}")
    click.echo(f"Total Spent: ${stats['total_spent']:.2f}")
    
    if stats['payments'] == 0:
        click.echo("\n💡 No transactions yet. Try: ap2test run")


if __name__ == '__main__':
    cli()
