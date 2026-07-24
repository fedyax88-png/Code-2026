# modules/video_settings_main.py
from PyQt6.QtWidgets import QFrame, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt
# Импортируем каждый блок настроек видео из их файлов
from modules.video.video_sett1 import VideoSettingBlock1
from modules.video.video_sett2 import VideoSettingBlock2
from modules.video.video_sett3 import VideoSettingBlock3
from modules.video.video_sett4 import VideoSettingBlock4

class VideoSettingsMainWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("MainSettingsCard")
        
        # Плавный диагональный неоновый голубой перелив большой рамки без резких стыков
        BORDER_GRADIENT = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #00d2ff, stop:0.4 #0077b6, stop:0.7 #03045e, stop:1 #00d2ff)"
        self.setStyleSheet(f"""
            QFrame#MainSettingsCard {{
                background-color: #03060f;
                border: 2px solid {BORDER_GRADIENT};
                border-radius: 12px;
            }}
        """)
        
        # Главный вертикальный слой окна настроек
        main_v_layout = QVBoxLayout(self)
        main_v_layout.setContentsMargins(12, 12, 12, 12)
        main_v_layout.setSpacing(10)
        
        # Сетка 2х2 для размещения четырех блоков настроек видео
        grid_layout = QGridLayout()
        grid_layout.setSpacing(12)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        
        # Инициализируем подмодули
        self.block1 = VideoSettingBlock1(self)
        self.block2 = VideoSettingBlock2(self)
        self.block3 = VideoSettingBlock3(self)
        self.block4 = VideoSettingBlock4(self)
        
        # Добавляем блоки в сетку 2х2
        grid_layout.addWidget(self.block1, 0, 0)  # Строка 0, Колонка 0
        grid_layout.addWidget(self.block2, 0, 1)  # Строка 0, Колонка 1
        grid_layout.addWidget(self.block3, 1, 0)  # Строка 1, Колонка 0
        grid_layout.addWidget(self.block4, 1, 1)  # Строка 1, Колонка 1
        
        main_v_layout.addLayout(grid_layout)

