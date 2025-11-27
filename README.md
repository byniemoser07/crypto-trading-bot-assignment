# Junior Python Developer - Crypto Trading Bot

This repository contains the completed submission for the Junior Python Developer application task: a simplified command-line interface (CLI) trading bot for the Bybit Perpetual Futures Testnet.

The bot is implemented in a single Python file (`basic_bot.py`) and is designed to handle API connection, user input, order placement, and comprehensive logging.

## Features Implemented

The bot successfully meets all core requirements and includes the following **bonus enhancements**:

| Feature | Requirement Status | Description |
| :--- | :--- | :--- |
| **MARKET & LIMIT Orders** | **Core** | Supports immediate and specific-price order placement (BUY/SELL). |
| **Comprehensive Logging** | **Core** | Logs all API requests, responses, and errors to the console and to the required file: `trading_bot_log.txt`. |
| **Input Validation** | **Core** | Validates user input for command types, side, and positive quantities/prices. |
| **STOP_LIMIT Order** | **Bonus** | Implements a third, advanced order type (Conditional Stop-Limit). |
| **BALANCE Command** | **Bonus** | CLI enhancement to instantly query and display the Testnet account's available USDT balance. |

## 🚀 Setup and Installation

### Prerequisites
* Python 3.x
* Virtual Environment (`venv`)
* Bybit Testnet API Key and Secret

### Steps to Run

1.  **Clone the Repository (or ensure files are present):**
    ```bash
    cd [Your Project Directory] # e.g., cd crypto-bot-project
    ```

2.  **Activate Virtual Environment:**
    ```bash
    source bot-env/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install pybit python-dotenv
    ```

4.  **Configure API Keys:**
    * Create a file named **`.env`** in the root directory.
    * Add your Bybit Testnet keys (these are NOT included in this repository):
        ```
        BYBIT_API_KEY="[Your Testnet Key]"
        BYBIT_API_SECRET="[Your Testnet Secret]"
        ```

5.  **Start the Bot:**
    ```bash
    python3 basic_bot.py
    ```

## ⌨️ CLI Command Guide

Once the bot is running, use the following commands at the prompt:

| Command | Usage | Description |
| :--- | :--- | :--- |
| `MARKET` | `MARKET -> BTCUSDT -> BUY/SELL -> Quantity` | Places an order instantly at the current market price. |
| `LIMIT` | `LIMIT -> BTCUSDT -> BUY/SELL -> Quantity -> Price` | Places an order at a specified limit price. |
| **`STOP_LIMIT` (Bonus)** | `STOP_LIMIT -> ... -> Quantity -> Limit Price -> Trigger Price` | Places a conditional order that activates when the market hits the Trigger Price. |
| **`BALANCE` (Bonus)** | `BALANCE` | Queries and displays the current USDT account equity and available balance. |
| `EXIT` | `EXIT` | Terminates the bot and finalizes the `trading_bot_log.txt` file. |

## 📜 Log File

The file **`trading_bot_log.txt`** contains a record of the entire execution sequence, demonstrating:
* Successful connection to the Bybit Testnet.
* Successful execution of `MARKET`, `LIMIT`, and `STOP_LIMIT` orders.
* Successful execution of the `BALANCE` command.
* Successful handling and logging of an invalid quantity input error.
