import requests

# Find insider wallets from early meme coin buys
def find_insider_wallets():
    url = "https://api.dexscreener.com/latest/dex/pairs/solana"
    response = requests.get(url).json()

    top_wallets = []

    for pair in response["pairs"]:
        if pair["volume"]["h24"] > 100000:  # Look for high-volume meme coins
            token_address = pair["baseToken"]["address"]
            buyers_url = f"https://api.solscan.io/token/holders?token={token_address}"
            buyers_response = requests.get(buyers_url).json()

            for holder in buyers_response.get("data", {}).get("result", [])[:5]:  # Avoid KeyError
                top_wallets.append(holder.get("owner", "Unknown"))

    return top_wallets  # 🔥 Move return inside the function
