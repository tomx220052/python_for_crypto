"""
常數定義模組
包含幣種列表、日期限制等常數
"""

# 幣種列表（按 symbol 字母順序排列）
COIN_LIST = [
    {"symbol": "AAVE", "id": "aave", "name": "Aave"},
    {"symbol": "ADA", "id": "cardano", "name": "Cardano"},
    {"symbol": "ALGO", "id": "algorand", "name": "Algorand"},
    {"symbol": "ALICE", "id": "my-neighbor-alice", "name": "My Neighbor Alice"},
    {"symbol": "APE", "id": "apecoin", "name": "ApeCoin"},
    {"symbol": "ARB", "id": "arbitrum", "name": "Arbitrum"},
    {"symbol": "AVAX", "id": "avalanche-2", "name": "Avalanche"},
    {"symbol": "AXS", "id": "axie-infinity", "name": "Axie Infinity"},
    {"symbol": "BCH", "id": "bitcoin-cash", "name": "Bitcoin Cash"},
    {"symbol": "BCNT", "id": "bincentive", "name": "Bincentive"},
    {"symbol": "BNB", "id": "binancecoin", "name": "BNB"},
    {"symbol": "BTC", "id": "bitcoin", "name": "Bitcoin"},
    {"symbol": "CHZ", "id": "chiliz", "name": "Chiliz"},
    {"symbol": "COMP", "id": "compound-governance-token", "name": "Compound"},
    {"symbol": "DAI", "id": "dai", "name": "Dai"},
    {"symbol": "DOGE", "id": "dogecoin", "name": "Dogecoin"},
    {"symbol": "DOT", "id": "polkadot", "name": "Polkadot"},
    {"symbol": "ENS", "id": "ethereum-name-service", "name": "Ethereum Name Service"},
    {"symbol": "ETC", "id": "ethereum-classic", "name": "Ethereum Classic"},
    {"symbol": "ETH", "id": "ethereum", "name": "Ethereum"},
    {"symbol": "FIL", "id": "filecoin", "name": "Filecoin"},
    {"symbol": "GALA", "id": "gala", "name": "Gala"},
    {"symbol": "GMT", "id": "stepn", "name": "GMT"},
    {"symbol": "GRT", "id": "the-graph", "name": "The Graph"},
    {"symbol": "GST", "id": "green-satoshi-token", "name": "Green Satoshi Token"},
    {"symbol": "LDO", "id": "lido-dao", "name": "Lido DAO"},
    {"symbol": "LINK", "id": "chainlink", "name": "Chainlink"},
    {"symbol": "LOOKS", "id": "looksrare", "name": "LooksRare"},
    {"symbol": "LOOT", "id": "loot", "name": "Lootex"},
    {"symbol": "LTC", "id": "litecoin", "name": "Litecoin"},
    {"symbol": "MANA", "id": "decentraland", "name": "Decentraland"},
    {"symbol": "MASK", "id": "mask-network", "name": "Mask Network"},
    {"symbol": "MITH", "id": "mithril", "name": "Mithril"},
    {"symbol": "PAXG", "id": "pax-gold", "name": "PAX Gold"},
    {"symbol": "POL", "id": "polygon-ecosystem-token", "name": "Polymath"},
    {"symbol": "RLY", "id": "rally-2", "name": "Rally"},
    {"symbol": "SAND", "id": "the-sandbox", "name": "The Sandbox"},
    {"symbol": "SHIB", "id": "shiba-inu", "name": "Shiba Inu"},
    {"symbol": "SLP", "id": "smooth-love-potion", "name": "Smooth Love Potion"},
    {"symbol": "SOL", "id": "solana", "name": "Solana"},
    {"symbol": "TRX", "id": "tron", "name": "TRON"},
    {"symbol": "UNI", "id": "uniswap", "name": "Uniswap"},
    {"symbol": "USDC", "id": "usd-coin", "name": "USD Coin"},
    {"symbol": "USDT", "id": "tether", "name": "Tether"},
    {"symbol": "XLM", "id": "stellar", "name": "Stellar"},
    {"symbol": "XRP", "id": "ripple", "name": "XRP"},
    {"symbol": "XTZ", "id": "tezos", "name": "Tezos"},
    {"symbol": "YFI", "id": "yearn-finance", "name": "Yearn Finance"},
]

# 建立顯示文字到 ID 的映射（用於快速查詢）
COIN_MAPPING = {
    f"{coin['symbol']} - {coin['name']}": coin['id']
    for coin in COIN_LIST
}

# 日期限制常數
DATE_MAX_DAYS = 365
