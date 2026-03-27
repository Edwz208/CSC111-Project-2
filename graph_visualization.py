from __future__ import annotations

from user_graph import load_user_graph

from PySide6.QtWidgets import*
from PySide6.QtGui import QFont, QPixmap
import sys
import networkx as nx
import matplotlib.pyplot as plt


class MainWindow(QMainWindow):
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
        self.title.setStyleSheet('color: #FC809F')
        self.title.setFont(QFont('Comic Sans MS', 32))
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

    def load_graph(self) -> None:

        list_of_anime = self.anime_list_input.text().split(', ')

        # HARD CODED VALUES FOR LIMITS RN
        try:
            # adds button to window
            inputted_user_graph = load_user_graph('profiles.csv', 'animes.csv')
            user_recs = inputted_user_graph.recommend_anime(list_of_anime, 50, 20)

            for anime in user_recs:
                user_recommendations = QLabel(anime)
                user_recommendations.setFont(QFont('Helvetica', 8))
                self.main_layout.addWidget(user_recommendations)

            # visualize using networkx --> WILL MAKE BETTER LOOKING
            g = inputted_user_graph.to_networkx(200)
            nx.draw(g, with_labels=True, node_color='pink', edge_color='#FC809F', node_size=1200, font_size=12)
            plt.savefig('data/graph.png')

            btn_visualize = QPushButton('Visualize recommendations')
            self.main_layout.addWidget(btn_visualize)
            btn_visualize.clicked.connect(self._visualize)

        except KeyError:
            error_dialog = QErrorMessage()
            error_dialog.showMessage('Your input was not accepted. Please try again.')
            error_dialog.exec()

        except ValueError:
            error_dialog = QErrorMessage()
            error_dialog.showMessage('Your input was not accepted. Please try again.')
            error_dialog.exec()


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
    window = MainWindow()
    window.show()
    sys.exit(app.exec())