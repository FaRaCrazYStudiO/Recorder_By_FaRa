import sys
import cv2
import numpy as np
import pyautogui
import os
import sounddevice as sd
from scipy.io.wavfile import write
from PyQt5 import QtWidgets, QtGui, QtCore

# Default settings
DEFAULT_AUDIO_FS = 44100  # Default sample rate
FALLBACK_AUDIO_FS = 22050  # Alternative sample rate if the default fails
DEFAULT_VIDEO_RESOLUTION = (1920, 1080)  # Video resolution
DEFAULT_OUTPUT_DIR = os.path.expanduser("~")  # Default output directory

# Локализация
LANGUAGES = {
    'en': {
        'settings_title': "Settings",
        'output_directory': "Output Directory:",
        'browse': "Browse",
        'audio_sample_rate': "Audio Sample Rate:",
        'video_resolution': "Video Resolution (Width x Height):",
        'save': "Save",
        'record': "▷",
        'stop': "□",
        'pause': "⏸️",
        'settings': "⚙️",
        'countdown_text': "{}",
        'pause_resume': "▶️",
        'resume': "⏸️"
    },
    'ru': {
        'settings_title': "Настройки",
        'output_directory': "Директория для сохранения:",
        'browse': "Обзор",
        'audio_sample_rate': "Частота дискретизации аудио:",
        'video_resolution': "Разрешение видео (Ширина x Высота):",
        'save': "Сохранить",
        'record': "▷",
        'stop': "□",
        'pause': "⏸️",
        'settings': "⚙️",
        'countdown_text': "{}",
        'pause_resume': "▶️",
        'resume': "⏸️"
    },
    # Испанский и немецкий языки
    'es': {
        'settings_title': "Configuraciones",
        'output_directory': "Directorio de salida:",
        'browse': "Buscar",
        'audio_sample_rate': "Tasa de muestreo de audio:",
        'video_resolution': "Resolución de Video (Ancho x Alto):",
        'save': "Guardar",
        'record': "▷",
        'stop': "□",
        'pause': "⏸️",
        'settings': "⚙️",
        'countdown_text': "{}",
        'pause_resume': "▶️",
        'resume': "⏸️"
    },
    'de': {
        'settings_title': "Einstellungen",
        'output_directory': "Ausgabeverzeichnis:",
        'browse': "Durchsuchen",
        'audio_sample_rate': "Audio-Abtastrate:",
        'video_resolution': "Videoauflösung (Breite x Höhe):",
        'save': "Speichern",
        'record': "▷",
        'stop': "□",
        'pause': "⏸️",
        'settings': "⚙️",
        'countdown_text': "{}",
        'pause_resume': "▶️",
        'resume': "⏸️"
    },
}

class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, language):
        super().__init__()
        self.language = language
        self.setWindowTitle(LANGUAGES[self.language]['settings_title'])
        
        self.layout = QtWidgets.QVBoxLayout()
        
        # Директория для сохранения
        self.output_dir_label = QtWidgets.QLabel(LANGUAGES[self.language]['output_directory'])
        self.output_dir_input = QtWidgets.QLineEdit(DEFAULT_OUTPUT_DIR)
        self.browse_button = QtWidgets.QPushButton(LANGUAGES[self.language]['browse'])
        self.browse_button.clicked.connect(self.browse_output_directory)
        
        self.layout.addWidget(self.output_dir_label)
        self.layout.addWidget(self.output_dir_input)
        self.layout.addWidget(self.browse_button)
        
        # Качество аудио
        self.audio_fs_label = QtWidgets.QLabel(LANGUAGES[self.language]['audio_sample_rate'])
        self.audio_fs_input = QtWidgets.QSpinBox()
        self.audio_fs_input.setValue(DEFAULT_AUDIO_FS)
        self.layout.addWidget(self.audio_fs_label)
        self.layout.addWidget(self.audio_fs_input)

        # Разрешение видео
        self.video_res_label = QtWidgets.QLabel(LANGUAGES[self.language]['video_resolution'])
        self.video_width_input = QtWidgets.QSpinBox()
        self.video_height_input = QtWidgets.QSpinBox()
        self.video_width_input.setValue(DEFAULT_VIDEO_RESOLUTION[0])
        self.video_height_input.setValue(DEFAULT_VIDEO_RESOLUTION[1])
        
        width_layout = QtWidgets.QHBoxLayout()
        width_layout.addWidget(self.video_width_input)
        width_layout.addWidget(QtWidgets.QLabel("x"))
        width_layout.addWidget(self.video_height_input)
        
        self.layout.addWidget(self.video_res_label)
        self.layout.addLayout(width_layout)

        # Язык
        self.language_label = QtWidgets.QLabel("Language:")
        self.language_combobox = QtWidgets.QComboBox()
        self.language_combobox.addItems(list(LANGUAGES.keys()))
        self.language_combobox.setCurrentText(self.language)
        self.language_combobox.currentTextChanged.connect(self.update_language)
        
        self.layout.addWidget(self.language_label)
        self.layout.addWidget(self.language_combobox)

        self.save_button = QtWidgets.QPushButton(LANGUAGES[self.language]['save'])
        self.save_button.clicked.connect(self.accept)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

    def browse_output_directory(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if folder:
            self.output_dir_input.setText(folder)

    def get_settings(self):
        return {
            'audio_fs': self.audio_fs_input.value(),
            'video_resolution': (self.video_width_input.value(), self.video_height_input.value()),
            'output_dir': self.output_dir_input.text(),
            'language': self.language_combobox.currentText()
        }

    def update_language(self):
        self.language = self.language_combobox.currentText()
        self.setWindowTitle(LANGUAGES[self.language]['settings_title'])
        self.output_dir_label.setText(LANGUAGES[self.language]['output_directory'])
        self.audio_fs_label.setText(LANGUAGES[self.language]['audio_sample_rate'])
        self.video_res_label.setText(LANGUAGES[self.language]['video_resolution'])
        self.save_button.setText(LANGUAGES[self.language]['save'])
        self.browse_button.setText(LANGUAGES[self.language]['browse'])
        self.language_label.setText("Language:")

class CountdownWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(0, 0, 400, 400)  # Set a fixed size
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        # Create a label for showing the countdown
        self.label = QtWidgets.QLabel(self)
        self.label.setStyleSheet("font-size: 100px; color: rgba(255, 0, 0, 200);")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        
        # Center the label in the widget
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setAlignment(QtCore.Qt.AlignCenter)

    def start_countdown(self):
        # Center the widget on the screen
        screen_geometry = QtWidgets.QDesktopWidget().screenGeometry()
        self.setGeometry((screen_geometry.width() - self.width()) // 2,
                         (screen_geometry.height() - self.height()) // 2,
                         self.width(), self.height())
                         
        for i in range(3, 0, -1):
            self.label.setText(str(i))
            self.show()
            QtCore.QCoreApplication.processEvents()
            QtCore.QThread.sleep(1)
        self.hide()  # Hide the countdown after completion

class RecorderApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.recording_video = False
        self.recording_audio = False
        self.is_paused = False
        self.audio_buffer = []
        self.audio_thread = None
        self.countdown_widget = CountdownWidget()  # Initialize the countdown widget

        # Default settings
        self.audio_fs = DEFAULT_AUDIO_FS
        self.video_resolution = DEFAULT_VIDEO_RESOLUTION
        self.output_dir = DEFAULT_OUTPUT_DIR
        self.language = 'en'  # Default language
        
        self.video_filename = os.path.join(self.output_dir, "Recording.avi")
        self.audio_filename = os.path.join(self.output_dir, "Recording.wav")

        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setGeometry(100, 100, 200, 50)

        self.init_ui()

        self.setStyleSheet("""
            QWidget {
                background-color: rgba(46, 46, 46, 200);
                border: 2px solid #6ebf73;
                border-radius: 25px;
                padding: 10px;
            }
        """)

        self.show()

    def init_ui(self):
        layout = QtWidgets.QHBoxLayout()

        self.record_button = QtWidgets.QPushButton("▷")
        self.record_button.setStyleSheet("font-size: 20px; color: #6ebf73;")
        self.record_button.clicked.connect(self.toggle_recording)
        layout.addWidget(self.record_button)

        self.stop_button = QtWidgets.QPushButton("□")
        self.stop_button.setStyleSheet("font-size: 20px; color: #6ebf73;")
        self.stop_button.clicked.connect(self.stop_recording)
        self.stop_button.setEnabled(False)
        layout.addWidget(self.stop_button)

        self.pause_button = QtWidgets.QPushButton("⏸️")
        self.pause_button.setStyleSheet("font-size: 20px; color: #6ebf73;")
        self.pause_button.clicked.connect(self.toggle_pause)
        self.pause_button.setEnabled(False)
        layout.addWidget(self.pause_button)

        self.settings_button = QtWidgets.QPushButton("⚙️")
        self.settings_button.clicked.connect(self.open_settings)
        layout.addWidget(self.settings_button)

        self.setLayout(layout)

    def open_settings(self):
        settings_dialog = SettingsDialog(self.language)
        if settings_dialog.exec_():
            settings = settings_dialog.get_settings()
            self.audio_fs = settings['audio_fs']
            self.video_resolution = settings['video_resolution']
            self.output_dir = settings['output_dir']
            self.language = settings['language']  # Save selected language
            self.video_filename = os.path.join(self.output_dir, "Recording.avi")
            self.audio_filename = os.path.join(self.output_dir, "Recording.wav")

    def countdown(self):
        self.countdown_widget.start_countdown()  # Start the countdown in the widget

    def start_recording_indicators(self):
        self.countdown()  # Call the countdown function

    def record_video(self):
        codec = cv2.VideoWriter_fourcc(*"XVID")
        out = cv2.VideoWriter(self.video_filename, codec, 20.0, self.video_resolution)

        while self.recording_video:
            if self.is_paused:
                continue
            img = pyautogui.screenshot()
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            out.write(frame)
            cv2.waitKey(1)
        out.release()

    def record_audio(self):
        while self.recording_audio:
            if self.is_paused:
                continue
            audio = sd.rec(int(self.audio_fs), samplerate=self.audio_fs, channels=2, dtype='float64')
            sd.wait()  # Wait until the recording is finished
            self.audio_buffer.append(audio)

        if self.audio_buffer:
            audio_full = np.concatenate(self.audio_buffer, axis=0)
            write(self.audio_filename, self.audio_fs, audio_full)

    def toggle_recording(self):
        if not self.recording_video and not self.recording_audio:
            self.recording_video = True
            self.recording_audio = True
            self.record_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.pause_button.setEnabled(True)

            self.start_recording_indicators()  # Show indicators before starting recording

            self.record_thread_video = QtCore.QThread()
            self.record_thread_video.run = self.record_video
            self.record_thread_video.start()

            # Create audio thread if it's not already created
            if self.audio_thread is None or not self.audio_thread.isRunning():
                self.audio_thread = QtCore.QThread()
                self.audio_thread.run = self.record_audio
                self.audio_thread.start()
        else:
            self.stop_recording()

    def stop_recording(self):
        if self.recording_video or self.recording_audio:
            self.recording_video = False
            self.recording_audio = False
            self.record_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.pause_button.setEnabled(False)

            if self.record_thread_video:
                self.record_thread_video.quit()
                self.record_thread_video.wait()
                self.record_thread_video = None  # Clean up the thread reference

            if self.audio_thread:
                self.audio_thread.quit()
                self.audio_thread.wait()  # Wait for audio thread to complete
                self.audio_thread = None  # Clean up the thread reference
            
            # Show message box for stopped recording
            self.show_message("Recording Stopped")

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        self.pause_button.setText("▶️" if self.is_paused else "⏸️")  # Change button text
        
        # Show message box for paused recording
        if self.is_paused:
            self.show_message("Recording Paused")

    def show_message(self, message):
        msg_box = QtWidgets.QMessageBox()
        msg_box.setWindowTitle("Recording Status")
        msg_box.setText(message)
        msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg_box.exec_()  # Show message box until the user closes it

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    recorder = RecorderApp()
    sys.exit(app.exec_())