from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty, QRect
from PyQt5.QtWidgets import (
    QMainWindow,
    QDesktopWidget,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QFrame,
    QSizePolicy,
    QGraphicsDropShadowEffect,
)
from PyQt5.QtGui import (
    QColor,
    QPalette,
    QFont,
    QLinearGradient,
    QBrush,
    QPainter,
    QPen,
    QFontDatabase,
)

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from typing import Any


BG_BASE        = "#0A0C0F"
BG_PANEL       = "#0F1217"
BG_CARD        = "#13171E"
BG_ROW_ALT    = "#161B23"
ACCENT_CYAN    = "#00D4FF"
ACCENT_GREEN   = "#00E5A0"
ACCENT_RED     = "#FF4D6A"
ACCENT_AMBER   = "#FFB547"
TEXT_PRIMARY   = "#E8EDF5"
TEXT_SECONDARY = "#6B7A99"
TEXT_MUTED     = "#3A4560"
BORDER_SUBTLE  = "#1C2235"
BORDER_ACCENT  = "#1E2D4A"



class CardFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            CardFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 10px;
            }}
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 120))
        self.setGraphicsEffect(shadow)


class StatTile(CardFrame):
    def __init__(self, label: str, value: str = "—", accent: str = ACCENT_CYAN, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(88)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(4)

        lbl = QLabel(label.upper())
        lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 10px; letter-spacing: 1.5px; font-weight: 600; background: transparent; border: none;")
        layout.addWidget(lbl)

        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(f"color: {accent}; font-size: 22px; font-weight: 700; font-family: 'Courier New'; background: transparent; border: none;")
        layout.addWidget(self.value_label)

    def set_value(self, text: str):
        self.value_label.setText(text)



class Divider(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(1)
        self.setStyleSheet(f"background-color: {BORDER_SUBTLE};")


def section_label(text: str) -> QLabel:
    lbl = QLabel(text.upper())
    lbl.setStyleSheet(
        f"color: {TEXT_SECONDARY}; font-size: 10px; letter-spacing: 2px; "
        f"font-weight: 700; padding: 0px 0px 2px 0px; background: transparent;"
    )
    return lbl


class PortfolioView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CRYPTOLEDGER  ·  Portfolio Manager")
        self.setGeometry(0, 0, 1080, 720)
        self._apply_global_palette()
        self.center_window()
        self.setup_ui()

    def _apply_global_palette(self):
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background-color: {BG_BASE};
                color: {TEXT_PRIMARY};
                font-family: 'Segoe UI', 'SF Pro Display', sans-serif;
                font-size: 13px;
            }}
            QScrollBar:vertical {{
                background: {BG_BASE};
                width: 6px;
                border-radius: 3px;
            }}
            QScrollBar::handle:vertical {{
                background: {TEXT_MUTED};
                border-radius: 3px;
                min-height: 20px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)

    def center_window(self):
        geo = self.frameGeometry()
        center = QDesktopWidget().availableGeometry().center()
        geo.moveCenter(center)
        self.move(geo.topLeft())

    def setup_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        navbar = QWidget()
        navbar.setFixedHeight(56)
        navbar.setStyleSheet(f"""
            background-color: {BG_PANEL};
            border-bottom: 1px solid {BORDER_SUBTLE};
        """)
        nav_layout = QHBoxLayout(navbar)
        nav_layout.setContentsMargins(28, 0, 28, 0)

        logo = QLabel("◈  CRYPTOLEDGER")
        logo.setStyleSheet(f"color: {ACCENT_CYAN}; font-size: 14px; font-weight: 800; letter-spacing: 3px; background: transparent;")
        nav_layout.addWidget(logo)
        nav_layout.addStretch()

        self.add_coin_button = QPushButton("+ Add Coin")
        self.add_coin_button.setCursor(Qt.PointingHandCursor)
        self.add_coin_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT_CYAN};
                color: {BG_BASE};
                border: none;
                border-radius: 8px;
                padding: 7px 14px;
                font-size: 12px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background-color: #43DEFF;
            }}
            QPushButton:pressed {{
                background-color: #00B7DB;
            }}
        """)
        nav_layout.addWidget(self.add_coin_button)

        self.remove_coin_button = QPushButton("Remove Coin")
        self.remove_coin_button.setCursor(Qt.PointingHandCursor)
        self.remove_coin_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {TEXT_SECONDARY};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 8px;
                padding: 7px 14px;
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                border: 1px solid {BORDER_ACCENT};
                color: {TEXT_PRIMARY};
            }}
            QPushButton:pressed {{
                background-color: {BG_CARD};
            }}
        """)
        nav_layout.addWidget(self.remove_coin_button)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setCursor(Qt.PointingHandCursor)
        self.refresh_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {TEXT_SECONDARY};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 8px;
                padding: 7px 12px;
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                border: 1px solid {BORDER_ACCENT};
                color: {TEXT_PRIMARY};
            }}
            QPushButton:pressed {{
                background-color: {BG_CARD};
            }}
        """)
        nav_layout.addWidget(self.refresh_button)

        self.status_label = QLabel("● LIVE")
        self.status_label.setStyleSheet(f"color: {ACCENT_GREEN}; font-size: 11px; letter-spacing: 1px; font-weight: 600; background: transparent;")
        nav_layout.addWidget(self.status_label)

        root_layout.addWidget(navbar)

        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(28, 24, 28, 24)
        body_layout.setSpacing(20)

        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(14)

        self.tile_total   = StatTile("Total Value",    "$ —",  ACCENT_CYAN)
        self.tile_coins   = StatTile("Assets Held",    "—",    ACCENT_AMBER)
        self.tile_change  = StatTile("24h Change",     "—",    ACCENT_GREEN)
        self.tile_top     = StatTile("Top Holding",    "—",    TEXT_PRIMARY)

        for tile in (self.tile_total, self.tile_coins, self.tile_change, self.tile_top):
            kpi_row.addWidget(tile)

        body_layout.addLayout(kpi_row)

        split = QHBoxLayout()
        split.setSpacing(16)

        table_card = CardFrame()
        table_card_layout = QVBoxLayout(table_card)
        table_card_layout.setContentsMargins(16, 16, 16, 16)
        table_card_layout.setSpacing(10)
        table_card_layout.addWidget(section_label("Holdings"))
        table_card_layout.addWidget(Divider())

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Asset", "Amount", "Value (USD)", "24h Δ"])
        self._style_table()
        table_card_layout.addWidget(self.table)
        split.addWidget(table_card, 3)

        chart_card = CardFrame()
        chart_card_layout = QVBoxLayout(chart_card)
        chart_card_layout.setContentsMargins(16, 16, 16, 16)
        chart_card_layout.setSpacing(10)
        chart_card_layout.addWidget(section_label("Allocation"))
        chart_card_layout.addWidget(Divider())

        self.figure = Figure(figsize=(4, 3.5), dpi=100)
        self.figure.patch.set_facecolor(BG_CARD)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet(f"background: {BG_CARD}; border: none;")
        self.graph_ax = self.figure.add_subplot(111)
        chart_card_layout.addWidget(self.canvas)
        split.addWidget(chart_card, 2)

        body_layout.addLayout(split)
        root_layout.addWidget(body)

        self.mini_graph([])

    def _style_table(self):
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: transparent;
                alternate-background-color: {BG_ROW_ALT};
                color: {TEXT_PRIMARY};
                border: none;
                border-radius: 6px;
                selection-background-color: {BORDER_ACCENT};
                font-size: 13px;
                gridline-color: transparent;
            }}
            QHeaderView::section {{
                background-color: transparent;
                color: {TEXT_SECONDARY};
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 1.4px;
                text-transform: uppercase;
                padding: 8px 12px;
                border: none;
                border-bottom: 1px solid {BORDER_SUBTLE};
            }}
            QTableWidget::item {{
                padding: 10px 12px;
                border: none;
            }}
            QTableWidget::item:selected {{
                background-color: {BORDER_ACCENT};
                color: {TEXT_PRIMARY};
            }}
        """)

    def update_holdings_table(self, rows: list[dict[str, Any]]):
        self.table.setRowCount(len(rows))

        total_value = sum(float(c.get("value_usd", 0) or 0) for c in rows)
        changes = [c.get("change_24h") for c in rows if c.get("change_24h") is not None]
        avg_change = sum(changes) / len(changes) if changes else None
        top = max(rows, key=lambda c: float(c.get("value_usd", 0) or 0), default=None)

        self.tile_total.set_value(f"${total_value:,.2f}")
        self.tile_coins.set_value(str(len(rows)))
        if avg_change is not None:
            color = ACCENT_GREEN if avg_change >= 0 else ACCENT_RED
            sign  = "+" if avg_change >= 0 else ""
            self.tile_change.value_label.setStyleSheet(
                f"color: {color}; font-size: 22px; font-weight: 700; font-family: 'Courier New'; background: transparent; border: none;"
            )
            self.tile_change.set_value(f"{sign}{avg_change:.2f}%")
        if top:
            self.tile_top.set_value(str(top.get("symbol", "—")).upper())

        for row_idx, coin in enumerate(rows):
            symbol_item = QTableWidgetItem(str(coin.get("symbol", "")).upper())
            symbol_item.setForeground(QColor(ACCENT_CYAN))
            font = symbol_item.font()
            font.setWeight(QFont.Bold)
            symbol_item.setFont(font)

            amount_item = QTableWidgetItem(f"{coin.get('amount', 0):.6f}")
            amount_item.setForeground(QColor(TEXT_PRIMARY))
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            value_item = QTableWidgetItem(f"${coin.get('value_usd', 0):,.2f}")
            value_item.setForeground(QColor(TEXT_PRIMARY))
            value_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            change_24h = coin.get("change_24h")
            if change_24h is None:
                change_text = "N/A"
                change_color = TEXT_MUTED
            else:
                sign = "+" if change_24h >= 0 else ""
                change_text = f"{sign}{change_24h:.2f}%"
                change_color = ACCENT_GREEN if change_24h >= 0 else ACCENT_RED
            change_item = QTableWidgetItem(change_text)
            change_item.setForeground(QColor(change_color))
            change_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            self.table.setItem(row_idx, 0, symbol_item)
            self.table.setItem(row_idx, 1, amount_item)
            self.table.setItem(row_idx, 2, value_item)
            self.table.setItem(row_idx, 3, change_item)

        self.table.resizeRowsToContents()

    def mini_graph(self, coin_data: list[dict[str, Any]]):
        self.graph_ax.clear()
        self.graph_ax.set_facecolor(BG_CARD)

        if not coin_data:
            self.graph_ax.set_title("No Data", color=TEXT_MUTED, fontsize=11, pad=10)
            self.graph_ax.text(0.5, 0.5, "Add holdings to see allocation",
                               ha="center", va="center",
                               transform=self.graph_ax.transAxes,
                               color=TEXT_SECONDARY, fontsize=10)
            self.graph_ax.set_xticks([])
            self.graph_ax.set_yticks([])
            for spine in self.graph_ax.spines.values():
                spine.set_visible(False)
            self.figure.tight_layout(pad=1.2)
            self.canvas.draw_idle()
            return

        labels = [str(c.get("symbol", "?")).upper() for c in coin_data]
        values = [float(c.get("value_usd", 0) or 0) for c in coin_data]

        palette = [
            "#00D4FF", "#00E5A0", "#FFB547", "#FF4D6A",
            "#A78BFA", "#FB923C", "#34D399", "#60A5FA",
        ]
        colors = [palette[i % len(palette)] for i in range(len(labels))]

        wedges, texts, autotexts = self.graph_ax.pie(
            values,
            labels=None,
            colors=colors,
            autopct=lambda p: f"{p:.1f}%" if p > 4 else "",
            pctdistance=0.78,
            startangle=90,
            wedgeprops=dict(width=0.52, edgecolor=BG_CARD, linewidth=2),
        )

        for at in autotexts:
            at.set_color(BG_BASE)
            at.set_fontsize(8)
            at.set_fontweight("bold")

        legend_patches = [
            mpatches.Patch(facecolor=colors[i], label=labels[i])
            for i in range(len(labels))
        ]
        self.graph_ax.legend(
            handles=legend_patches,
            loc="lower center",
            bbox_to_anchor=(0.5, -0.18),
            ncol=min(len(labels), 4),
            frameon=False,
            fontsize=9,
            labelcolor=TEXT_SECONDARY,
        )

        self.graph_ax.set_title("Portfolio Allocation", color=TEXT_SECONDARY,
                                fontsize=10, pad=10, fontweight="600", loc="center")

        for spine in self.graph_ax.spines.values():
            spine.set_visible(False)

        self.figure.tight_layout(pad=1.2)
        self.canvas.draw_idle()

    def set_status(self, text: str, ok: bool = True):
        color = ACCENT_GREEN if ok else ACCENT_RED
        dot   = "●" if ok else "⚠"
        self.status_label.setText(f"{dot} {text.upper()}")
        self.status_label.setStyleSheet(
            f"color: {color}; font-size: 11px; letter-spacing: 1px; font-weight: 600; background: transparent;"
        )