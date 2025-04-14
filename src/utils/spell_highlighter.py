from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor
from spellchecker import SpellChecker
import re

class SpellHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.spell = SpellChecker(language='pt')
        self.errors = []

    def highlightBlock(self, text):
        words = re.findall(r'\b\w+\b', text)
        for word in words:
            if word.lower() not in self.spell:
                start = text.find(word)
                if start >= 0:
                    fmt = QTextCharFormat()
                    fmt.setUnderlineColor(QColor("red"))
                    fmt.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)
                    self.setFormat(start, len(word), fmt)

    def checkText(self, text):
        words = re.findall(r'\b\w+\b', text)
        self.errors = self.spell.unknown(words)
        self.rehighlight()
        
        
        
        
# import os
# from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor
# from spellchecker import SpellChecker
# import re

# from utils.resource import internalPath

# class SpellHighlighter(QSyntaxHighlighter):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         dictionary_path = internalPath('utils/pt.json.gz')
#         dictionary_path = os.path.normpath(dictionary_path)       
    
#         self.spell = SpellChecker(language=None, local_dictionary=dictionary_path)
#         self.errors = []

#     def highlightBlock(self, text):
#         words = re.findall(r'\b\w+\b', text)
#         for word in words:
#             if word.lower() not in self.spell:
#                 start = text.find(word)
#                 if start >= 0:
#                     fmt = QTextCharFormat()
#                     fmt.setUnderlineColor(QColor("red"))
#                     fmt.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)
#                     self.setFormat(start, len(word), fmt)

#     def checkText(self, text):
#         words = re.findall(r'\b\w+\b', text)
#         self.errors = self.spell.unknown(words)
#         self.rehighlight()