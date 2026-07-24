# modules/mouse/mouse_sett2.py - ЧАСТЬ 1 ИЗ 5
import os
import sys
import config_manager
import styles
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider, QCheckBox, QSpinBox, QComboBox
from PyQt6.QtCore import Qt

class MouseSettingBlock2(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingCard")
        
        # ЗАГРУЖАЕМ сохраненные настройки из JSON файла при старте
        self.config = config_manager.load_config()
        self.current_prof = self.config.get("current_profile", "Default Profile")
        self.mouse_data = self.config["profiles"][self.current_prof]["mouse"]
        
        # УЛЬТРА-СТИЛИЗАЦИЯ: Добавлена видимая неоновая зеленая прокрутка для списка звуков
        self.setStyleSheet("""
            QFrame#SettingCard { background-color: #030a06; border: 1px solid #10381f; border-radius: 10px; }
            QLabel { color: #ffffff; font-family: 'Segoe UI', sans-serif; font-size: 12px; background: transparent; border: none; }
            
            /* Ползунки мыши */
            QSlider::groove:horizontal { border: 1px solid #123d22; height: 4px; background: #05140b; border-radius: 2px; }
            QSlider::sub-page:horizontal { background: #2ed573; border-radius: 2px; }
            QSlider::handle:horizontal {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0 #ffffff, stop:0.3 #2ed573, stop:1 rgba(46,213,115,0));
                width: 16px; height: 16px; margin: -6px 0; border-radius: 8px;
            }
            
            /* Чекбоксы мыши */
            QCheckBox { color: #ffffff; font-size: 12px; spacing: 8px; background: transparent; border: none; }
            QCheckBox::indicator { width: 14px; height: 14px; border: 1px solid #123d22; border-radius: 3px; background-color: #05140b; }
            QCheckBox::indicator:checked { background-color: #2ed573; border-color: #ffffff; }
            QCheckBox::indicator:hover { border-color: #2ed573; }
            
            /* Спинбоксы и Комбобоксы */
            QSpinBox, QComboBox {
                background-color: #05140b; color: #ffffff; border: 1px solid #123d22; border-radius: 4px;
                padding-left: 5px; font-size: 11px; font-weight: 500;
            }
            QComboBox QAbstractItemView {
                background-color: #05140b; color: #ffffff; border: 1px solid #123d22;
                selection-background-color: #2ed573; selection-color: #000000; outline: none;
            }
            
            /* ФИРМЕННАЯ ЗЕЛЕНАЯ СТИЛИЗАЦИЯ СКРОЛЛБАРА ДЛЯ ВЫПАДАЮЩЕГО СПИСКА */
            QComboBox QAbstractItemView QScrollBar:vertical {
                border: 1px solid #123d22; background-color: #05140b; width: 20px; margin: 0px; border-radius: 4px;
            }
            QComboBox QAbstractItemView QScrollBar::handle:vertical { background-color: #123d22; border: 1px solid #2ed573; min-height: 15px; border-radius: 3px; }
            QComboBox QAbstractItemView QScrollBar::handle:vertical:hover { background-color: #2ed573; border-color: #ffffff; }
            QComboBox QAbstractItemView QScrollBar::add-line:vertical, QComboBox QAbstractItemView QScrollBar::sub-line:vertical { border: none; background: none; height: 0px; }
            QComboBox QAbstractItemView QScrollBar::add-page:vertical, QComboBox QAbstractItemView QScrollBar::sub-page:vertical { background: none; }
            
            /* Зеленый внутренний квадрат настроек справа */
            QFrame#GreenBox { background-color: #020804; border: 1px solid #2ed573; border-radius: 6px; }
        """)
# modules/mouse/mouse_sett2.py - ЧАСТЬ 2 ИЗ 5
        # Главный вертикальный слой карточки
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 12, 15, 12)
        main_layout.setSpacing(8)
        
        # Верхняя строка: Иконка + Заголовок + Свитч
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)
        
        ico = QLabel()
        ico.setStyleSheet("background: transparent; border: none;")
        from PyQt6.QtGui import QPixmap
        pix = QPixmap(styles.get_image("mouse1.png"))
        if not pix.isNull():
            ico.setPixmap(pix.scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        top_layout.addWidget(ico)
        
        title = QLabel("Настройка Кликов и Отображения")
        title.setStyleSheet("color: #ffffff; font-size: 13px; font-weight: bold; background: transparent; border: none;")
        top_layout.addWidget(title)
        top_layout.addStretch()
        
        self.toggle = QPushButton("●")
        self.toggle.setCheckable(True)
        self.toggle.setChecked(self.mouse_data.get("setting_2", True))
        self.toggle.setFixedSize(44, 20)
        self.toggle.setStyleSheet("background-color: #2ed573; border: none; border-radius: 10px; text-align: right; padding-right: 0px; color: white; font-size: 34px; font-weight: bold; padding-top: -10px;")
        top_layout.addWidget(self.toggle)
        main_layout.addLayout(top_layout)
        
        # Тонкая линия разделителя
        line = QFrame(); line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #123d22; min-height: 1px; max-height: 1px; border: none;")
        main_layout.addWidget(line)
        
        # ОСНОВНОЙ ГОРИЗОНТАЛЬНЫЙ СЛОЙ ДЛЯ ДЕЛЕНИЯ НА ЛЕВУЮ ПАНЕЛЬ И ПРАВЫЙ ЗЕЛЕНЫЙ КВАДРАТ
        content_hbox = QHBoxLayout()
        content_hbox.setSpacing(15)
        
        # ЛЕВАЯ ЧАСТЬ: Ползунки и Чекбоксы
        left_panel_layout = QVBoxLayout()
        left_panel_layout.setSpacing(6)
        
        saved_delay = int(self.mouse_data.get("click_delay", 0.6) * 10)
        delay_txt_layout = QHBoxLayout()
        delay_lbl = QLabel("Задержка срабатывания клика:")
        self.lbl_delay_val = QLabel(f"{saved_delay / 10.0} сек")
        self.lbl_delay_val.setStyleSheet("color: #2ed573; font-weight: bold;")
        delay_txt_layout.addWidget(delay_lbl); delay_txt_layout.addStretch(); delay_txt_layout.addWidget(self.lbl_delay_val)
        left_panel_layout.addLayout(delay_txt_layout)
        
        self.slider_delay = QSlider(Qt.Orientation.Horizontal)
        self.slider_delay.setRange(2, 20)  
        self.slider_delay.setValue(saved_delay)
        self.slider_delay.valueChanged.connect(self.on_delay_changed)
        left_panel_layout.addWidget(self.slider_delay)
        
        # Ползунок Радиуса удержания (ПО ВАШЕМУ ТЗ: СТРОГО ОТ 1 ДО 20 ПИКСЕЛЕЙ)
        saved_radius = int(self.mouse_data.get("click_radius", 15))
        if saved_radius > 20: saved_radius = 20
        if saved_radius < 1: saved_radius = 1
        
        radius_txt_layout = QHBoxLayout()
        radius_lbl = QLabel("Область удержания (Радиус):")
        self.lbl_radius_val = QLabel(f"{saved_radius} px")
        self.lbl_radius_val.setStyleSheet("color: #2ed573; font-weight: bold;")
        radius_txt_layout.addWidget(radius_lbl); radius_txt_layout.addStretch(); radius_txt_layout.addWidget(self.lbl_radius_val)
        left_panel_layout.addLayout(radius_txt_layout)
        
        self.slider_radius = QSlider(Qt.Orientation.Horizontal)
        self.slider_radius.setRange(1, 20)  
        self.slider_radius.setValue(saved_radius)
        self.slider_radius.valueChanged.connect(self.on_radius_changed)
        left_panel_layout.addWidget(self.slider_radius)
        left_panel_layout.addSpacing(5)
# modules/mouse/mouse_sett2.py - ЧАСТЬ 3 ИЗ 5
        # 4 Флажка слева
        self.chk_win_mouse = QCheckBox("Управление системной мышью Windows")
        self.chk_win_mouse.setChecked(self.mouse_data.get("use_win_mouse", True))
        self.chk_win_mouse.stateChanged.connect(self.on_win_mouse_changed)
        left_panel_layout.addWidget(self.chk_win_mouse)
        
        self.chk_custom_cursor = QCheckBox("Отображать кастомный ИИ-курсор (картинку)")
        self.chk_custom_cursor.setChecked(self.mouse_data.get("show_custom_cursor", False))
        self.chk_custom_cursor.stateChanged.connect(self.on_custom_cursor_changed)
        left_panel_layout.addWidget(self.chk_custom_cursor)
        
        self.chk_show_circle = QCheckBox("Показывать круговую индикацию перед кликом")
        self.chk_show_circle.setChecked(self.mouse_data.get("show_click_circle", True))
        self.chk_show_circle.stateChanged.connect(self.on_show_circle_changed)
        left_panel_layout.addWidget(self.chk_show_circle)
        
        self.chk_sound = QCheckBox("Звуковое подтверждение клика (Сигнал)")
        self.chk_sound.setChecked(self.mouse_data.get("click_sound_enabled", True))
        self.chk_sound.stateChanged.connect(self.on_sound_changed)
        left_panel_layout.addWidget(self.chk_sound)
        
        content_hbox.addLayout(left_panel_layout, stretch=2)

        # ПРАВАЯ ЧАСТЬ: Зеленый внутренний квадрат (Расширенные настройки звука и времени клика)
        self.right_box_frame = QFrame()
        self.right_box_frame.setObjectName("GreenBox")
        self.right_box_frame.setFixedWidth(240)
        
        right_box_lay = QVBoxLayout(self.right_box_frame)
        right_box_lay.setContentsMargins(12, 12, 12, 12)
        right_box_lay.setSpacing(8)
        
        hold_time_layout = QHBoxLayout()
        hold_time_layout.setSpacing(8)
        
        lbl_hold_title = QLabel("время клика")
        lbl_hold_title.setStyleSheet("font-weight: 500;")
        lbl_hold_title.setFixedWidth(75)
        
        self.spin_hold = QSpinBox()
        self.spin_hold.setRange(10, 5000)
        self.spin_hold.setSingleStep(10)
        
        # Наша идеальная ширина в 90 пикселей из скриншота
        self.spin_hold.setFixedSize(90, 24)
        self.spin_hold.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # ЖЁСТКИЙ ФИКС БЛОКИРОВКИ СТРЕЛОЧЕК (0% ОШИБОК КОМПИЛЯЦИИ):
        self.spin_hold.setButtonSymbols(QSpinBox.ButtonSymbols.UpDownArrows)
        
        # Запрещаем текстовому полю выделяться, переопределяя событие клика через пустую функцию
        self.spin_hold.lineEdit().mousePressEvent = lambda event: None
        
        # Полностью отключаем фокус ввода, чтобы клавиатура не забирала клики со стрелочек
        self.spin_hold.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.spin_hold.lineEdit().setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        # Заставляем текстовое поле пропускать клики мыши насквозь прямо на стрелочки
        self.spin_hold.lineEdit().setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        
        saved_hold_ms = self.mouse_data.get("click_hold_ms", 50)
        if saved_hold_ms < 10 or saved_hold_ms > 5000:
            saved_hold_ms = 50
            
        self.spin_hold.setValue(saved_hold_ms)
        self.spin_hold.valueChanged.connect(self.on_hold_time_changed)


# modules/mouse/mouse_sett2.py - ЧАСТЬ 4 ИЗ 5
        # ЖЁСТКИЙ ИНТЕРФЕЙСНЫЙ ФИКС ПО ТЗ: урезаем ширину надписи и сдвигаем её,
        # чтобы она физически не могла перекрыть стрелочку "Вверх" спинбокса!
        lbl_hold_unit = QLabel("мсек")
        lbl_hold_unit.setFixedWidth(40)
        lbl_hold_unit.setStyleSheet("QLabel { padding-left: 6px; color: #ffffff; background: transparent; border: none; }")
        
        hold_time_layout.addWidget(lbl_hold_title)
        hold_time_layout.addWidget(self.spin_hold)
        hold_time_layout.addWidget(lbl_hold_unit)
        hold_time_layout.addStretch() # Пружина-отступ: освобождает доступ к кнопке Вверх
        right_box_lay.addLayout(hold_time_layout)

        # 2. Строка ВЫБОРA ЗВУКA КЛИКА (ComboBox)
        lbl_sound_title = QLabel("Звук клика:")
        lbl_sound_title.setStyleSheet("color: #a1a3b5; font-size: 11px;")
        right_box_lay.addWidget(lbl_sound_title)
        
        self.combo_sounds = QComboBox()
        self.combo_sounds.setFixedHeight(26)
        self.combo_sounds.addItem("default")
        
        self.scan_sounds_directory()
        
        saved_sound_file = self.mouse_data.get("selected_sound_file", "default")
        idx_sound = self.combo_sounds.findText(saved_sound_file)
        if idx_sound >= 0:
            self.combo_sounds.setCurrentIndex(idx_sound)
            
        self.combo_sounds.currentTextChanged.connect(self.on_sound_file_selected)
        right_box_lay.addWidget(self.combo_sounds)
        
        # 3. Кнопка ОТКРЫТИЯ ПАПКИ СО ЗВУКАМИ
        self.btn_open_folder = QPushButton("Папка со звуками")
        self.btn_open_folder.setFixedHeight(26)
        self.btn_open_folder.setStyleSheet("QPushButton { background-color: #05140b; color: #2ed573; border: 1px solid #123d22; border-radius: 4px; font-size: 11px; font-weight: 500; } QPushButton:hover { background-color: #2ed573; color: black; border-color: white; }")
        self.btn_open_folder.clicked.connect(self.open_sounds_folder_in_explorer)
        right_box_lay.addWidget(self.btn_open_folder)
        
        # 4. НАСТРОЙКА ГРОМКОСТИ КЛИКА
        saved_vol = int(self.mouse_data.get("click_volume", 80))
        self.lbl_vol_title = QLabel(f"Громкость: {saved_vol}%")
        self.lbl_vol_title.setStyleSheet("color: #ffffff; font-size: 11px; font-weight: 500; margin-top: 4px;")
        right_box_lay.addWidget(self.lbl_vol_title)
        
        self.slider_volume = QSlider(Qt.Orientation.Horizontal)
        self.slider_volume.setRange(0, 100)
        self.slider_volume.setValue(saved_vol)
        self.slider_volume.setFixedHeight(18)
        self.slider_volume.valueChanged.connect(self.on_volume_changed)
        right_box_lay.addWidget(self.slider_volume)
        
        # Кнопка Сброса настроек клика по умолчанию
        self.btn_reset_clicks = QPushButton("Сбросить по умолчанию")
        self.btn_reset_clicks.setFixedHeight(24)
        self.btn_reset_clicks.setStyleSheet("QPushButton { background-color: #05140b; color: #2ed573; border: 1px solid #123d22; border-radius: 4px; font-size: 11px; font-weight: 500; } QPushButton:hover { background-color: #b22222; color: #ffffff; border-color: #ffffff; }")
        self.btn_reset_clicks.clicked.connect(self.on_reset_clicks_clicked)
        right_box_lay.addWidget(self.btn_reset_clicks)
        
        right_box_lay.addStretch()
        content_hbox.addWidget(self.right_box_frame, stretch=1)
        main_layout.addLayout(content_hbox)
        main_layout.addStretch()

# modules/mouse/mouse_sett2.py - ЧАСТЬ 5 ИЗ 5
    def scan_sounds_directory(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        sound_folder = os.path.join(base_dir, "sounds")
        if not os.path.exists(sound_folder):
            try: os.makedirs(sound_folder)
            except Exception: return
        try:
            for file_name in os.listdir(sound_folder):
                if file_name.lower().endswith(".wav"):
                    self.combo_sounds.addItem(file_name)
        except Exception: pass

    def open_sounds_folder_in_explorer(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        sound_folder = os.path.join(base_dir, "sounds")
        if os.path.exists(sound_folder):
            try: os.startfile(sound_folder)
            except Exception: pass

    def on_volume_changed(self, value):
        self.lbl_vol_title.setText(f"Громкость: {value}%")
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        config["profiles"][current_prof]["mouse"]["click_volume"] = int(value)
        config_manager.save_config(config)

    def on_hold_time_changed(self, value):
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        config["profiles"][current_prof]["mouse"]["click_hold_ms"] = int(value)
        config_manager.save_config(config)

    def on_sound_file_selected(self, sound_name):
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        config["profiles"][current_prof]["mouse"]["selected_sound_file"] = sound_name
        config_manager.save_config(config)

    def on_delay_changed(self, value):
        float_val = value / 10.0
        self.lbl_delay_val.setText(f"{float_val} сек")
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        config["profiles"][current_prof]["mouse"]["click_delay"] = float_val
        config_manager.save_config(config)

    def on_radius_changed(self, value):
        self.lbl_radius_val.setText(f"{value} px")
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        config["profiles"][current_prof]["mouse"]["click_radius"] = int(value)
        config_manager.save_config(config)

    def on_win_mouse_changed(self, state):
        bool_val = (state == 2)
        if bool_val:
            self.execute_win_mouse_logic(True)
        else:
            from PyQt6.QtWidgets import QMessageBox
            msg = QMessageBox(self)
            msg.setWindowTitle("Предупреждение")
            msg.setText("ВНИМАНИЕ!\n\nВы отключаете управление СИСТЕМНОЙ мышью Windows.\nКурсор ОС перестанет двигаться за вашей головой.\n\nВы уверены, что хотите отключить системную мышь?")
            msg.setIcon(QMessageBox.Icon.Warning)
            yes_btn = msg.addButton("Да, отключить", QMessageBox.ButtonRole.YesRole)
            no_btn = msg.addButton("Отмена", QMessageBox.ButtonRole.NoRole)
            msg.setDefaultButton(no_btn)
            msg.setStyleSheet("QMessageBox { background-color: #030a06; border: 2px solid #2ed573; border-radius: 10px; } QLabel { color: #ffffff; font-family: 'Segoe UI', sans-serif; font-size: 12px; font-weight: bold; } QPushButton { background-color: #05140b; color: #2ed573; border: 1px solid #123d22; border-radius: 4px; padding: 6px 14px; font-weight: bold; min-width: 80px; } QPushButton:hover { background-color: #2ed573; color: black; border-color: white; }")
            msg.exec()
            if msg.clickedButton() == yes_btn:
                self.execute_win_mouse_logic(False)
            else:
                self.chk_win_mouse.blockSignals(True)
                self.chk_win_mouse.setChecked(True)
                self.chk_win_mouse.blockSignals(False)

    def execute_win_mouse_logic(self, bool_val):
       config = config_manager.load_config()
       current_prof = config.get("current_profile", "Default Profile")
       config["profiles"][current_prof]["mouse"]["use_win_mouse"] = bool_val
       config_manager.save_config(config)

    def on_custom_cursor_changed(self, state):
       config = config_manager.load_config()
       current_prof = config.get("current_profile", "Default Profile")
       config["profiles"][current_prof]["mouse"]["show_custom_cursor"] = (state == 2)
       config_manager.save_config(config)

    def on_show_circle_changed(self, state):
       config = config_manager.load_config()
       current_prof = config.get("current_profile", "Default Profile")
       config["profiles"][current_prof]["mouse"]["show_click_circle"] = (state == 2)
       config_manager.save_config(config)

    def on_sound_changed(self, state):
       config = config_manager.load_config()
       current_prof = config.get("current_profile", "Default Profile")
       config["profiles"][current_prof]["mouse"]["click_sound_enabled"] = (state == 2)
       config_manager.save_config(config)

    def on_reset_clicks_clicked(self):
       self.slider_delay.setValue(6)      
       self.slider_radius.setValue(8)     
       self.spin_hold.setValue(50)         
       self.chk_win_mouse.setChecked(True)
       self.chk_custom_cursor.setChecked(False)
       self.chk_show_circle.setChecked(True)
       self.chk_sound.setChecked(True)
