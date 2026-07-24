# modules/kb_module.py - ЧАСТЬ 1 ИЗ 5
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap, QIcon
import styles
import config_manager  # ПОДКЛЮЧАЕМ НАШ МЕНЕДЖЕР СОХРАНЕНИЙ

# Импортируем созданный нами независимый ИИ-модуль наэкранных кликеров поверх окон
from modules.kb.kb_overlay_buttons import OverlayKeysManager

class KeyboardControlModule(QFrame):
    # Сигнал для открытия окна детальных настроек клавиатуры
    settings_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        
        # ЗАГРУЖАЕМ сохраненные настройки из JSON файла при старте
        self.config = config_manager.load_config()
        self.current_prof = self.config.get("current_profile", "Default Profile")
        self.kb_data = self.config["profiles"][self.current_prof]["kb"]
        
        # СТРОГО ПО ТЗ: Инициализируем менеджер наэкранных окон один раз при старте
        self.overlay_manager = OverlayKeysManager()
        
        # Основной вертикальный слой карточки
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 1, 5, 10)
        self.main_layout.setSpacing(10)
        
        # ==========================================
        # 1. ВЕРХНЯЯ ПАНЕЛЬ ЗАГОЛОВКА (Оригинальный чистый вид)
        # ==========================================
        self.header_panel = QFrame()
        self.header_panel.setStyleSheet("""
            QFrame {
                background-color: #070314;   /* Индивидуальный темный фон плашки заголовка клавиатуры */
                border: 1px solid #1a1038;   /* Тонкая обводка плашки */
                border-radius: 6px;
            }
        """)
        title_layout = QHBoxLayout(self.header_panel)
        title_layout.setContentsMargins(12, 10, 12, 10)
        title_layout.setSpacing(20)
        
        # Картинка kb1.png перед надписью "3. КЛАВИАТУРА"
        self.kb_icon = QLabel()
        self.kb_icon.setStyleSheet("background: transparent; border: none;")
        kb_top_pixmap = QPixmap(styles.get_image("kb1.png"))
        if not kb_top_pixmap.isNull():
            self.kb_icon.setPixmap(kb_top_pixmap.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        title_layout.addWidget(self.kb_icon)
        
        # Текст заголовка
        self.title_label = QLabel("3. КЛАВИАТУРА")
        self.title_label.setStyleSheet(f"font-weight: bold; font-size: 13px; color: {styles.TEXT_WHITE}; background: transparent; border: none;")
        title_layout.addWidget(self.title_label)
        
        title_layout.addStretch()
        
        # Customный крупный переключатель-полоска (Toggle) строго по размерам прошлых модулей
        self.toggle_btn = QPushButton()
        self.toggle_btn.setCheckable(True)
        
        # СЧИТЫВАЕМ СОСТОЯНИЕ БЕГУНКА ИЗ КОНФИГУРАЦИИ JSON:
        saved_toggle_state = self.kb_data.get("main_toggle", True)
        self.toggle_btn.setChecked(saved_toggle_state)
        
        self.toggle_btn.setFixedSize(44, 20)
        self.toggle_btn.clicked.connect(self.on_toggle_clicked)
        title_layout.addWidget(self.toggle_btn)
        
        self.main_layout.addWidget(self.header_panel)
# modules/kb_module.py - ЧАСТЬ 2 ИЗ 5
        # ==========================================
        # 2. ЦЕНТРАЛЬНАЯ ЧАСТЬ (Картинка клавиатуры слева, блок справа)
        # ==========================================
        content_layout = QHBoxLayout()
        content_layout.setSpacing(5)
        
        # --- ЛЕВАЯ СТОРОНА: Главная большая картинка клавиатуры (keyboard.png) ---
        self.kb_img = QLabel()
        self.kb_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.kb_img.setStyleSheet("background: transparent; border: none;")
        kb_pixmap = QPixmap(styles.get_image("keyboard.png"))
        if not kb_pixmap.isNull():
            self.kb_img.setPixmap(kb_pixmap.scaled(320, 240, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        content_layout.addWidget(self.kb_img, stretch=1)
        
        # --- ПРАВАЯ СТОРОНА: Высокий вертикальный прямоугольник статуса ---
        right_blocks_layout = QVBoxLayout()
        right_blocks_layout.setSpacing(5)
        
        # Высокий прямоугольник статуса
        self.status_block = QFrame()
        status_lay = QVBoxLayout(self.status_block)
        status_lay.setContentsMargins(12, 12, 12, 12)
        status_lay.setSpacing(10)
        
        # Иконка внутри блока (дублирует kb1.png)
        status_ico = QLabel()
        status_ico.setStyleSheet("background: transparent; border: none;")
        if not kb_top_pixmap.isNull():
            status_ico.setPixmap(kb_top_pixmap.scaled(35, 35, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        status_lay.addWidget(status_ico, alignment=Qt.AlignmentFlag.AlignLeft)
        
        # Информационный текстовый слой
        self.status_title = QLabel("Модуль клавиатуры")
        self.status_title.setStyleSheet("color: #ffffff; font-size: 13px; font-weight: 500; background: transparent; border: none;")
        status_lay.addWidget(self.status_title)
        
        # Динамически выставляем правильный стартовый текст на основе сохраненного JSON
        self.status_value = QLabel()
        if saved_toggle_state:
            self.status_value.setText("Включен")
            self.status_value.setStyleSheet(f"color: {styles.COLOR_GREEN}; font-weight: bold; font-size: 11px; background: transparent; border: none;")
        else:
            self.status_value.setText("Отключен")
            self.status_value.setStyleSheet(f"color: {styles.TEXT_MUTED}; font-size: 11px; background: transparent; border: none;")
        status_lay.addWidget(self.status_value)
        
        # Тонкая разделительная линия внутри блока, как на образце
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #1a1038; border: none; min-height: 1px; max-height: 1px;")
        status_lay.addWidget(line)
        
        # СТРОГО ПО ТЗ: Кнопка "Центрировать" вмонтирована прямо в прямоугольник вместо неактивного текста описания
        self.btn_calibrate = QPushButton("Центрировать")
        self.btn_calibrate.setFixedHeight(28)
        self.btn_calibrate.setStyleSheet("""
            QPushButton {
                background-color: #0b0617; 
                color: #a347ff; 
                border: 1px solid #401970; 
                border-radius: 5px;
                font-size: 11px; 
                font-weight: bold; 
                padding: 4px 8px;
            }
            QPushButton:hover { 
                background-color: #8a2be2; 
                color: white; 
                border-color: white; 
            }
        """)
        self.btn_calibrate.clicked.connect(self.trigger_manual_calibration)
        status_lay.addWidget(self.btn_calibrate)
        
        status_lay.addStretch()
        
        self.status_block.setFixedWidth(160) # Точная ширина по сетке
        right_blocks_layout.addWidget(self.status_block)
        
        right_blocks_layout.addStretch()
        content_layout.addLayout(right_blocks_layout, stretch=1)
        self.main_layout.addLayout(content_layout)
        
        self.main_layout.addStretch()
# modules/kb_module.py - ЧАСТЬ 3 ИЗ 5
        # ==========================================
        # 3. НИЖНЯЯ ПАНЕЛЬ С КНОПКАМИ УПРАВЛЕНИЯ
        # ==========================================
        bottom_buttons = QHBoxLayout()
        bottom_buttons.setSpacing(6)
        
        # Считываем сохраненные состояния ИИ-режимов клавиатуры из JSON профиля
        self.saved_gestures_mode = self.kb_data.get("gestures_enabled", True)
        
        # ЖЕСТКИЙ СБРОС СЕССИИ ПО ТЗ: При старте программы горячие клавиши ВСЕГДА принудительно выключены!
        self.saved_hotkeys_mode = False
        
        # Сразу перезаписываем это безопасное состояние в JSON-конфиг, чтобы данные не расходились
        self.kb_data["hotkeys_enabled"] = False
        config_manager.save_config(self.config)
        
        # Переводим Кнопку 1 в режим тумблера "Жесты"
        self.btn_1 = QPushButton()
        self.btn_1.setCheckable(True)
        self.btn_1.setChecked(self.saved_gestures_mode)
        if self.saved_gestures_mode:
            self.btn_1.setText("Жесты вкл")
        else:
            self.btn_1.setText("Жесты выкл")
            
        # Переводим Кнопку 2 в режим тумблера "Горячие клавиши" СТРОГО В БЕЗОПАСНЫЙ РЕЖИМ ВЫКЛЮЧЕНИЯ
        self.btn_2 = QPushButton()
        self.btn_2.setCheckable(True)
        self.btn_2.setChecked(False) # Всегда отжата при старте
        self.btn_2.setText("Горячие клавиши выкл")

            
        self.btn_settings = QPushButton("Настройки клавиатуры")
        
        # Подгружаем иконку шестерёнки для кнопки настроек из файла Settings.png
        gear_icon = QIcon(styles.get_image("Settings.png"))
        if not gear_icon.isNull():
            self.btn_settings.setIcon(gear_icon)
            self.btn_settings.setIconSize(QSize(14, 14))
        
        # Фиксируем высоты нижних кнопок для аккуратности
        for btn in [self.btn_1, self.btn_2, self.btn_settings]:
            btn.setFixedHeight(40)
            
        # Подключаем клики нижних кнопок к интерактивным методам
        self.btn_1.clicked.connect(self.on_gestures_button_clicked)
        self.btn_2.clicked.connect(self.on_hotkeys_button_clicked)
        self.btn_settings.clicked.connect(self.settings_clicked.emit)
            
        bottom_buttons.addWidget(self.btn_1, stretch=1)
        bottom_buttons.addWidget(self.btn_2, stretch=1)
        bottom_buttons.addWidget(self.btn_settings, stretch=2) # Растягиваем главную кнопку настроек сильнее
        
        self.main_layout.addLayout(bottom_buttons)
        
        # Применяем неоновую обводку, настраиваемые фоны и обновляем стили тумблеров
        self.update_module_colors()
        self.update_toggle_style()
        self.update_gestures_button_style()   
        self.update_hotkeys_button_style()

    def trigger_manual_calibration(self):
        """Передает сквозную команду в ИИ-трекер сделать снимок центрального положения лица"""
        main_win = self.window()
        if main_win and hasattr(main_win, 'mod_video') and main_win.mod_video:
            if hasattr(main_win.mod_video, 'camera_thread') and main_win.mod_video.camera_thread:
                if main_win.mod_video.camera_thread.tracker:
                    # Посылаем приказ ядру залочить нули
                    main_win.mod_video.camera_thread.tracker.calibrate_zero()

    def update_module_colors(self):
        """ЗДЕСЬ НАСТРАИВАЮТСЯ ВСЕ ИНДИВИДУАЛЬНЫЕ ЦВЕTA МОДУЛЯ 3 (КЛАВИАТУРА)"""
        CARD_BG = "#04030d"        # Очень темный фон внутри модуля
        
        # НАШ ФИОЛЕТОВЫЙ ГРАДИЕНТ С УЗКИМ СИНИМ ЦЕНТРОМ
        BORDER_GRADIENT = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8a2be2, stop:0.25 #9a4ca7, stop:0.7 #00d2ff, stop:0.25 #9a4ca7, stop:1 #8a2be2)"
        
        BLOCK_BG = "#080514"       # Цвет внутри прямоугольника статуса
        BLOCK_BORDER = "#1a1038"   # Цвет тонкой обводки этого прямоугольника
        
        # ФИОЛЕТОВЫЕ ЦВЕТА КНОПОК
        BTN_BG = "#0b0617"         
        BTN_BORDER = "#401970"     
        BTN_TEXT = "#a347ff"       # Чистый фиолетовый неон для текста и контуров кнопок
        
        # Применяем индивидуальные стили к главной рамке карточки и нижним кнопкам
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
                background-color: #8a2be2;  /* Фиолетовая неоновая подсветка при наведении */
                color: #ffffff;
                border-color: #ffffff;
            }}
        """)
        
        # Применяем изолированный стиль к правому прямоугольнику статуса
        self.status_block.setStyleSheet(f"QFrame {{ background-color: {BLOCK_BG}; border: 1px solid {BLOCK_BORDER}; border-radius: 8px; }}")
# modules/kb_sett2.py - ЧАСТЬ 4 ИЗ 5
    def on_toggle_clicked(self, checked):
        """Логика главного рубильника клавиатурного модуля с защитой от случайного выключения"""
        if checked:
            self.execute_kb_toggle_logic(True)
        else:
            # Фирменная защита от случайного срыва взгляда в фиолетовых тонах
            from PyQt6.QtWidgets import QMessageBox
            
            msg = QMessageBox(self)
            msg.setWindowTitle("Предупреждение")
            msg.setText("ВНИМАНИЕ!\n\nВы отключаете главный блок КЛАВИАТУРЫ.\nИИ-управление жестами лица полностью прекратится.\n\nВы уверены, что хотите отключить модуль?")
            msg.setIcon(QMessageBox.Icon.Warning)
            
            yes_btn = msg.addButton("Да, отключить", QMessageBox.ButtonRole.YesRole)
            no_btn = msg.addButton("Отмена", QMessageBox.ButtonRole.NoRole)
            msg.setDefaultButton(no_btn)
            
            msg.setStyleSheet("""
                QMessageBox { background-color: #04030d; border: 2px solid #8a2be2; border-radius: 10px; }
                QLabel { color: #ffffff; font-family: 'Segoe UI', sans-serif; font-size: 12px; font-weight: bold; }
                QPushButton { background-color: #0b0617; color: #a347ff; border: 1px solid #401970; border-radius: 4px; padding: 6px 14px; font-weight: bold; min-width: 80px; }
                QPushButton:hover { background-color: #8a2be2; color: white; border-color: white; }
            """)
            
            msg.exec()
            
            if msg.clickedButton() == yes_btn:
                self.execute_kb_toggle_logic(False)
            else:
                self.toggle_btn.blockSignals(True)
                self.toggle_btn.setChecked(True)
                self.toggle_btn.blockSignals(False)
                self.update_toggle_style()

    def execute_kb_toggle_logic(self, checked):
        """Вспомогательный метод для переключения логики рубильника клавиатуры"""
        self.update_toggle_style()
        if checked:
            self.status_value.setText("Включен")
            self.status_value.setStyleSheet(f"color: {styles.COLOR_GREEN}; font-weight: bold; font-size: 11px; background: transparent; border: none;")
        else:
            self.status_value.setText("Отключен")
            self.status_value.setStyleSheet(f"color: {styles.TEXT_MUTED}; font-size: 11px; background: transparent; border: none;")
            
            # СТРОГО ПО ТЗ: Если вырубили модуль целиком — принудительно гасим и все наэкранные кнопки
            if hasattr(self, 'overlay_manager') and self.overlay_manager:
                self.overlay_manager.destroy_all_buttons()
                self.btn_2.setChecked(False)
                self.btn_2.setText("Горячие клавиши выкл")
                self.update_hotkeys_button_style()

        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        config["profiles"][current_prof]["kb"]["main_toggle"] = checked
        config_manager.save_config(config)

    def update_toggle_style(self):
        """Отрисовка кастомной фиолетовой/темной полоски переключателя строго по вашим размерам"""
        if self.toggle_btn.isChecked():
            self.toggle_btn.setStyleSheet("""
                QPushButton { background-color: #8a2be2; border: 1px solid #711fba; border-radius: 10px; text-align: right; padding-right: 2px; color: white; font-size: 34px; font-weight: bold; padding-top: -10px; padding-bottom: 0px; }
            """)
            self.toggle_btn.setText("●")
        else:
            self.toggle_btn.setStyleSheet("""
                QPushButton { background-color: #1a1038; border: 1px solid #401970; border-radius: 10px; text-align: left; padding-left: 2px; color: white; font-size: 34px; font-weight: bold; padding-top: -10px; padding-bottom: 0px; }
            """)
            self.toggle_btn.setText("●")

    def on_gestures_button_clicked(self, checked):
        """Логика кнопки Жесты вкл/выкл с защитой от случайного отключения макросов в игре"""
        if checked:
            self.execute_gestures_logic(True)
        else:
            from PyQt6.QtWidgets import QMessageBox
            
            msg = QMessageBox(self)
            msg.setWindowTitle("Предупреждение")
            msg.setText("ВНИМАНИЕ!\n\nВы отключаете ИИ-УПРАВЛЕНИЕ ЖЕСТАМИ лица.\nКлавиатура ПЕРЕСТАНЕТ нажимать кнопки при мимике.\n\nВы уверены, что хотите остановить жесты?")
            msg.setIcon(QMessageBox.Icon.Warning)
            
            yes_btn = msg.addButton("Да, отключить", QMessageBox.ButtonRole.YesRole)
            no_btn = msg.addButton("Отмена", QMessageBox.ButtonRole.NoRole)
            msg.setDefaultButton(no_btn)
            
            msg.setStyleSheet("""
                QMessageBox { background-color: #04030d; border: 2px solid #8a2be2; border-radius: 10px; }
                QLabel { color: #ffffff; font-family: 'Segoe UI', sans-serif; font-size: 12px; font-weight: bold; }
                QPushButton { background-color: #0b0617; color: #a347ff; border: 1px solid #401970; border-radius: 4px; padding: 6px 14px; font-weight: bold; min-width: 80px; }
                QPushButton:hover { background-color: #8a2be2; color: white; border-color: white; }
            """)
            msg.exec()
            
            if msg.clickedButton() == yes_btn:
                self.execute_gestures_logic(False)
            else:
                self.btn_1.setChecked(True)
                self.btn_1.setText("Жесты вкл")
                self.update_gestures_button_style()
# modules/kb_module.py - ЧАСТЬ 5 ИЗ 5
    def execute_gestures_logic(self, checked):
        if checked: self.btn_1.setText("Жесты вкл")
        else: self.btn_1.setText("Жесты выкл")
        self.update_gestures_button_style()
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        config["profiles"][current_prof]["kb"]["gestures_enabled"] = checked
        config_manager.save_config(config)

    def on_hotkeys_button_clicked(self, checked):
        """
        СЛОТ УПРАВЛЕНИЯ ГОРЯЧИМИ КЛАВИШАМИ ПО ТЗ:
        При включении — считывает массив выбранных букв из Block3 и спавнит их на экране.
        При выключении — полностью стирает оверлеи поверх всех окон.
        """
        if checked: 
            self.btn_2.setText("Горячие клавиши вкл")
            
            # Считываем свежие данные конфигурации из JSON
            config = config_manager.load_config()
            current_prof = config.get("current_profile", "Default Profile")
            kb_conf = config["profiles"][current_prof].get("kb", {})
            
            # Извлекаем массив букв, которые вы выбрали кликами в карточке Set 3
            selected_keys = kb_conf.get("overlay_selected_keys", [])
            
            # Если геймер выбрал кнопки — приказываем менеджеру вывести их на экран поверх игр
            if selected_keys and hasattr(self, 'overlay_manager') and self.overlay_manager:
                self.overlay_manager.spawn_overlay_buttons(selected_keys)
        else: 
            self.btn_2.setText("Горячие клавиши выкл")
            
            # Жестко и бесследно стираем оверлеи с монитора при отключении тумблера
            if hasattr(self, 'overlay_manager') and self.overlay_manager:
                self.overlay_manager.destroy_all_buttons()
                
        self.update_hotkeys_button_style()
        
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        config["profiles"][current_prof]["kb"]["hotkeys_enabled"] = checked
        config_manager.save_config(config)

    def update_gestures_button_style(self):
        if self.btn_1.isChecked():
            self.btn_1.setStyleSheet("QPushButton { background-color: #0b0617; color: #a347ff; border: 1px solid #8a2be2; font-weight: bold; border-radius: 6px; }")
        else:
            self.btn_1.setStyleSheet("QPushButton { background-color: #0b0617; color: #50386b; border: 1px solid #401970; border-radius: 6px; font-weight: 500; }")

    def update_hotkeys_button_style(self):
        if self.btn_2.isChecked():
            self.btn_2.setStyleSheet("QPushButton { background-color: #0b0617; color: #a347ff; border: 1px solid #8a2be2; font-weight: bold; border-radius: 6px; }")
        else:
            self.btn_2.setStyleSheet("QPushButton { background-color: #0b0617; color: #50386b; border: 1px solid #401970; border-radius: 6px; font-weight: 500; }")
