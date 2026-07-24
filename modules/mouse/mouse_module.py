# modules/mouse/mouse_module.py ( 1 часть из 7 )
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QTimer
# Находим в самом верху файла mouse_module.py строку импорта QtGui и приводим её к такому виду:
from PyQt6.QtGui import QPixmap, QIcon, QCursor
import styles
import config_manager  # НАШ МЕНЕДЖЕР СОХРАНЕНИЙ

# ИМПОРТИРУЕМ КЛАССЫ СКОРОСТИ И НАШЕЙ НОВОЙ ПЛАВАЮЩЕЙ ПАНЕЛИ КЛИКOВ:
from modules.mouse.start_mouse import MouseController
from modules.mouse.click_toolbar import ClickTypeToolbar

class MouseControlModule(QFrame):
    # Сигнал для открытия окна детальных настроек мыши
    settings_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        
        # ЗАГРУЖАЕМ сохраненные настройки из JSON файла при старте
        self.config = config_manager.load_config()
        self.current_prof = self.config.get("current_profile", "Default Profile")
        self.mouse_data = self.config["profiles"][self.current_prof]["mouse"]
        
        # ИНИЦИАЛИЗИРУЕМ НАШ КАСТОМНЫЙ КОНТРОЛЛЕР МЫШИ С ДИНАМИЧЕСКИМ РАЗГОНОМ
        self.mouse_controller = MouseController()
        
        # Ссылка под плавающее оверлей-окно панели типа кликов из eViacam
        self.toolbar_window = None
        
        # Основной вертикальный слой карточки (Полностью сохраняем геометрию прошлых блоков)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 1, 5, 10)
        self.main_layout.setSpacing(10)
        
        # ==========================================
        # 1. ВЕРХНЯЯ ПАНЕЛЬ ЗАГОЛОВКА (Отдельный темный прямоугольник)
        # ==========================================
        self.header_panel = QFrame()
        self.header_panel.setStyleSheet("""
            QFrame {
                background-color: #030d08;   /* Индивидуальный темный фон плашки заголовка мыши */
                border: 1px solid #10381f;   /* Тонкая обводка плашки */
                border-radius: 6px;
            }
        """)
        title_layout = QHBoxLayout(self.header_panel)
        title_layout.setContentsMargins(12, 10, 12, 10)
        title_layout.setSpacing(20)
        
        # Картинка mouse1.png перед надписью "2. МЫШЬ"
        self.mouse_icon = QLabel()
        self.mouse_icon.setStyleSheet("background: transparent; border: none;")
        mouse_top_pixmap = QPixmap(styles.get_image("mouse1.png"))
        if not mouse_top_pixmap.isNull():
            self.mouse_icon.setPixmap(mouse_top_pixmap.scaled(30, 30, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        title_layout.addWidget(self.mouse_icon)
        
        # Текст заголовка
        self.title_label = QLabel("2. МЫШЬ")
        self.title_label.setStyleSheet(f"font-weight: bold; font-size: 13px; color: {styles.TEXT_WHITE}; background: transparent; border: none;")
        title_layout.addWidget(self.title_label)
        
        title_layout.addStretch()
        
        # Кастомный крупный переключатель-полоска (Toggle) строго по размерам прошлых модулей
        self.toggle_btn = QPushButton()
        self.toggle_btn.setCheckable(True)
        
        # СЧИТЫВАЕМ СОСТОЯНИЕ ГЛАВНОГО БЕГУНКА ИЗ КОНФИГУРАЦИИ JSON:
        saved_toggle_state = self.mouse_data.get("main_toggle", True)
        self.toggle_btn.setChecked(saved_toggle_state)
        
        self.toggle_btn.setFixedSize(44, 20)
        self.toggle_btn.clicked.connect(self.on_toggle_clicked)
        title_layout.addWidget(self.toggle_btn)
        
        self.main_layout.addWidget(self.header_panel)

        # ==========================================
        # 2. ЦЕНТРАЛЬНАЯ ЧАСТЬ (Картинка мыши слева, блоки справа)
        # ==========================================
        content_layout = QHBoxLayout()
        content_layout.setSpacing(5)
        
        # --- ЛЕВАЯ СТОРОНА: Главная большая картинка мышки (mouse.png) ---
        self.mouse_img = QLabel()
        self.mouse_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mouse_img.setStyleSheet("background: transparent; border: none;")
        mouse_pixmap = QPixmap(styles.get_image("mouse.png"))
        if not mouse_pixmap.isNull():
            self.mouse_img.setPixmap(mouse_pixmap.scaled(280, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        content_layout.addWidget(self.mouse_img, stretch=1)
        
        # --- ПРАВАЯ СТОРОНА: Два прямоугольника (Автокликер и Панель) ---
        right_blocks_layout = QVBoxLayout()
        right_blocks_layout.setSpacing(5)

# modules/mouse/mouse_module.py ( 2 часть из 7 )        
        # ПРЯМОУГОЛЬНИК А: Автокликер (С иконкой молнии mouse2.png)
        self.autoclick_block = QFrame()
        ac_lay = QHBoxLayout(self.autoclick_block)
        ac_lay.setContentsMargins(10, 10, 10, 10)
        ac_lay.setSpacing(10)
        
        ac_ico = QLabel()
        ac_ico.setStyleSheet("background: transparent; border: none;")
        ac_pixmap = QPixmap(styles.get_image("mouse2.png"))
        if not ac_pixmap.isNull():
            ac_ico.setPixmap(ac_pixmap.scaled(25, 25, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        ac_lay.addWidget(ac_ico)
        
        ac_text_lay = QVBoxLayout()
        ac_text_lay.setSpacing(2)
        ac_title = QLabel("Автокликер")
        ac_title.setStyleSheet("color: #ffffff; font-size: 12px; font-weight: 500; background: transparent; border: none;")
        
        # Текст автокликера инициализируется на основе JSON через метод update_autoclicker_status
        self.ac_value = QLabel()
        
        ac_text_lay.addWidget(ac_title)
        ac_text_lay.addWidget(self.ac_value)
        ac_lay.addLayout(ac_text_lay)
        ac_lay.addStretch()
        
        self.autoclick_block.setFixedWidth(165)
        right_blocks_layout.addWidget(self.autoclick_block)
        
        # ПРЯМОУГОЛЬНИК Б: Панель на экране (С иконкой глаза mouse3.png и кнопкой внутри)
        self.panel_block = QFrame()
        panel_lay = QVBoxLayout(self.panel_block)
        panel_lay.setContentsMargins(10, 10, 10, 10)
        panel_lay.setSpacing(6)
        
        panel_top_lay = QHBoxLayout()
        panel_top_lay.setSpacing(10)
        
        eye_ico = QLabel()
        eye_ico.setStyleSheet("background: transparent; border: none;")
        eye_pixmap = QPixmap(styles.get_image("mouse3.png"))
        if not eye_pixmap.isNull():
            eye_ico.setPixmap(eye_pixmap.scaled(35, 35, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        panel_top_lay.addWidget(eye_ico)
        
        panel_text_lay = QVBoxLayout()
        panel_text_lay.setSpacing(2)
        panel_title = QLabel("Панель на экране")
        panel_title.setStyleSheet("color: #ffffff; font-size: 12px; font-weight: 500; background: transparent; border: none;")
        
        # СЧИТЫВАЕМ СОСТОЯНИЕ КНОПКИ ПАНЕЛИ ИЗ КОНФИГУРАЦИИ JSON:
        self.is_panel_shown = self.mouse_data.get("panel_on_screen", False)
        
        self.panel_value = QLabel()
        self.btn_show_panel = QPushButton()
        # Динамически выставляем правильный стартовый текст для надписи и кнопки
        if self.is_panel_shown:
            self.panel_value.setText("Включено")
            self.panel_value.setStyleSheet(f"color: {styles.COLOR_GREEN}; font-weight: bold; font-size: 11px; background: transparent; border: none; margin-top: 4px;")
            self.btn_show_panel.setText("Скрыть панель")
        else:
            self.panel_value.setText("Скрыта")
            self.panel_value.setStyleSheet(f"color: {styles.TEXT_MUTED}; font-size: 11px; background: transparent; border: none; margin-top: 4px;")
            self.btn_show_panel.setText("Показать панель")
            
        panel_text_lay.addWidget(panel_title)
        panel_text_lay.addWidget(self.panel_value)
        panel_top_lay.addLayout(panel_text_lay)
        panel_top_lay.addStretch()
        panel_lay.addLayout(panel_top_lay)
        
        # Внутренняя кнопка "Показать панель"
        self.btn_show_panel.setFixedHeight(24)
        self.btn_show_panel.setStyleSheet("""
            QPushButton {
                background-color: #05140d; color: #2ed573; border: 1px solid #10381f; border-radius: 4px; font-size: 11px;
            }
            QPushButton:hover {
                background-color: #2ed573; color: black; border-color: white;
            }
        """)
        panel_lay.addWidget(self.btn_show_panel)
        
        self.panel_block.setFixedWidth(165)
        right_blocks_layout.addWidget(self.panel_block)
        
        right_blocks_layout.addStretch()
        content_layout.addLayout(right_blocks_layout, stretch=1)
        self.main_layout.addLayout(content_layout)
        
        self.main_layout.addStretch()
        
        # АВТОМАТИЧЕСКИЙ СТАРТ ПЛАВАЮЩЕЙ ПАНЕЛИ ИИ ПРИ ЗАПУСКЕ:
        if self.mouse_data.get("toolbar_enabled", False):
            QTimer.singleShot(100, lambda: self.initialize_live_toolbar_window())
        
        # БЕЗОПАСНЫЙ СТАРТ: задержка 150мс и мягкая проверка наличия advanced_panel_window в MainWindow
        if self.mouse_data.get("panel_on_screen", False):
            QTimer.singleShot(150, lambda: self.safe_show_advanced_panel())

# modules/mouse/mouse_module.py ( 3 часть из 7 )            
        # ==========================================
        # 3. НИЖНЯЯ ПАНЕЛЬ С КНОПКАМИ УПРАВЛЕНИЯ
        # ==========================================
        bottom_buttons = QHBoxLayout()
        bottom_buttons.setSpacing(6)
        
        # Считываем сохраненные состояния кнопок Движения, Клика и нашей новой Панели ИИ из JSON
        self.saved_move_mode = self.mouse_data.get("move_mode", True)
        self.saved_click_mode = self.mouse_data.get("click_mode", True)
        self.saved_toolbar_mode = self.mouse_data.get("toolbar_enabled", False)
        
        # Переводим Кнопку 1 в режим тумблера "Движение"
        self.btn_1 = QPushButton()
        self.btn_1.setCheckable(True)
        self.btn_1.setChecked(self.saved_move_mode)
        if self.saved_move_mode:
            self.btn_1.setText("Движение вкл")
        else:
            self.btn_1.setText("Движение выкл")
            
        # Переводим Кнопку 2 в режим тумблера "Клик"
        self.btn_2 = QPushButton()
        self.btn_2.setCheckable(True)
        self.btn_2.setChecked(self.saved_click_mode)
        if self.saved_click_mode:
            self.btn_2.setText("Клик вкл")
        else:
            self.btn_2.setText("Клик выкл")
            
        # ПЕРЕИМЕНОВЫВАЕМ КНОПКУ 3 В ТУМБЛЕР ПАНЕЛИ ИИ ИЗ eViacam (Checkable)
        self.btn_3 = QPushButton()
        self.btn_3.setCheckable(True)
        self.btn_3.setChecked(self.saved_toolbar_mode)
        if self.saved_toolbar_mode:
            self.btn_3.setText("Панель ИИ вкл")
        else:
            self.btn_3.setText("Панель ИИ выкл")
            
        self.btn_settings = QPushButton("Настройки мыши")
        
        # Подгружаем иконку шестерёнки для кнопки настроек из файла Settings.png
        gear_icon = QIcon(styles.get_image("Settings.png"))
        if not gear_icon.isNull():
            self.btn_settings.setIcon(gear_icon)
            self.btn_settings.setIconSize(QSize(14, 14))
        
        # Фиксируем высоты нижних кнопок для аккуратности (Ваш размер 40)
        for btn in [self.btn_1, self.btn_2, self.btn_3, self.btn_settings]:
            btn.setFixedHeight(40)
            
        # Подключаем клики нижних кнопок к интерактивным методам
        self.btn_1.clicked.connect(self.on_move_button_clicked)
        self.btn_2.clicked.connect(self.on_click_button_clicked)
        self.btn_3.clicked.connect(self.on_toolbar_button_clicked) 
        self.btn_settings.clicked.connect(self.settings_clicked.emit)
            
        bottom_buttons.addWidget(self.btn_1, stretch=1)
        bottom_buttons.addWidget(self.btn_2, stretch=1)
        bottom_buttons.addWidget(self.btn_3, stretch=1)
        bottom_buttons.addWidget(self.btn_settings, stretch=2) 
        
        self.main_layout.addLayout(bottom_buttons)
        
        # Подключаем клик внутренней кнопки к интерактивному методу
        self.btn_show_panel.clicked.connect(self.on_panel_btn_clicked)
        
        # Применяем неоновую обводку, настраиваемые фоны и обновляем стили бегунка/кнопок
        self.update_module_colors()
        self.update_toggle_style()
        self.update_move_button_style()   
        self.update_click_button_style()  
        self.update_toolbar_button_style() 
        
        # Считываем и инициализируем сохранённый статус автокликера напрямую из сохранённого JSON
        self.update_autoclicker_status(self.toggle_btn.isChecked())

    def safe_show_advanced_panel(self):
        """Вспомогательный метод для абсолютно безопасного вызова макрос-панели при старте"""
        main_win = self.window()
        if main_win and hasattr(main_win, 'advanced_panel_window') and main_win.advanced_panel_window:
            main_win.advanced_panel_window.show()

# modules/mouse/mouse_module.py ( 4 часть из 7 )
    def update_module_colors(self):
        """ЗДЕСЬ НАСТРАИВАЮТСЯ ВСЕ ИНДИВИДУАЛЬНЫЕ ЦВЕTA МОДУЛЯ 2 (МЫШЬ)"""
        CARD_BG = "#030a06"        # Очень темный фон внутри модуля (под картинкой и кнопками)
        
        # ИДЕАЛЬНЫЙ ЗЕРКАЛЬНЫЙ ЛИНЕЙНЫЙ НЕОНОВЫЙ ГРАДИЕНТ РАМКИ
        BORDER_GRADIENT = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2ed573, stop:0.5 #5d1b94, stop:1 #2ed573)"
        
        BLOCK_BG = "#04140a"       # Цвет внутри прямоугольников статуса с правой стороны
        BLOCK_BORDER = "#10381f"   # Цвет тонкой обводки этих прямоугольников
        
        # Фирменные neo-зеленые цвета для нижних кнопок управления модуля мыши
        self.btn_bg_color = "#05140b"         
        self.btn_border_color = "#123d22"     
        self.btn_text_color = "#2ed573"       
        
        # Применяем индивидуальные стили к главной рамке карточки и нижним кнопкам
        self.setStyleSheet(f"""
            QFrame#Card {{
                background-color: {CARD_BG};
                border: 2px solid {BORDER_GRADIENT};
                border-radius: 12px;
            }}
            QPushButton {{
                background-color: {self.btn_bg_color};
                color: {self.btn_text_color};
                border: 1px solid {self.btn_border_color};
                border-radius: 6px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: #2ed573;
                color: #000000;
                border-color: #ffffff;
            }}
        """)
        
        # Применяем изолированные стили к двум правым прямоугольникам отдельно от основного окна
        block_style = f"QFrame {{ background-color: {BLOCK_BG}; border: 1px solid {BLOCK_BORDER}; border-radius: 8px; }}"
        self.autoclick_block.setStyleSheet(block_style)
        self.panel_block.setStyleSheet(block_style)

    def update_move_button_style(self):
        """Отрисовка сочного ярко-зеленого неонового ободка на кнопке Движение при включении"""
        if self.btn_1.isChecked():
            self.btn_1.setStyleSheet(f"""
                QPushButton {{
                    background-color: #04140a; color: #2ed573; border: 1px solid #2ed573; font-weight: bold; border-radius: 6px;
                }}
                QPushButton:hover {{ background-color: #2ed573; color: #000000; border-color: #ffffff; }}
            """)
        else:
            self.btn_1.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.btn_bg_color}; color: #557560; border: 1px solid {self.btn_border_color}; border-radius: 6px; font-weight: 500;
                }}
                QPushButton:hover {{ background-color: #2ed573; color: #000000; border-color: #ffffff; }}
            """)

    def update_click_button_style(self):
        """Отрисовка сочного ярко-зеленого неонового ободка на кнопке Клик при включении"""
        if self.btn_2.isChecked():
            self.btn_2.setStyleSheet(f"""
                QPushButton {{
                    background-color: #04140a; color: #2ed573; border: 1px solid #2ed573; font-weight: bold; border-radius: 6px;
                }}
                QPushButton:hover {{ background-color: #2ed573; color: #000000; border-color: #ffffff; }}
            """)
        else:
            self.btn_2.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.btn_bg_color}; color: #557560; border: 1px solid {self.btn_border_color}; border-radius: 6px; font-weight: 500;
                }}
                QPushButton:hover {{ background-color: #2ed573; color: #000000; border-color: #ffffff; }}
            """)

    def update_toolbar_button_style(self):
        """Отрисовка сочного ярко-зеленого неонового ободка на кнопке Панель ИИ при включении"""
        if self.btn_3.isChecked():
            self.btn_3.setStyleSheet(f"""
                QPushButton {{
                    background-color: #04140a; color: #2ed573; border: 1px solid #2ed573; font-weight: bold; border-radius: 6px;
                }}
                QPushButton:hover {{ background-color: #2ed573; color: #000000; border-color: #ffffff; }}
            """)
        else:
            self.btn_3.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.btn_bg_color}; color: #557560; border: 1px solid #self.btn_border_color; border-radius: 6px; font-weight: 500;
                }}
                QPushButton:hover {{ background-color: #2ed573; color: #000000; border-color: #ffffff; }}
            """)

    def update_click_buttons_from_json(self):
        """Синхронизирует состояние Кнопки 2 на главном экране при нажатии Пуск/Пауза в плавающей панели"""
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        is_click_enabled = config["profiles"][current_prof]["mouse"].get("click_mode", True)
        
        self.btn_2.setChecked(is_click_enabled)
        if is_click_enabled:
            self.btn_2.setText("Клик вкл")
        else:
            self.btn_2.setText("Клик выкл")
        self.update_click_button_style()

# modules/mouse/mouse_module.py ( 5 часть из 7 )
    def initialize_live_toolbar_window(self):
        """Безопасная初始化 плавающей панели поверх всех окон Windows"""
        if not self.toolbar_window:
            self.toolbar_window = ClickTypeToolbar(self.window())
            self.toolbar_window.show()

    def hot_rebuild_toolbar_geometry(self):
        """МЕТОД Hot-Rebuild: на лету пересобирает слои панели из горизонтальных в вертикальные"""
        if self.toolbar_window:
            self.toolbar_window.close()
            self.toolbar_window = None
            self.initialize_live_toolbar_window()

    def on_toolbar_button_clicked(self, checked):
        """Логика кнопки Панель ИИ: на лету создает оверлей или уничтожает его из памяти"""
        if checked:
            self.btn_3.setText("Панель ИИ вкл")
            self.initialize_live_toolbar_window()
        else:
            self.btn_3.setText("Панель ИИ выкл")
            if self.toolbar_window:
                # Мягко закрываем окно, Qt сам безопасно остановит таймеры и очистит память
                self.toolbar_window.close()
                self.toolbar_window = None
                
        self.update_toolbar_button_style()
        
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        config["profiles"][current_prof]["mouse"]["toolbar_enabled"] = checked
        config_manager.save_config(config)


    def on_move_button_clicked(self, checked):
        """Логика кнопки Движение с защитой от случайного отключения трекинга головы"""
        # Если пользователь ВКЛЮЧАЕТ движение — делаем это сразу без окон подтверждения
        if checked:
            self.execute_move_logic(True)
        else:
            # Если выключает — блокируем и выводим фирменное предупреждение
            from PyQt6.QtWidgets import QMessageBox
            
            msg = QMessageBox(self)
            msg.setWindowTitle("Предупреждение")
            msg.setText("ВНИМАНИЕ!\n\nВы отключаете ДВИЖЕНИЕ курсора.\nФизическая мышь ПЕРЕСТАНЕТ ходить за вашей головой.\n\nВы уверены, что хотите остановить движение курсора?")
            msg.setIcon(QMessageBox.Icon.Warning)
            
            yes_btn = msg.addButton("Да, отключить", QMessageBox.ButtonRole.YesRole)
            no_btn = msg.addButton("Отмена", QMessageBox.ButtonRole.NoRole)
            msg.setDefaultButton(no_btn)
            
            msg.setStyleSheet("""
                QMessageBox { background-color: #030a06; border: 2px solid #2ed573; border-radius: 10px; }
                QLabel { color: #ffffff; font-family: 'Segoe UI', sans-serif; font-size: 12px; font-weight: bold; }
                QPushButton { background-color: #05140b; color: #2ed573; border: 1px solid #123d22; border-radius: 4px; padding: 6px 14px; font-weight: bold; min-width: 80px; }
                QPushButton:hover { background-color: #2ed573; color: black; border-color: white; }
            """)
            
            msg.exec()
            
            if msg.clickedButton() == yes_btn:
                self.execute_move_logic(False)
            else:
                # Отмена: возвращаем кнопку назад в нажатое (включенное) состояние
                self.btn_1.setChecked(True)
                self.btn_1.setText("Движение вкл")
                self.update_move_button_style()

    def execute_move_logic(self, checked):
        """Вспомогательный метод для выполнения оригинальной логики переключения движения"""
        if checked:
            self.btn_1.setText("Движение вкл")
        else:
            self.btn_1.setText("Движение выкл")
        self.update_move_button_style()
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        config["profiles"][current_prof]["mouse"]["move_mode"] = checked
        config_manager.save_config(config)

# modules/mouse/mouse_module.py ( 6 часть из 7 )
    def on_click_button_clicked(self, checked):
        """Логика кнопки Клик с защитой от случайного отключения автоматического нажатия"""
        # Если пользователь ВКЛЮЧАЕТ клик — делаем это сразу без окон подтверждения
        if checked:
            self.execute_click_logic(True)
        else:
            # Если выключает — блокируем и выводим фирменное предупреждение
            from PyQt6.QtWidgets import QMessageBox
            
            msg = QMessageBox(self)
            msg.setWindowTitle("Предупреждение")
            msg.setText("ВНИМАНИЕ!\n\nВы отключаете АВТОМАТИЧЕСКИЙ КЛИК.\nПрограмма ПЕРЕСТАНЕТ нажимать на кнопки при фиксации взгляда.\n\nВы уверены, что хотите остановить клики?")
            msg.setIcon(QMessageBox.Icon.Warning)
            
            yes_btn = msg.addButton("Да, отключить", QMessageBox.ButtonRole.YesRole)
            no_btn = msg.addButton("Отмена", QMessageBox.ButtonRole.NoRole)
            msg.setDefaultButton(no_btn)
            
            msg.setStyleSheet("""
                QMessageBox { background-color: #030a06; border: 2px solid #2ed573; border-radius: 10px; }
                QLabel { color: #ffffff; font-family: 'Segoe UI', sans-serif; font-size: 12px; font-weight: bold; }
                QPushButton { background-color: #05140b; color: #2ed573; border: 1px solid #123d22; border-radius: 4px; padding: 6px 14px; font-weight: bold; min-width: 80px; }
                QPushButton:hover { background-color: #2ed573; color: black; border-color: white; }
            """)
            
            msg.exec()
            
            if msg.clickedButton() == yes_btn:
                self.execute_click_logic(False)
            else:
                # Отмена: возвращаем кнопку назад в нажатое (включенное) состояние
                self.btn_2.setChecked(True)
                self.btn_2.setText("Клик вкл")
                self.update_click_button_style()

    def execute_click_logic(self, checked):
        """Вспомогательный метод для выполнения оригинальной логики переключения клика"""
        if checked:
            self.btn_2.setText("Клик вкл")
        else:
            self.btn_2.setText("Клик выкл")
        self.update_click_button_style()
        
        # Обновляем стили на плавающей панели, если она сейчас открыта на экране
        if self.toolbar_window:
            self.toolbar_window.refresh_all_button_images() 
            
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        config["profiles"][current_prof]["mouse"]["click_mode"] = checked
        config_manager.save_config(config)


    def on_toggle_clicked(self, checked):
        """Логика главного рубильника мыши с защитой от случайного выключения"""
        # Если пользователь ХОЧЕТ ВКЛЮЧИТЬ модуль — включаем мгновенно и без вопросов!
        if checked:
            self.execute_toggle_logic(True)
        else:
            # Если пользователь пытается ВЫКЛЮЧИТЬ — блокируем и запрашиваем подтверждение
            from PyQt6.QtWidgets import QMessageBox
            
            msg = QMessageBox(self)
            msg.setWindowTitle("Предупреждение")
            msg.setText("ВНИМАНИЕ!\n\nВы отключаете главный блок управления мышью.\nЭто приведет к ПОЛНОЙ ПОТЕРЕ КОНТРОЛЯ над курсором через голову.\n\nВы уверены, что хотите отключить модуль?")
            msg.setIcon(QMessageBox.Icon.Warning)
            
            # Добавляем стандартные кнопки
            yes_btn = msg.addButton("Да, отключить", QMessageBox.ButtonRole.YesRole)
            no_btn = msg.addButton("Отмена", QMessageBox.ButtonRole.NoRole)
            msg.setDefaultButton(no_btn)
            
            # Стилизуем окно под ваш фирменный неоновый зелено-фиолетовый интерфейс
            msg.setStyleSheet("""
                QMessageBox { background-color: #030a06; border: 2px solid #2ed573; border-radius: 10px; }
                QLabel { color: #ffffff; font-family: 'Segoe UI', sans-serif; font-size: 12px; font-weight: bold; }
                QPushButton { background-color: #05140b; color: #2ed573; border: 1px solid #123d22; border-radius: 4px; padding: 6px 14px; font-weight: bold; min-width: 80px; }
                QPushButton:hover { background-color: #2ed573; color: black; border-color: white; }
            """)
            
            # Запускаем окно
            msg.exec()
            
            if msg.clickedButton() == yes_btn:
                # Пользователь осознанно подтвердил выключение
                self.execute_toggle_logic(False)
            else:
                # Отмена: возвращаем тумблер в активное (нажатое) состояние
                self.toggle_btn.setChecked(True)
                self.update_toggle_style()

# modules/mouse/mouse_module.py ( 7 часть из 7 )
    def execute_toggle_logic(self, checked):
        """Вспомогательный метод для выполнения оригинальной логики главного тумблера"""
        self.update_autoclicker_status(checked)
        self.update_toggle_style()
        
        # Если выключили главный рубильник мыши — жестко принудительно прячем плавающую панель ИИ
        if not checked and self.toolbar_window:
            self.toolbar_window.close()
            self.toolbar_window = None
            self.btn_3.setChecked(False)
            self.btn_3.setText("Панель ИИ выкл")
            self.update_toolbar_button_style()
            
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        config["profiles"][current_prof]["mouse"]["main_toggle"] = checked
        config["profiles"][current_prof]["mouse"]["autoclicker"] = checked
        if not checked:
            config["profiles"][current_prof]["mouse"]["toolbar_enabled"] = False
        config_manager.save_config(config)

    def update_autoclicker_status(self, is_enabled):
        """Обновление текстового статуса работы ИИ-автокликера"""
        if is_enabled:
            self.ac_value.setText("Включено")
            self.ac_value.setStyleSheet(f"color: {styles.COLOR_GREEN}; font-weight: bold; font-size: 11px; background: transparent; border: none; margin-top: 4px;")
        else:
            self.ac_value.setText("Отключен")
            self.ac_value.setStyleSheet(f"color: {styles.TEXT_MUTED}; font-size: 11px; background: transparent; border: none; margin-top: 4px;")

    def on_panel_btn_clicked(self):
        """ЖЕСТКИЙ ФИКС ДВОЙНОГО КЛИКА: Управление панелью со сбросом и временным дебаунс-барьером"""
        self.is_panel_shown = not self.is_panel_shown
        
        # Получаем прямую ссылку на главное окно
        main_win = self.window()
        
        if main_win:
            import time
            # ВЗВОДИМ 1.5-СЕКУНДНЫЙ НЕПРОБИВАЕМЫЙ БАРЬЕР ЗАЩИТЫ ОТ ПУЛЕМЕТА
            main_win.last_panel_switch_time = time.time()
            
            # Сбрасываем базовый кликер главного окна в текущей точке
            if hasattr(main_win, 'dwell_clicker') and main_win.dwell_clicker:
                pos = QCursor.pos()
                main_win.dwell_clicker.reset(float(pos.x()), float(pos.y()))
                main_win.dwell_clicker.force_reset_to_default_left()
                
            # Управляем видимостью Advanced Panel
            if hasattr(main_win, 'advanced_panel_window') and main_win.advanced_panel_window:
                if self.is_panel_shown:
                    main_win.advanced_panel_window.show()
                else:
                    main_win.advanced_panel_window.hide()
        
        if self.is_panel_shown:
            self.panel_value.setText("Включено")
            self.panel_value.setStyleSheet(f"color: {styles.COLOR_GREEN}; font-weight: bold; font-size: 11px; background: transparent; border: none; margin-top: 4px;")
            self.btn_show_panel.setText("Скрыть панель")
        else:
            self.panel_value.setText("Скрыта")
            self.panel_value.setStyleSheet(f"color: {styles.TEXT_MUTED}; font-size: 11px; background: transparent; border: none; margin-top: 4px;")
            self.btn_show_panel.setText("Показать панель")
            
        self.btn_show_panel.setStyleSheet("""
            QPushButton { background-color: #05140b; color: #2ed573; border: 1px solid #10381f; border-radius: 4px; font-size: 11px; }
            QPushButton:hover { background-color: #2ed573; color: black; border-color: white; }
        """)
        
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        config["profiles"][current_prof]["mouse"]["panel_on_screen"] = self.is_panel_shown
        config_manager.save_config(config)

    def update_toggle_style(self):
        """Обновление неонового вида главного тумблера включения мыши"""
        if self.toggle_btn.isChecked():
            self.toggle_btn.setStyleSheet("""
                QPushButton { background-color: #2ed573; border: 1px solid #26b361; border-radius: 10px; text-align: right; padding-right: 0px; color: white; font-size: 34px; font-weight: bold; padding-top: -10px; padding-bottom: 0px; }
            """)
            self.toggle_btn.setText("●")
        else:
            self.toggle_btn.setStyleSheet("""
                QPushButton { background-color: #10381f; border: 1px solid #123d22; border-radius: 10px; text-align: left; padding-left: 0px; color: white; font-size: 34px; font-weight: bold; padding-top: -10px; padding-bottom: 0px; }
            """)
            self.toggle_btn.setText("●")
