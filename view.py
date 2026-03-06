from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
QMainWindow, 
QDesktopWidget, 
QWidget, 
QLabel, 
QVBoxLayout, 
QTableWidget, 
QTableWidgetItem, 
)

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from typing import Any

class PortfolioView(QMainWindow):
    def __init__(self):
     super().__init__()
     self.setWindowTitle("Cryptocurrency Portfolio Manager")
     self.setGeometry(0, 0, 800, 600)
     self.center_window()
     self.setup_ui()
     
    def center_window(self):
     """"Centralises GUI to the screen"""
     geo_of_main_window = self.frameGeometry()                                                                # calculates geo of screen
     center_point_of_window = QDesktopWidget().availableGeometry().center()                                   # gets center point of screen available
     geo_of_main_window.moveCenter(center_point_of_window)                                                    # moves window center to screen's center point
     self.move(geo_of_main_window.topLeft())                                                                  # moves screen to top-left we just calculated

    def setup_ui(self):
      """Sets up the UI components"""
      central_widget = QWidget()                                                                        # creates central widget and aligns it to the left
      self.setCentralWidget(central_widget)

      self.main_layout = QVBoxLayout()
      central_widget.setLayout(self.main_layout)

      welcome_label = QLabel("Welcome to the Cryptocurrency Portfolio Manager!")
      welcome_label.setStyleSheet("font-size: 18px; font-weight: bold;")
      welcome_label.setAlignment(Qt.AlignLeft)
      self.main_layout.addWidget(welcome_label)


      self.status_label = QLabel("Status: Ready")
      self.main_layout.addWidget(self.status_label)

      # The Real Table
      self.table = QTableWidget()
      self.table.setColumnCount(4)
      self.table.setHorizontalHeaderLabels(["Coin", "Amount", "Value (USD)", "change_24 (%)"])
      self.table.horizontalHeader().setStretchLastSection(True)  
      self.main_layout.addWidget(self.table)

      # Keep a persistent figure/canvas so updates redraw in-place.
      self.figure = Figure(figsize=(6, 2.5), dpi=100)
      self.canvas = FigureCanvas(self.figure)
      self.graph_ax = self.figure.add_subplot(111)
      self.main_layout.addWidget(self.canvas)
      self.mini_graph([])  # Initialize with empty graph

    def update_holdings_table(self, rows: list[dict[str, Any]]):
     """Updates the holdings table with new data"""
     self.table.setRowCount(len(rows))  

     for row_idx, coin in enumerate(rows):
         self.table.setItem(row_idx, 0, QTableWidgetItem(coin["symbol"]))
         self.table.setItem(row_idx, 1, QTableWidgetItem(f"{coin['amount']:.6f}"))
         self.table.setItem(row_idx, 2, QTableWidgetItem(f"${coin['value_usd']:,.2f}"))
         change_24h = coin.get("change_24h")
         change_text = "N/A" if change_24h is None else f"{change_24h:.2f}%"
         self.table.setItem(row_idx, 3, QTableWidgetItem(change_text))
     self.table.resizeColumnsToContents()  

    def mini_graph (self, coin_data: list[dict[str, Any]]):
      """Graphs current portfolio value per coin."""
      self.graph_ax.clear()

      if not coin_data:
        self.graph_ax.set_title("Portfolio Value by Coin")
        self.graph_ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=self.graph_ax.transAxes)
        self.graph_ax.set_xticks([])
        self.graph_ax.set_yticks([])
        self.figure.tight_layout(pad=1.0)
        self.canvas.draw_idle()
        return

      labels = [str(coin.get("symbol", "?")).upper() for coin in coin_data]
      values = [float(coin.get("value_usd", 0.0) or 0.0) for coin in coin_data]

      self.graph_ax.bar(labels, values, color="red", alpha=0.8)
      self.graph_ax.set_title("Portfolio Value by Coin")
      self.graph_ax.set_xlabel("Coin")
      self.graph_ax.set_ylabel("Value (USD)")
      self.graph_ax.tick_params(axis="x", rotation=30)
      self.graph_ax.grid(True, linestyle="--", alpha=0.4)
      self.figure.tight_layout(pad=1.0)
      self.canvas.draw_idle()


