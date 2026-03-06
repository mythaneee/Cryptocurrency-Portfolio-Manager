# controller.py

from model import Portfolio, CoinGeckoAPI     
from view import PortfolioView
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QInputDialog, QMessageBox, QAction
import sys
from pathlib import Path

class PriceUpdater(QThread):
    update_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)
    status_signal = pyqtSignal(str)

    def __init__(self, api, interval_seconds=300, parent=None):
        super().__init__(parent)
        self.api = api
        self.interval_seconds = interval_seconds
        self._coin_ids = []
        self._running = True
        self._pending_refresh = True

    def set_coin_ids(self, coin_ids):
        """ Update the list of coin IDs to fetch prices for."""
        new_coin_ids = list(coin_ids)
        if new_coin_ids != self._coin_ids:
            self._coin_ids = new_coin_ids
            self._pending_refresh = True

    def request_refresh(self):
        """ Request an immediate refresh of prices on the next loop iteration."""
        self._pending_refresh = True

    def stop(self):
        """ Stop the background updater thread."""
        self._running = False

    def run(self):
        """ Main loop for the background price updater thread."""
        self.status_signal.emit("Background updater started.")
        next_fetch_in_ms = 0
        while self._running:
            if not self._coin_ids:
                self.status_signal.emit("Portfolio is empty - add a coin.")
                self.msleep(500)
                continue

            if self._pending_refresh or next_fetch_in_ms <= 0:
                self._pending_refresh = False
                try:
                    prices = self.api.fetch_batch_prices(self._coin_ids)
                    self.update_signal.emit(prices)
                except Exception as e:
                    self.error_signal.emit(str(e))
                next_fetch_in_ms = max(1000, self.interval_seconds * 1000)

            self.msleep(500)
            next_fetch_in_ms -= 500

        self.status_signal.emit("Background updater stopped.")

class Controller:
    def __init__(self):
        self.portfolio = Portfolio()
        self.view = PortfolioView()
        self.api = CoinGeckoAPI()
        self.data_file = Path(__file__).with_name("portfolio_data.json")

        self.portfolio.load_from_file(str(self.data_file))
        if self.portfolio.holdings:
            self.portfolio.save_to_file(str(self.data_file))
            self.view.update_holdings_table(self.portfolio.get_table_rows())
            self.view.status_label.setText(f"Loaded {len(self.portfolio.holdings)} saved coin(s).")

        self.price_updater = PriceUpdater(self.api, interval_seconds=300)
        self.price_updater.update_signal.connect(self.on_prices_updated)
        self.price_updater.error_signal.connect(self.on_update_error)
        self.price_updater.status_signal.connect(self.on_updater_status)
        self.price_updater.set_coin_ids(list(self.portfolio.holdings.keys()))
        self.price_updater.start()

        self.setup_actions()

        self.add_coin()  # Prompt user to add a coin on startup

    def setup_actions(self):
        """ Sets up menu actions for adding/removing coins and refreshing prices."""
        menu = self.view.menuBar().addMenu("Portfolio")

        add_action = QAction("Add Coin", self.view)
        add_action.triggered.connect(self.add_coin)
        menu.addAction(add_action)

        remove_action = QAction("Remove Coin", self.view)
        remove_action.triggered.connect(self.remove_coin)
        menu.addAction(remove_action)

        refresh_action = QAction("Refresh Prices", self.view)
        refresh_action.triggered.connect(self.refresh_prices)
        menu.addAction(refresh_action)

    
    def add_coin(self):
        """ Prompts user to enter a CoinGecko coin ID to add to the portfolio."""
        coin_id, ok = QInputDialog.getText(
            self.view, "Add Cryptocurrency", "Enter CoinGecko ID (e.g., 'bitcoin'):",

            text = ""
        )

        if not ok or not coin_id.strip():
            return  # User cancelled or entered empty ID
        coin_id = coin_id.strip().lower()

        if not self.api.coin_id_exists(coin_id):
           QMessageBox.warning(self.view, "Not Found", f"Coin {coin_id} not found in CoinGecko.")
           return
        
        self.portfolio.add_holding(coin_id)
        self.portfolio.save_to_file(str(self.data_file))
        self.price_updater.set_coin_ids(list(self.portfolio.holdings.keys()))
        self.price_updater.request_refresh()
        QMessageBox.information(self.view, "Coin Added", f"{coin_id} has been added to your portfolio.")

    def remove_coin(self):
        """ Prompts user to select a coin to remove from the portfolio."""
        coin_ids = sorted(self.portfolio.holdings.keys())
        if not coin_ids:
            QMessageBox.information(self.view, "Remove Coin", "Portfolio is empty.")
            return

        coin_id, ok = QInputDialog.getItem(
            self.view,
            "Remove Cryptocurrency",
            "Select coin to remove:",
            coin_ids,
            0,
            False,
        )

        if not ok or not coin_id:
            return

        removed = self.portfolio.remove_holding(coin_id)
        if not removed:
            QMessageBox.warning(self.view, "Remove Coin", f"{coin_id} not found in portfolio.")
            return

        self.portfolio.save_to_file(str(self.data_file))
        self.price_updater.set_coin_ids(list(self.portfolio.holdings.keys()))
        self.price_updater.request_refresh()

        rows = self.portfolio.get_table_rows()
        self.view.update_holdings_table(rows)
        self.view.mini_graph()

        if self.portfolio.holdings:
            self.view.status_label.setText("Background refresh running every 5 minutes.")
        else:
            self.view.status_label.setText("Portfolio is empty - add a coin.")
            self.view.table.setRowCount(0)

        QMessageBox.information(self.view, "Coin Removed", f"{coin_id} has been removed.")

    def refresh_prices(self):
        """ Manually trigger a price refresh from the background updater thread."""
        coin_ids = list(self.portfolio.holdings.keys())

        if not coin_ids:
            self.view.status_label.setText("Portfolio is empty - add a coin.")
            self.view.table.setRowCount(0)  # Clear table if no holdings
            return
        self.price_updater.set_coin_ids(coin_ids)
        self.price_updater.request_refresh()
        self.view.status_label.setText("Fetching prices in background... (auto refresh: 5 minutes)")

    def on_prices_updated(self, prices_data):
        """ Called when new price data is received from the background updater thread."""
        self.portfolio.update_prices(prices_data)
        self.portfolio.save_to_file(str(self.data_file))
        rows = self.portfolio.get_table_rows()
        self.view.update_holdings_table(rows)
        self.view.mini_graph(rows)
        total = self.portfolio.get_total_value_usd()
        coin_count = len(self.portfolio.holdings)
        self.view.status_label.setText(f"Updated {coin_count} coin(s) • Total: ${total:.2f}")

    def on_update_error(self, message):
        self.view.status_label.setText(f"Error fetching prices: {message}")

    def on_updater_status(self, message):
        """ Update status label with messages from the background updater thread."""
        if not self.portfolio.holdings:
            self.view.status_label.setText(message)

    def shutdown(self):
        """ Cleanly shutdown the background updater thread and save portfolio data."""
        self.portfolio.save_to_file(str(self.data_file))
        if self.price_updater.isRunning():
            self.price_updater.stop()
            self.price_updater.wait(3000)  
    
def main():
    app = QApplication(sys.argv)
    controller = Controller()
    app.aboutToQuit.connect(controller.shutdown)
    controller.view.show()
    sys.exit(app.exec_())   

if __name__ == "__main__":
    main()