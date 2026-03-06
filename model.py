import requests
from typing import Optional, List, Dict, Any
import json
from pathlib import Path

class CoinGeckoAPI:
   
    base_url = "https://api.coingecko.com/api/v3"
    
    def fetch_batch_prices(self, coin_ids: List[str]) -> Dict[str, Any]:
        if not coin_ids or isinstance(coin_ids, str):
            raise ValueError("coin_ids must be a non-empty list of strings")
        
        ids_param = ",".join(coin_ids)
        url = f"{CoinGeckoAPI.base_url}/simple/price?ids={ids_param}&vs_currencies=usd&include_24hr_change=true"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise ConnectionError(f"Error fetching prices: {e}") from e
     
    def coin_id_exists(self, coin_ids: str) -> bool:
        if not coin_ids:
            return False
        
        url = f"{CoinGeckoAPI.base_url}/coins/list"
        try:
            coins_response = requests.get(url, timeout = 8)
            coins_response.raise_for_status()
            coins = coins_response.json()
            return any(c.get("id") == coin_ids.lower() for c in coins)
        except Exception:
            return False

class Portfolio:
    def __init__(self):
        # key = coin_id (coingecko style: "bitcoin", "ethereum", ...)
        self.holdings: Dict[str, Dict[str, Any]] = {}

    def add_holding(self, coin_id: str, name: str = "Unknown", symbol: str = "", amount: float = 1.0, change_24h: Optional[float] = None):
        """ purchase_price is optional – mostly for future PnL calculation """
        self.holdings[coin_id] = {
            "name": name,
            "symbol": symbol.upper() or coin_id.upper(),  # fallback to coin_id if symbol is missing
            "amount": float(amount),
            "change_24h": change_24h,
            "current_price": 0.0,       # will be updated from API
            "value_usd": 0.0,          # will be updated from API
        }

    def remove_holding(self, coin_id: str) -> bool:
        if coin_id in self.holdings:
            del self.holdings[coin_id]
            return True
        return False

    def update_prices(self, api_data: Dict[str, Any]):
        """ Expects list of dicts from CoinGecko /coins/markets or /simple/price """
        for coin_id, price_info in api_data.items():
            if coin_id in self.holdings:
                price = price_info.get("usd", 0.0)      # /simple/price
                self.holdings[coin_id]["current_price"] = float(price)
                self.holdings[coin_id]["value_usd"] = self.holdings[coin_id]["amount"] * price 
                if "usd_24h_change" in price_info:
                    self.holdings[coin_id]["change_24h"] = round(float(price_info["usd_24h_change"]), 2)

    def get_table_rows(self) -> List[Dict[str, Any]]:
        """ Returns data ready for table – you can easily add more columns later """
        return [
            {
                "symbol": h["symbol"],
                "amount": h["amount"],
                "value_usd": h["value_usd"],
                "change_24h": h["change_24h"], 
            }
            for h in self.holdings.values()
        ]
    
    def get_total_value_usd(self) -> float:
        return sum(h["value_usd"] for h in self.holdings.values())

    def save_to_file(self, file_path: str) -> None:
        path = Path(file_path)
        normalized: Dict[str, Dict[str, Any]] = {}
        for coin_id, holding in self.holdings.items():
            change_24h = holding.get("change_24h")
            normalized[coin_id] = {
                "name": holding.get("name", "Unknown"),
                "symbol": str(holding.get("symbol", coin_id)).upper(),
                "amount": round(float(holding.get("amount", 1.0)), 6),
                "change_24h": None if change_24h is None else round(float(change_24h), 2),
                "current_price": round(float(holding.get("current_price", 0.0)), 2),
                "value_usd": round(float(holding.get("value_usd", 0.0)), 2),
            }

        payload = {"holdings": normalized}
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def load_from_file(self, file_path: str) -> bool:
        path = Path(file_path)
        if not path.exists():
            return False

        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            loaded_holdings = payload.get("holdings", {})
            if not isinstance(loaded_holdings, dict):
                return False

            normalized: Dict[str, Dict[str, Any]] = {}
            for coin_id, holding in loaded_holdings.items():
                if not isinstance(holding, dict):
                    continue
                normalized[coin_id] = {
                    "name": holding.get("name", "Unknown"),
                    "symbol": str(holding.get("symbol", coin_id)).upper(),
                    "amount": float(holding.get("amount", 1.0)),
                    "change_24h": None if holding.get("change_24h") is None else round(float(holding.get("change_24h")), 2),
                    "current_price": float(holding.get("current_price", 0.0)),
                    "value_usd": float(holding.get("value_usd", 0.0)),
                }

            self.holdings = normalized
            return True
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            return False
    
    
    