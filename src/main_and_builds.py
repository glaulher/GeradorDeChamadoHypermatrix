'''
pip install PyQt5
pip install pyinstaller ou pip install nuitka ordered-set zstandard
pip install pyperclip
pip install pandas
python -m pip install requests
pip install jinja2
pip install pylint
pip install pyspellchecker
pip install python-dotenv


pyinstaller --clean --onefile --noconsole `
--icon=assets/logo.ico `
--add-data "data/recipients.json;data" `
--add-data "styles/sidebar.qss;styles" `
--add-data "styles/ui.qss;styles" `
--add-data "ui/email_chamados.html;ui" `
--add-data "utils/jre1.8.0_202;utils/jre1.8.0_202" `
--add-data "assets/logo_small.ico;assets" `
main_and_builds.py

pyinstaller --clean --onefile --noconsole `
--icon=assets/logo.ico `
--add-data "data/recipients.json;data" `
--add-data "styles/sidebar.qss;styles" `
--add-data "styles/ui.qss;styles" `
--add-data "ui/email_chamados.html;ui" `
--add-data "assets/logo_small.ico;assets" `
--add-data "spellchecker/resources/pt.json.gz;spellchecker/resources" `
--add-data "../.env;." `
main_and_builds.py



nuitka `
--standalone `
--enable-plugin=pyqt5 `
--windows-console-mode=disable `
--windows-icon-from-ico=assets/logo.ico `
--include-data-file=data/recipients.json=data/recipients.json `
--include-data-file=styles/sidebar.qss=styles/sidebar.qss `
--include-data-file=styles/ui.qss=styles/ui.qss `
--include-data-file=ui/email_chamados.html=ui/email_chamados.html `
--include-data-dir=utils/jre1.8.0_202=utils/jre1.8.0_202 `
--include-data-file=assets/logo_small.ico=assets/logo_small.ico `
--onefile `
main_and_builds.py

'''


import sys

from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from utils.resource import internalPath

if __name__ == '__main__':   
    app = QApplication(sys.argv)
    with open(internalPath("styles/ui.qss"), "r") as f:app.setStyleSheet(f.read())
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
