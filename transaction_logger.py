import pandas as pd
import requests

# Save insider trades into CSV for manual tracking
def save_to_csv(wallet_address):
    url = f"https://api.solscan.io/account/transactions?address={wallet_address}"
    response = requests.get(url).json()

    transactions = []
    for tx in response["data"]:
        transactions.append({
            "Wallet": wallet_address,
            "Amount (SOL)": tx["lamports"],
            "To": tx["receiver"],
            "Timestamp": tx["blockTime"]
        })

    df = pd.DataFrame(transactions)
    df.to_csv("insider_wallets.csv", mode="a", index=False, header=False)
    print(f"✅ Saved transactions for {wallet_address}")
