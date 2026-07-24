# modules/kb/kb_sett4.py - ЧАСТЬ 1 ИЗ 5
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider, QWidget, QCheckBox, QDialog, QComboBox, QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import styles
import config_manager

class KeyboardSettingBlock4(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingCard4")
        
        self.config = config_manager.load_config()
        self.current_prof = self.config.get("current_profile", "Default Profile")
        self.kb_data = self.config["profiles"][self.current_prof]["kb"]
        
        # Базовые параметры оверлеев
        self.saved_size = self.kb_data.get("overlay_size", 60)
        self.saved_cross_opacity = self.kb_data.get("cross_opacity", 100)
        self.cross_enabled = self.kb_data.get("cross_enabled", False)
        
        # СТРОГО ПО ТЗ: Внедряем 5-ю кнопку Center (Space) и флажки индивидуальной видимости visible
        if "cross_custom_binds" not in self.kb_data:
            self.kb_data["cross_custom_binds"] = {
                "top": {"key": "🡡", "w": 60, "h": 40, "visible": True},
                "bottom": {"key": "🡣", "w": 60, "h": 40, "visible": True},
                "left": {"key": "🡠", "w": 60, "h": 40, "visible": True},
                "right": {"key": "🡢", "w": 60, "h": 40, "visible": True},
                "center": {"key": "Space", "w": 60, "h": 40, "visible": True} # Новая пятая центральная кнопка
            }
        
        # Защитная проверка: если структура старая, дописываем центральную кнопку и флажки visible на лету
        self.cross_binds = self.kb_data["cross_custom_binds"]
        for pos in ["top", "bottom", "left", "right", "center"]:
            if pos not in self.cross_binds:
                if pos == "center": self.cross_binds["center"] = {"key": "Space", "w": 60, "h": 40, "visible": True}
                else: self.cross_binds[pos] = {"key": "🡡", "w": 60, "h": 40, "visible": True}
            if "visible" not in self.cross_binds[pos]:
                self.cross_binds[pos]["visible"] = True
                
        self.matrix_squares = {}

        self.setStyleSheet("""
            QFrame#SettingCard4 { background-color: #04030d; border: 1px solid #1a1038; border-radius: 10px; }
            QLabel { color: #ffffff; font-family: 'Segoe UI', sans-serif; font-size: 11px; background: transparent; border: none; }
            QCheckBox { color: #ffffff; font-size: 11px; spacing: 6px; background: transparent; border: none; }
            QCheckBox::indicator { width: 12px; height: 12px; border: 1px solid #401970; border-radius: 3px; background-color: #0b0617; }
            QCheckBox::indicator:checked { background-color: #8a2be2; border-color: #ffffff; }
            
            QSlider::groove:horizontal { border: 1px solid #401970; height: 4px; background: #0b0617; border-radius: 2px; }
            QSlider::sub-page:horizontal { background: #8a2be2; border-radius: 2px; }
            QSlider::handle:horizontal {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0 #ffffff, stop:0.3 #8a2be2, stop:1 rgba(138,43,226,0));
                width: 12px; height: 12px; margin: -4px 0; border-radius: 6px;
            }
        """)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(12, 10, 12, 12)
        self.main_layout.setSpacing(6)
        
        top_layout = QHBoxLayout(); top_layout.setSpacing(10)
        ico = QLabel(); ico.setStyleSheet("background: transparent; border: none;")
        pix = QPixmap(styles.get_image("kb1.png"))
        if not pix.isNull(): ico.setPixmap(pix.scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        top_layout.addWidget(ico)
        
        title = QLabel("Внешний вид горячих клавиш")
        title.setStyleSheet("color: #ffffff; font-size: 13px; font-weight: bold;")
        top_layout.addWidget(title); top_layout.addStretch()
        
        self.toggle = QPushButton("●"); self.toggle.setCheckable(True)
        saved_open_state = self.kb_data.get("setting_4", True)
        self.toggle.setChecked(saved_open_state); self.toggle.setFixedSize(44, 20)
        self.toggle.clicked.connect(self.on_setting_toggle_clicked)
        top_layout.addWidget(self.toggle); self.main_layout.addLayout(top_layout)
        
        self.line = QFrame(); self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setStyleSheet("background-color: #1a1038; min-height: 1px; max-height: 1px; border: none;")
        self.main_layout.addWidget(self.line)
        
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container); self.container_layout.setContentsMargins(0, 0, 0, 0); self.container_layout.setSpacing(6)
        
        # Ползунок прозрачности креста
        opacity_hbox = QHBoxLayout()
        opacity_hbox.addWidget(QLabel("Прозрачность креста:")); opacity_hbox.addStretch()
        self.lbl_opacity_val = QLabel(f"{self.saved_cross_opacity}%"); self.lbl_opacity_val.setStyleSheet("color: #8a2be2; font-weight: bold;")
        opacity_hbox.addWidget(self.lbl_opacity_val); self.container_layout.addLayout(opacity_hbox)
        
        self.slider_opacity = QSlider(Qt.Orientation.Horizontal); self.slider_opacity.setRange(10, 100); self.slider_opacity.setValue(self.saved_cross_opacity)
        self.slider_opacity.valueChanged.connect(self.on_opacity_slider_changed); self.container_layout.addWidget(self.slider_opacity)
        
        # Общий размер матричных кнопок
        size_hbox = QHBoxLayout()
        size_hbox.addWidget(QLabel("Размер кнопок матрицы:")); size_hbox.addStretch()
        self.lbl_size_val = QLabel(f"{self.saved_size} px"); self.lbl_size_val.setStyleSheet("color: #8a2be2; font-weight: bold;")
        size_hbox.addWidget(self.lbl_size_val); self.container_layout.addLayout(size_hbox)
        
        self.slider_size = QSlider(Qt.Orientation.Horizontal); self.slider_size.setRange(20, 120); self.slider_size.setValue(self.saved_size)
        self.slider_size.valueChanged.connect(self.on_size_slider_changed); self.container_layout.addWidget(self.slider_size)
        
        cross_line = QFrame(); cross_line.setFrameShape(QFrame.Shape.HLine)
        cross_line.setStyleSheet("background-color: #1a1038; min-height: 1px; max-height: 1px; border: none; margin-top: 2px;")
        self.container_layout.addWidget(cross_line)
        
        self.chk_cross_enable = QCheckBox("Вкл наэкранный пульт (5 клавиш)")
        self.chk_cross_enable.setChecked(self.cross_enabled)
        self.chk_cross_enable.stateChanged.connect(self.on_cross_toggle_changed)
        self.container_layout.addWidget(self.chk_cross_enable)


# modules/kb/kb_sett4.py - ЧАСТЬ 2 ИЗ 5
        # ОТРИСОВКА ПО ТЗ: 5 КВАДРАТОВ СВЕРХУ ВНИЗ С МИКРО-ПОЛЗУНКАМИ РАЗМЕРОВ СПРАВА (РАСШИРЕНО ДО 500PX)
        positions_order = [
            ("top", "Клавиша ВВЕРХ"), 
            ("bottom", "Клавиша ВНИЗ"), 
            ("left", "Клавиша ЛЕВО"), 
            ("right", "Клавиша ПРАВО"),
            ("center", "Клавиша ЦЕНТР (Space)") # Добавлена пятая кнопка в список отрисовки
        ]
        
        for pos_id, readable_title in positions_order:
            row_widget = QWidget()
            row_lay = QHBoxLayout(row_widget)
            row_lay.setContentsMargins(0, 2, 0, 2)
            row_lay.setSpacing(10)
            
            # 1. Квадратный интерактивный пульт выбора бинда
            btn_square = QPushButton(self.cross_binds[pos_id]["key"])
            btn_square.setFixedSize(50, 50) # Идеальный квадрат
            btn_square.setStyleSheet("""
                QPushButton {
                    background-color: #0b0617; color: #a347ff; border: 1px solid #401970; border-radius: 6px;
                    font-family: 'Segoe UI', sans-serif; font-size: 11px; font-weight: bold;
                }
                QPushButton:hover { background-color: #8a2be2; color: white; border-color: white; }
            """)
            btn_square.clicked.connect(lambda chk, p=pos_id: self.open_full_keyboard_dialog(p))
            self.matrix_squares[pos_id] = btn_square
            row_lay.addWidget(btn_square)
            
            # Правая сторона: Текстовое описание + 2 компактных ползунка
            sliders_vbox = QVBoxLayout()
            sliders_vbox.setSpacing(2)
            
            lbl_info = QLabel(readable_title)
            lbl_info.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 10px;")
            sliders_vbox.addWidget(lbl_info)
            
            # Ползунок ширины (w) - РАСШИРЕНО ДО 500 ПИКСЕЛЕЙ ПО ТЗ
            w_hbox = QHBoxLayout()
            w_val = self.cross_binds[pos_id]["w"]
            lbl_w = QLabel(f"Ширина: {w_val}px")
            lbl_w.setStyleSheet("color: #a1a3b5; font-size: 9px;")
            slider_w = QSlider(Qt.Orientation.Horizontal)
            slider_w.setRange(20, 500) # По вашему ТЗ верхняя планка поднята до 500px
            slider_w.setValue(w_val)
            slider_w.setFixedHeight(12)
            slider_w.valueChanged.connect(lambda v, p=pos_id, l=lbl_w: self.on_cross_individual_dimension_changed(p, "w", v, l))
            w_hbox.addWidget(lbl_w); w_hbox.addWidget(slider_w)
            sliders_vbox.addLayout(w_hbox)
            
            # Ползунок высоты (h) - РАСШИРЕНО ДО 500 ПИКСЕЛЕЙ ПО ТЗ
            h_hbox = QHBoxLayout()
            h_val = self.cross_binds[pos_id]["h"]
            lbl_h = QLabel(f"Высота: {h_val}px")
            lbl_h.setStyleSheet("color: #a1a3b5; font-size: 9px;")
            slider_h = QSlider(Qt.Orientation.Horizontal)
            slider_h.setRange(20, 500) # По вашему ТЗ верхняя планка поднята до 500px
            slider_h.setValue(h_val)
            slider_h.setFixedHeight(12)
            slider_h.valueChanged.connect(lambda v, p=pos_id, l=lbl_h: self.on_cross_individual_dimension_changed(p, "h", v, l))
            h_hbox.addWidget(lbl_h); h_hbox.addWidget(slider_h)
            sliders_vbox.addLayout(h_hbox)
            
            row_lay.addLayout(sliders_vbox)
            self.container_layout.addWidget(row_widget)
            
        # КНОПКА ГЛОБАЛЬНОГО СБРОСА: ПЕРЕКРАШЕНА В КРАСНЫЙ И ПЕРЕИМЕНОВАНА СТРОГО ПО ТЗ
        self.btn_reset_pos = QPushButton("Сбросить расстановку ВСЕХ кнопок")
        self.btn_reset_pos.setFixedHeight(24)
        self.btn_reset_pos.setStyleSheet("""
            QPushButton { 
                background-color: #1c060d; color: #ff4d4d; border: 1px solid #ff4d4d; border-radius: 4px; 
                font-size: 10px; font-weight: bold; 
            } 
            QPushButton:hover { background-color: #ff4d4d; color: white; border-color: white; }
        """)
        self.btn_reset_pos.clicked.connect(self.on_reset_positions_clicked)
        self.container_layout.addWidget(self.btn_reset_pos)
        
        self.main_layout.addWidget(self.container)
        self.apply_visibility_layout_state(saved_open_state)


# modules/kb/kb_sett4.py - ЧАСТЬ 3 ИЗ 5
    def open_full_keyboard_dialog(self, position_id):
        """Всплывающее КАСТОМНОЕ безрамочное окно выбора абсолютно любой клавиши из списка клавиатуры по ТЗ"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Выберите клавишу джойстика")
        dialog.setFixedSize(320, 210)  # Слегка увеличили высоту для чекбокса «Показывать кнопку» и «Сбросить»
        
        dialog.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        
        # Полная очистка зажимов мыши при уничтожении диалога
        def force_clean_all_mouse_states_cross():
            from PyQt6.QtCore import QTimer
            def run_delayed_release_cross():
                import ctypes
                try:
                    ctypes.windll.user32.mouse_event(0x0004, 0, 0, 0, 0) # LEFTUP
                    ctypes.windll.user32.mouse_event(0x0010, 0, 0, 0, 0) # RIGHTUP
                except Exception: pass
                
                main_win = self.window()
                if main_win and hasattr(main_win, 'mod_keyboard') and main_win.mod_keyboard:
                    mod = main_win.mod_keyboard
                    if hasattr(mod, 'overlay_manager') and mod.overlay_manager:
                        for btn in mod.overlay_manager.active_buttons:
                            if btn.key_name in ["lmb", "rmb", "mmb"]:
                                btn.is_physically_pressed = False
                                btn.set_neon_style(is_active=False)
            QTimer.singleShot(100, run_delayed_release_cross)
                            
        dialog.destroyed.connect(force_clean_all_mouse_states_cross)
        
        dialog.setStyleSheet("""
            QDialog { background-color: #04030d; border: 2px solid #8a2be2; border-radius: 10px; }
            QLabel { color: #ffffff; font-weight: bold; background: transparent; border: none; }
            QCheckBox { color: #ffffff; font-size: 11px; spacing: 6px; background: transparent; border: none; font-weight: bold; }
            QCheckBox::indicator { width: 12px; height: 12px; border: 1px solid #401970; border-radius: 3px; background-color: #0b0617; }
            QCheckBox::indicator:checked { background-color: #2ed573; border-color: #ffffff; }
            QComboBox { background-color: #0b0617; color: #ffffff; border: 1px solid #401970; border-radius: 4px; height: 26px; padding-left: 5px; font-weight: bold; }
            QComboBox QAbstractItemView { background-color: #0b0617; color: #ffffff; border: 1px solid #401970; selection-background-color: #8a2be2; selection-color: #ffffff; outline: none; }
            
            /* РОДНАЯ СТИЛИЗАЦИЯ ИЗ SET 1: РАСШИРЕНА В 2 РAЗА ДЛЯ УДОБСТВА ЕVIACAM (24PX) */
            QComboBox QAbstractItemView QScrollBar:vertical {
                border: 1px solid #1a1038; 
                background-color: #0b0617; 
                width: 24px; /* Ровно в два раза шире, чтобы легко попадать! */
                margin: 0px; 
                border-radius: 12px;
            }
            QComboBox QAbstractItemView QScrollBar::handle:vertical { 
                background-color: #401970; 
                border: 2px solid #8a2be2; 
                min-height: 20px; 
                border-radius: 10px; 
            }
            QComboBox QAbstractItemView QScrollBar::handle:vertical:hover { 
                background-color: #8a2be2; 
                border-color: #ffffff; 
            }
            QComboBox QAbstractItemView QScrollBar::add-line:vertical, QComboBox QAbstractItemView QScrollBar::sub-line:vertical { 
                border: none; 
                background: none; 
                height: 0px; 
            }
            QComboBox QAbstractItemView QScrollBar::up-arrow:vertical, QComboBox QAbstractItemView QScrollBar::down-arrow:vertical { 
                border: none; 
                background: none; 
            }
            QComboBox QAbstractItemView QScrollBar::add-page:vertical, QComboBox QAbstractItemView QScrollBar::sub-page:vertical { 
                background: none; 
            }
            
            QPushButton { background-color: #0b0617; color: #a347ff; border: 1px solid #401970; border-radius: 4px; height: 26px; font-weight: bold; }
            QPushButton:hover { background-color: #8a2be2; color: white; border-color: white; }
            QPushButton#BtnResetPos { background-color: #160a0f; color: #ff4757; border: 1px solid #ff4757; border-radius: 4px; font-size: 11px; font-weight: bold; height: 26px; }
            QPushButton#BtnResetPos:hover { background-color: #ff4757; color: white; border-color: white; }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(15, 12, 15, 15)
        layout.setSpacing(10)
        
        title_hbox = QHBoxLayout()
        lbl_title = QLabel("Выберите клавишу пульта")
        title_hbox.addWidget(lbl_title); title_hbox.addStretch()
        
        btn_close_cross = QPushButton("✕")
        btn_close_cross.setFixedSize(22, 22)
        btn_close_cross.setStyleSheet("QPushButton { background-color: #160a0f; color: #ff4757; border: 1px solid #ff4757; border-radius: 5px; font-size: 11px; font-weight: bold; height: 22px; } QPushButton:hover { background-color: #ff4757; color: white; border-color: white; }")
        btn_close_cross.clicked.connect(dialog.reject)
        title_hbox.addWidget(btn_close_cross)
        layout.addLayout(title_hbox)
        
        combo = QComboBox()
        all_keys = [
            "Esc", "LMB", "RMB", "MMB", "OSK", "ЛП", "СК", "APP", "CTR", "K+", "F10", "F11", "F12",
            "~", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", "Backspace",
            "Tab", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "[", "]", "\\",
            "Caps", "A", "S", "D", "F", "G", "H", "J", "K", "L", ";", "'", "Enter",
            "LShift", "Z", "X", "C", "V", "B", "N", "M", ",", ".", "/", "RShift",
            "LCtrl", "Win", "LAlt", "Space", "RAlt", "RCtrl", "🡠", "🡡", "🡣", "🡢"
        ]
        combo.addItems(all_keys)
        
        current_key = self.cross_binds[position_id]["key"]
        idx = combo.findText(current_key, Qt.MatchFlag.MatchFixedString)
        if idx >= 0: combo.setCurrentIndex(idx)
        layout.addWidget(combo)
        
        chk_visible = QCheckBox("Показывать кнопку")
        chk_visible.setChecked(self.cross_binds[position_id].get("visible", True))
        layout.addWidget(chk_visible)
        
        btn_save = QPushButton("Сохранить выбор")


# modules/kb/kb_sett4.py - ЧАСТЬ 4 ИЗ 5
        def save_logic():
            selected_txt = combo.currentText()
            is_btn_visible = chk_visible.isChecked()
            
            self.cross_binds[position_id]["key"] = selected_txt
            self.cross_binds[position_id]["visible"] = is_btn_visible
            self.matrix_squares[position_id].setText(selected_txt)
            
            cfg = config_manager.load_config()
            prof = cfg.get("current_profile", "Default Profile")
            cfg["profiles"][prof]["kb"]["cross_custom_binds"] = self.cross_binds
            config_manager.save_config(cfg)
            
            dialog.accept()
            self.notify_overlay_manager_update()
            
        btn_save.clicked.connect(save_logic)
        layout.addWidget(btn_save)
        
        # --- ПО ТЗ: ТОЧЕЧНАЯ КНОПКА СБРОСА ДЛЯ КОНКРЕТНОЙ ПОЗИЦИИ В РОМБОВИДНЫЙ КРЕСТ ---
        action_hbox = QHBoxLayout()
        action_hbox.addStretch() # Прижимает кнопку к правому нижнему углу
        
        btn_reset_this = QPushButton("Сбросить")
        btn_reset_this.setObjectName("BtnResetPos")
        btn_reset_this.setFixedSize(80, 20) # Компактная маленькая кнопка
        
        def reset_this_position_logic():
            cfg = config_manager.load_config()
            prof = cfg.get("current_profile", "Default Profile")
            if "overlay_positions" not in cfg["profiles"][prof]["kb"]:
                cfg["profiles"][prof]["kb"]["overlay_positions"] = {}
                
            positions = cfg["profiles"][prof]["kb"]["overlay_positions"]
            unique_cross_id = f"cross_4v_{position_id}"
            
            screen_geo = QApplication.primaryScreen().geometry()
            center_x = screen_geo.width() // 2
            center_y = screen_geo.height() // 2
            
            # Математические зазоры смещения для красивого креста без наложений
            offset = 75 
            
            # ГЕОМЕТРИЧЕСКАЯ СЕТКА КРЕСТА ПО ТЗ (Space лежит ниже по центру ромба)
            cross_grid = {
                "top": (center_x - 30, center_y - offset - 20),
                "bottom": (center_x - 30, center_y + offset + 20),
                "left": (center_x - offset - 30, center_y - 20),
                "right": (center_x + offset - 30, center_y - 20),
                "center": (center_x - 30, center_y + 35) # Space сдвинут ниже
            }
            
            final_x, final_y = cross_grid.get(position_id, (center_x, center_y))
            positions[unique_cross_id] = {"x": int(final_x), "y": int(final_y)}
            config_manager.save_config(cfg)
            
            dialog.accept()
            self.notify_overlay_manager_update()
            
        btn_reset_this.clicked.connect(reset_this_position_logic)
        action_hbox.addWidget(btn_reset_this)
        layout.addLayout(action_hbox)
        
        dialog.open()

    def on_cross_individual_dimension_changed(self, position_id, dimension, value, label_obj):
        label_obj.setText(f"{'Ширина' if dimension == 'w' else 'Высота'}: {value}px")
        self.cross_binds[position_id][dimension] = int(value)
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        config["profiles"][current_prof]["kb"]["cross_custom_binds"] = self.cross_binds
        config_manager.save_config(config)
        self.notify_overlay_manager_update()

    def on_opacity_slider_changed(self, value):
        self.lbl_opacity_val.setText(f"{value}%")
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        config["profiles"][current_prof]["kb"]["cross_opacity"] = int(value)
        config_manager.save_config(config)
        self.notify_overlay_manager_update()

# modules/kb/kb_sett4.py - ЧАСТЬ 5 ИЗ 5
    def on_size_slider_changed(self, value):
        self.lbl_size_val.setText(f"{value} px")
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        config["profiles"][current_prof]["kb"]["overlay_size"] = int(value)
        config_manager.save_config(config)
        self.notify_overlay_manager_update()

    def on_cross_toggle_changed(self, state):
        checked = (state == 2 or state == True)
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        config["profiles"][current_prof]["kb"]["cross_enabled"] = checked
        config_manager.save_config(config)
        self.notify_overlay_manager_update()

    def on_reset_positions_clicked(self):
        """Слот обработки клика по красной кнопке сброса с кастомным неоновым окном подтверждения"""
        from PyQt6.QtWidgets import QMessageBox
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Подтверждение сброса")
        msg.setText("ВНИМАНИЕ!\n\nВы собираетесь полностью сбросить расположение ВСЕХ наэкранных кнопок программы (матрицы Set 3 и пультов Set 4).\n\nВы действительно хотите это сделать?")
        msg.setIcon(QMessageBox.Icon.Warning)
        
        yes_btn = msg.addButton("Да, сбросить всё", QMessageBox.ButtonRole.YesRole)
        no_btn = msg.addButton("Отмена", QMessageBox.ButtonRole.NoRole)
        msg.setDefaultButton(no_btn)
        
        msg.setStyleSheet("""
            QMessageBox { background-color: #04030d; border: 2px solid #ff4d4d; border-radius: 10px; } 
            QLabel { color: #ffffff; font-family: 'Segoe UI', sans-serif; font-size: 12px; font-weight: bold; } 
            QPushButton { background-color: #0b0617; color: #ff4d4d; border: 1px solid #401970; border-radius: 4px; padding: 5px 12px; font-weight: bold; } 
            QPushButton:hover { background-color: #ff4d4d; color: white; border-color: white; }
        """)
        msg.exec()
        
        if msg.clickedButton() != yes_btn:
            return

        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        if "overlay_positions" in config["profiles"][current_prof]["kb"]:
            config["profiles"][current_prof]["kb"]["overlay_positions"] = {}
        config_manager.save_config(config)
        self.notify_overlay_manager_update()

    # ЖЕСТКИЙ ФИКС ОПЕЧАТКИ: Метод переименован в точное и правильное системное имя!
    def notify_overlay_manager_update(self):
        main_win = self.window()
        if main_win and hasattr(main_win, 'mod_keyboard') and main_win.mod_keyboard:
            mod = main_win.mod_keyboard
            if hasattr(mod, 'overlay_manager') and mod.overlay_manager and mod.btn_2.isChecked():
                config = config_manager.load_config()
                current_prof = config.get("current_profile", "Default Profile")
                selected_keys = config["profiles"][current_prof]["kb"].get("overlay_selected_keys", [])
                mod.overlay_manager.spawn_overlay_buttons(selected_keys)

    def on_setting_toggle_clicked(self, checked):
        self.apply_visibility_layout_state(checked)
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        config["profiles"][current_prof]["kb"]["setting_4"] = checked
        config_manager.save_config(config)

    def apply_visibility_layout_state(self, is_open):
        if is_open:
            self.container.show()
            self.line.show()
            self.toggle.setStyleSheet("background-color: #8a2be2; border: none; border-radius: 10px; text-align: right; color: white; font-size: 34px; font-weight: bold; padding-top: -10px; padding-right: 2px;")
            self.toggle.setText("●")
            self.setMinimumHeight(0); self.setMaximumHeight(16777215)
        else:
            self.container.hide()
            self.line.hide()
            self.toggle.setStyleSheet("background-color: #1a1038; border: 1px solid #401970; border-radius: 10px; text-align: left; color: white; font-size: 34px; font-weight: bold; padding-top: -10px; padding-left: 2px;")
            self.toggle.setText("●")
            self.setFixedHeight(42)
            self.toggle.update(); self.toggle.repaint()
