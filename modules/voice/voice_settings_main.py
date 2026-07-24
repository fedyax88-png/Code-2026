# modules/voice_settings_main.py
from PyQt6.QtWidgets import QFrame, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QWidget
from PyQt6.QtCore import Qt, pyqtSignal
# Импортируем каждый блок настроек из их отдельных файлов
from modules.voice.voice_sett1 import VoiceSettingBlock1
from modules.voice.voice_sett2 import VoiceSettingBlock2
from modules.voice.voice_sett3 import VoiceSettingBlock3
from modules.voice.voice_sett4 import VoiceSettingBlock4

class VoiceSettingsMainWidget(QFrame):
    # Сигнал для возврата обратно на главный экран
    back_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("MainSettingsCard")
        
        # Бесшовный диагональный перелив большой рамки, как мы настроили в модуле 4
        BORDER_GRADIENT = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ff007f, stop:0.4 #b817b0, stop:0.7 #8a2be2, stop:1 #ff007f)"
        self.setStyleSheet(f"""
            QFrame#MainSettingsCard {{
                background-color: #040314;
                border: 2px solid {BORDER_GRADIENT};
                border-radius: 12px;
            }}
        """)
        
        # Главный вертикальный слой окна настроек
        main_v_layout = QVBoxLayout(self)
        main_v_layout.setContentsMargins(12, 12, 12, 12)
        main_v_layout.setSpacing(10)
        
        # Сетка 2х2 для размещения четырех блоков настроек
        grid_layout = QGridLayout()
        grid_layout.setSpacing(12)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        
        # Инициализируем подмодули
        self.block1 = VoiceSettingBlock1(self)
        self.block2 = VoiceSettingBlock2(self)
        self.block3 = VoiceSettingBlock3(self)
        self.block4 = VoiceSettingBlock4(self)
        
        # Добавляем блоки в сетку 2х2
        grid_layout.addWidget(self.block1, 0, 0)  # Строка 0, Колонка 0
        grid_layout.addWidget(self.block2, 0, 1)  # Строка 0, Колонка 1
        grid_layout.addWidget(self.block3, 1, 0)  # Строка 1, Колонка 0
        grid_layout.addWidget(self.block4, 1, 1)  # Строка 1, Колонка 1
        
        main_v_layout.addLayout(grid_layout)

