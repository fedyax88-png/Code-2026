# modules/voice_module.py Часть 1 из 4
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QIcon
import styles
import config_manager  # ПОДКЛЮЧАЕМ НАШ МЕНЕДЖЕР СОХРАНЕНИЙ

class VoiceControlModule(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")  # Применяет стиль карточки из styles.py
        
        # ЗАГРУЖАЕМ сохраненные настройки из JSON файла при старте
        self.config = config_manager.load_config()
        self.current_prof = self.config.get("current_profile", "Default Profile")
        self.voice_data = self.config["profiles"][self.current_prof]["voice"]
        
        # Основной vertical слой карточки (Все ваши отступы и зазоры сохранены)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 1, 10, 10)
        self.main_layout.setSpacing(10)
        
        # ==========================================
        # 1. ВЕРХНЯЯ ПАНЕЛЬ ЗАГОЛОВКА (Панель со своим независимым фоном)
        # ==========================================
        self.header_panel = QFrame()
        self.header_panel.setStyleSheet("""
            QFrame {
                background-color: #0b071a;   /* Выделенный цвет плашки заголовка */
                border: 1px solid #1a1230;   /* Тонкая рамка плашки */
                border-radius: 6px;
            }
        """)
        title_layout = QHBoxLayout(self.header_panel)
        title_layout.setContentsMargins(12, 10, 12, 10) # Ваши отступы внутри плашки заголовка
        title_layout.setSpacing(20) # Ваша оригинальная строка отступа
        
        # Иконка в заголовке заменена на маленькую microphone1.png (Ваш размер 30x30)
        self.mic_icon = QLabel()
        self.mic_icon.setStyleSheet("background: transparent; border: none;")
        mic_small_pixmap = QPixmap(styles.get_image("microphone1.png"))
        if not mic_small_pixmap.isNull():
            self.mic_icon.setPixmap(mic_small_pixmap.scaled(30, 30, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        title_layout.addWidget(self.mic_icon)
        
        # Текст заголовка
        self.title_label = QLabel("4. ГОЛОСОВОЕ УПРАВЛЕНИЕ")
        self.title_label.setStyleSheet(f"font-weight: bold; font-size: 13px; color: {styles.TEXT_WHITE}; background: transparent; border: none;")
        title_layout.addWidget(self.title_label)
        
        title_layout.addStretch()
        
        # Кастомный розовый переключатель-полоска (Toggle)
        self.toggle_btn = QPushButton()
        self.toggle_btn.setCheckable(True)
        
        # СЧИТЫВАЕМ СОСТОЯНИЕ БЕГУНКА ИЗ КОНФИГУРАЦИИ JSON:
        saved_toggle_state = self.voice_data.get("main_toggle", True)
        self.toggle_btn.setChecked(saved_toggle_state)
        
        self.toggle_btn.setFixedSize(44, 20)
        self.update_toggle_style()
        self.toggle_btn.clicked.connect(self.on_toggle_clicked)
        title_layout.addWidget(self.toggle_btn)
        
        # Добавляем плашку заголовка в основной контейнер карточки
        self.main_layout.addWidget(self.header_panel)

# modules/voice_module.py Часть 2 из 4        
        # ==========================================
        # 2. ЦЕНТРАЛЬНАЯ ЧАСТЬ (Зеркальная компоновка строго по макету)
        # ==========================================
        content_layout = QHBoxLayout()
        content_layout.setSpacing(5) # Ваш отступ между левой и правой стороной
        
        # --- ЛЕВАЯ СТОРОНА: Главная большая картинка остается microphone.png (Ваш размер 320x240) ---
        self.big_mic_img = QLabel()
        self.big_mic_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.big_mic_img.setStyleSheet("background: transparent; border: none;")
        mic_big_pixmap = QPixmap(styles.get_image("microphone.png"))
        if not mic_big_pixmap.isNull():
            self.big_mic_img.setPixmap(mic_big_pixmap.scaled(320, 240, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        content_layout.addWidget(self.big_mic_img, stretch=1)
        
        # --- ПРАВАЯ СТОРОНА: Вертикальные блоки статуса и режимов ---
        right_blocks_layout = QVBoxLayout()
        right_blocks_layout.setSpacing(5)
        # БЛОК А: Статус работы (Виджет в рамке под две строки текста)
        self.status_block = QFrame()
        status_lay = QHBoxLayout(self.status_block)
        status_lay.setContentsMargins(15, 10, 10, 10)
        status_lay.setSpacing(10)
        
        # Иконка внутри блока статуса заменена на маленькую microphone1.png (Ваш размер 25x25)
        status_ico = QLabel()
        status_ico.setStyleSheet("background: transparent; border: none;")
        if not mic_small_pixmap.isNull():
            status_ico.setPixmap(mic_small_pixmap.scaled(25, 25, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        status_lay.addWidget(status_ico)
        
        # Текстовый слой (Перенос слова "управление" на новую строку с помощью <br>)
        status_text_lay = QVBoxLayout()
        status_text_lay.setSpacing(2)
        status_title = QLabel("Голосовое<br>управление")
        status_title.setStyleSheet("color: #ffffff; font-size: 12px; font-weight: 500; background: transparent; border: none; line-height: 1.1;")
        
        # Динамически выставляем правильный стартовый текст на основе сохраненного JSON
        self.status_value = QLabel()
        if saved_toggle_state:
            self.status_value.setText("Включена")
            self.status_value.setStyleSheet(f"color: {styles.COLOR_GREEN}; font-weight: bold; font-size: 11px; background: transparent; border: none; margin-top: 4px;")
        else:
            self.status_value.setText("Отключено")
            self.status_value.setStyleSheet(f"color: {styles.TEXT_MUTED}; font-size: 11px; background: transparent; border: none; margin-top: 4px;")
            
        status_text_lay.addWidget(status_title)
        status_text_lay.addWidget(self.status_value)
        
        status_lay.addLayout(status_text_lay)
        status_lay.addStretch()
        
        # Ограничиваем максимальную ширину блока статуса (Ваш размер 160)
        self.status_block.setFixedWidth(160)
        right_blocks_layout.addWidget(self.status_block)
        # БЛОК Б: Панель режима работы (Режим работы + две кнопки вертикально)
        self.mode_block = QFrame()
        mode_lay = QVBoxLayout(self.mode_block)
        mode_lay.setContentsMargins(12, 8, 12, 8)
        mode_lay.setSpacing(6)
        
        mode_title = QLabel("Режим работы")
        mode_title.setStyleSheet("color: #ffffff; font-size: 12px; font-weight: 500; background: transparent; border: none;")
        mode_lay.addWidget(mode_title)
        
        # Кнопки режимов: вертикальный слой (QVBoxLayout) для расположения друг под другом
        modes_btn_layout = QVBoxLayout()
        modes_btn_layout.setSpacing(6)  # Отступ между кнопками по вертикали
        
        self.btn_mode_std = QPushButton("Стандартный")
        self.btn_mode_std.setCheckable(True)
        
        self.btn_mode_game = QPushButton("Игровой")
        self.btn_mode_game.setCheckable(True)
        
        # СЧИТЫВАЕМ АКТИВНЫЙ РЕЖИМ ИЗ КОНФИГУРАЦИИ JSON:
        saved_mode = self.voice_data.get("mode", "Стандартный")
        if saved_mode == "Игровой":
            self.btn_mode_std.setChecked(False)
            self.btn_mode_game.setChecked(True)
        else:
            self.btn_mode_std.setChecked(True)
            self.btn_mode_game.setChecked(False)
        
        self.btn_mode_std.setFixedSize(130, 26)  # Подогнали под суженный блок
        self.btn_mode_game.setFixedSize(130, 26)
        
        # Связываем кнопки в группу взаимоисключения
        self.btn_mode_std.clicked.connect(lambda: self.switch_mode(True))
        self.btn_mode_game.clicked.connect(lambda: self.switch_mode(False))
        
        modes_btn_layout.addWidget(self.btn_mode_std, alignment=Qt.AlignmentFlag.AlignLeft)
        modes_btn_layout.addWidget(self.btn_mode_game, alignment=Qt.AlignmentFlag.AlignLeft)
        mode_lay.addLayout(modes_btn_layout)
        
        # Делаем блок режимов точно такой же ширины, как и блок статуса выше (Ваш размер 160)
        self.mode_block.setFixedWidth(160)
        right_blocks_layout.addWidget(self.mode_block)
        
        content_layout.addLayout(right_blocks_layout, stretch=1)
        self.main_layout.addLayout(content_layout)
        
        # Нам нужен автоматический отступ, чтобы кнопки управления всегда прижимались к низу карточки
        self.main_layout.addStretch()

# modules/voice_module.py Часть 3 из 4
        # ==========================================
        # 3. НИЖНЯЯ ПАНЕЛЬ С КНОПКАМИ УПРАВЛЕНИЯ
        # ==========================================
        bottom_buttons = QHBoxLayout()
        bottom_buttons.setSpacing(6)
        
        self.btn_1 = QPushButton("Кнопка 1")
        self.btn_2 = QPushButton("Кнопка 2")
        self.btn_settings = QPushButton("Настройки голосового управления")
        
        # Подгружаем иконку шестерёнки для кнопки настроек из файла Settings.png
        gear_icon = QIcon(styles.get_image("Settings.png"))
        if not gear_icon.isNull():
            self.btn_settings.setIcon(gear_icon)
            self.btn_settings.setIconSize(QSize(14, 14))
        
        # Фиксируем высоты нижних кнопок для аккуратности (Ваш размер 40)
        for btn in [self.btn_1, self.btn_2, self.btn_settings]:
            btn.setFixedHeight(40)
            
        bottom_buttons.addWidget(self.btn_1, stretch=1)
        bottom_buttons.addWidget(self.btn_2, stretch=1)
        bottom_buttons.addWidget(self.btn_settings, stretch=2) # Растягиваем главную кнопку настроек сильнее остальных
        
        self.main_layout.addLayout(bottom_buttons)
        
        # Применяем неоновую обводку, настраиваемые фоны и запускаем стили режимов при сборке
        self.update_module_colors()
        self.update_mode_styles()
        self.update_toggle_style()
    def update_module_colors(self):
        """
        ЗДЕСЬ НАСТРАИВАЮТСЯ ВСЕ ИНДИВИДУАЛЬНЫЕ ЦВЕTA МОДУЛЯ 4:
        """
        CARD_BG = "#06030d"        # Очень темный фон внутри модуля (под картинкой и кнопками)
        
        # МЯГКИЙ ДИАГОНАЛЬНЫЙ ГРАДИЕНТ РАМКИ КАРТОЧКИ
        BORDER_GRADIENT = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ff007f, stop:0.4 #b817b0, stop:0.7 #8a2be2, stop:1 #ff007f)"
        
        BLOCK_BG = "#0d091a"       # Цвет внутри двух прямоугольников с правой стороны
        BLOCK_BORDER = "#1a1230"   # Цвет тонкой обводки этих прямоугольников
        
        # ВОЗВРАЩАЕМ ЦВЕТА КНОПОК: тёмно-фиолетовый фон, розовый текст, фиолетовый контур
        BTN_BG = "#130a21"         
        BTN_BORDER = "#2f174d"     
        BTN_TEXT = "#ff007f"       
        
        # Применяем индивидуальные стили к главной рамке карточки и возвращаем красивый розовый стиль кнопкам
        self.setStyleSheet(f"""
            QFrame#Card {{
                background-color: {CARD_BG};
                border: 2px solid {BORDER_GRADIENT};
                border-radius: 12px;
            }}
            QPushButton {{
                background-color: {BTN_BG};
                color: {BTN_TEXT};
                border: 1px solid {BTN_BORDER};
                border-radius: 6px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: #ff007f;
                color: #ffffff;
                border-color: #ffffff;
            }}
        """)
        
        # Применяем изолированные стили к двум правым прямоугольникам отдельно от основного окна
        block_style = f"QFrame {{ background-color: {BLOCK_BG}; border: 1px solid {BLOCK_BORDER}; border-radius: 8px; }}"
        self.status_block.setStyleSheet(block_style)
        self.mode_block.setStyleSheet(block_style)

# modules/voice_module.py Часть 4 из 4
    def on_toggle_clicked(self, checked):
        """Переключатель логики статуса (Вкл/Выкл) с МГНОВЕННЫМ сохранением в JSON"""
        if checked:
            self.status_value.setText("Включена")
            self.status_value.setStyleSheet(f"color: {styles.COLOR_GREEN}; font-weight: bold; font-size: 11px; background: transparent; border: none;")
        else:
            self.status_value.setText("Отключено")
            self.status_value.setStyleSheet(f"color: {styles.TEXT_MUTED}; font-size: 11px; background: transparent; border: none;")
        self.update_toggle_style()
        
        # Записываем новое положение бегунка в config.json
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        config["profiles"][current_prof]["voice"]["main_toggle"] = checked
        config_manager.save_config(config)

    def update_toggle_style(self):
        """Отрисовка кастомной розовой/темной полоски переключателя"""
        if self.toggle_btn.isChecked():
            # Розовый active режим ползунка (Ваш размер сохранен)
            self.toggle_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {styles.COLOR_PINK};
                    border: 1px solid #ff0055;
                    border-radius: 10px;
                    text-align: right;
                    padding-right: 0px;
                    color: white;
                    font-size: 34px;
                    font-weight: bold;
                    padding-top: -10px;
                    padding-bottom: 0px;
                }}
            """)
            self.toggle_btn.setText("●")
        else:
            # Выключенный серый/темный режим полоски (Ваш размер сохранен)
            self.toggle_btn.setStyleSheet("""
                QPushButton {
                    background-color: #1a153a;
                    border: 1px solid #2a2254;
                    border-radius: 10px;
                    text-align: left;
                    padding-left: 0px;
                    color: white;
                    font-size: 34px;
                    font-weight: bold;
                    padding-top: -10px;
                    padding-bottom: 0px;
                }
            """)
            self.toggle_btn.setText("●")

    def switch_mode(self, is_std):
        """Логика эксклюзивного выбора режима работы с МГНОВЕННЫМ сохранением в JSON"""
        if is_std:
            self.btn_mode_std.setChecked(True)
            self.btn_mode_game.setChecked(False)
            mode_text = "Стандартный"
        else:
            self.btn_mode_std.setChecked(False)
            self.btn_mode_game.setChecked(True)
            mode_text = "Игровой"
        self.update_mode_styles()
        
        # Записываем выбранный режим работы в config.json
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        config["profiles"][current_prof]["voice"]["mode"] = mode_text
        config_manager.save_config(config)

    def update_mode_styles(self):
        """Обновление подсветки кнопок режимов под стиль интерфейса"""
        active_style = f"background-color: #1a081a; color: {styles.TEXT_WHITE}; border: 1px solid {styles.COLOR_PINK}; font-weight: 500; border-radius: 5px;"
        inactive_style = "background-color: #0b0914; color: #555e75; border: 1px solid #1a153a; border-radius: 5px;"
        
        self.btn_mode_std.setStyleSheet(active_style if self.btn_mode_std.isChecked() else inactive_style)
        self.btn_mode_game.setStyleSheet(active_style if self.btn_mode_game.isChecked() else inactive_style)
