# AP2Test - Comprehensive Documentation

**Version:** 0.1.2  
**Protocol:** Agent Payments Protocol (AP2)  
**Purpose:** Testing AI agent payment implementations with cryptographic mandates

---

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Data Storage](#data-storage)
4. [Commands Reference](#commands-reference)
5. [Data Structures](#data-structures)
6. [Payment Methods](#payment-methods)
7. [Workflow Examples](#workflow-examples)
8. [Output Formats](#output-formats)
9. [Troubleshooting](#troubleshooting)

---

## Overview

AP2Test is a command-line testing tool for the Agent Payments Protocol (AP2). It simulates the cryptographic mandate flow where:

1. **Users** authorize AI agents to make purchases
2. **Agents** create shopping carts within authorized limits
3. **Payments** execute with cryptographic audit trails

### Key Concepts

- **Intent Mandate**: User authorization for agent to shop (max amount, merchants, categories)
- **Cart Mandate**: Specific cart approval with exact items and prices
- **Payment**: Executed transaction with cryptographic proof chain
- **Autonomous**: Transactions where human is not present for final approval

---

## Installation

### Prerequisites

- Python 3.8+
- `uv` package manager (recommended) or `pip`

### Install AP2 Repository

```bash
# Install uv (choose one method):
sudo snap install astral-uv --classic
# OR
curl -LsSf https://astral.sh/uv/install.sh | sh
# OR
pip install uv

# Clone and install
git clone https://github.com/google-agentic-commerce/AP2.git
cd AP2/samples/python
uv sync

# Set up API key (optional for basic testing)
export GOOGLE_API_KEY="your-key-here"
```

### Verify Installation

```bash
ap2test --version
# Should output: AP2Test, version 0.1.2
```

---

## Data Storage

### Primary Data File

**Location:** `~/.ap2test_data.json`

This JSON file stores all test data:
- Intent Mandates
- Cart Mandates
- Payment Transactions
- User/Agent IDs
- Cryptographic Signatures

### File Structure

```json
{
  "user_id": "test_user",
  "agent_id": "test_agent",
  "intent_mandates": [
    {
      "user_id": "test_user",
      "agent_id": "test_agent",
      "max_amount": 100.0,
      "currency": "USD",
      "valid_until": "2025-10-02T05:05:11.562339",
      "merchant_whitelist": ["amazon", "bestbuy"],
      "categories": ["electronics"],
      "signature": "4e8bbf296aa9997f..."
    }
  ],
  "cart_mandates": [
    {
      "merchant_id": "amazon",
      "total_amount": 79.99,
      "currency": "USD",
      "items": [...],
      "signature": "a1b2c3d4e5f6..."
    }
  ],
  "payments": [
    {
      "transaction_id": "a0e4d0241ecdef07",
      "amount": 79.99,
      "currency": "USD",
      "timestamp": "2025-10-01T04:58:59.010166",
      "payment_method": "crypto",
      "autonomous": false
    }
  ]
}
```

### Viewing Raw Data

```bash
# Pretty print entire file
cat ~/.ap2test_data.json | python3 -m json.tool

# Or with jq (if installed)
cat ~/.ap2test_data.json | jq '.'

# View specific sections
cat ~/.ap2test_data.json | jq '.intent_mandates'
cat ~/.ap2test_data.json | jq '.cart_mandates'
cat ~/.ap2test_data.json | jq '.payments'
```

---

## Commands Reference

### 1. `ap2test run`

**Purpose:** Run complete test scenarios with multiple flows

**Usage:**
```bash
ap2test run
```

**What it does:**
- Creates Intent Mandates
- Tests authorized purchases
- Tests autonomous purchases
- Tests mandate violations
- Tests unauthorized merchants
- Displays comprehensive summary

**Output:** Complete test suite results

**Save to file:**
```bash
ap2test run > test_results.txt
ap2test run 2>&1 | tee test_session.log
```

---

### 2. `ap2test create-intent`

**Purpose:** Create an Intent Mandate to authorize agent shopping

**Syntax:**
```bash
ap2test create-intent --amount <float> [OPTIONS]
```

**Required Options:**
- `--amount FLOAT` - Maximum amount agent can spend

**Optional Options:**
- `--currency TEXT` - Currency code (default: USD)
- `--hours INTEGER` - Validity period in hours (default: 24)
- `--merchant TEXT` - Whitelisted merchant (can use multiple times)
- `--category TEXT` - Allowed category (can use multiple times)

**Examples:**

```bash
# Basic intent
ap2test create-intent --amount 100

# With specific merchants and categories
ap2test create-intent --amount 500 \
  --merchant amazon \
  --merchant bestbuy \
  --category electronics \
  --category books

# Short validity period
ap2test create-intent --amount 50 --hours 1

# Multiple currencies
ap2test create-intent --amount 100 --currency EUR
```

**Output Fields:**
- User ID
- Agent ID
- Max Amount
- Valid Until (timestamp)
- Merchants (whitelist)
- Categories (allowed)
- Signature (cryptographic proof)

**Save output:**
```bash
ap2test create-intent --amount 100 > intent_mandate.txt
```

---

### 3. `ap2test create-cart`

**Purpose:** Create a Cart Mandate with specific items

**Syntax:**
```bash
ap2test create-cart --items <format> --merchant <id>
```

**Required Options:**
- `--items TEXT` - Items in format: `name:price:qty,name:price:qty`
- `--merchant TEXT` - Merchant ID

**Item Format:**
```
ProductName:Price:Quantity,ProductName:Price:Quantity
```

**Examples:**

```bash
# Single item
ap2test create-cart \
  --items "Wireless Keyboard:79.99:1" \
  --merchant amazon

# Multiple items
ap2test create-cart \
  --items "Keyboard:79.99:1,Mouse:29.99:2,Cable:15.99:3" \
  --merchant amazon

# Will fail if exceeds intent mandate
ap2test create-cart \
  --items "Laptop:1299.99:1" \
  --merchant amazon
```

**Output on Success:**
- Merchant ID
- Total Amount
- Number of Items
- Item details (name, quantity, price, subtotal)
- Signature

**Output on Failure:**
- Rejection reason (exceeds max, unauthorized merchant, etc.)
- Current intent mandate limits

**Save output:**
```bash
ap2test create-cart --items "Item:50:1" --merchant amazon > cart_mandate.txt
```

---

### 4. `ap2test execute-payment`

**Purpose:** Execute a payment transaction

**Syntax:**
```bash
ap2test execute-payment [OPTIONS]
```

**Options:**
- `--method CHOICE` - Payment method (default: card)
  - Choices: `card`, `bank_transfer`, `stablecoin`, `crypto`
- `--human-present` - Human is present (default)
- `--no-human-present` - Autonomous transaction

**Examples:**

```bash
# Standard card payment
ap2test execute-payment --method card

# Crypto payment
ap2test execute-payment --method crypto

# Autonomous payment (no human)
ap2test execute-payment --method stablecoin --no-human-present

# Bank transfer with human present
ap2test execute-payment --method bank_transfer --human-present
```

**Output Fields:**
- Transaction ID
- Payment Method
- Amount
- Currency
- Agent Present (always True)
- Human Present (based on flag)
- Timestamp
- Autonomous warning (if applicable)

**Save output:**
```bash
ap2test execute-payment --method crypto > payment.txt
```

**Note:** Requires an existing Cart Mandate. Create one first with `create-cart` or run `ap2test run`.

---

### 5. `ap2test audit`

**Purpose:** View complete audit trail of all transactions

**Syntax:**
```bash
ap2test audit [OPTIONS]
```

**Options:**
- `--format CHOICE` - Output format (default: text)
  - Choices: `text`, `json`

**Examples:**

```bash
# Human-readable format
ap2test audit

# JSON format
ap2test audit --format json

# JSON with filtering (requires jq)
ap2test audit --format json | jq '.transactions[] | select(.payment_method=="crypto")'

# Save to file
ap2test audit > audit_log.txt
ap2test audit --format json > audit.json
```

**Text Output Includes:**
- User ID / Agent ID
- Summary statistics
  - Intent Mandates count
  - Cart Mandates count
  - Total payments
  - Total amount spent
  - Autonomous transaction count
- Transaction history (chronological)

**JSON Output Structure:**
```json
{
  "user_id": "test_user",
  "agent_id": "test_agent",
  "summary": {
    "intent_mandates": 2,
    "cart_mandates": 3,
    "payments": 5,
    "total_spent": 361.93,
    "autonomous_transactions": 1
  },
  "transactions": [...]
}
```

---

### 6. `ap2test status`

**Purpose:** Show current test data status summary

**Syntax:**
```bash
ap2test status
```

**No options available**

**Output:**
- Intent Mandates count
- Cart Mandates count
- Payments count
- Total Spent amount
- Helpful tip if no transactions yet

**Example:**
```bash
ap2test status > status.txt
```

---

### 7. `ap2test reset`

**Purpose:** Clear all test data

**Syntax:**
```bash
ap2test reset
```

**Behavior:**
- Prompts for confirmation (type 'y' or 'yes')
- Deletes `~/.ap2test_data.json`
- Cannot be undone

**Example:**
```bash
ap2test reset
# Prompt: Are you sure you want to clear all test data? [y/N]:
```

**Force reset (skip confirmation):**
```bash
# Backup first!
cp ~/.ap2test_data.json ~/.ap2test_data.backup.json
# Then force delete
rm ~/.ap2test_data.json
```

---

## Data Structures

### Intent Mandate

**Purpose:** User authorization for agent to make purchases

**Fields:**
- `user_id` - User identifier
- `agent_id` - AI agent identifier
- `max_amount` - Maximum spending limit
- `currency` - Currency code (USD, EUR, etc.)
- `valid_until` - Expiration timestamp
- `merchant_whitelist` - Allowed merchant IDs (array)
- `categories` - Allowed product categories (array)
- `signature` - Cryptographic signature (hex string)

**Example:**
```json
{
  "user_id": "test_user",
  "agent_id": "test_agent",
  "max_amount": 500.0,
  "currency": "USD",
  "valid_until": "2025-10-02T13:56:22.328143",
  "merchant_whitelist": ["amazon", "bestbuy"],
  "categories": ["electronics", "books"],
  "signature": "4e8bbf296aa9997f6c8d5e2a..."
}
```

---

### Cart Mandate

**Purpose:** Specific cart approval with items and total

**Fields:**
- `merchant_id` - Merchant identifier
- `total_amount` - Cart total (calculated)
- `currency` - Currency code
- `items` - Array of cart items
- `signature` - Cryptographic signature

**Cart Item Fields:**
- `name` - Product name
- `price` - Unit price
- `quantity` - Number of items
- `merchant_id` - Merchant selling item

**Example:**
```json
{
  "merchant_id": "amazon",
  "total_amount": 111.97,
  "currency": "USD",
  "items": [
    {
      "name": "Wireless Keyboard",
      "price": 79.99,
      "quantity": 1,
      "merchant_id": "amazon"
    },
    {
      "name": "USB-C Cable",
      "price": 15.99,
      "quantity": 2,
      "merchant_id": "amazon"
    }
  ],
  "signature": "a1b2c3d4e5f67890abcdef..."
}
```

---

### Payment Transaction

**Purpose:** Executed payment with audit trail

**Fields:**
- `transaction_id` - Unique transaction identifier (hex)
- `amount` - Payment amount
- `currency` - Currency code
- `timestamp` - ISO 8601 timestamp
- `payment_method` - Method used (card, crypto, etc.)
- `autonomous` - Boolean (true if no human present)

**Note:** Payments do NOT have signatures. They inherit authorization from the Cart Mandate signature.

**Example:**
```json
{
  "transaction_id": "a0e4d0241ecdef07",
  "amount": 79.99,
  "currency": "USD",
  "timestamp": "2025-10-01T04:58:59.010166",
  "payment_method": "crypto",
  "autonomous": false
}
```

---

## Payment Methods

### Available Methods

1. **card** - Credit/debit card payments
2. **bank_transfer** - Direct bank transfers
3. **stablecoin** - Cryptocurrency stablecoins (e.g., USDC, USDT)
4. **crypto** - General cryptocurrencies (BTC, ETH, etc.)

### Important Notes

- **No cryptocurrency-specific details** are tracked:
  - No wallet addresses
  - No blockchain network (Bitcoin, Ethereum, Solana)
  - No actual crypto amounts (always USD)
  - No transaction hashes
  - No gas fees

- **Crypto is generic:** The tool treats `crypto` and `stablecoin` as payment method labels only, not real blockchain transactions

- **Fixed amount:** All payments default to $79.99 (no custom amount option in execute-payment)

### Testing Different Methods

```bash
# Test all four methods
ap2test execute-payment --method card
ap2test execute-payment --method bank_transfer
ap2test execute-payment --method stablecoin
ap2test execute-payment --method crypto

# Compare in audit
ap2test audit --format json | jq '.transactions[] | {method: .payment_method, amount, autonomous}'
```

---

## Workflow Examples

### Example 1: Basic Human-Present Purchase

```bash
# Step 1: Create intent (authorize agent)
ap2test create-intent --amount 200 --merchant amazon

# Step 2: Create cart
ap2test create-cart --items "Keyboard:79.99:1,Mouse:29.99:1" --merchant amazon

# Step 3: Execute payment
ap2test execute-payment --method card

# Step 4: View results
ap2test audit
```

---

### Example 2: Autonomous Agent Purchase

```bash
# Step 1: Create intent
ap2test create-intent --amount 50 --merchant netflix --category subscriptions

# Step 2: Create cart
ap2test create-cart --items "Premium Subscription:15.99:1" --merchant netflix

# Step 3: Execute autonomous payment
ap2test execute-payment --method bank_transfer --no-human-present

# Step 4: Check for autonomous flag
ap2test audit --format json | jq '.summary.autonomous_transactions'
```

---

### Example 3: Testing Crypto Payments

```bash
# Create authorization
ap2test create-intent --amount 500 --merchant coinbase

# Create cart
ap2test create-cart --items "Bitcoin Purchase:100:1" --merchant coinbase

# Execute with different crypto methods
ap2test execute-payment --method crypto
ap2test execute-payment --method stablecoin

# Filter crypto transactions
ap2test audit --format json | jq '.transactions[] | select(.payment_method=="crypto" or .payment_method=="stablecoin")'
```

---

### Example 4: Testing Mandate Violations

```bash
# Create limited intent
ap2test create-intent --amount 100 --merchant amazon

# Try to exceed limit (will fail)
ap2test create-cart --items "Expensive Item:500:1" --merchant amazon
# Output: ✗ Cart Mandate REJECTED - Exceeds maximum amount

# Try unauthorized merchant (will fail)
ap2test create-cart --items "Book:20:1" --merchant ebay
# Output: ✗ Cart Mandate REJECTED - Merchant not in whitelist
```

---

### Example 5: Complete Test Suite

```bash
# Run all scenarios
ap2test run > full_test.log

# Review results
cat full_test.log

# Extract JSON data
ap2test audit --format json > complete_audit.json

# Generate summary report
ap2test status
```

---

## Output Formats

### Saving to Files

```bash
# Individual commands
ap2test create-intent --amount 100 > intent.txt
ap2test audit > audit.txt
ap2test audit --format json > audit.json

# Append to log
ap2test execute-payment --method card >> transactions.log

# Capture everything (stdout + stderr)
ap2test run &> complete_output.txt

# See and save simultaneously
ap2test audit | tee audit_backup.txt
```

### JSON Query Examples

```bash
# Requires jq tool: sudo apt install jq

# Filter by payment method
ap2test audit --format json | jq '.transactions[] | select(.payment_method=="crypto")'

# Count transactions by method
ap2test audit --format json | jq '.transactions | group_by(.payment_method) | map({method: .[0].payment_method, count: length})'

# Show only autonomous transactions
ap2test audit --format json | jq '.transactions[] | select(.autonomous==true)'

# Calculate total by method
ap2test audit --format json | jq '.transactions | group_by(.payment_method) | map({method: .[0].payment_method, total: map(.amount) | add})'

# Extract signatures
cat ~/.ap2test_data.json | jq '.intent_mandates[] | {max_amount, signature}'
```

---

## Troubleshooting

### Common Issues

**1. "Command 'ap2test' not found"**
```bash
# Check installation
which ap2test

# Reinstall
cd ~/test/AP2/samples/python
uv sync

# Add to PATH if needed
export PATH="$HOME/.local/bin:$PATH"
```

**2. "Cart Mandate REJECTED"**
```bash
# Check current limits
ap2test status

# View active intent mandate
cat ~/.ap2test_data.json | jq '.intent_mandates[-1]'

# Create new intent with higher limit
ap2test create-intent --amount 1000
```

**3. "No such option: --currency" (in execute-payment)**
- The `execute-payment` command does NOT support `--currency` or `--amount`
- These are fixed at USD 79.99
- Only `--method` and `--human-present` are available

**4. "Invalid value for '--method'"**
- Only four methods: `card`, `bank_transfer`, `stablecoin`, `crypto`
- No `eth`, `btc`, or other specific crypto names

**5. Data file corruption**
```bash
# Backup first
cp ~/.ap2test_data.json ~/.ap2test_data.backup.json

# Reset and start fresh
ap2test reset
```

**6. No transactions showing**
```bash
# Check if data file exists
ls -la ~/.ap2test_data.json

# If empty, run test suite
ap2test run

# Verify
ap2test status
```

---

## Advanced Usage

### Session Logging

Record entire testing session:
```bash
# Start recording
script -a ap2_session_$(date +%Y%m%d_%H%M%S).log

# Run your tests
ap2test run
ap2test audit

# Stop recording
exit
```

### Batch Testing

Create a test script:
```bash
#!/bin/bash
# test_ap2.sh

echo "=== AP2 Testing Suite ==="
date

# Test 1: Card payments
ap2test create-intent --amount 500 --merchant amazon
ap2test create-cart --items "Item1:50:1" --merchant amazon
ap2test execute-payment --method card

# Test 2: Crypto payments
ap2test create-cart --items "Item2:75:1" --merchant amazon
ap2test execute-payment --method crypto

# Results
ap2test audit --format json > results_$(date +%Y%m%d).json
ap2test status

echo "=== Tests Complete ==="
```

Run it:
```bash
chmod +x test_ap2.sh
./test_ap2.sh
```

---

## Quick Reference Card

```
COMMANDS:
  run              - Run complete test scenarios
  create-intent    - Create Intent Mandate (--amount required)
  create-cart      - Create Cart Mandate (--items, --merchant required)
  execute-payment  - Execute payment (--method optional)
  audit            - View audit trail (--format text|json)
  status           - Show summary
  reset            - Clear all data

DATA LOCATION:
  ~/.ap2test_data.json

PAYMENT METHODS:
  card, bank_transfer, stablecoin, crypto

OUTPUT:
  > file           - Save to file
  >> file          - Append to file
  | tee file       - Show and save
  --format json    - JSON output (audit only)
```

---

## Additional Resources

- **AP2 Protocol Docs:** https://ap2-protocol.org/
- **GitHub Repository:** https://github.com/google-agentic-commerce/AP2
- **Google Cloud Blog:** https://cloud.google.com/blog/products/ai-machine-learning/announcing-agents-to-payments-ap2-protocol

---

**Document Version:** 1.0  
**Last Updated:** October 2025
