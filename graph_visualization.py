from __future__ import annotations

import user_graph

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QFormLayout, QLineEdit
from PySide6.QtGui import QFont, QPixmap
import sys
import networkx as nx
import matplotlib.pyplot as plt

class Window(QMainWindow):
    """The interactive text shell for the anime recommendation system.
    """

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle('AniRecs')
        self.setGeometry(100, 100, 500, 400)

        self._setup_ui()
        self._setup_events()

    def _setup_ui(self) -> None:
        # container
        self.central_widget = QWidget(self)

        # layout
        self.main_layout = QVBoxLayout()

        # labels
        self.title = QLabel('Anime Recommendations')
        self.title.setStyleSheet('color: pink')
        self.title.setFont(QFont('Times New Roman', 32))
        self.main_layout.addWidget(self.title)

        self.instructions = QLabel('Enter a list of at least five anime to receive personalized recommendations!')
        self.main_layout.addWidget(self.instructions)

        # interactive form
        self.form_layout = QFormLayout()
        self.anime_list_input = QLineEdit()
        self.form_layout.addRow('Your list:', self.anime_list_input)
        self.btn_recommendations = QPushButton('Curate recommendations')
        self.btn_clear = QPushButton('Clear')

        self.main_layout.addLayout(self.form_layout)
        self.main_layout.addWidget(self.btn_recommendations)
        self.main_layout.addWidget(self.btn_clear)

        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)

    def _setup_events(self) -> None:
        self.btn_recommendations.clicked.connect(self.load_graph)
        self.btn_clear.clicked.connect(self.clear_form)

    # MAKE GRAPH PRETTIER LOOKING
    def load_graph(self) -> None:
        # loads a sample graph
        list_of_anime = self.anime_list_input.text().split(', ')
        print(list_of_anime)



        # nx.draw(my_graph)
        plt.savefig('data/graph.png')

        # adds button to window
        self.btn_visualize = QPushButton('Visualize recommendations')
        self.main_layout.addWidget(self.btn_visualize)
        self.btn_visualize.clicked.connect(self._visualize)

    def _visualize(self) -> None:
        new_label = QLabel(self)
        image = QPixmap('data/graph.png')
        self.main_layout.addWidget(new_label)
        new_label.setPixmap(image)

    def clear_form(self) -> None:
        self.anime_list_input.clear()

def load_stylesheet(app: QApplication) -> None:
    with open('data/style.qss', 'r') as file:
        qss = file.read()
        app.setStyleSheet(qss)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    load_stylesheet(app)
    window = Window()
    window.show()
    sys.exit(app.exec())