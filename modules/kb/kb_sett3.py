# modules/kb_sett3.py - ЧАСТЬ 1 ИЗ 5 (ОФИЦИАЛЬНОЕ РОЖДЕНИЕ КНОПКИ K+ В МАТРИЦЕ) База.
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import styles
import config_manager

class KeyboardSettingBlock3(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingCard3")
        
        # Загружаем конфигурацию профиля
        self.config = config_manager.load_config()
        self.current_prof = self.config.get("current_profile", "Default Profile")
        self.kb_data = self.config["profiles"][self.current_prof]["kb"]
        
        # КЭШ В ОЗУ ДЛЯ СВЕРХБЫСТРОГО ДОСТУПА К СПИСКУ ВЫБРАННЫХ НАЭКРАННЫХ КЛAВИШ
        self.selected_overlay_keys = self.kb_data.get("overlay_selected_keys", [])
        
        # Словарь для хранения ссылок на физические объекты кнопок матрицы
        self.matrix_buttons = {}
        
        # Единый темно-фиолетовый неоновый стиль по вашему золотому стандарту
        self.setStyleSheet("""
            QFrame#SettingCard3 { background-color: #04030d; border: 1px solid #1a1038; border-radius: 10px; }
            QLabel { color: #ffffff; font-family: 'Segoe UI', sans-serif; font-size: 11px; background: transparent; border: none; }
        """)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(12, 10, 12, 12)
        self.main_layout.setSpacing(6)
        
        # Верхняя строка: Иконка + Короткий заголовок + Кнопка «Вкл нажатия» + Свитч сворачивания
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)
        
        ico = QLabel()
        ico.setStyleSheet("background: transparent; border: none;")
        pix = QPixmap(styles.get_image("kb1.png"))
        if not pix.isNull():
            ico.setPixmap(pix.scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        top_layout.addWidget(ico)
        
        title = QLabel("Горячие клавиши")
        title.setStyleSheet("color: #ffffff; font-size: 13px; font-weight: bold;")
        top_layout.addWidget(title)
        top_layout.addStretch()
        
        # СТРОГО ПО ТЗ: Добавлена интерактивная кнопка физического переключения наэкранного ввода в ОС
        self.btn_overlay_press = QPushButton()
        self.btn_overlay_press.setCheckable(True)
        
        # Загружаем сохраненный статус эмуляции (по дефолту True — нажимать кнопки в Windows)
        saved_press_state = self.kb_data.get("overlay_press_enabled", True)
        self.btn_overlay_press.setChecked(saved_press_state)
        self.btn_overlay_press.setFixedSize(105, 22)
        self.btn_overlay_press.clicked.connect(self.on_overlay_press_toggle_clicked)
        top_layout.addWidget(self.btn_overlay_press)
        
        # НАШ КРАСИВЫЙ РОДНОЙ СВИТЧ СВОРАЧИВАНИЯ С БЕЛЫМ КРУГЛЯШКОМ ●
        self.toggle = QPushButton("●")
        self.toggle.setCheckable(True)
        saved_open_state = self.kb_data.get("setting_3", True)
        self.toggle.setChecked(saved_open_state)
        self.toggle.setFixedSize(44, 20)
        self.toggle.clicked.connect(self.on_setting_toggle_clicked)
        top_layout.addWidget(self.toggle)
        self.main_layout.addLayout(top_layout)
        
        self.line = QFrame(); self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setStyleSheet("background-color: #1a1038; min-height: 1px; max-height: 1px; border: none;")
        self.main_layout.addWidget(self.line)
        
        # Контейнер для полной матрицы букв
        self.container = QWidget()
        self.matrix_vbox = QVBoxLayout(self.container)
        self.matrix_vbox.setContentsMargins(0, 0, 0, 0)
        self.matrix_vbox.setSpacing(4)
        
        # ИСПРАВЛЕНО НА 100%: Клавиша F9 полностью стёрта, вместо неё встала кнопка K+ шириной 30px!
        row0_layout = QHBoxLayout(); row0_layout.setSpacing(3)
        self.create_matrix_button("Esc", 35, row0_layout)
        row0_layout.addSpacing(15)
        self.create_matrix_button("LMB", 30, row0_layout)
        self.create_matrix_button("RMB", 30, row0_layout)
        self.create_matrix_button("MMB", 30, row0_layout)
        self.create_matrix_button("OSK", 30, row0_layout)
        self.create_matrix_button("ЛП", 30, row0_layout)
        self.create_matrix_button("СК", 30, row0_layout)  
        self.create_matrix_button("APP", 30, row0_layout)  
        row0_layout.addSpacing(10)
        self.create_matrix_button("CTR", 30, row0_layout)   
        row0_layout.addSpacing(10)
        
        # Создаем кнопку K+ шириной 30px ровно на месте бывшей f9
        self.create_matrix_button("K+", 30, row0_layout)
        for f_key in ["F10", "F11", "F12"]: self.create_matrix_button(f_key, 30, row0_layout)
        self.matrix_vbox.addLayout(row0_layout)
        self.matrix_vbox.addSpacing(4)

# modules/kb_sett3.py - ЧАСТЬ 2 ИЗ 5
        # РЯД 1: Цифры и спецсимволы
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(3)
        num_keys = ["~", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", "Backspace"]
        for key in num_keys:
            w = 55 if key == "Backspace" else 30
            self.create_matrix_button(key, w, row1_layout)
        self.matrix_vbox.addLayout(row1_layout)

        # РЯД 2: Буквенный ряд QWERTY с кнопкой Tab
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(3)
        self.create_matrix_button("Tab", 45, row2_layout)
        q_keys = ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "[", "]", "\\"]
        for key in q_keys:
            self.create_matrix_button(key, 30, row2_layout)
        self.matrix_vbox.addLayout(row2_layout)

        # РЯД 3: Буквенный ряд ASDFG с кнопками Caps и Enter
        row3_layout = QHBoxLayout()
        row3_layout.setSpacing(3)
        self.create_matrix_button("Caps", 52, row3_layout)
        a_keys = ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";", "'"]
        for key in a_keys:
            self.create_matrix_button(key, 30, row3_layout)
        self.create_matrix_button("Enter", 58, row3_layout)
        self.matrix_vbox.addLayout(row3_layout)

        # РЯД 4: Буквенный ряд ZXCVB с кнопками Shift
        row4_layout = QHBoxLayout()
        row4_layout.setSpacing(3)
        self.create_matrix_button("LShift", 70, row4_layout)
        z_keys = ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"]
        for key in z_keys:
            self.create_matrix_button(key, 30, row4_layout)
        self.create_matrix_button("RShift", 75, row4_layout)
        self.matrix_vbox.addLayout(row4_layout)

        # РЯД 5: Системные клавиши (Ctrl, Alt, Пробел) и Стрелочки управления
        row5_layout = QHBoxLayout()
        row5_layout.setSpacing(3)
        self.create_matrix_button("LCtrl", 40, row5_layout)
        self.create_matrix_button("Win", 35, row5_layout)
        self.create_matrix_button("LAlt", 40, row5_layout)
        self.create_matrix_button("Space", 135, row5_layout)  
        self.create_matrix_button("RAlt", 40, row5_layout)
        self.create_matrix_button("RCtrl", 40, row5_layout)
        
        row5_layout.addSpacing(10)
        self.create_matrix_button("🡠", 30, row5_layout)
        
        arrow_vbox = QVBoxLayout()
        arrow_vbox.setSpacing(2)
        self.create_matrix_button("🡡", 30, arrow_vbox, height=14)
        self.create_matrix_button("🡣", 30, arrow_vbox, height=14)
        row5_layout.addLayout(arrow_vbox)
        
        self.create_matrix_button("🡢", 30, row5_layout)
        self.matrix_vbox.addLayout(row5_layout)

        self.main_layout.addWidget(self.container)
        self.apply_visibility_layout_state(saved_open_state)

    def on_overlay_press_toggle_clicked(self, checked):
        """Слот обработки клика по кнопке 'Вкл нажатия' оверлеев с защитным окном по вашему ТЗ"""
        if not checked:
            # Если пользователь ВЫКЛЮЧАЕТ физический зажим оверлейных кнопок мыши в ОС — выводим QMessageBox
            from PyQt6.QtWidgets import QMessageBox
            msg = QMessageBox(self)
            msg.setWindowTitle("Предупреждение системы")
            msg.setText("ВНИМАНИЕ!\n\nВы отключаете физическую эмуляцию НАЭКРАННЫХ кнопок мыши (LMB/RMB) в Windows.\n\nГорячие клавиши на экране перестанут нажимать кран и газ в играх (останется только визуальная подсветка).\n\nВы уверены?")
            msg.setIcon(QMessageBox.Icon.Warning)
            
            yes_btn = msg.addButton("Да, отключить", QMessageBox.ButtonRole.YesRole)
            no_btn = msg.addButton("Отмена", QMessageBox.ButtonRole.NoRole)
            msg.setDefaultButton(no_btn)
            
            msg.setStyleSheet("QMessageBox { background-color: #04030d; border: 2px solid #8a2be2; border-radius: 10px; } QLabel { color: #ffffff; font-family: 'Segoe UI', sans-serif; font-size: 12px; font-weight: bold; } QPushButton { background-color: #0b0617; color: #a347ff; border: 1px solid #401970; border-radius: 4px; padding: 5px 12px; font-weight: bold; } QPushButton:hover { background-color: #8a2be2; color: white; border-color: white; }")
            msg.exec()
            
            if msg.clickedButton() != yes_btn:
                # Отмена: принудительно возвращаем кнопку в активное включенное положение
                self.btn_overlay_press.blockSignals(True)
                self.btn_overlay_press.setChecked(True)
                self.btn_overlay_press.blockSignals(False)
                self.update_real_press_button_style()
                return

        # Фиксируем и сохраняем подтвержденный статус
        self.update_real_press_button_style()
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        config["profiles"][current_prof]["kb"]["overlay_press_enabled"] = self.btn_overlay_press.isChecked()

        config_manager.save_config(config)

# modules/kb_sett3.py - ЧАСТЬ 3 ИЗ 5 
    def update_real_press_button_style(self):
        """Переключает неоновые стили кнопки (зеленый/красный) в зависимости от активности аппаратного ввода"""
        if self.btn_overlay_press.isChecked():
            self.btn_overlay_press.setText("Включено нажатия")
            self.btn_overlay_press.setStyleSheet("QPushButton { background-color: #0c2414; color: #2ed573; border: 1px solid #2ed573; border-radius: 4px; font-size: 10px; font-weight: bold; } QPushButton:hover { background-color: #2ed573; color: black; border-color: white; }")
        else:
            self.btn_overlay_press.setText("Выключено нажатия")
            self.btn_overlay_press.setStyleSheet("QPushButton { background-color: #160a0f; color: #ff4757; border: 1px solid #ff4757; border-radius: 4px; font-size: 10px; font-weight: bold; } QPushButton:hover { background-color: #ff4757; color: white; border-color: white; }")

    def create_matrix_button(self, text, width, target_layout, height=30):
        """Создает индивидуальную кнопку для матрицы выбора горячих наэкранных клавиш"""
        btn = QPushButton(text)
        btn.setFixedSize(width, height)
        btn.clicked.connect(lambda checked, t=text: self.open_overlay_mode_dialog(t))
        self.matrix_buttons[text] = btn
        target_layout.addWidget(btn)

    def open_overlay_mode_dialog(self, key_text):
        """Всплывающее КАСТОМНОЕ безрамочное окно выбора режимов работы оверлея и сброса позиции"""
        from PyQt6.QtWidgets import QDialog, QComboBox, QApplication
        from PyQt6.QtCore import QTimer
        
        dialog = QDialog(self)
        dialog.setFixedSize(360, 225)
        dialog.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        
        dialog.setStyleSheet("""
            QDialog { background-color: #04030d; border: 2px solid #8a2be2; border-radius: 12px; }
            QLabel { color: #ffffff; font-family: 'Segoe UI', sans-serif; font-size: 12px; font-weight: bold; background: transparent; border: none; }
            QComboBox {
                background-color: #0b0617; color: #ffffff; border: 1px solid #401970; border-radius: 4px;
                padding-left: 5px; font-size: 11px; font-weight: bold; height: 26px;
            }
            QComboBox QAbstractItemView {
                background-color: #0b0617; color: #ffffff; border: 1px solid #401970;
                outline: none;
            }
            QComboBox QAbstractItemView::item:selected, QComboBox QAbstractItemView::item:hover {
                background-color: #00d2ff !important;
                color: #000000 !important;
                font-weight: bold;
            }
            QComboBox QAbstractItemView QScrollBar:vertical {
                border: 1px solid #1a1038; background-color: #04030d; width: 12px; margin: 0px; border-radius: 6px;
            }
            QComboBox QAbstractItemView QScrollBar::handle:vertical {
                background-color: #401970; border: 2px solid #8a2be2; min-height: 20px; border-radius: 4px;
            }
            QComboBox QAbstractItemView QScrollBar::handle:vertical:hover { background-color: #8a2be2; border-color: #ffffff; }
            QComboBox QAbstractItemView QScrollBar::add-line:vertical, QComboBox QAbstractItemView QScrollBar::sub-line:vertical { border: none; background: none; height: 0px; }
            QComboBox QAbstractItemView QScrollBar::add-page:vertical, QComboBox QAbstractItemView QScrollBar::sub-page:vertical {
                background-color: #04030d;
                border-radius: 6px;
            }
            
            QPushButton {
                background-color: #0b0617; color: #a347ff; border: 1px solid #401970; border-radius: 4px;
                font-size: 11px; font-weight: bold; height: 28px;
            }
            QPushButton:hover { background-color: #8a2be2; color: white; border-color: white; }
            
            /* СТИЛИЗАЦИЯ ДЛЯ НОВОЙ УМЕНЬШЕННОЙ КНОПКИ СБРОСА КООРДИНАТ */
            QPushButton#BtnResetPos {
                background-color: #160a0f; color: #ff4757; border: 1px solid #ff4757; border-radius: 4px;
                font-size: 10px; font-weight: bold; height: 20px; padding: 0px 10px;
            }
            QPushButton#BtnResetPos:hover { background-color: #ff4757; color: white; border-color: white; }
        """)
        
        dlg_layout = QVBoxLayout(dialog)
        dlg_layout.setContentsMargins(15, 12, 15, 15)
        dlg_layout.setSpacing(10)
        
        title_hbox = QHBoxLayout()
        lbl_title = QLabel(f"ИИ-Режим для оверлея [{key_text.upper()}]")
        title_hbox.addWidget(lbl_title); title_hbox.addStretch()
        
        btn_close = QPushButton("✕")
        btn_close.setFixedSize(22, 22)
        btn_close.setStyleSheet("QPushButton { background-color: #160a0f; color: #ff4757; border: 1px solid #ff4757; border-radius: 5px; font-size: 11px; font-weight: bold; height: 22px; } QPushButton:hover { background-color: #ff4757; color: white; border-color: white; }")
        btn_close.clicked.connect(dialog.reject)
        title_hbox.addWidget(btn_close)
        dlg_layout.addLayout(title_hbox)
        
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        kb_conf = config["profiles"][current_prof].get("kb", {})
        overlay_modes = kb_conf.get("overlay_modes", {})
        
        current_mode = overlay_modes.get(key_text.lower(), "none")
        
        combo_modes = QComboBox()
        
        mode_items = [
            ("none", "выключить оверлей (убрать с экрана)"),
            ("hover", "нажатие при наведении (активно пока мышь внутри)"),
            ("click_once", "нажатие при клике (один импульс на 50 мс)"),
            ("toggle_click", "переключатель кликом — Вкл/Выкл"),
            ("toggle_hover", "переключатель при наведении — Вкл/Выкл"),
            ("click_on_hover_off", "включение кликом, выключение наведением")
        ]
        
        for internal_id, readable_name in mode_items:
            combo_modes.addItem(readable_name, internal_id)
            
        for idx in range(combo_modes.count()):
            if combo_modes.itemData(idx) == current_mode:
                combo_modes.setCurrentIndex(idx)
                break
                
        dlg_layout.addWidget(combo_modes)
        dlg_layout.addSpacing(2)
        
        btn_save = QPushButton("Сохранить ИИ-режим")


# modules/kb/kb_sett3.py - ЧАСТЬ 4 ИЗ 5
        def save_mode_logic():
            selected_id = combo_modes.itemData(combo_modes.currentIndex())
            cfg = config_manager.load_config()
            prof = cfg.get("current_profile", "Default Profile")
            k_conf = cfg["profiles"][prof]["kb"]
            
            if "overlay_selected_keys" not in k_conf: k_conf["overlay_selected_keys"] = []
            if "overlay_modes" not in k_conf: k_conf["overlay_modes"] = {}
            
            pure_id = key_text.lower()
            
            if selected_id == "none":
                if key_text in self.selected_overlay_keys:
                    self.selected_overlay_keys.remove(key_text)
                if pure_id in k_conf["overlay_modes"]:
                    del k_conf["overlay_modes"][pure_id]
            else:
                if key_text not in self.selected_overlay_keys:
                    self.selected_overlay_keys.append(key_text)
                k_conf["overlay_modes"][pure_id] = selected_id
                
            k_conf["overlay_selected_keys"] = self.selected_overlay_keys
            config_manager.save_config(cfg)
            
            self.update_matrix_buttons_style()
            dialog.accept()
            
            main_win = self.window()
            if main_win and hasattr(main_win, 'mod_keyboard') and main_win.mod_keyboard:
                mod = main_win.mod_keyboard
                if hasattr(mod, 'overlay_manager') and mod.overlay_manager and mod.btn_2.isChecked():
                    mod.overlay_manager.spawn_overlay_buttons(self.selected_overlay_keys)
                    
        btn_save.clicked.connect(save_mode_logic)
        dlg_layout.addWidget(btn_save)
        
        # --- МОДИФИЦИРОВАННАЯ КНОПКА СБРОСА: ПРИЖАТА ВПРАВО, МЕНЬШЕ И НАЗЫВАЕТСЯ «Сбросить» ---
        reset_hbox = QHBoxLayout()
        reset_hbox.addStretch() # Аппаратно отталкивает кнопку в самый правый угол
        
        btn_reset_pos = QPushButton("Сбросить")
        btn_reset_pos.setObjectName("BtnResetPos")
        btn_reset_pos.setFixedSize(80, 20) # Делаем её компактной и маленькой
        
        def reset_position_logic():
            cfg = config_manager.load_config()
            prof = cfg.get("current_profile", "Default Profile")
            
            if "overlay_positions" not in cfg["profiles"][prof]["kb"]:
                cfg["profiles"][prof]["kb"]["overlay_positions"] = {}
                
            positions = cfg["profiles"][prof]["kb"]["overlay_positions"]
            pure_id = key_text.lower()
            
            btn_size = cfg["profiles"][prof]["kb"].get("overlay_size", 60)
            spacing = int(btn_size + 8) 
            
            keyboard_grid_map = {
                "esc": (0, 0), "lmb": (0, spacing + 15), "rmb": (0, spacing*2 + 15), "mmb": (0, spacing*3 + 15),
                "osk": (0, spacing*4 + 15), "лп": (0, spacing*5 + 15), "ск": (0, spacing*6 + 15), "app": (0, spacing*7 + 15),
                "ctr": (0, spacing*8 + 25), "k+": (0, spacing*9 + 35), "f10": (0, spacing*10 + 35), "f11": (0, spacing*11 + 35), "f12": (0, spacing*12 + 35),
                
                "~": (1, 0), "1": (1, spacing), "2": (1, spacing*2), "3": (1, spacing*3), "4": (1, spacing*4), "5": (1, spacing*5),
                "6": (1, spacing*6), "7": (1, spacing*7), "8": (1, spacing*8), "9": (1, spacing*9), "0": (1, spacing*10),
                "-": (1, spacing*11), "=": (1, spacing*12), "backspace": (1, spacing*13),
                
                "tab": (2, 0), "q": (2, spacing + 15), "w": (2, spacing*2 + 15), "e": (2, spacing*3 + 15), "r": (2, spacing*4 + 15),
                "t": (2, spacing*5 + 15), "y": (2, spacing*6 + 15), "u": (2, spacing*7 + 15), "i": (2, spacing*8 + 15), "o": (2, spacing*9 + 15),
                "p": (2, spacing*10 + 15), "[": (2, spacing*11 + 15), "]": (2, spacing*12 + 15), "\\": (2, spacing*13 + 15),
                
                "caps": (3, 0), "a": (3, spacing + 22), "s": (3, spacing*2 + 22), "d": (3, spacing*3 + 22), "f": (3, spacing*4 + 22),
                "g": (3, spacing*5 + 22), "h": (3, spacing*6 + 22), "j": (3, spacing*7 + 22), "k": (3, spacing*8 + 22), "l": (3, spacing*9 + 22),
                ";": (3, spacing*10 + 22), "'": (3, spacing*11 + 22), "enter": (3, spacing*12 + 22),
                
                "lshift": (4, 0), "z": (4, spacing + 40), "x": (4, spacing*2 + 40), "c": (4, spacing*3 + 40), "v": (4, spacing*4 + 40),
                "b": (4, spacing*5 + 40), "n": (4, spacing*6 + 40), "m": (4, spacing*7 + 40), ",": (4, spacing*8 + 40), ".": (4, spacing*9 + 40),
                "/": (4, spacing*10 + 40), "rshift": (4, spacing*11 + 40),
                
                "lctrl": (5, 0), "win": (5, spacing + 10), "lalt": (5, spacing*2 + 15), "space": (5, spacing*3 + 25),
                "ralt": (5, spacing*6 + 50), "rctrl": (5, spacing*7 + 55),
                "🡠": (5, spacing*8 + 70), "🡡": (5, spacing*9 + 75), "🡣": (5, spacing*9 + 75), "🡢": (5, spacing*10 + 80)
            }
            
            row_idx, offset_x = keyboard_grid_map.get(pure_id, (2, 0))
            
            offset_y = row_idx * spacing
            if pure_id == "🡡":
                offset_y -= int(spacing / 2)
            elif pure_id == "🡣":
                offset_y += int(spacing / 2)
            
            screen_geo = QApplication.primaryScreen().geometry()
            
            total_grid_width = 14 * spacing
            total_grid_height = 6 * spacing
            
            start_grid_x = (screen_geo.width() - total_grid_width) / 2
            start_grid_y = (screen_geo.height() - total_grid_height) / 2
            
            final_x = int(start_grid_x + offset_x)
            final_y = int(start_grid_y + offset_y)
            
            positions[pure_id] = {"x": final_x, "y": final_y}
            config_manager.save_config(cfg)
            
            main_win = self.window()
            if main_win and hasattr(main_win, 'mod_keyboard') and main_win.mod_keyboard:
                mod = main_win.mod_keyboard
                if hasattr(mod, 'overlay_manager') and mod.overlay_manager and mod.btn_2.isChecked():
                    mod.overlay_manager.spawn_overlay_buttons(self.selected_overlay_keys)
            
            dialog.accept()
            
        btn_reset_pos.clicked.connect(reset_position_logic)
        reset_hbox.addWidget(btn_reset_pos)
        dlg_layout.addLayout(reset_hbox) # Добавляем выровненный ряд в главное окно диалога
        dialog.open()



# modules/kb_sett3.py - ЧАСТЬ 5 ИЗ 5 
    def update_matrix_buttons_style(self):
        """Обновляет неоновые стили кнопок: выбранные горят ярко-зелёным, остальные — фиолетовым"""
        for btn_text, btn_obj in self.matrix_buttons.items():
            if btn_text in self.selected_overlay_keys:
                btn_obj.setStyleSheet("""
                    QPushButton {
                        background-color: #0c2414; color: #2ed573; border: 1px solid #2ed573; border-radius: 4px;
                        font-family: 'Segoe UI', sans-serif; font-size: 10px; font-weight: bold;
                    }
                    QPushButton:hover { background-color: #2ed573; color: black; border-color: white; }
                """)
            else:
                btn_obj.setStyleSheet("""
                    QPushButton {
                        background-color: #0b0617; color: #a347ff; border: 1px solid #401970; border-radius: 4px;
                        font-family: 'Segoe UI', sans-serif; font-size: 10px; font-weight: bold;
                    }
                    QPushButton:hover { background-color: #8a2be2; color: #ffffff; border-color: #ffffff; }
                """)

    def on_setting_toggle_clicked(self, checked):
        self.apply_visibility_layout_state(checked)
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        config["profiles"][current_prof]["kb"]["setting_3"] = checked
        config_manager.save_config(config)

    def apply_visibility_layout_state(self, is_open):
        """Вспомогательный метод: мгновенно сворачивает или распахивает сетку выбора клавиш"""
        if is_open:
            self.container.show()
            self.line.show()
            self.toggle.setStyleSheet("""
                QPushButton {
                    background-color: #8a2be2; border: 1px solid #a347ff; border-radius: 10px;
                    text-align: right; color: #ffffff; font-size: 34px; font-weight: bold;
                    padding-top: -10px; padding-right: 2px;
                }
                QPushButton:hover { border-color: #ffffff; }
            """)
            self.toggle.setText("●")
            self.setMinimumHeight(0)
            self.setMaximumHeight(16777215)
        else:
            self.container.hide()
            self.line.hide()
            self.toggle.setStyleSheet("""
                QPushButton {
                    background-color: #1a1038; border: 1px solid #401970; border-radius: 10px;
                    text-align: left; color: #ffffff; font-size: 34px; font-weight: bold;
                    padding-top: -10px; padding-left: 2px;
                }
                QPushButton:hover { border-color: #8a2be2; }
            """)
            self.toggle.setText("●")
            self.setFixedHeight(42)

        self.update_matrix_buttons_style()
        self.update_real_press_button_style()
        self.toggle.update()
        self.toggle.repaint()


