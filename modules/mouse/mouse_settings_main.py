# modules/mouse_settings_main.py
from PyQt6.QtWidgets import QFrame, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt
# Импортируем каждый блок настроек мыши из их отдельных файлов
from modules.mouse.mouse_sett1 import MouseSettingBlock1
from modules.mouse.mouse_sett2 import MouseSettingBlock2
from modules.mouse.mouse_sett3 import MouseSettingBlock3
from modules.mouse.mouse_sett4 import MouseSettingBlock4

class MouseSettingsMainWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("MainSettingsCard")
        
        # Плавный диагональный неоновый зелено-фиолетовый перелив большой рамки без швов
        BORDER_GRADIENT = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2ed573, stop:0.5 #5d1b94, stop:1 #2ed573)"
        self.setStyleSheet(f"""
            QFrame#MainSettingsCard {{
                background-color: #030a06;
                border: 2px solid {BORDER_GRADIENT};
                border-radius: 12px;
            }}
        """)
        
        # Главный вертикальный слой окна настроек
        main_v_layout = QVBoxLayout(self)
        main_v_layout.setContentsMargins(12, 12, 12, 12)
        main_v_layout.setSpacing(10)
        
        # Сетка 2х2 для размещения четырех блоков настроек мыши
        grid_layout = QGridLayout()
        grid_layout.setSpacing(12)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        
        # Инициализируем подмодули
        self.block1 = MouseSettingBlock1(self)
        self.block2 = MouseSettingBlock2(self)
        self.block3 = MouseSettingBlock3(self)
        self.block4 = MouseSettingBlock4(self)
        
        # Добавляем блоки в сетку 2х2
        grid_layout.addWidget(self.block1, 0, 0)  # Строка 0, Колонка 0
        grid_layout.addWidget(self.block2, 0, 1)  # Строка 0, Колонка 1
        grid_layout.addWidget(self.block3, 1, 0)  # Строка 1, Колонка 0
        grid_layout.addWidget(self.block4, 1, 1)  # Строка 1, Колонка 1
        
        main_v_layout.addLayout(grid_layout)

