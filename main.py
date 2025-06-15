import json
import os
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QTextEdit, QListWidget, QMessageBox, QFormLayout, QSplitter, QListWidgetItem, QApplication, QLabel
)

JSON_FILE = "woerterbuch.json"

def load_all_begriffe():
    if not os.path.exists(JSON_FILE):
        return []
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        try:
            begriffe = json.load(f)
            for b in begriffe:
                b.setdefault("begriff", "")
                b.setdefault("beschreibung", "")
            return begriffe
        except json.JSONDecodeError:
            return []

def save_all_begriffe(begriffe):
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(begriffe, f, ensure_ascii=False, indent=2)

class DictionaryApp(QWidget):
    def __init__(self):
        super().__init__()
        self.all_begriffe = []
        self.initUI()
        self.load_begriffe()

    def initUI(self):
        self.setWindowTitle('Wörterbuch App')
        self.setGeometry(100, 100, 800, 500)
        self.setStyleSheet("""
            QWidget {
                background-color: #23272e;
                color: #f8f8f2;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: 15px;
            }
            QLineEdit, QTextEdit {
                background: #282c34;
                border-radius: 8px;
                border: 1px solid #44475a;
                padding: 6px;
                color: #f8f8f2;
            }
            QListWidget {
                background: #282c34;
                border-radius: 8px;
                border: 1px solid #44475a;
                color: #f8f8f2;
            }
            QPushButton {
                background: #6272a4;
                border-radius: 8px;
                padding: 8px 16px;
                color: #f8f8f2;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #50fa7b;
                color: #23272e;
            }
            QPushButton:pressed {
                background: #bd93f9;
            }
            QFormLayout > QLabel {
                font-weight: bold;
                color: #8be9fd;
            }
            QLabel#searchLabel {
                font-weight: bold;
                color: #50fa7b;
                padding-left: 5px;
            }
        """)

        mainLayout = QHBoxLayout(self)
        splitter = QSplitter(self)
        mainLayout.addWidget(splitter)

        leftWidget = QWidget()
        leftLayout = QVBoxLayout(leftWidget)
        leftLayout.setContentsMargins(0,0,0,0)

        searchLabel = QLabel("Live Suche")
        searchLabel.setObjectName("searchLabel")
        self.searchInput = QLineEdit()
        self.searchInput.setPlaceholderText("Begriff oder Beschreibung suchen...")
        self.searchInput.textChanged.connect(self.filter_begriffe)

        self.begriffList = QListWidget()
        self.begriffList.setFont(QFont("Segoe UI", 12))
        self.begriffList.setStyleSheet("QListWidget::item:selected { background: #44475a; color: #50fa7b; }")
        self.begriffList.itemClicked.connect(self.load_begriff)

        leftLayout.addWidget(searchLabel)
        leftLayout.addWidget(self.searchInput)
        leftLayout.addWidget(self.begriffList)

        splitter.addWidget(leftWidget)
        splitter.setStretchFactor(0, 1)
        splitter.setMinimumWidth(300)

        rightWidget = QWidget()
        rightLayout = QVBoxLayout(rightWidget)

        formLayout = QFormLayout()
        self.begriffInput = QLineEdit()
        self.beschreibungInput = QTextEdit()
        self.beschreibungInput.setFixedHeight(120)
        formLayout.addRow('Begriff:', self.begriffInput)
        formLayout.addRow('Beschreibung:', self.beschreibungInput)

        buttonLayout = QHBoxLayout()
        self.addButton = QPushButton('Hinzufügen')
        self.updateButton = QPushButton('Aktualisieren')
        self.deleteButton = QPushButton('Löschen')
        self.clearButton = QPushButton('Leeren')
        for btn in [self.addButton, self.updateButton, self.deleteButton, self.clearButton]:
            btn.setMinimumWidth(120)
            btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        buttonLayout.addWidget(self.addButton)
        buttonLayout.addWidget(self.updateButton)
        buttonLayout.addWidget(self.deleteButton)
        buttonLayout.addWidget(self.clearButton)

        rightLayout.addLayout(formLayout)
        rightLayout.addSpacing(10)
        rightLayout.addLayout(buttonLayout)
        rightLayout.addStretch()
        splitter.addWidget(rightWidget)
        splitter.setStretchFactor(1, 2)

        self.addButton.clicked.connect(self.add_begriff)
        self.updateButton.clicked.connect(self.update_begriff)
        self.deleteButton.clicked.connect(self.delete_begriff)
        self.clearButton.clicked.connect(self.clear_inputs)

        self.setLayout(mainLayout)
        self.show()

    def load_begriffe(self):
        self.all_begriffe = load_all_begriffe()
        self.filter_begriffe()

    def filter_begriffe(self):
        search_text = self.searchInput.text().lower()
        self.begriffList.clear()
        for b in self.all_begriffe:
            begriff = b.get("begriff", "").lower()
            beschreibung = b.get("beschreibung", "").lower()
            if search_text in begriff or search_text in beschreibung:
                item = QListWidgetItem(b.get("begriff", ""))
                self.begriffList.addItem(item)

    def add_begriff(self):
        begriff = self.begriffInput.text().strip()
        beschreibung = self.beschreibungInput.toPlainText().strip()

        if not begriff or not beschreibung:
            QMessageBox.warning(self, 'Warnung', 'Begriff und Beschreibung dürfen nicht leer sein.')
            return

        if any(b.get("begriff", "").lower() == begriff.lower() for b in self.all_begriffe):
            QMessageBox.warning(self, 'Warnung', 'Der Begriff ist bereits vorhanden.')
            return

        self.all_begriffe.append({
            "begriff": begriff,
            "beschreibung": beschreibung
        })
        save_all_begriffe(self.all_begriffe)
        self.load_begriffe()
        self.clear_inputs()

    def update_begriff(self):
        current_item = self.begriffList.currentItem()
        if not current_item:
            return
        selected_begriff = current_item.text()
        begriff = self.begriffInput.text().strip()
        beschreibung = self.beschreibungInput.toPlainText().strip()

        if not begriff or not beschreibung:
            QMessageBox.warning(self, 'Warnung', 'Begriff und Beschreibung dürfen nicht leer sein.')
            return

        for b in self.all_begriffe:
            if b.get("begriff", "") == selected_begriff:
                b["begriff"] = begriff
                b["beschreibung"] = beschreibung
                break
        save_all_begriffe(self.all_begriffe)
        self.load_begriffe()
        self.clear_inputs()

    def delete_begriff(self):
        current_item = self.begriffList.currentItem()
        if not current_item:
            return
        selected_begriff = current_item.text()
        reply = QMessageBox.question(self, 'Bestätigung', 'Möchten Sie diesen Begriff wirklich löschen?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.all_begriffe = [b for b in self.all_begriffe if b.get("begriff", "") != selected_begriff]
            save_all_begriffe(self.all_begriffe)
            self.load_begriffe()
            self.clear_inputs()

    def load_begriff(self, item):
        selected_begriff = item.text()
        for b in self.all_begriffe:
            if b.get("begriff", "") == selected_begriff:
                self.begriffInput.setText(b.get("begriff", ""))
                self.beschreibungInput.setPlainText(b.get("beschreibung", ""))
                return
        self.clear_inputs()

    def clear_inputs(self):
        self.begriffInput.clear()
        self.beschreibungInput.clear()
        self.begriffList.clearSelection()
        self.searchInput.clear()

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    ex = DictionaryApp()
    sys.exit(app.exec_())