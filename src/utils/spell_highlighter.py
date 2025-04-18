import logging
import re

from PySide6.QtGui import QColor, QSyntaxHighlighter, QTextCharFormat

from spellchecker import SpellChecker


class SpellHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.spell = SpellChecker(language="pt")
        self.errors = []
        self.sensitive_words = set()

    def highlightBlock(self, text):  # pylint: disable=invalid-name
        try:
            words = re.findall(r"\b\w+\b", text)
            for word in words:
                is_known_lower = word.lower() in self.spell
                is_sensitive_match = word in self.sensitive_words

                if not is_known_lower or (
                    word.lower() in self.spell
                    and not is_sensitive_match
                    and word.upper() in self.sensitive_words
                ):
                    start = text.find(word)

                    if start >= 0:
                        fmt = QTextCharFormat()
                        fmt.setUnderlineColor(QColor("red"))
                        fmt.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)
                        self.setFormat(start, len(word), fmt)
        except ValueError as err:
            logging.exception("Error in highlightBlock: %s", err)

    def check_text(self, text):
        words = re.findall(r"\b\w+\b", text)

        self.errors = self.spell.unknown(words)
        self.rehighlight()
