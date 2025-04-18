# import re

# from PySide6.QtGui import QColor, QSyntaxHighlighter, QTextCharFormat

# from spellchecker import SpellChecker


# class SpellHighlighter(QSyntaxHighlighter):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.spell = SpellChecker(language="pt")
#         self.errors = []
#         self.sensitive_words = set()

#     def highlight_block(self, text):
#         words = re.findall(r"\b\w+\b", text)
#         for word in words:
#             is_known_lower = word.lower() in self.spell
#             is_sensitive_match = word in self.sensitive_words

#             if not is_known_lower or (
#                 word.lower() in self.spell
#                 and not is_sensitive_match
#                 and word.upper() in self.sensitive_words
#             ):
#                 start = text.find(word)

#                 if start >= 0:
#                     fmt = QTextCharFormat()
#                     fmt.setUnderlineColor(QColor("red"))
#                     fmt.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)
#                     self.setFormat(start, len(word), fmt)

#     def check_text(self, text):
#         words = re.findall(r"\b\w+\b", text)
#         self.errors = self.spell.unknown(words)
#         self.rehighlight()


import json
from resource import external_path

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QAction, QColor, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import QApplication, QMainWindow, QMenu, QTextEdit

from spellchecker import SpellChecker


class HighlighterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Highlighter com SpellChecker")

        # Configuração do editor de texto
        self.text_edit = QTextEdit(self)
        self.setCentralWidget(self.text_edit)
        self.text_edit.textChanged.connect(self.highlight_errors)
        self.text_edit.setContextMenuPolicy(Qt.CustomContextMenu)
        self.text_edit.customContextMenuRequested.connect(self.show_context_menu)

        # Configuração do SpellChecker e dicionário personalizado
        self.spellchecker = SpellChecker()
        self.load_personal_dict("../data/dicionario_personalizado.txt")
        self.load_custom_corrections("../data/correcoes_personalizadas.json")

    def load_personal_dict(self, path):
        try:
            with open(path, "r", encoding="utf-8") as file:
                personal_words = file.read().splitlines()
                self.spellchecker.word_frequency.load_words(personal_words)
        except FileNotFoundError:
            print(f"Arquivo de dicionário personalizado não encontrado: {path}")

    def load_custom_corrections(self, path):
        try:
            with open(path, "r", encoding="utf-8") as file:
                self.custom_corrections = json.load(file)
        except FileNotFoundError:
            print(f"Arquivo de correções personalizadas não encontrado: {path}")

    def highlight_errors(self):
        try:
            self.text_edit.textChanged.disconnect()

            text = self.text_edit.toPlainText()
            words = text.split()
            incorrect_words = self.spellchecker.unknown(words)

            cursor = self.text_edit.textCursor()
            cursor.select(QTextCursor.Document)
            cursor.setCharFormat(QTextCharFormat())

            for word_index, word in enumerate(words):
                if word in incorrect_words:
                    fmt = QTextCharFormat()
                    fmt.setBackground(QColor("yellow"))
                    fmt.setForeground(QColor("red"))

                    pos = text.find(word, sum(len(w) + 1 for w in words[:word_index]))
                    cursor.setPosition(pos)
                    cursor.movePosition(
                        QTextCursor.Right, QTextCursor.KeepAnchor, len(word)
                    )
                    cursor.setCharFormat(fmt)

            self.text_edit.textChanged.connect(self.highlight_errors)
        except Exception as e:
            print(f"Erro ao destacar palavras: {e}")
            self.text_edit.textChanged.connect(self.highlight_errors)

            # Aplicar correções personalizadas
            for word, correction in self.custom_corrections.items():
                text = text.replace(word, correction)
                self.text_edit.setPlainText(text)

            self.text_edit.textChanged.connect(self.highlight_errors)
        except Exception as e:
            print(f"Erro ao destacar palavras: {e}")
            self.text_edit.textChanged.connect(self.highlight_errors)

    def show_context_menu(self, point: QPoint):
        # # Criar um menu de contexto
        # context_menu = QMenu(self)
        # clear_format_action = context_menu.addAction("Limpar formatação")

        # # Conectar ações
        # clear_format_action.triggered.connect(self.clear_format)

        # # Exibir o menu
        # context_menu.exec(self.text_edit.mapToGlobal(point))

        cursor = self.text_edit.cursorForPosition(point)

        cursor.select(QTextCursor.WordUnderCursor)
        word = cursor.selectedText().lower()

        if not word or word in self.spellchecker:
            return

        suggestions = []

        if word in self.custom_corrections:
            suggestions = [self.custom_corrections[word]]
        else:
            correction = self.spellchecker.correction(word)
            candidates = list(self.spellchecker.candidates(word) or [])
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

            menu.exec_(self.text_edit.mapToGlobal(point))

    def clear_format(self):
        cursor = self.text_edit.textCursor()
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(QTextCharFormat())

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
        path = external_path("data/dicionario_personalizado.txt")
        # word = word.lower()


if __name__ == "__main__":
    app = QApplication([])
    window = HighlighterApp()
    window.resize(600, 400)
    window.show()
    app.exec()
