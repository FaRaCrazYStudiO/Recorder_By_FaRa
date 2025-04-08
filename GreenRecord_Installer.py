import sys
import os
import subprocess
from PyQt5 import QtWidgets, QtGui, QtCore

from GreenRecord import LANGUAGES

class MainApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        
        self.language = 'ru'  # Default language set to Russian
        self.setWindowTitle("Настройка и Установка Рекордера")
        self.setFixedSize(800, 600)  # Set window size to 800x600
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # Setting a central widget with a rounded border
        self.setStyleSheet("""
            QMainWindow {
                background-color: rgba(46, 46, 46, 200);
                border-radius: 15px;
            }
            QPushButton {
                background-color: #6ebf73;
                border: none;
                border-radius: 10px;
                padding: 10px;
                color: white;
                font-size: 16px;
            }
        """)

        self.init_ui()

    def init_ui(self):
        # Main layout
        layout = QtWidgets.QVBoxLayout()

        # Header
        self.header = QtWidgets.QLabel("Добро пожаловать в приложение Рекордера")
        self.header.setStyleSheet("font-size: 24px; color: #FFFFFF;")
        layout.addWidget(self.header)

        # Language Selection
        self.language_combo = QtWidgets.QComboBox()
        self.language_combo.addItems(["English", "Русский", "Español", "Deutsch"])
        layout.addWidget(self.language_combo)

        # Apply Language Button
        self.apply_language_button = QtWidgets.QPushButton("Применить")
        self.apply_language_button.clicked.connect(self.apply_language)
        layout.addWidget(self.apply_language_button)

        # Documentation Button
        self.doc_button = QtWidgets.QPushButton("Документация")
        self.doc_button.clicked.connect(self.show_documentation)
        layout.addWidget(self.doc_button)
        
        # Support Author Button
        self.support_button = QtWidgets.QPushButton("Поддержать автора")
        self.support_button.clicked.connect(self.support_author)
        layout.addWidget(self.support_button)

        # Install Button
        self.install_button = QtWidgets.QPushButton("Установить Рекордер")
        self.install_button.clicked.connect(self.install_recorder)
        layout.addWidget(self.install_button)

        # Documentation area
        self.documentation_area = QtWidgets.QTextEdit()
        self.documentation_area.setReadOnly(True)
        self.documentation_area.setStyleSheet("background-color: rgba(255, 255, 255, 200); border-radius: 10px;")
        self.documentation_area.setPlainText(self.get_documentation())
        layout.addWidget(self.documentation_area)

        self.setLayout(layout)

    def get_documentation(self):
        if self.language == 'ru':
            return (
                "Документация приложения Рекордера\n\n"
                "1. **Выбор языка:**\n"
                "   Вы можете выбрать язык интерфейса из выпадающего списка. Доступные языки: английский, русский, испанский и немецкий.\n\n"
                "2. **Запись видео и аудио:**\n"
                "   Чтобы начать запись, нажмите кнопку '▷'. Запись видео и аудио начнется через небольшой таймер.\n\n"
                "3. **Остановка записи:**\n"
                "   Для остановки записи нажмите кнопку '□'. Это сохранит все записанное ранее.\n\n"
                "4. **Приостановка записи:**\n"
                "   Вы можете приостановить запись, нажав кнопку '⏸️'. Повторное нажатие продолжит запись.\n\n"
                "5. **Настройки:**\n"
                "   Настройте параметры записи, такие как частота дискретизации аудио и разрешение видео, нажав кнопку '⚙️'. Не забудьте сохранить изменения.\n\n"
                "6. **Документация:**\n"
                "   Нажмите кнопку 'Документация', чтобы открыть это окно и ознакомиться с доступными функциями приложения.\n\n"
                "7. **Поддержка автора:**\n"
                "   Если вам понравилось приложение, нажмите кнопку 'Поддержать автора', чтобы внести свой вклад и помочь в дальнейшем развитии проекта."
            )
        elif self.language == 'en':
            return (
                "Recorder Application Documentation\n\n"
                "1. **Language Selection:**\n"
                "   You can select the interface language from the dropdown. Available languages: English, Russian, Spanish, and German.\n\n"
                "2. **Recording Video and Audio:**\n"
                "   To start recording, press the button '▷'. Video and audio recording will start after a short timer.\n\n"
                "3. **Stopping Recording:**\n"
                "   To stop the recording, press the button '□'. This will save everything recorded so far.\n\n"
                "4. **Pausing Recording:**\n"
                "   You can pause the recording by pressing the button '⏸️'. Pressing it again will resume the recording.\n\n"
                "5. **Settings:**\n"
                "   Adjust recording parameters like audio sampling rate and video resolution by pressing the button '⚙️'. Remember to save your changes.\n\n"
                "6. **Documentation:**\n"
                "   Click the 'Documentation' button to open this window and learn about the functionalities of the application.\n\n"
                "7. **Support Author:**\n"
                "   If you like the application, press the 'Support Author' button to contribute and help develop the project further."
            )
        # Add documentation for other languages, if needed...

    def show_documentation(self):
        QtWidgets.QMessageBox.information(self, "Документация", "Посмотрите на документацию внутри приложения.")

    def support_author(self):
        QtWidgets.QMessageBox.information(self, "Поддержка", "Спасибо за вашу поддержку!")

    def install_recorder(self):
        command = [sys.executable, "-m", "PyInstaller", "--onefile", "--windowed", "--noconsole", "--name=ScreenRecorder", "GreenRecord.py"]
        try:
            result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            QtWidgets.QMessageBox.information(self, "Успех", "Рекордер успешно установлен!")
        except subprocess.CalledProcessError as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при установке:\n{e.stderr.decode()}")

    def apply_language(self):
        selected_language = self.language_combo.currentText()
        if selected_language == "English":
            self.language = 'en'
        elif selected_language == "Русский":
            self.language = 'ru'
        elif selected_language == "Español":
            self.language = 'es'  # Add Spanish support
        elif selected_language == "Deutsch":
            self.language = 'de'  # Add German support
        
        # Update all UI elements based on the selected language
        self.header.setText("Добро пожаловать в приложение Рекордера" if self.language == 'ru' else "Welcome to the Recorder Application")
        self.doc_button.setText(LANGUAGES[self.language]['documentation'])
        self.support_button.setText(LANGUAGES[self.language]['support_author'])
        self.install_button.setText(LANGUAGES[self.language]['install_recorder'])
        self.documentation_area.setPlainText(self.get_documentation())  # Update documentation
        self.apply_language_button.setText("Применить")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_app = MainApp()
    main_app.show()
    sys.exit(app.exec_())