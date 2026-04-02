"""CSC111 Winter 2026 Project 2: Anime Recommendations GUI

Module Description
==================
This module handles the graphical user interface for the anime recommendations app.
It also displays the graphs created in graph_visualization.

This file is Copyright (c) 2026 Lily Annelise Canete-Goodine, Parmida Arab, Miray Ozdemir, Edwin Zeng
"""

from __future__ import annotations
from typing import Any
from PySide6.QtWidgets import (QMainWindow, QLabel, QPushButton, QErrorMessage, QTabWidget,
                               QWidget, QVBoxLayout, QFormLayout, QLineEdit, QApplication, QListWidget)
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtCore import QRect

import attribute_graph
import user_graph
import user_rating_graph
import graph_visualization
import main


class MainWindow(QMainWindow):
    """The interactive text shell for the anime recommendation system.

    Instance Attributes
    - main_layout: the main layout for the window
    - anime_input: the input for the user's list of anime
    - anime_ranking: the (optional) input for the user's anime list rankings
    - num_recs: the (optional) input for the number of recommendations the user wants to return
    - btn_clear: button to clear the inputs and recommendations of the program
    - output: the list widget containing anime recommendations
    - graph_tab: the tab widget to display the visualizations of the graphs
    """
    main_layout: QVBoxLayout
    anime_input: QLineEdit
    anime_ranking: QLineEdit
    num_recs: QLineEdit
    btn_clear: QPushButton
    output: QListWidget
    graph_tab: QTabWidget

    def __init__(self) -> None:
        """Initializes the main window.
        """
        super().__init__()
        self.setWindowTitle('Recommendinator')
        self.setGeometry(100, 100, 500, 700)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Initializes the containers, labels, and buttons for the main window.
        """
        # container
        central_widget = QWidget(self)

        # layout
        self.main_layout = QVBoxLayout()
        central_widget.setLayout(self.main_layout)

        # wrapper
        wrapper = QVBoxLayout()
        wrapper.setGeometry(QRect(0, 0, 200, 50))

        # labels & instructions
        title = QLabel('Recommendinator')
        title.setStyleSheet('color: #FC809F')
        title.setFont(QFont('Allura', 32))
        wrapper.addWidget(title)

        instructions1 = QLabel('Enter a list of 3-10 anime to receive personalized recommendations!')
        instructions1.setFont(QFont('Allura', 11))
        wrapper.addWidget(instructions1)
        example1 = QLabel('ex. Haikyuu!!, Kimetsu no Yaiba, Shingeki no Kyojin')
        example1.setFont(QFont('Allura', 8))
        wrapper.addWidget(example1)

        instructions2 = QLabel(
            'Optional: Rank each of your inputted anime from 1 (worst) to 10 (best) for more accurate recommendations!')
        instructions2.setFont(QFont('Allura', 11))
        wrapper.addWidget(instructions2)
        instructions3 = QLabel('Note: Please enter whole numbers for rankings. Decimals will be truncated.')
        instructions3.setFont(QFont('Allura', 8))
        wrapper.addWidget(instructions3)
        example2 = QLabel('ex. 8, 1, 10')
        example2.setFont(QFont('Allura', 8))
        wrapper.addWidget(example2)

        # interactive form
        form_layout = QFormLayout()
        self.anime_input = QLineEdit()
        form_layout.addWidget(self.anime_input)
        form_layout.addRow('Anime:', self.anime_input)
        self.anime_ranking = QLineEdit()
        form_layout.addRow('Rankings (1-10):', self.anime_ranking)
        form_layout.addWidget(self.anime_ranking)
        self.num_recs = QLineEdit()
        form_layout.addWidget(self.num_recs)
        self.num_recs.setFixedSize(50, 30)
        form_layout.addRow('Number of recommendations (default: 20, max: 100):', self.num_recs)

        # buttons
        btn_recommendations = QPushButton('Curate recommendations')
        btn_recommendations.clicked.connect(self.load_recs)

        self.btn_clear = QPushButton('Clear all')
        self.btn_clear.clicked.connect(self.clear_form)

        self.main_layout.addLayout(wrapper)
        self.main_layout.addLayout(form_layout)
        self.main_layout.addWidget(btn_recommendations)
        self.main_layout.addWidget(self.btn_clear)

        self.output = QListWidget()

        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)

    def load_recs(self) -> None:
        """Event generated when user clicks 'Curate recommendations.' Calls on recommendation methods
        in user_graph, user_rating_graph, and attribute_graph.
        """
        list_of_anime = self.clean_inputs()[0]
        anime_to_ranking = self.clean_inputs()[1]
        num_recs = self.clean_inputs()[2]
        if self.anime_ranking.text().split(', ') == ['']:
            try:
                users = user_graph.load_user_graph('profiles.csv', 'animes.csv')
                user_recs = users.recommend_anime(list_of_anime, 200, 100)

                attributes = attribute_graph.load_the_graph('animes.csv')
                attr_recs = attributes.recommend_new_show(list_of_anime, 200)

                final_recs = main.combined_recommendation(user_recs, attr_recs, num_recs)
                self._print_recs(final_recs)

                self.load_graph('user', users, list_of_anime, anime_to_ranking)
                self.load_graph('anime', attributes, list_of_anime, anime_to_ranking)

                btn_visualize = QPushButton('Visualize recommendations')
                self.main_layout.addWidget(btn_visualize)
                btn_visualize.clicked.connect(self._visualize)
            except ValueError:
                self.call_error()
            except KeyError:
                self.call_error()
        elif len(self.anime_ranking.text().split(', ')) == len(list_of_anime):
            try:
                for anime in self.anime_input.text().split(', '):
                    anime_to_ranking[anime] = (
                        int(self.clean_inputs()[3][list_of_anime.index(anime)]))
                users = user_rating_graph.load_user_graph('reviews.csv', 'animes.csv')
                attributes = attribute_graph.load_the_graph('animes.csv')
                final_recs = main.call_graphs_and_transform(attributes, users, anime_to_ranking, num_recs)
                self._print_recs(final_recs)

                self.load_graph('weighted_user', users, list_of_anime, anime_to_ranking)
                self.load_graph('anime', attributes, list_of_anime, anime_to_ranking)

                btn_visualize = QPushButton('Visualize recommendations')
                self.main_layout.addWidget(btn_visualize)
                btn_visualize.clicked.connect(self._visualize)

            except ValueError:
                self.call_error()
            except KeyError:
                self.call_error()
        else:
            error_dialog = QErrorMessage()
            error_dialog.showMessage(
                'The number of inputted rankings does not match the number of anime. Please try again.')
            error_dialog.exec()

    @staticmethod
    def load_graph(type_graph: str, graph_used: Any, list_of_anime: list[str], anime_to_ranking: dict[str, int]) \
            -> None:
        """Creates visualization of either a user_rating, user, or attribute based graph.
        """
        if type_graph == 'weighted_user':
            g = user_rating_graph.load_custom_user_graph(20, graph_used, anime_to_ranking)
            weights = list(g.get_top_similar_users('inputted_user', 20).values())
            user_output = graph_visualization.output_graph(g.to_networkx(500), 'user', weights, True)
            user_output.write_image('data/user_graph.png')
        elif type_graph == 'user':
            g = user_graph.load_custom_user_graph(20, graph_used, list_of_anime)
            user_output = graph_visualization.output_graph(g.to_networkx(500), 'user', [], False)
            user_output.write_image('data/user_graph.png')
        else:
            g = attribute_graph.load_custom_attribute_graph(20, graph_used, list_of_anime)
            user_output = graph_visualization.output_graph(g.to_networkx(500), 'genre', [], False)
            user_output.write_image('data/attribute_graph.png')

    def _visualize(self) -> None:
        """Displays graphs created by load_graph when 'Visualize recommendations' is clicked.
        """
        self.graph_tab = QTabWidget()
        widget1 = QWidget()
        shell = QVBoxLayout()
        widget1.setLayout(shell)
        user_graph_label = QLabel(self)
        image1 = QPixmap('data/user_graph.png')
        user_graph_label.setPixmap(image1)
        shell.addWidget(user_graph_label)
        self.graph_tab.addTab(widget1, 'User Graph')

        widget2 = QWidget()
        shell2 = QVBoxLayout()
        widget2.setLayout(shell2)
        attr_graph_label = QLabel(self)
        image3 = QPixmap('data/attribute_graph.png')
        attr_graph_label.setPixmap(image3)
        shell2.addWidget(attr_graph_label)
        self.graph_tab.addTab(widget2, 'Attribute Graph')

        self.graph_tab.show()
        button = self.sender()
        if self.btn_clear.clicked.connect(self.clear_form):
            button.deleteLater()

    def _print_recs(self, recs: list[str]) -> None:
        """Outputs recommendations to the user in the main window.
        """
        self.main_layout.addWidget(self.output)
        for anime in recs:
            self.output.addItem(anime)

    def clean_inputs(self) -> list:
        """Cleans the string based user inputs into suitable data types to be used in the user_graph,
        user_rating_graph and attribute_graph.
        """
        list_of_anime = self.anime_input.text().split(', ').copy()
        list_of_rankings = self.anime_ranking.text().split(', ').copy()
        anime_to_ranking = {}

        if self.num_recs.text() == '':
            num_recs = 20
        elif int(self.num_recs.text()) > 100:
            num_recs = 100
        else:
            num_recs = int(self.num_recs.text())

        if not (1 <= all(list(list_of_rankings)) <= 10) and not self.anime_ranking.text().split(', ') == ['']:
            error_dialog = QErrorMessage()
            error_dialog.showMessage(
                'One (or more) of your rankings is not in the accepted range. Please try again.')
            error_dialog.exec()

        return [list_of_anime, anime_to_ranking, num_recs, list_of_rankings]

    def clear_form(self) -> None:
        """Clears all inputs and recommendations for the user.
        """
        self.anime_input.clear()
        self.anime_ranking.clear()
        self.num_recs.clear()
        self.output.clear()

    @staticmethod
    def call_error() -> None:
        """Outputs a pre-written error message to the user.
        """
        error_dialog = QErrorMessage()
        error_dialog.showMessage('We do not recognize one (or more) of your inputs. Please try again.')
        error_dialog.exec()

    @staticmethod
    def load_stylesheet(app: QApplication) -> None:
        """Customizes the buttons of the main window.
        """
        with open('data/style.qss', 'r') as file:
            qss = file.read()
            app.setStyleSheet(qss)


if __name__ == "__main__":
    import python_ta.contracts

    python_ta.contracts.check_all_contracts()

    import doctest

    doctest.testmod()

    import python_ta

    python_ta.check_all(config={
        'max-line-length': 120,
        'extra-imports': ['user_graph', 'user_rating_graph', 'attribute_graph', 'graph_visualization',
                          'main', 'PySide6.QtWidgets.QMainWindow', 'PySide6.QtWidgets.QLabel',
                          'PySide6.QtWidgets.QPushButton', 'PySide6.QtWidgets.QErrorMessage',
                          'PySide6.QtWidgets.QTabWidget', 'PySide6.QtWidgets.QWidget', 'PySide6.QtWidgets.QVBoxLayout',
                          'PySide6.QtWidgets.QFormLayout', 'PySide6.QtWidgets.QLineEdit',
                          'PySide6.QtWidgets.QApplication', 'PySide6.QtWidgets.QListWidget', 'PySide6.QtGui.QFont',
                          'PySide6.QtGui.QPixmap', 'PySide6.QtCore.QRect'],
        'max-nested-blocks': 4
    })
