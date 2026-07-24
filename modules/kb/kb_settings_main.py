# modules/kb_settings_main.py
from PyQt6.QtWidgets import QFrame, QGridLayout, QVBoxLayout, QStackedWidget, QWidget
from PyQt6.QtCore import Qt
# Импортируем каждый блок настроек клавиатуры из их отдельных файлов
from modules.kb.kb_sett1 import KeyboardSettingBlock1
from modules.kb.kb_sett2 import KeyboardSettingBlock2
from modules.kb.kb_sett3 import KeyboardSettingBlock3
from modules.kb.kb_sett4 import KeyboardSettingBlock4
from modules.kb.kb_sett5 import KeyboardSettingBlock5 # ПОДКЛЮЧАЕМ НОВЫЙ ФАЙЛ SET 5

class KeyboardSettingsMainWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("MainSettingsCard")
        
        # Плавный диагональный неоновый фиолетово-синий перелив большой рамки без швов
        BORDER_GRADIENT = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8a2be2, stop:0.5 #00d2ff, stop:1 #8a2be2)"
        self.setStyleSheet(f"""
            QFrame#MainSettingsCard {{
                background-color: #04030d;
                border: 2px solid {BORDER_GRADIENT};
                border-radius: 12px;
            }}
        """)
        
        # Главный вертикальный слой окна настроек
        main_v_layout = QVBoxLayout(self)
        main_v_layout.setContentsMargins(12, 12, 12, 12)
        main_v_layout.setSpacing(10)
        
        # --- ИИ-СТЭК МНОГОСТРАНИЧНОСТИ ДЛЯ МГНОВЕННОГО ПЕРЕКЛЮЧЕНИЯ ОКНА ---
        self.stacked_widget = QStackedWidget()
        main_v_layout.addWidget(self.stacked_widget)
        
        # СТРАНИЦА 1: Ваша оригинальная матрица 2х2 (Set 1, 2, 3, 4)
        self.page_blocks_wrapper = QWidget()
        grid_layout = QGridLayout(self.page_blocks_wrapper)
        grid_layout.setSpacing(12)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        
        # Инициализируем подмодули
        self.block1 = KeyboardSettingBlock1(self)
        self.block2 = KeyboardSettingBlock2(self)
        self.block3 = KeyboardSettingBlock3(self)
        self.block4 = KeyboardSettingBlock4(self)
        
        # Добавляем блоки в сетку 2х2
        grid_layout.addWidget(self.block1, 0, 0)  # Строка 0, Колонка 0
        grid_layout.addWidget(self.block2, 0, 1)  # Строка 0, Колонка 1
        grid_layout.addWidget(self.block3, 1, 0)  # Строка 1, Колонка 0
        grid_layout.addWidget(self.block4, 1, 1)  # Строка 1, Колонка 1
        
        self.stacked_widget.addWidget(self.page_blocks_wrapper) # Индекс 0 в стэке
        
        # СТРАНИЦА 2: Совершенно новое пустое окно продвинутых настроек из kb_sett5.py
        self.block5 = KeyboardSettingBlock5(self)
        self.stacked_widget.addWidget(self.block5) # Индекс 1 в стэке
        
        self.stacked_widget.setCurrentIndex(0) # При старте всегда показываем блоки 1-4

    def set_active_page_index(self, index):
        """Связующий ИИ-метод: принимает команды переключения страниц от кнопок из шапки Z3.py"""
        self.stacked_widget.setCurrentIndex(index)
