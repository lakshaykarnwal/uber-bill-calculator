from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QFormLayout
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QIcon
import ast
import operator
import sys

class BillCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.dynamic_widgets = []
        self.meal_cost_entries = []

        self.setWindowTitle("Bill Calculator")
        self.setWindowIcon(QIcon('icon.icns'))  # Set the window icon
        self.setStyleSheet("background-color: #2E2E2E; color: white;")

        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(10)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        self.form_layout = QFormLayout()
        self.form_layout.setSpacing(10)

        self.nf_entry = QLineEdit()
        self.nf_entry.installEventFilter(self)  # Install event filter for the QLineEdit
        self.form_layout.addRow(QLabel("Number of Friends:"), self.nf_entry)

        self.main_layout.addLayout(self.form_layout)

        self.nf_button = self.create_button("Set Number of Friends", self.show_meal_cost_fields)
        self.main_layout.addWidget(self.nf_button)

        self.setLayout(self.main_layout)

    def create_button(self, text, function):
        button = QPushButton(text)
        button.setStyleSheet("""
            QPushButton {
                background-color: #5A9;
                color: white;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:pressed {
                background-color: #4A8;
            }
        """)
        button.clicked.connect(function)
        return button

    def eventFilter(self, source, event):
        if event.type() == QEvent.KeyPress:
            if source is self.nf_entry and (event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter):
                self.show_meal_cost_fields()
                return True
            if source in self.meal_cost_entries and (event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter):
                self.calculate_owed_amounts()
                return True
        return super().eventFilter(source, event)

    def show_meal_cost_fields(self):
        self.clear_dynamic_widgets()

        try:
            nf = self.safe_eval(self.nf_entry.text())
            nf = int(nf)
            self.nf_button.hide()  # Hide the Set Number of Friends button
            self.nf_entry.setDisabled(True)

            self.sc_entry = QLineEdit()
            self.form_layout.addRow(QLabel("Service Charge:"), self.sc_entry)

            self.tx_entry = QLineEdit()
            self.form_layout.addRow(QLabel("Tax:"), self.tx_entry)

            self.td_entry = QLineEdit()
            self.form_layout.addRow(QLabel("Total Discount:"), self.td_entry)

            self.dc_entry = QLineEdit()
            self.form_layout.addRow(QLabel("Delivery Charge:"), self.dc_entry)

            for i in range(nf):
                label = QLabel(f"Friend {i+1} Meal Cost:")
                label.setStyleSheet("padding: 5px;")
                self.main_layout.addWidget(label)
                self.dynamic_widgets.append(label)
                entry = QLineEdit()
                entry.setStyleSheet("background-color: #3A3A3A; color: white;")
                entry.installEventFilter(self)  # Install event filter for meal cost entries
                self.main_layout.addWidget(entry)
                self.dynamic_widgets.append(entry)
                self.meal_cost_entries.append(entry)

            self.calculate_button = self.create_button("Calculate", self.calculate_owed_amounts)
            self.main_layout.addWidget(self.calculate_button)
            self.dynamic_widgets.append(self.calculate_button)

            self.reset_button = self.create_button("Reset", self.reset_all_fields)
            self.main_layout.addWidget(self.reset_button)
            self.dynamic_widgets.append(self.reset_button)

            self.result_label = QLabel("")
            self.result_label.setStyleSheet("padding: 10px;")
            self.main_layout.addWidget(self.result_label)
            self.dynamic_widgets.append(self.result_label)

        except ValueError:
            QMessageBox.critical(self, "Invalid Input", "Please enter a valid number for NF")

    def calculate_owed_amounts(self):
        try:
            sc = self.safe_eval(self.sc_entry.text())
            tx = self.safe_eval(self.tx_entry.text())
            td = self.safe_eval(self.td_entry.text())
            dc = self.safe_eval(self.dc_entry.text())

            meal_costs = [self.safe_eval(entry.text()) for entry in self.meal_cost_entries]
            nf = len(meal_costs)
            total_meal_cost = sum(meal_costs)
            total_tax_service = sc + tx
            shared_dc = dc / nf

            owed_amounts = []
            for meal_cost in meal_costs:
                owed = round(meal_cost - (meal_cost / total_meal_cost) * td + (meal_cost / total_meal_cost) * total_tax_service + shared_dc, 2)
                owed_amounts.append(owed)

            result_text = "\n".join([f"Friend {i+1} owes: ${owed}" for i, owed in enumerate(owed_amounts)])
            self.result_label.setText(result_text)

        except Exception as e:
            QMessageBox.critical(self, "Invalid Input", f"Error in input: {e}")

    def safe_eval(self, expr):
        """
        Safely evaluate an arithmetic expression.
        """
        try:
            return float(self.eval_expr(ast.parse(expr, mode='eval').body))
        except Exception:
            raise ValueError("Invalid arithmetic expression")

    def eval_expr(self, node):
        """
        Recursively evaluate an AST node representing an arithmetic expression.
        """
        operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.BitXor: operator.xor,
        }
        if isinstance(node, ast.Num):  # <number>
            return node.n
        elif isinstance(node, ast.BinOp):  # <left> <operator> <right>
            return operators[type(node.op)](self.eval_expr(node.left), self.eval_expr(node.right))
        else:
            raise TypeError(node)

    def reset_all_fields(self):
        self.nf_entry.setDisabled(False)
        self.nf_entry.clear()
        self.nf_button.show()  # Show the Set Number of Friends button again
        self.clear_dynamic_widgets()
        self.form_layout.removeRow(self.sc_entry)
        self.form_layout.removeRow(self.tx_entry)
        self.form_layout.removeRow(self.td_entry)
        self.form_layout.removeRow(self.dc_entry)

    def clear_dynamic_widgets(self):
        for widget in self.dynamic_widgets:
            self.main_layout.removeWidget(widget)
            widget.deleteLater()
        self.dynamic_widgets.clear()
        self.meal_cost_entries.clear()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = BillCalculator()
    ex.show()
    sys.exit(app.exec_())
