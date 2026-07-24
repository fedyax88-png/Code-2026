# modules/mouse/mouse_sett3.py - ЧАСТЬ 1 ИЗ 3 (ПОЛНОСТЬЮ ИСПРАВЛЕННАЯ С РАДИОКНОПКАМИ ПОЗИЦИЙ И МГНОВЕННЫМ ПЕРЕЛЕТОМ)
import config_manager
import styles
from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, QApplication,
                             QPushButton, QSlider, QRadioButton, QCheckBox, QButtonGroup)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

class MouseSettingBlock3(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingCard")
        self.setStyleSheet("""
            QFrame#SettingCard { background-color: #030a06; border: 1px solid #10381f; border-radius: 10px; }
            QRadioButton { color: #ffffff; font-size: 11px; font-weight: 500; background: transparent; border: none; }
            QRadioButton::indicator { width: 14px; height: 14px; border-radius: 7px; border: 1px solid #123d22; background-color: #05140b; }
            QRadioButton::indicator:checked { background-color: #2ed573; border: 1px solid #ffffff; }
            QCheckBox { color: #ffffff; font-size: 11px; font-weight: 500; background: transparent; border: none; }
            QCheckBox::indicator { width: 14px; height: 14px; border-radius: 3px; border: 1px solid #123d22; background-color: #05140b; }
            QCheckBox::indicator:checked { background-color: #2ed573; border: 1px solid #ffffff; }
            QSlider::groove:horizontal { height: 4px; background: #10381f; border-radius: 2px; }
            QSlider::sub-page:horizontal { background: #2ed573; border-radius: 2px; }
            QSlider::handle:horizontal { background: #ffffff; border: 1px solid #2ed573; width: 12px; height: 12px; margin-top: -4px; margin-bottom: -4px; border-radius: 6px; }
        """)
        
        self.config = config_manager.load_config()
        self.current_prof = self.config.get("current_profile", "Default Profile")
        self.mouse_data = self.config["profiles"][self.current_prof]["mouse"]
        
        # Считываем уставки из JSON с безопасными дефолтами
        saved_auto_hide = self.mouse_data.get("toolbar_auto_hide", True)
        saved_opacity_enabled = self.mouse_data.get("toolbar_opacity_enabled", False)
        saved_opacity_val = self.mouse_data.get("toolbar_opacity_value", 80)
        saved_trigger_length = self.mouse_data.get("toolbar_trigger_length", 60)
        saved_trigger_width = self.mouse_data.get("toolbar_trigger_width", 6)
        saved_trigger_pos_idx = self.mouse_data.get("toolbar_trigger_position_idx", 1)
        saved_hide_delay = self.mouse_data.get("toolbar_hide_delay_sec", 5)
        saved_x = self.mouse_data.get("toolbar_anchor_x", -1)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(8)
        
        # 1. ЗАГОЛОВОК И ТУМБЛЕР Исчезновения
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)
        ico = QLabel()
        ico.setStyleSheet("background: transparent; border: none;")
        pix = QPixmap(styles.get_image("mouse1.png"))
        if not pix.isNull():
            ico.setPixmap(pix.scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        top_layout.addWidget(ico)
        
        title = QLabel("Управление Панелью ИИ")
        title.setStyleSheet("color: #ffffff; font-size: 12px; font-weight: bold; background: transparent; border: none;")
        top_layout.addWidget(title)
        top_layout.addStretch()
        
        self.toggle = QPushButton("●")
        self.toggle.setCheckable(True)
        self.toggle.setChecked(saved_auto_hide)
        self.toggle.setFixedSize(44, 20)
        self.toggle.clicked.connect(self.on_auto_hide_toggle_clicked)
        top_layout.addWidget(self.toggle)
        layout.addLayout(top_layout)
        
        # 2. РАДИО-КНОПКИ СТОРОН ЭКРАНА
        side_layout = QHBoxLayout()
        side_layout.setSpacing(12)
        side_title = QLabel("Сторона:")
        side_title.setStyleSheet("color: #557560; font-size: 11px; font-weight: bold; background: transparent; border: none;")
        side_layout.addWidget(side_title)
        
        self.radio_top = QRadioButton("Вверху")
        self.radio_left = QRadioButton("Слева")
        self.radio_right = QRadioButton("Справа")
        
        self.side_group = QButtonGroup(self)
        self.side_group.addButton(self.radio_top)
        self.side_group.addButton(self.radio_left)
        self.side_group.addButton(self.radio_right)
        
        screen = QApplication.primaryScreen().geometry()
        if saved_x > (screen.width() - 200):
            self.radio_right.setChecked(True)
        elif saved_x == 0:
            self.radio_left.setChecked(True)
        else:
            self.radio_top.setChecked(True)
            
        self.radio_top.clicked.connect(lambda: self.change_toolbar_side("top"))
        self.radio_left.clicked.connect(lambda: self.change_toolbar_side("left"))
        self.radio_right.clicked.connect(lambda: self.change_toolbar_side("right"))
        
        side_layout.addWidget(self.radio_top)
        side_layout.addWidget(self.radio_left)
        side_layout.addWidget(self.radio_right)
        side_layout.addStretch()
        layout.addLayout(side_layout)
# modules/mouse/mouse_sett3.py - ЧАСТЬ 2 ИЗ 3 (ПОЛНОСТЬЮ ИСПРАВЛЕННАЯ — РАДИОКНОПКИ ПОЗИЦИЙ И ПОЛЗУНКИ)
        # 3. СЛАЙДЕР СЕКУНД СКРЫТИЯ
        slider_layout = QHBoxLayout()
        slider_layout.setSpacing(10)
        self.slider_title = QLabel(f"Скрыть через: {saved_hide_delay} сек")
        self.slider_title.setStyleSheet("color: #ffffff; font-size: 11px; background: transparent; border: none;")
        slider_layout.addWidget(self.slider_title)
        
        self.delay_slider = QSlider(Qt.Orientation.Horizontal)
        self.delay_slider.setMinimum(3)
        self.delay_slider.setMaximum(15)
        self.delay_slider.setValue(saved_hide_delay)
        self.delay_slider.setFixedWidth(200)
        self.delay_slider.valueChanged.connect(self.on_delay_slider_changed)
        slider_layout.addWidget(self.delay_slider)
        slider_layout.addStretch()
        layout.addLayout(slider_layout)

        # 4. ПОЛЗУНОК ДЛИНЫ ТРИГГЕРА
        len_layout = QHBoxLayout()
        len_layout.setSpacing(10)
        self.len_title = QLabel(f"Длина триггера: {saved_trigger_length} px")
        self.len_title.setStyleSheet("color: #ffffff; font-size: 11px; background: transparent; border: none;")
        len_layout.addWidget(self.len_title)
        
        self.len_slider = QSlider(Qt.Orientation.Horizontal)
        self.len_slider.setMinimum(20)
        self.len_slider.setMaximum(200)
        self.len_slider.setValue(saved_trigger_length)
        self.len_slider.setFixedWidth(200)
        self.len_slider.valueChanged.connect(self.on_len_slider_changed)
        len_layout.addWidget(self.len_slider)
        len_layout.addStretch()
        layout.addLayout(len_layout)

        # 5. ПОЛЗУНОК ТОЛЩИНЫ (ШИРИНЫ) ТРИГГЕРА
        width_layout = QHBoxLayout()
        width_layout.setSpacing(10)
        self.width_title = QLabel(f"Толщина триггера: {saved_trigger_width} px")
        self.width_title.setStyleSheet("color: #ffffff; font-size: 11px; background: transparent; border: none;")
        width_layout.addWidget(self.width_title)
        
        self.width_slider = QSlider(Qt.Orientation.Horizontal)
        self.width_slider.setMinimum(2)
        self.width_slider.setMaximum(30)
        self.width_slider.setValue(saved_trigger_width)
        self.width_slider.setFixedWidth(200)
        self.width_slider.valueChanged.connect(self.on_width_slider_changed)
        width_layout.addWidget(self.width_slider)
        width_layout.addStretch()
        layout.addLayout(width_layout)

        # 6. РАДИО-КНОПКИ ПОЗИЦИИ НА СТОРОНЕ ЭКРАНА (ПОЛНАЯ ЗАМЕНА СТАРОГО COMBOBOX)
        pos_layout = QHBoxLayout()
        pos_layout.setSpacing(12)
        pos_title = QLabel("Позиция:")
        pos_title.setStyleSheet("color: #557560; font-size: 11px; font-weight: bold; background: transparent; border: none;")
        pos_layout.addWidget(pos_title)
        
        self.radio_pos1 = QRadioButton("Поз 1 (Низ/Лево)")
        self.radio_pos2 = QRadioButton("Поз 2 (Центр)")
        self.radio_pos3 = QRadioButton("Поз 3 (Верх/Право)")
        
        self.pos_group = QButtonGroup(self)
        self.pos_group.addButton(self.radio_pos1)
        self.pos_group.addButton(self.radio_pos2)
        self.pos_group.addButton(self.radio_pos3)
        
        # Выставляем галочку на основе индекса, сохраненного в JSON
        if saved_trigger_pos_idx == 0:
            self.radio_pos1.setChecked(True)
        elif saved_trigger_pos_idx == 2:
            self.radio_pos3.setChecked(True)
        else:
            self.radio_pos2.setChecked(True)
            
        self.radio_pos1.clicked.connect(lambda: self.change_toolbar_position_live(0))
        self.radio_pos2.clicked.connect(lambda: self.change_toolbar_position_live(1))
        self.radio_pos3.clicked.connect(lambda: self.change_toolbar_position_live(2))
        
        pos_layout.addWidget(self.radio_pos1)
        pos_layout.addWidget(self.radio_pos2)
        pos_layout.addWidget(self.radio_pos3)
        pos_layout.addStretch()
        layout.addLayout(pos_layout)
        
        # 7. ГАЛОЧКА И ПОЛЗУНОК ПРОЗРАЧНОСТИ
        self.opacity_check = QCheckBox("Включить прозрачность")
        self.opacity_check.setChecked(saved_opacity_enabled)
        self.opacity_check.clicked.connect(self.on_opacity_check_clicked)
        layout.addWidget(self.opacity_check)

        op_layout = QHBoxLayout()
        op_layout.setSpacing(10)
        self.op_title = QLabel(f"Прозрачность: {saved_opacity_val}%")
        self.op_title.setStyleSheet("color: #ffffff; font-size: 11px; background: transparent; border: none;")
        op_layout.addWidget(self.op_title)
        
        self.op_slider = QSlider(Qt.Orientation.Horizontal)
        self.op_slider.setMinimum(10)
        self.op_slider.setMaximum(100)
        self.op_slider.setValue(saved_opacity_val)
        self.op_slider.setFixedWidth(200)
        self.op_slider.valueChanged.connect(self.on_op_slider_changed)
        op_layout.addWidget(self.op_slider)
        op_layout.addStretch()
        layout.addLayout(op_layout)
        
        layout.addStretch()
        self.update_toggle_style()
# modules/mouse/mouse_sett3.py - ЧАСТЬ 3 ИЗ 3 (ТОЧЕЧНОЕ ИСПРАВЛЕНИЕ ПЕРЕМЕЩЕНИЯ ОТКРЫТОГО ТУЛБАРА ПО ПОЗИЦИЯМ)
    def on_auto_hide_toggle_clicked(self, checked):
        self.update_toggle_style()
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        config["profiles"][current_prof]["mouse"]["toolbar_auto_hide"] = checked
        config_manager.save_config(config)
        main_win = self.window()
        if hasattr(main_win, 'mod_mouse') and main_win.mod_mouse.toolbar_window:
            main_win.mod_mouse.toolbar_window.update_hide_policy_from_json()

    def on_delay_slider_changed(self, value):
        self.slider_title.setText(f"Скрыть через: {value} сек")
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        config["profiles"][current_prof]["mouse"]["toolbar_hide_delay_sec"] = value
        config_manager.save_config(config)

    def on_len_slider_changed(self, value):
        self.len_title.setText(f"Длина триггера: {value} px")
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        config["profiles"][current_prof]["mouse"]["toolbar_trigger_length"] = value
        config_manager.save_config(config)
        main_win = self.window()
        if hasattr(main_win, 'mod_mouse') and main_win.mod_mouse.toolbar_window:
            main_win.mod_mouse.toolbar_window.update_trigger_geometry_live()

    def on_width_slider_changed(self, value):
        self.width_title.setText(f"Толщина триггера: {value} px")
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        config["profiles"][current_prof]["mouse"]["toolbar_trigger_width"] = value
        config_manager.save_config(config)
        main_win = self.window()
        if hasattr(main_win, 'mod_mouse') and main_win.mod_mouse.toolbar_window:
            main_win.mod_mouse.toolbar_window.update_trigger_geometry_live()

    def change_toolbar_position_live(self, index):
        """МГНОВЕННЫЙ ПЕРЕЛЕТ: сохраняет позицию и сразу двигает тулбар на его текущей стороне"""
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        config["profiles"][current_prof]["mouse"]["toolbar_trigger_position_idx"] = index
        config_manager.save_config(config)
        
        # Определяем, на какой стороне сейчас находится тулбар по активной радиокнопке
        current_side = "top"
        if self.radio_left.isChecked():
            current_side = "left"
        elif self.radio_right.isChecked():
            current_side = "right"
            
        # Запускаем пересчет координат для этой стороны, но уже с учетом новой позиции!
        self.change_toolbar_side(current_side)

    def on_opacity_check_clicked(self, checked):
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        config["profiles"][current_prof]["mouse"]["toolbar_opacity_enabled"] = checked
        config_manager.save_config(config)
        main_win = self.window()
        if hasattr(main_win, 'mod_mouse') and main_win.mod_mouse.toolbar_window:
            main_win.mod_mouse.toolbar_window.apply_opacity_sync_logic()

    def on_op_slider_changed(self, value):
        self.op_title.setText(f"Прозрачность: {value}%")
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        config["profiles"][current_prof]["mouse"]["toolbar_opacity_value"] = value
        config_manager.save_config(config)
        main_win = self.window()
        if hasattr(main_win, 'mod_mouse') and main_win.mod_mouse.toolbar_window:
            main_win.mod_mouse.toolbar_window.apply_opacity_sync_logic()

    def change_toolbar_side(self, side):
        """МАТЕМАТИКА ОТКРЫТОГО РЕЖИМА: высчитывает координаты стороны СТРОГО с учетом позиции 1, 2, 3"""
        screen = QApplication.primaryScreen().geometry()
        btn_size = 42
        panel_long_dim = (btn_size + 4) * 8 + 30
        panel_short_dim = btn_size + 8
        
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        mouse_conf = config["profiles"][current_prof]["mouse"]
        
        # Считываем выбранную позицию (0 - низ/лево, 1 - центр, 2 - верх/право)
        pos_idx = mouse_conf.get("toolbar_trigger_position_idx", 1)
        
        new_x = -1
        new_y = 0
        
        if side == "right":
            new_x = screen.width() - panel_short_dim
            if pos_idx == 0:    # Позиция 1: Низ стороны
                new_y = screen.height() - panel_long_dim - 10
            elif pos_idx == 2:  # Позиция 3: Верх стороны
                new_y = 10
            else:               # Позиция 2: Центр стороны
                new_y = (screen.height() - panel_long_dim) // 2
                
        elif side == "left":
            new_x = 0
            if pos_idx == 0:    # Позиция 1: Низ стороны
                new_y = screen.height() - panel_long_dim - 10
            elif pos_idx == 2:  # Позиция 3: Верх стороны
                new_y = 10
            else:               # Позиция 2: Центр стороны
                new_y = (screen.height() - panel_long_dim) // 2
                
        else: # top (Панель горизонтальная вверху экрана)
            new_y = 0
            if pos_idx == 0:    # Позиция 1: Левый край верха
                new_x = 10
            elif pos_idx == 2:  # Позиция 3: Правый край верха
                new_x = screen.width() - panel_long_dim - 10
            else:               # Позиция 2: Центр верха
                new_x = (screen.width() - panel_long_dim) // 2
            
        mouse_conf["toolbar_anchor_x"] = new_x
        mouse_conf["toolbar_anchor_y"] = new_y
        config_manager.save_config(config)
        
        main_win = self.window()
        if hasattr(main_win, 'mod_mouse'):
            # Полностью пересоздаем тулбар, и он считает новые точные координаты из JSON
            main_win.mod_mouse.hot_rebuild_toolbar_geometry()

    def update_toggle_style(self):
        if self.toggle.isChecked():
            self.toggle.setStyleSheet("QPushButton { background-color: #2ed573; border: none; border-radius: 10px; text-align: right; padding-right: 0px; color: white; font-size: 34px; font-weight: bold; padding-top: -10px; }")
            self.toggle.setText("●")
        else:
            self.toggle.setStyleSheet("QPushButton { background-color: #10381f; border: none; border-radius: 10px; text-align: left; padding-left: 0px; color: white; font-size: 34px; font-weight: bold; padding-top: -10px; }")
            self.toggle.setText("●")
