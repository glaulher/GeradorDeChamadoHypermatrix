import json
import os
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtWidgets import QPlainTextEdit, QMenu, QAction
from PyQt5.QtGui import QTextCursor
from spellchecker import SpellChecker
from utils.spell_highlighter import SpellHighlighter
from utils.resource import externalPath

class SpellCheckPlainTextEdit(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.highlighter = SpellHighlighter(self.document())
        self.textChanged.connect(self._delayedCheck)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._checkSpelling)
        self.spell = SpellChecker(language='pt')
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_spellcheck_menu)

        with open(externalPath('data/correcoes_personalizadas.json'), 'r',encoding='utf-8') as file:
            self.custom_corrections = json.load(file)
        

    def load_custom_corrections(self, path):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _delayedCheck(self):
        self._timer.start(1000)

    def _checkSpelling(self):
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
            candidates = list(self.spell.candidates(word))
            suggestions = [correction] + [s for s in candidates if s != correction]

        if suggestions:
            menu = QMenu(self)
            for suggestion in suggestions:
                action = QAction(suggestion, self)
                action.triggered.connect(lambda _, s=suggestion, c=QTextCursor(cursor): self.replace_word(c, s))
                menu.addAction(action)
            menu.exec_(self.mapToGlobal(point))

    def replace_word(self, cursor: QTextCursor, suggestion: str):
        cursor.beginEditBlock()
        cursor.removeSelectedText()
        cursor.insertText(suggestion)
        cursor.endEditBlock()