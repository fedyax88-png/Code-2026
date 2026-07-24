# modules/kb/kb_sett5.py - ЧАСТЬ 1 ИЗ 3
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider, QWidget, QCheckBox, QDialog, QComboBox, QApplication
from PyQt6.QtCore import Qt
import config_manager

class KeyboardSettingBlock5(QFrame):
    """СТРОГО ПО ТЗ: Окно управления 8 полосами сброса игрового фокуса (Технология №4)"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingCard5")
        
        self.config = config_manager.load_config()
        self.current_prof = self.config.get("current_profile", "Default Profile")
        self.kb_data = self.config["profiles"][self.current_prof]["kb"]
        
        # Загружаем базовые параметры технологии №4
        self.lines_enabled = self.kb_data.get("focus_lines_enabled", False)
        self.lines_opacity = self.kb_data.get("focus_lines_opacity", 40)
        
        # Структура под 8 кастомных полос-оверлеев с индивидуальной видимостью и режимами
        if "focus_lines_binds" not in self.kb_data:
            self.kb_data["focus_lines_binds"] = {
                "top": {"name": "Вверх", "w": 300, "h": 20, "visible": True, "mode": "hover"},
                "bottom": {"name": "Вниз", "w": 300, "h": 20, "visible": True, "mode": "hover"},
                "left": {"name": "Лево", "w": 20, "h": 300, "visible": True, "mode": "hover"},
                "right": {"name": "Право", "w": 20, "h": 300, "visible": True, "mode": "hover"},
                "nw": {"name": "Сев-Запад", "w": 150, "h": 20, "visible": True, "mode": "hover"},
                "ne": {"name": "Сев-Восток", "w": 150, "h": 20, "visible": True, "mode": "hover"},
                "sw": {"name": "Юг-Запад", "w": 150, "h": 20, "visible": True, "mode": "hover"},
                "se": {"name": "Юг-Восток", "w": 150, "h": 20, "visible": True, "mode": "hover"}
            }
        self.lines_binds = self.kb_data["focus_lines_binds"]
        self.matrix_squares = {}

        self.setStyleSheet("""
            QFrame#SettingCard5 { background-color: #04030d; border: 1px solid #1a1038; border-radius: 10px; }
            QLabel { color: #ffffff; font-family: 'Segoe UI', sans-serif; font-size: 11px; background: transparent; border: none; }
            QCheckBox { color: #ffffff; font-size: 11px; spacing: 6px; background: transparent; border: none; font-weight: bold; }
            QCheckBox::indicator { width: 12px; height: 12px; border: 1px solid #401970; border-radius: 3px; background-color: #0b0617; }
            QCheckBox::indicator:checked { background-color: #2ed573; border-color: #ffffff; }
            
            QSlider::groove:horizontal { border: 1px solid #401970; height: 4px; background: #0b0617; border-radius: 2px; }
            QSlider::sub-page:horizontal { background: #8a2be2; border-radius: 2px; }
            QSlider::handle:horizontal {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0 #ffffff, stop:0.3 #8a2be2, stop:1 rgba(138,43,226,0));
                width: 12px; height: 12px; margin: -4px 0; border-radius: 6px;
            }
        """)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(8)

        # Верхняя панель: Включение функции + Ползунок прозрачности
        top_hbox = QHBoxLayout()
        self.chk_enable = QCheckBox("Вкл полосы фиксации фокуса (8 линий)")
        self.chk_enable.setChecked(self.lines_enabled)
        self.chk_enable.stateChanged.connect(self.on_global_toggle_changed)
        top_hbox.addWidget(self.chk_enable)
        
        top_hbox.addStretch()
        
        top_hbox.addWidget(QLabel("Прозрачность полос:"))
        self.lbl_opacity_val = QLabel(f"{self.lines_opacity}%")
        self.lbl_opacity_val.setStyleSheet("color: #8a2be2; font-weight: bold;")
        top_hbox.addWidget(self.lbl_opacity_val)
        
        self.slider_opacity = QSlider(Qt.Orientation.Horizontal)
        self.slider_opacity.setRange(5, 100)
        self.slider_opacity.setValue(self.lines_opacity)
        self.slider_opacity.setFixedWidth(120)
        self.slider_opacity.valueChanged.connect(self.on_opacity_slider_changed)
        top_hbox.addWidget(self.slider_opacity)
        
        self.layout.addLayout(top_hbox)
        
        # Разделитель
        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: #1a1038; min-height: 1px; max-height: 1px; border: none;")
        self.layout.addWidget(sep)

        # Список отрисовки 8 интерактивных полос
        lines_order = [
            ("top", "1. Полоса ВВЕРХ"), ("bottom", "2. Полоса ВНИЗ"), 
            ("left", "3. Полоса ЛЕВО"), ("right", "4. Полоса ПРАВО"),
            ("nw", "5. Диагональ СЗ"), ("ne", "6. Диагональ СВ"), 
            ("sw", "7. Диагональ ЮЗ"), ("se", "8. Диагональ ЮВ")
        ]

# modules/kb/kb_sett5.py - ЧАСТЬ 2 ИЗ 3
        for pos_id, readable_title in lines_order:
            row_widget = QWidget()
            row_lay = QHBoxLayout(row_widget)
            row_lay.setContentsMargins(0, 2, 0, 2)
            row_lay.setSpacing(10)
            
            # Квадратная кнопка вызова расширенного меню полосы
            btn_square = QPushButton(self.lines_binds[pos_id]["name"])
            btn_square.setFixedSize(90, 44)
            btn_square.setStyleSheet("""
                QPushButton {
                    background-color: #0b0617; color: #a347ff; border: 1px solid #401970; border-radius: 6px;
                    font-family: 'Segoe UI', sans-serif; font-size: 11px; font-weight: bold;
                }
                QPushButton:hover { background-color: #8a2be2; color: white; border-color: white; }
            """)
            btn_square.clicked.connect(lambda chk, p=pos_id: self.open_line_settings_dialog(p))
            self.matrix_squares[pos_id] = btn_square
            row_lay.addWidget(btn_square)
            
            # Контейнер ползунков размеров
            sliders_vbox = QVBoxLayout()
            sliders_vbox.setSpacing(2)
            
            lbl_info = QLabel(readable_title)
            lbl_info.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 10px;")
            sliders_vbox.addWidget(lbl_info)
            
            # Ползунок ширины (w) - ТЕПЕРЬ РАСШИРЕНО ДО 2000 ПИКСЕЛЕЙ ПО ТЗ
            w_hbox = QHBoxLayout()
            w_val = self.lines_binds[pos_id]["w"]
            lbl_w = QLabel(f"Ширина: {w_val}px")
            lbl_w.setStyleSheet("color: #a1a3b5; font-size: 9px; min-width: 75px;")
            slider_w = QSlider(Qt.Orientation.Horizontal)
            slider_w.setRange(4, 2000) # Максимальная планка поднята до 2000px
            slider_w.setValue(w_val)
            slider_w.setFixedHeight(12)
            slider_w.valueChanged.connect(lambda v, p=pos_id, l=lbl_w: self.on_line_dimension_changed(p, "w", v, l))
            w_hbox.addWidget(lbl_w); w_hbox.addWidget(slider_w)
            sliders_vbox.addLayout(w_hbox)
            
            # Ползунок высоты (h) - ТЕПЕРЬ РАСШИРЕНО ДО 2000 ПИКСЕЛЕЙ ПО ТЗ
            h_hbox = QHBoxLayout()
            h_val = self.lines_binds[pos_id]["h"]
            lbl_h = QLabel(f"Высота: {h_val}px")
            lbl_h.setStyleSheet("color: #a1a3b5; font-size: 9px; min-width: 75px;")
            slider_h = QSlider(Qt.Orientation.Horizontal)
            slider_h.setRange(4, 2000) # Максимальная планка поднята до 2000px
            slider_h.setValue(h_val)
            slider_h.setFixedHeight(12)
            slider_h.valueChanged.connect(lambda v, p=pos_id, l=lbl_h: self.on_line_dimension_changed(p, "h", v, l))
            h_hbox.addWidget(lbl_h); h_hbox.addWidget(slider_h)
            sliders_vbox.addLayout(h_hbox)
            
            row_lay.addLayout(sliders_vbox)
            self.layout.addWidget(row_widget)


    def open_line_settings_dialog(self, position_id):
        """Всплывающее кастомное окно параметров конкретной полосы сброса фокуса со сбросом позиций"""
        dialog = QDialog(self)
        dialog.setFixedSize(300, 210)  # Высота увеличена для кнопки «Сбросить»
        dialog.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        
        dialog.setStyleSheet("""
            QDialog { background-color: #04030d; border: 2px solid #8a2be2; border-radius: 10px; }
            QLabel { color: #ffffff; font-weight: bold; background: transparent; border: none; }
            QCheckBox { color: #ffffff; font-size: 11px; spacing: 6px; background: transparent; border: none; font-weight: bold; }
            QCheckBox::indicator { width: 12px; height: 12px; border: 1px solid #401970; border-radius: 3px; background-color: #0b0617; }
            QCheckBox::indicator:checked { background-color: #2ed573; border-color: #ffffff; }
            QComboBox { background-color: #0b0617; color: #ffffff; border: 1px solid #401970; border-radius: 4px; height: 26px; padding-left: 5px; font-weight: bold; }
            QComboBox QAbstractItemView { background-color: #0b0617; color: #ffffff; border: 1px solid #401970; selection-background-color: #8a2be2; outline: none; }
            
            /* УДОБНЫЙ ШИРОКИЙ СКРОЛЛБАР ДЛЯ ШТАТНОГО ВЫПАДАЮЩЕГО СПИСКА (24PX) */
            QComboBox QAbstractItemView QScrollBar:vertical {
                border: 1px solid #1a1038; background-color: #04030d; width: 24px; margin: 0px; border-radius: 12px;
            }
            QComboBox QAbstractItemView QScrollBar::handle:vertical {
                background-color: #401970; border: 2px solid #8a2be2; min-height: 20px; border-radius: 10px;
            }
            QComboBox QAbstractItemView QScrollBar::handle:vertical:hover { background-color: #8a2be2; border-color: #ffffff; }
            QComboBox QAbstractItemView QScrollBar::add-line:vertical, QComboBox QAbstractItemView QScrollBar::sub-line:vertical { border: none; background: none; height: 0px; }
            QComboBox QAbstractItemView QScrollBar::add-page:vertical, QComboBox QAbstractItemView QScrollBar::sub-page:vertical { background-color: #04030d; border-radius: 12px; }
            
            QPushButton { background-color: #0b0617; color: #a347ff; border: 1px solid #401970; border-radius: 4px; height: 26px; font-weight: bold; }
            QPushButton:hover { background-color: #8a2be2; color: white; border-color: white; }
            QPushButton#BtnResetPos { background-color: #160a0f; color: #ff4757; border: 1px solid #ff4757; border-radius: 4px; font-size: 11px; font-weight: bold; height: 26px; }
            QPushButton#BtnResetPos:hover { background-color: #ff4757; color: white; border-color: white; }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(15, 12, 15, 15)
        layout.setSpacing(10)
        
        title_hbox = QHBoxLayout()
        lbl_title = QLabel(f"Настройка: {self.lines_binds[position_id]['name']}")
        title_hbox.addWidget(lbl_title); title_hbox.addStretch()
        
        btn_close = QPushButton("✕")
        btn_close.setFixedSize(22, 22)
        btn_close.setStyleSheet("QPushButton { background-color: #160a0f; color: #ff4757; border: 1px solid #ff4757; border-radius: 5px; font-size: 11px; font-weight: bold; height: 22px; } QPushButton:hover { background-color: #ff4757; color: white; border-color: white; }")
        btn_close.clicked.connect(dialog.reject)
        title_hbox.addWidget(btn_close)
        layout.addLayout(title_hbox)
        
        chk_visible = QCheckBox("Показывать эту полосу на экране")
        chk_visible.setChecked(self.lines_binds[position_id].get("visible", True))
        layout.addWidget(chk_visible)
        
        layout.addWidget(QLabel("Режим активации фиксации фокуса:"))
        combo_mode = QComboBox()
        combo_mode.addItem("Нажатие при наведении (Рекомендуется)", "hover")
        combo_mode.addItem("Нажатие при клике автокликера", "click")
        
        current_mode = self.lines_binds[position_id].get("mode", "hover")
        for i in range(combo_mode.count()):
            if combo_mode.itemData(i) == current_mode:
                combo_mode.setCurrentIndex(i); break
        layout.addWidget(combo_mode)
        
        btn_save = QPushButton("Сохранить параметры")

# modules/kb/kb_sett5.py - ЧАСТЬ 3 ИЗ 3
        def save_line_logic():
            self.lines_binds[position_id]["visible"] = chk_visible.isChecked()
            self.lines_binds[position_id]["mode"] = combo_mode.itemData(combo_mode.currentIndex())
            
            cfg = config_manager.load_config()
            prof = cfg.get("current_profile", "Default Profile")
            cfg["profiles"][prof]["kb"]["focus_lines_binds"] = self.lines_binds
            config_manager.save_config(cfg)
            
            dialog.accept()
            self.notify_manager_refresh()
            
        btn_save.clicked.connect(save_line_logic)
        layout.addWidget(btn_save)

        # --- СТРОГО ПО ТЗ: КНОПКА ТОЧЕЧНОГО СБРОСА КООРДИНАТ ДЛЯ ВЫБРАННОЙ ЛИНИИ ---
        action_hbox = QHBoxLayout()
        action_hbox.addStretch()
        
        btn_reset_this = QPushButton("Сбросить")
        btn_reset_this.setObjectName("BtnResetPos")
        btn_reset_this.setFixedSize(80, 20)
        
        def reset_this_line_logic():
            cfg = config_manager.load_config()
            prof = cfg.get("current_profile", "Default Profile")
            if "overlay_positions" not in cfg["profiles"][prof]["kb"]:
                cfg["profiles"][prof]["kb"]["overlay_positions"] = {}
                
            positions = cfg["profiles"][prof]["kb"]["overlay_positions"]
            unique_line_id = f"focus_line_4v_{position_id}"
            
            screen_geo = QApplication.primaryScreen().geometry()
            cx = screen_geo.width() // 2
            cy = screen_geo.height() // 2
            
            # Базовые математические стартовые позиции вокруг центра экрана
            offset = 120
            lines_grid = {
                "top": (cx - 150, cy - offset - 40),
                "bottom": (cx - 150, cy + offset),
                "left": (cx - offset - 40, cy - 150),
                "right": (cx + offset, cy - 150),
                "nw": (cx - offset - 80, cy - offset - 40),
                "ne": (cx + offset, cy - offset - 40),
                "sw": (cx - offset - 80, cy + offset),
                "se": (cx + offset, cy + offset)
            }
            
            final_x, final_y = lines_grid.get(position_id, (cx, cy))
            positions[unique_line_id] = {"x": int(final_x), "y": int(final_y)}
            config_manager.save_config(cfg)
            
            dialog.accept()
            self.notify_manager_refresh()
            
        btn_reset_this.clicked.connect(reset_this_line_logic)
        action_hbox.addWidget(btn_reset_this)
        layout.addLayout(action_hbox)
        
        dialog.open()

    def on_line_dimension_changed(self, position_id, dimension, value, label_obj):
        label_obj.setText(f"{'Ширина' if dimension == 'w' else 'Высота'}: {value}px")
        self.lines_binds[position_id][dimension] = int(value)
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        config["profiles"][current_prof]["kb"]["focus_lines_binds"] = self.lines_binds
        config_manager.save_config(config)
        self.notify_manager_refresh()

    def on_opacity_slider_changed(self, value):
        self.lbl_opacity_val.setText(f"{value}%")
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        config["profiles"][current_prof]["kb"]["focus_lines_opacity"] = int(value)
        config_manager.save_config(config)
        self.notify_manager_refresh()

    def on_global_toggle_changed(self, state):
        checked = (state == 2 or state == True)
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        config["profiles"][current_prof]["kb"]["focus_lines_enabled"] = checked
        config_manager.save_config(config)
        self.notify_manager_refresh()

    def notify_manager_refresh(self):
        main_win = self.window()
        if main_win and hasattr(main_win, 'mod_keyboard') and main_win.mod_keyboard:
            mod = main_win.mod_keyboard
            if hasattr(mod, 'overlay_manager') and mod.overlay_manager:
                if mod.btn_2.isChecked():
                    selected_keys = config_manager.load_config()["profiles"][self.current_prof]["kb"].get("overlay_selected_keys", [])
                    mod.overlay_manager.spawn_overlay_buttons(selected_keys)
