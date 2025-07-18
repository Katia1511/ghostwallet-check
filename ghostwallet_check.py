import requests
import argparse
import datetime

ETHPLORER_API_KEY = "freekey"  # У Ethplorer есть публичный free API

def get_wallet_data(address):
    url = f"https://api.ethplorer.io/getAddressInfo/{address}?apiKey={ETHPLORER_API_KEY}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def is_token_inactive(token_data, months_threshold=6):
    last_tx = token_data.get("lastTxTimestamp")
    if not last_tx:
        return True  # Если нет транзакций вообще
    last_tx_date = datetime.datetime.utcfromtimestamp(last_tx)
    return (datetime.datetime.utcnow() - last_tx_date).days > (months_threshold * 30)

def analyze_wallet(address):
    print(f"[+] Анализ кошелька: {address}")
    data = get_wallet_data(address)
    dead_tokens = []

    tokens = data.get("tokens", [])
    if not tokens:
        print("[-] Токены не найдены.")
        return

    for token in tokens:
        token_info = token.get("tokenInfo", {})
        name = token_info.get("name", "Unknown")
        symbol = token_info.get("symbol", "???")
        decimals = int(token_info.get("decimals", 0)) if token_info.get("decimals") else 0
        raw_balance = float(token.get("rawBalance", 0)) / (10 ** decimals) if decimals else 0

        if is_token_inactive(token):
            dead_tokens.append((name, symbol, raw_balance))

    if dead_tokens:
        print("\n[!] Найдены мертвые/неактивные токены:")
        for name, symbol, balance in dead_tokens:
            print(f"   • {name} ({symbol}): {balance}")
    else:
        print("[✓] Все токены активны или использовались недавно.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ghost Wallet Checker — найди мертвые токены в своём кошельке.")
    parser.add_argument("address", help="Ethereum-адрес кошелька (например, 0x...)")
    args = parser.parse_args()
    analyze_wallet(args.address)
