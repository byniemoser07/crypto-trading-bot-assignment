import sys
import logging
import os
from pybit.unified_trading import HTTP
from pybit.exceptions import InvalidRequestError, FailedRequestError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- 1. CONFIGURE LOGGING (Logs to file and console) ---
LOG_FILE = 'trading_bot_log.txt'

# Create a logger instance
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Check if handlers already exist to prevent duplicate logs
if not logger.handlers:
    # File Handler (for log file submission)
    file_handler = logging.FileHandler(LOG_FILE)
    file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
    file_handler.setFormatter(file_format)

    # Console Handler (for real-time feedback)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(file_format)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)


class BasicBot:
    """A simplified trading bot for Bybit Futures Testnet."""
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        """Initializes the Bybit trading client."""
        
        self.category = 'linear' # USDT Perpetual Futures (USDT-M)
        logger.info("Initializing BasicBot...")

        try:
            self.client = HTTP(
                testnet=testnet,
                api_key=api_key,
                api_secret=api_secret
            )
            
            # Test the connection 
            server_time_s = self.client.get_server_time().get('result', {}).get('timeSecond')
            logger.info(f"✅ Connection successful. Testnet: {testnet}. Server time: {server_time_s}")

        except Exception as e:
            logger.error(f"❌ Failed to initialize Bybit client. Check API keys and network connection: {e}")
            sys.exit(1)

    # --- BONUS TASK METHOD: Check Account Balance ---
    def get_balance(self):
        """Fetches and displays the USDT balance."""
        logger.info("-> Fetching wallet balance...")
        try:
            # We fetch Unified Margin Account (UMA) balance
            response = self.client.get_wallet_balance(accountType="UNIFIED")
            
            # Find the USDT coin information
            usdt_balance = "N/A"
            total_equity = "N/A"
            
            result = response.get('result', {})
            if result and result.get('list'):
                account_info = result['list'][0]
                total_equity = account_info.get('totalEquity', 'N/A')
                
                if account_info.get('coin'):
                    for coin_data in account_info['coin']:
                        if coin_data.get('coin') == 'USDT':
                            usdt_balance = coin_data.get('availableToWithdraw', 'N/A')
                            break

            logger.info(f"💰 Account Balance (Unified Margin):")
            logger.info(f"  - Total Equity (USDT): {total_equity}")
            logger.info(f"  - Available Balance (USDT): {usdt_balance}")
            logger.info(f"  - Full Response: {response}")

        except Exception as e:
            logger.error(f"❌ Failed to fetch balance: {e}")


    def _place_order(self, symbol: str, side: str, order_type: str, qty: float, price: float = None, trigger_price: float = None):
        """
        Internal method to place a generic order (Market/Limit/Stop-Limit).
        Handles API call, logging, and error handling.
        """
        
        valid_order_types = ('MARKET', 'LIMIT', 'STOP_LIMIT')
        if side.upper() not in ('BUY', 'SELL') or order_type.upper() not in valid_order_types:
            logger.error(f"Invalid parameters: Side='{side}', Type='{order_type}'.")
            return None

        # Price validation for LIMIT and STOP_LIMIT
        if order_type.upper() in ('LIMIT', 'STOP_LIMIT') and (price is None or price <= 0):
            logger.error(f"{order_type} order requires a valid positive price.")
            return None
        
        # Trigger price validation for STOP_LIMIT
        if order_type.upper() == 'STOP_LIMIT' and (trigger_price is None or trigger_price <= 0):
            logger.error("STOP_LIMIT order requires a valid positive trigger price.")
            return None


        params = {
            'category': self.category,
            'symbol': symbol.upper(),
            'side': side.capitalize(), 
            # Note: Bybit uses 'Limit' for the orderType when placing a Stop-Limit conditional order
            'orderType': order_type.capitalize() if order_type.upper() != 'STOP_LIMIT' else 'Limit', 
            'qty': str(qty),
            'timeInForce': 'GTC'
        }

        # Add price for LIMIT and STOP_LIMIT
        if order_type.upper() in ('LIMIT', 'STOP_LIMIT'):
            params['price'] = str(price)
        
        # Add conditional parameters for STOP_LIMIT
        if order_type.upper() == 'STOP_LIMIT':
            params['stopOrderType'] = 'Stop'
            params['triggerPrice'] = str(trigger_price)
            # 1=Buy/Above, 2=Sell/Below
            params['triggerDirection'] = 1 if side.upper() == 'BUY' else 2 
            
            log_type = f"STOP_LIMIT (Trigger: {trigger_price})"
        else:
            log_type = order_type
            
        logger.info(f"-> Sending API Request for {log_type} order: {params}")

        try:
            response = self.client.place_order(**params)
            
            # Output Order Details and Execution Status
            order_id = response.get('result', {}).get('orderId')
            
            if order_id:
                logger.info(f"✅ ORDER PLACED (ID: {order_id})")
                logger.info(f"  - Details: {side} {qty} {symbol} @ {log_type} (Price: {price or 'N/A'})")
                logger.info(f"  - Full Response: {response}")
            else:
                logger.error(f"Order failed, no Order ID in response. Response: {response}")

            return response
            
        except InvalidRequestError as e:
            logger.error(f"❌ API Error (Invalid Request): {e}. Check symbol, qty, and price precision.")
        except FailedRequestError as e:
            logger.error(f"❌ API Error (Failed Request): {e}. Authentication or Rate Limit issue.")
        except Exception as e:
            logger.error(f"❌ An unexpected error occurred: {e}")
        
        return None

    def place_market_order(self, symbol: str, side: str, qty: float):
        """Places a market order."""
        return self._place_order(symbol, side, 'MARKET', qty)

    def place_limit_order(self, symbol: str, side: str, qty: float, price: float):
        """Places a limit order."""
        return self._place_order(symbol, side, 'LIMIT', qty, price)
        
    def place_stop_limit_order(self, symbol: str, side: str, qty: float, price: float, trigger_price: float):
        """Places a stop-limit order (Bonus Task)."""
        return self._place_order(symbol, side, 'STOP_LIMIT', qty, price, trigger_price)


# --- CLI INTERFACE (Includes Bonus Commands) ---

def run_cli_interface(bot: BasicBot):
    """Handles command-line user input for trading."""
    
    print("\n--- Bybit Bot CLI Interface ---")
    print("Available Commands: MARKET, LIMIT, STOP_LIMIT, BALANCE, EXIT")
    
    while True:
        try:
            command = input("\nEnter command (MARKET, LIMIT, STOP_LIMIT, BALANCE, EXIT): ").strip().upper()
            
            if command == 'EXIT':
                print("Exiting bot. Goodbye! Your log file is saved as 'trading_bot_log.txt'.")
                break
            
            if command == 'BALANCE': # Handle new BALANCE command
                bot.get_balance()
                continue
                
            valid_commands = ('MARKET', 'LIMIT', 'STOP_LIMIT')
            if command not in valid_commands:
                logger.warning(f"Invalid command: {command}. Please use one of the available options.")
                continue

            # --- Trading Commands (MARKET, LIMIT, STOP_LIMIT) ---
            symbol = input("Enter symbol (e.g., BTCUSDT): ").strip().upper()
            side = input("Enter side (BUY or SELL): ").strip().upper()
            
            if side not in ('BUY', 'SELL'):
                logger.warning(f"Invalid side: {side}. Must be BUY or SELL.")
                continue

            try:
                qty = float(input("Enter quantity: ").strip())
                if qty <= 0:
                    raise ValueError("Quantity must be positive.")
            except ValueError as e:
                logger.error(f"Invalid quantity input: {e}")
                continue

            # Execute based on command
            if command == 'MARKET':
                bot.place_market_order(symbol, side, qty)
            
            elif command == 'LIMIT':
                try:
                    price = float(input("Enter limit price: ").strip())
                    if price <= 0:
                        raise ValueError("Price must be positive.")
                except ValueError as e:
                    logger.error(f"Invalid price input: {e}")
                    continue
                    
                bot.place_limit_order(symbol, side, qty, price)

            elif command == 'STOP_LIMIT': # Handle new STOP_LIMIT command
                try:
                    price = float(input("Enter limit price (Order Price): ").strip())
                    trigger_price = float(input("Enter trigger price (Stop Price): ").strip())
                    if price <= 0 or trigger_price <= 0:
                        raise ValueError("Prices must be positive.")
                except ValueError as e:
                    logger.error(f"Invalid price input: {e}")
                    continue

                bot.place_stop_limit_order(symbol, side, qty, price, trigger_price)


        except Exception as e:
            logger.error(f"An unexpected error occurred during CLI input: {e}")


# --- MAIN EXECUTION BLOCK ---

if __name__ == '__main__':
    API_KEY = os.environ.get("BYBIT_API_KEY")
    API_SECRET = os.environ.get("BYBIT_API_SECRET")
    
    if not API_KEY or not API_SECRET:
        logger.error("API Key or Secret not found. Please ensure your .env file is configured correctly.")
        sys.exit(1)
        
    my_bot = BasicBot(API_KEY, API_SECRET, testnet=True)
    run_cli_interface(my_bot)
