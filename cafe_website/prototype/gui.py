import PyQt5, sys
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QGridLayout, QFrame, QDialog, QHBoxLayout, QComboBox, QScrollArea, QLineEdit
import sqlite3

class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.con = sqlite3.connect("cafe.db", check_same_thread=False)

        self.setWindowTitle("My Cafe")
        self.setGeometry(100, 100, 1200, 800)
        
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        layout = QGridLayout(self.main_widget)
        self.statistics = QLabel()
        self.statistics.setAlignment(Qt.AlignTop)
        self.get_statistics()
        layout.addWidget(self.statistics, 0, 0, 5, 1)

        self.recent_order = QLabel()
        self.recent_order.setAlignment(Qt.AlignTop)
        self.get_recent_order()
        layout.addWidget(self.recent_order, 0, 1, 5, 1)

        order_button = QPushButton("Start an Order")
        order_button.clicked.connect(self.start_order)
        layout.addWidget(order_button, 6, 0, 1, 2)

    def get_statistics(self):
        cur = self.con.cursor()
        cur.execute("""
            SELECT item_id, SUM(quantity) AS total_quantity
            FROM orderItems
            GROUP BY item_id
            ORDER BY total_quantity DESC
            LIMIT 1;
            """)
        most_bought = cur.fetchone()
        cur.execute(f"SELECT item_name FROM item WHERE item_id = {most_bought[0]}")
        most_bought_item = cur.fetchone()

        cur.execute("SELECT order_id, quantity from orders ORDER BY quantity DESC LIMIT 1")
        biggest_order = cur.fetchone()
        self.statistics.setText(f'''Most Bought Item: {most_bought_item[0]}: {most_bought[1]}\nBiggest Order: ${biggest_order[1]}\n''')
        cur.close()

    def get_recent_order(self):
        cur = self.con.cursor()
        order_id = cur.execute("Select order_id, total_price from orders ORDER BY order_ts DESC LIMIT 1")
        order_id = cur.fetchone()
        items = cur.execute("SELECT * from orderItems where order_id = ?", (order_id[0],))
        items = cur.fetchall()

        txt = "Most Recent Order\n"
        for item in items:
            cur.execute(f"SELECT item_name from item where item_id = {item[2]}")
            name = cur.fetchone()
            txt += f"{name[0]}: {item[3]}\n"
        txt += f"Total Price: {order_id[1]}"
        self.recent_order.setText(txt)
        cur.close()


    def start_order(self):
        self.order = OrderModule(self.con)
        self.order.exec_()
    def closeEvent(self, event):
        if self.con:
            self.con.close()
            print("Succesfully Closed database connection")
        event.accept()

class OrderModule(QDialog):
    def __init__(self, con):
        super().__init__()
        self.con = con
        self.setWindowTitle("Order")
        self.setGeometry(100, 100, 1200, 700)
        self.cur_order = []
        self.order_length = 0
        self.total = 0

        self.main_layout = QHBoxLayout(self)
        self.v_layout = QVBoxLayout()
        self.scroll_area = QScrollArea()
        # self.scroll_area.setWidgetResizable(False)
        self.scroll_layout = QGridLayout()
        cur = self.con.cursor()
        row, col = 0, 0
        for drink in cur.execute("SELECT * from item"):
            self.scroll_layout.addWidget(self.create_widget(drink), row, col)
            if col == 1:
                col = 0
                row += 1
            else:
                col = 1
        cur.close()
        
        self.scroll_area.setLayout(self.scroll_layout)
        self.button = QPushButton("Finish Order")
        self.button.clicked.connect(self.close_order)
        self.v_layout.addWidget(self.scroll_area)
        self.v_layout.addWidget(self.button)
        self.main_layout.addLayout(self.v_layout, stretch=2)

        self.summary = QVBoxLayout()
        self.summary_label = QLabel("Order Summary")
        self.summary_label.setAlignment(Qt.AlignTop)
        self.summary.addWidget(self.summary_label, stretch=1)

        self.sum_list = QGridLayout()
        self.summary.addLayout(self.sum_list, stretch=8)

        self.total_label = QLabel("Total: $0.00")
        self.total_label.setAlignment(Qt.AlignBottom)
        self.summary.addWidget(self.total_label, stretch=1)
        self.main_layout.addLayout(self.summary, stretch=1)



    def create_widget(self, drink):
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setFrameShadow(QFrame.Raised)
        layout = QVBoxLayout(frame)
        hor = QHBoxLayout()
        title_label = QLabel(drink[1])
        hor.addWidget(title_label)
        add_button = QPushButton("Select")
        add_button.clicked.connect(lambda: self.get_item_details(drink))
        hor.addWidget(add_button)
        layout.addLayout(hor)
        return frame

    def get_item_details(self, drink):
        self.item_module = ItemModule(drink)
        self.item_module.confirm_signal.connect(self.item_handler)
        self.item_module.exec_()

    def item_handler(self, signal):
        print(signal)
        self.cur_order.append(signal)
        self.reload_summary()


    def clear_layout(self, layout):
        while layout.count():  # While there are items in the layout
            item = layout.takeAt(0)  # Take the first item
            widget = item.widget()  # Get the widget, if it's a widget
            if widget is not None:
                widget.deleteLater()  # Schedule the widget for deletion
            elif item.layout() is not None:
                self.clear_layout(item.layout())  # Recursively clear sub-layouts

    def reload_summary(self):
        self.clear_layout(self.sum_list)
        idx = 1
        tot = 0
        quantity = 0
        for item in self.cur_order:
            item_desc = QGridLayout()
            item_desc.addWidget(QLabel(item[1]), 0, 0, 1, 3)
            item_desc.addWidget(QLabel(str(item[2])), 0, 4, 1, 1)
            self.sum_list.addLayout(item_desc, idx, 0, 1, 1)
            tot += item[2] * item[3]
            quantity += item[3]
            idx += 1
        self.total_label.setText(f"Total: ${round(tot, 2)}")
        self.total = tot
        self.quantity = quantity
    def close_order(self):
        if self.total == 0:
            return
        cur = self.con.cursor()
        order = cur.execute("INSERT into ORDERS (emp_id, cust_id, quantity, total_price) values (?, ?, ?, ?)", (1, 1, self.quantity, self.total))
        self.con.commit()
        order_id = order.lastrowid
        for item in self.cur_order:
            cur.execute("INSERT into orderItems (order_id, item_id, quantity) values (?, ?, ?)", (order_id, item[0], item[3]))
        self.con.commit()
        cur.close()
        self.sender().parent().accept()




class ItemModule(QDialog):
    confirm_signal = pyqtSignal(list)
    def __init__(self, drink):
        super().__init__()
        self.drink = drink
        self.setWindowTitle(f"{drink[1]}")
        self.setGeometry(300, 300, 500, 400)
        self.layout = QHBoxLayout(self)
        self.image = QLabel(f"{drink[1]} image")
        self.layout.addWidget(self.image)

        self.v_layout = QVBoxLayout()
        self.v_layout.addWidget(QLabel(f"{self.drink[1]}"))
        self.v_layout.addWidget(QLabel(f"${self.drink[4]}"))
        self.quantity = QComboBox()
        self.quantity.addItems(['1', '2', '3', '4', '5'])
        self.cur_quantity = 1
        self.quantity.currentIndexChanged.connect(self.update_quantity)
        self.v_layout.addWidget(self.quantity)
        self.button = QPushButton("Add Item")
        self.button.clicked.connect(self.update_item)
        self.v_layout.addWidget(self.button)
        self.layout.addLayout(self.v_layout)


    def update_quantity(self):
        self.cur_quantity = self.quantity.currentText()

    def update_item(self):
        self.confirm_signal.emit([self.drink[0], self.drink[1], self.drink[4], self.cur_quantity])
        self.sender().parent().accept()





app = QApplication(sys.argv)
dashboard = Dashboard()
dashboard.show()
sys.exit(app.exec_())