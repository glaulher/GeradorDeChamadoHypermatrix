import json
import os

from PySide6.QtCore import QPoint, Qt, QTimer
from PySide6.QtGui import QAction, QTextCursor
from PySide6.QtWidgets import QMenu, QPlainTextEdit

from spellchecker import SpellChecker
from utils.resource import externalPath
from utils.spell_highlighter import SpellHighlighter


class SpellCheckPlainTextEdit(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.spell = SpellChecker(language="pt")
        self.highlighter = SpellHighlighter(self.document())
        self.load_personal_dict(externalPath("data/dicionario_personalizado.txt"))

        self.textChanged.connect(self._delayed_check)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._check_spelling)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_spellcheck_menu)

        with open(
            externalPath("data/correcoes_personalizadas.json"), "r", encoding="utf-8"
        ) as file:
            self.custom_corrections = json.load(file)

    def load_personal_dict(self, path):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                words = [line.strip() for line in f if line.strip()]

                self.spell = SpellChecker(language="pt")
                self.spell.word_frequency.load_words([w.lower() for w in words])
                self.highlighter.sensitive_words = set(words)

                self.highlighter.spell = self.spell

    def load_custom_corrections(self, path):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _delayed_check(self):
        self._timer.start(1000)

    def _check_spelling(self):
        text = self.toPlainText()
        self.highlighter.checkText(text)

    def show_spellcheck_menu(self, point: QPoint):
        cursor = self.cursorForPosition(point)
        cursor.select(QTextCursor.WordUnderCursor)
        word = cursor.selectedText().lower()

        if not word or word in self.spell:
            return

        suggestions = []

        if word in self.custom_corrections:
            suggestions = [self.custom_corrections[word]]
        else:
            correction = self.spell.correction(word)
            candidates = list(self.spell.candidates(word) or [])
            suggestions = [correction] + [s for s in candidates if s != correction]

        if suggestions:
            menu = QMenu(self)
            for suggestion in suggestions:
                action = QAction(suggestion, self)
                action.triggered.connect(
                    lambda _, s=suggestion, c=QTextCursor(cursor): self.replace_word(
                        c, s
                    )
                )
                menu.addAction(action)

            menu.addSeparator()
            add_action = QAction(f"Adicionar '{word}' ao dicionário", self)
            add_action.triggered.connect(
                lambda _, w=word: self.add_to_custom_dictionary(w)
            )
            menu.addAction(add_action)

            menu.exec_(self.mapToGlobal(point))

    def replace_word(self, cursor: QTextCursor, suggestion: str):
        original = cursor.selectedText()

        if original.isupper():
            suggestion = suggestion.upper()
        elif original.istitle():
            suggestion = suggestion.capitalize()
        elif original.islower():
            suggestion = suggestion.lower()

        cursor.beginEditBlock()
        cursor.removeSelectedText()
        cursor.insertText(suggestion)
        cursor.endEditBlock()

    def add_to_custom_dictionary(self, word):
        path = externalPath("data/dicionario_personalizado.txt")
        # word = word.lower()

        with open(path, "r", encoding="utf-8") as f:
            words = {line.strip() for line in f if line.strip()}

        if word not in words:
            with open(path, "a", encoding="utf-8") as file:
                file.write(f"{word}\n")

        self.load_personal_dict(path)
        self.highlighter.checkText(self.toPlainText())
