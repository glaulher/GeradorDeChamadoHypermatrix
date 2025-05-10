"""
pip install PySide6
pip install pyinstaller ou pip install nuitka ordered-set zstandard
pip install pyperclip
pip install pandas
pip install requests
pip install jinja2
pip install pylint
pip install pyspellchecker
pip install python-dotenv



pyinstaller --clean --onefile --noconsole `
--icon=assets/logo.ico `
--add-data "data/recipients.json;data" `
--add-data "styles/sidebar.qss;styles" `
--add-data "styles/ui.qss;styles" `
--add-data "styles/light.qss;styles" `
--add-data "styles/dark.qss;styles" `
--add-data "ui/email_chamados.html;ui" `
--add-data "assets/logo_small.ico;assets" `
--add-data "spellchecker/resources/pt.json.gz;spellchecker/resources" `
--add-data "../.env;." `
main_and_builds.py





pyinstaller \
--add-data=data/recipients.json:data \
--add-data=styles/sidebar.qss:styles \
--add-data=styles/ui.qss:styles \
--add-data=styles/light.qss:styles \
--add-data=styles/dark.qss:styles \
--add-data=ui/email_chamados.html:ui \
--add-data=assets/logo_small.ico:assets \
--add-data=spellchecker/resources/pt.json.gz:spellchecker/resources \
--add-data=../.env:. \
main_and_builds.py

"""

import sys

from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow
from ui.splash_screen import SplashScreen
from utils.resource import internal_path
from utils.theme_config import load_theme_name

theme_name = load_theme_name()


def main():
    app = QApplication(sys.argv)

    with open(internal_path("styles/ui.qss"), "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())

    splash = SplashScreen()
    splash.show()
    splash.start()

    def launch_main():
        window = MainWindow()
        window.show()
        splash.close()

    splash.finished.connect(launch_main)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
