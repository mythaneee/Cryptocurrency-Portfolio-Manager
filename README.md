# Cryptocurrency Portfolio Manager

Simple, offline-first desktop application to track your cryptocurrency holdings using CoinGecko API.

![screenshot](docs/screenshot.png)  <!-- add one later -->

## Features

- Add / remove coins by CoinGecko ID
- Live price updates every 5 minutes
- Portfolio total value + 24h change
- Mini bar chart visualization
- Persistent JSON storage

## Installation

```bash
# Recommended: use uv / pipx / pip
git clone https://github.com/mythaneee/crypto-portfolio-manager.git
cd crypto-portfolio-manager

# Install dependencies
pip install -r requirements.txt

# Run
python -m cryptofolio
# or after pip install -e .

cryptofolio
