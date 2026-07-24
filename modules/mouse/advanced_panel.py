# modules/mouse/advanced_panel.py - ЧАСТЬ 1 ИЗ 4 (ИСПРАВЛЕННАЯ — ИНИЦИАЛИЗАЦИЯ И НЕОНОВЫЕ СТИЛИ КАРТОЧКИ)
import os
import config_manager
import styles
import subprocess
import ctypes
import time
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QApplication, QFrame, QLabel, QCheckBox, QSpinBox
from PyQt6.QtCore import Qt, QSize, QPoint
from PyQt6.QtGui import QCursor, QIcon, QPixmap

# Подключаем наш автономный кликер
from modules.mouse.advanced_clicker import AdvancedDwellClicker

class MouseAdvancedPanel(QWidget):
    def __init__(self, main_window_ref):
        super().__init__()
        self.main_win = main_window_ref  # Ссылка на MainWindow
        
        # Создаем собственный изолированный движок кликов
        self.advanced_clicker = AdvancedDwellClicker()
        self.advanced_clicker.panel_ref = self  # Связываем кликер с панелью для сброса графики
        
        # Переменные перемещения окна
        self.drag_position = None
        
        # Настройка флагов окна: без рамок, поверх всего, Tool-окно (не забирает фокус ввода ОС)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        
        # Увеличиваем высоту с 200 до 245 пикселей под новый нижний ряд из 3-х системных кнопок
        self.setFixedSize(250, 245)
        
        # Центрируем карточку на основном мониторе при первом показе
        screen = QApplication.primaryScreen().geometry()
        self.move((screen.width() - 250) // 2, (screen.height() - 245) // 2)
        
        # Главный контейнер-карточка (Темно-зеленый фон с яркой неоновой голубой рамкой)
        self.bg_frame = QFrame(self)
        self.bg_frame.setObjectName("AdvancedCard")
        self.bg_frame.setGeometry(0, 0, 250, 245)
        self.bg_frame.setStyleSheet("""
            QFrame#AdvancedCard { background-color: rgba(25, 45, 30, 0.95); border: 2px solid #00d2ff; border-radius: 12px; }
            QLabel { color: #ffffff; font-family: 'Segoe UI', sans-serif; font-size: 11px; font-weight: bold; background: transparent; border: none; }
            
            /* Стилизация квадратных зеленых флажков-чекбоксов под ваш макет */
            QCheckBox { background: transparent; border: none; }
            QCheckBox::indicator { width: 16px; height: 16px; border: 1px solid #2ed573; border-radius: 4px; background-color: #2ed573; }
            QCheckBox::indicator:unchecked { background-color: #2ed573; border-color: #2ed573; }
            QCheckBox::indicator:checked { background-color: #00d2ff; border-color: #ffffff; }
            
            /* Темные спинбоксы с белым текстом */
            QSpinBox { background-color: #030d08; color: #ffffff; border: 1px solid #10381f; border-radius: 4px; padding-right: 15px; font-size: 11px; font-weight: bold; }
            
            /* Специальные стили для трех новых системных кнопок аварийного вызова */
            QPushButton#SysBtn { background-color: #0c2014; color: #00d2ff; border: 1px solid #00d2ff; border-radius: 6px; font-family: 'Segoe UI', sans-serif; font-size: 10px; font-weight: bold; }
            QPushButton#SysBtn:hover { background-color: #00d2ff; color: #030d08; }
        """)
        
        card_v_layout = QVBoxLayout(self.bg_frame)
        card_v_layout.setContentsMargins(12, 10, 12, 12)
        card_v_layout.setSpacing(8)
        
        # =========================================================================
        # ВЕРХНИЙ БЛОК: НАСТРОЙКА УДЕРЖАНИЯ КЛИКА ПО ВРЕМЕНИ С АВТОСОХРАНЕНИЕМ
        # =========================================================================
        macro_top_layout = QHBoxLayout()
        macro_top_layout.setSpacing(10)
        macro_top_layout.setContentsMargins(2, 2, 2, 2)
# modules/mouse/advanced_panel.py - ЧАСТЬ 2 ИЗ 4 (БЛОКИ НАСТРОЕК ТАЙМЕРОВ И КНОПКИ РЕЖИМОВ МЫШИ)
        # --- ЛЕВАЯ СТOРOНА: Макрос для Левой Кнопки Мыши (ЛКМ) ---
        l_layout = QHBoxLayout()
        l_layout.setSpacing(4)
        self.chk_hold_left = QCheckBox()
        self.chk_hold_left.setFixedSize(16, 16)
        self.chk_hold_left.toggled.connect(self.on_left_time_hold_toggled)
        self.spin_hold_left = QSpinBox()
        self.spin_hold_left.setRange(1, 60)
        self.spin_hold_left.setValue(1)
        self.spin_hold_left.setFixedSize(65, 22)
        self.spin_hold_left.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spin_hold_left.setEnabled(True)
        self.spin_hold_left.valueChanged.connect(self.save_advanced_timers_config)
        lbl_sec_l = QLabel("сек")
        lbl_sec_l.setStyleSheet("color: #ffffff; font-weight: bold;")
        l_layout.addWidget(self.chk_hold_left)
        l_layout.addWidget(self.spin_hold_left)
        l_layout.addWidget(lbl_sec_l)
        macro_top_layout.addLayout(l_layout)
        macro_top_layout.addStretch()

        # --- ПРAВАЯ СТOРOНА: Макрос для Правой Кнопки Мыши (ПКМ) ---
        r_layout = QHBoxLayout()
        r_layout.setSpacing(4)
        self.chk_hold_right = QCheckBox()
        self.chk_hold_right.setFixedSize(16, 16)
        self.chk_hold_right.toggled.connect(self.on_right_time_hold_toggled)
        self.spin_hold_right = QSpinBox()
        self.spin_hold_right.setRange(1, 60)
        self.spin_hold_right.setValue(4)
        self.spin_hold_right.setFixedSize(65, 22)
        self.spin_hold_right.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spin_hold_right.setEnabled(True)
        self.spin_hold_right.valueChanged.connect(self.save_advanced_timers_config)
        lbl_sec_r = QLabel("сек")
        lbl_sec_r.setStyleSheet("color: #ffffff; font-weight: bold;")
        r_layout.addWidget(self.chk_hold_right)
        r_layout.addWidget(self.spin_hold_right)
        r_layout.addWidget(lbl_sec_r)
        macro_top_layout.addLayout(r_layout)
        card_v_layout.addLayout(macro_top_layout)

        # Ряд для трех кнопок с вашими размерами (85-45-85) и отступами (2)
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(2)
        self.btn_lmb = QPushButton()
        self.btn_lmb.setFixedSize(85, 110)
        self.btn_lmb.clicked.connect(lambda: self.change_autonomous_mode("left"))
        self.btn_mmb = QPushButton()
        self.btn_mmb.setFixedSize(45, 110)
        self.btn_mmb.clicked.connect(lambda: self.change_autonomous_mode("middle"))
        self.btn_rmb = QPushButton()
        self.btn_rmb.setFixedSize(85, 110)
        self.btn_rmb.clicked.connect(lambda: self.change_autonomous_mode("right"))
        self.load_button_icons()
        buttons_layout.addWidget(self.btn_lmb)
        buttons_layout.addWidget(self.btn_mmb)
        buttons_layout.addWidget(self.btn_rmb)
        card_v_layout.addLayout(buttons_layout)

        # =========================================================================
        # НИЖНИЙ РЯД: МОДИФИКАТОРЫ, «УДЕРЖ», «2х», «2К» И «СКРОЛЛ»
        # =========================================================================
        macro_bottom_layout = QHBoxLayout()
        macro_bottom_layout.setSpacing(6)
        macro_bottom_layout.setContentsMargins(2, 0, 2, 0)
        macro_bottom_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        lbl_uderzh = QLabel("удерж")
        lbl_uderzh.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 11px;")
        self.chk_drag_hold = QCheckBox()
        self.chk_drag_hold.setFixedSize(14, 14)
        self.chk_drag_hold.toggled.connect(self.on_drag_hold_toggled)
        macro_bottom_layout.addWidget(lbl_uderzh)
        macro_bottom_layout.addWidget(self.chk_drag_hold)
        macro_bottom_layout.addSpacing(6)
        
        lbl_double = QLabel("2х")
        lbl_double.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 11px;")
        self.chk_double_click = QCheckBox()
        self.chk_double_click.setFixedSize(14, 14)
        self.chk_double_click.toggled.connect(self.on_double_click_toggled)
        macro_bottom_layout.addWidget(lbl_double)
        macro_bottom_layout.addWidget(self.chk_double_click)
        macro_bottom_layout.addSpacing(6)
        
        lbl_2k = QLabel("2К")
        lbl_2k.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 11px;")
        self.chk_2k_combo = QCheckBox()
        self.chk_2k_combo.setFixedSize(14, 14)
        self.chk_2k_combo.toggled.connect(self.on_2k_combo_toggled)
        macro_bottom_layout.addWidget(lbl_2k)
        macro_bottom_layout.addWidget(self.chk_2k_combo)
        macro_bottom_layout.addSpacing(6)
        
        lbl_scroll = QLabel("скролл")
        lbl_scroll.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 11px;")
        self.chk_scroll_mode = QCheckBox()
        self.chk_scroll_mode.setFixedSize(14, 14)
        self.chk_scroll_mode.toggled.connect(self.on_scroll_mode_toggled)
        macro_bottom_layout.addWidget(lbl_scroll)
        macro_bottom_layout.addWidget(self.chk_scroll_mode)
        card_v_layout.addLayout(macro_bottom_layout)
# modules/mouse/advanced_panel.py - ЧАСТЬ 3 ИЗ 4 (СИСТЕМНЫЕ КНОПКИ И МЕТОДЫ-ПЕРЕХВАТЧИКИ ФЛАЖКОВ)
        # =========================================================================
        # НОВЕЙШИЙ РЯД: 3 СИСТЕМНЫЕ КНОПКИ (ПРОГРАММА, WINDOWS, КЛАВИАТУРА)
        # =========================================================================
        sys_buttons_layout = QHBoxLayout()
        sys_buttons_layout.setSpacing(4)
        sys_buttons_layout.setContentsMargins(2, 2, 2, 0)
        
        self.btn_sys_app = QPushButton("Программа")
        self.btn_sys_app.setObjectName("SysBtn")
        self.btn_sys_app.setFixedSize(72, 22)
        self.btn_sys_app.clicked.connect(self.execute_system_app_call)
        
        self.btn_sys_win = QPushButton("Windows")
        self.btn_sys_win.setObjectName("SysBtn")
        self.btn_sys_win.setFixedSize(72, 22)
        self.btn_sys_win.clicked.connect(self.execute_system_win_call)
        
        self.btn_sys_kbd = QPushButton("Клава")
        self.btn_sys_kbd.setObjectName("SysBtn")
        self.btn_sys_kbd.setFixedSize(72, 22)
        self.btn_sys_kbd.clicked.connect(self.execute_system_kbd_call)
        
        sys_buttons_layout.addWidget(self.btn_sys_app)
        sys_buttons_layout.addWidget(self.btn_sys_win)
        sys_buttons_layout.addWidget(self.btn_sys_kbd)
        card_v_layout.addLayout(sys_buttons_layout)
        
        self.combo_buttons_selected = {"left": True, "right": True}
        self.update_button_styles()

    def on_left_time_hold_toggled(self, checked):
        if checked:
            self.chk_drag_hold.blockSignals(True); self.chk_drag_hold.setChecked(False); self.chk_drag_hold.blockSignals(False)
            self.chk_double_click.blockSignals(True); self.chk_double_click.setChecked(False); self.chk_double_click.blockSignals(False)
            self.chk_2k_combo.blockSignals(True); self.chk_2k_combo.setChecked(False); self.chk_2k_combo.blockSignals(False)
            self.chk_scroll_mode.blockSignals(True); self.chk_scroll_mode.setChecked(False); self.chk_scroll_mode.blockSignals(False)

    def on_right_time_hold_toggled(self, checked):
        if checked:
            self.chk_drag_hold.blockSignals(True); self.chk_drag_hold.setChecked(False); self.chk_drag_hold.blockSignals(False)
            self.chk_double_click.blockSignals(True); self.chk_double_click.setChecked(False); self.chk_double_click.blockSignals(False)
            self.chk_2k_combo.blockSignals(True); self.chk_2k_combo.setChecked(False); self.chk_2k_combo.blockSignals(False)
            self.chk_scroll_mode.blockSignals(True); self.chk_scroll_mode.setChecked(False); self.chk_scroll_mode.blockSignals(False)

    def on_drag_hold_toggled(self, checked):
        if checked:
            self.chk_hold_left.blockSignals(True); self.chk_hold_left.setChecked(False); self.chk_hold_left.blockSignals(False)
            self.chk_hold_right.blockSignals(True); self.chk_hold_right.setChecked(False); self.chk_hold_right.blockSignals(False)
            self.chk_double_click.blockSignals(True); self.chk_double_click.setChecked(False); self.chk_double_click.blockSignals(False)
            self.chk_2k_combo.blockSignals(True); self.chk_2k_combo.setChecked(False); self.chk_2k_combo.blockSignals(False)
            self.chk_scroll_mode.blockSignals(True); self.chk_scroll_mode.setChecked(False); self.chk_scroll_mode.blockSignals(False)
        else:
            if hasattr(self.advanced_clicker, 'reset_drag_hold_state'):
                self.advanced_clicker.reset_drag_hold_state()

    def on_double_click_toggled(self, checked):
        if checked:
            self.chk_hold_left.blockSignals(True); self.chk_hold_left.setChecked(False); self.chk_hold_left.blockSignals(False)
            self.chk_hold_right.blockSignals(True); self.chk_hold_right.setChecked(False); self.chk_hold_right.blockSignals(False)
            self.chk_drag_hold.blockSignals(True); self.chk_drag_hold.setChecked(False); self.chk_drag_hold.blockSignals(False)
            self.chk_2k_combo.blockSignals(True); self.chk_2k_combo.setChecked(False); self.chk_2k_combo.blockSignals(False)
            self.chk_scroll_mode.blockSignals(True); self.chk_scroll_mode.setChecked(False); self.chk_scroll_mode.blockSignals(False)

    def on_2k_combo_toggled(self, checked):
        if checked:
            self.chk_hold_left.blockSignals(True); self.chk_hold_left.setChecked(False); self.chk_hold_left.blockSignals(False)
            self.chk_hold_right.blockSignals(True); self.chk_hold_right.setChecked(False); self.chk_hold_right.blockSignals(False)
            self.chk_drag_hold.blockSignals(True); self.chk_drag_hold.setChecked(False); self.chk_drag_hold.blockSignals(False)
            self.chk_double_click.blockSignals(True); self.chk_double_click.setChecked(False); self.chk_double_click.blockSignals(False)
            self.chk_scroll_mode.blockSignals(True); self.chk_scroll_mode.setChecked(False); self.chk_scroll_mode.blockSignals(False)
            self.combo_buttons_selected = {"left": True, "right": True}
        else:
            if hasattr(self.advanced_clicker, 'reset_2k_combo_state'):
                self.advanced_clicker.reset_2k_combo_state()
            self.update_button_styles()

    def on_scroll_mode_toggled(self, checked):
        if checked:
            self.chk_hold_left.blockSignals(True); self.chk_hold_left.setChecked(False); self.chk_hold_left.blockSignals(False)
            self.chk_hold_right.blockSignals(True); self.chk_hold_right.setChecked(False); self.chk_hold_right.blockSignals(False)
            self.chk_drag_hold.blockSignals(True); self.chk_drag_hold.setChecked(False); self.chk_drag_hold.blockSignals(False)
            self.chk_double_click.blockSignals(True); self.chk_double_click.setChecked(False); self.chk_double_click.blockSignals(False)
            self.chk_2k_combo.blockSignals(True); self.chk_2k_combo.setChecked(False); self.chk_2k_combo.blockSignals(False)
            self.advanced_clicker.click_type = "middle"
        else:
            if hasattr(self.advanced_clicker, 'close_scroll_joystick_hardware'):
                self.advanced_clicker.close_scroll_joystick_hardware()
            self.advanced_clicker.click_type = "left"
            self.update_button_styles()
# modules/mouse/advanced_panel.py - ЧАСТЬ 4 ИЗ 4 (УЛЬТРА-ОПТИМИЗИРОВАННАЯ СИСТЕМНАЯ ВЕРСИЯ БЕЗ НАГРУЗКИ НА ОЗУ)
    def uncheck_hold_visuals(self, button_type):
        if button_type == "left":
            self.chk_hold_left.setChecked(False)
        elif button_type == "right":
            self.chk_hold_right.setChecked(False)
        elif button_type == "drag_hold_finished":
            self.chk_drag_hold.setChecked(False)
        elif button_type == "double_click_finished":
            self.chk_double_click.setChecked(False)
        elif button_type == "2k_combo_finished":
            self.chk_2k_combo.setChecked(False)
            self.update_button_styles()
        elif button_type == "scroll_mode_finished":
            self.chk_scroll_mode.setChecked(False)
            self.update_button_styles()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = None
            event.accept()

    def load_button_icons(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        lmb_path = os.path.join(base_dir, "images", "btn_lmb.png")
        mmb_path = os.path.join(base_dir, "images", "btn_mmb.png")
        rmb_path = os.path.join(base_dir, "images", "btn_rmb.png")
        if os.path.exists(lmb_path):
            self.btn_lmb.setIcon(QIcon(lmb_path)); self.btn_lmb.setIconSize(QSize(75, 100))
        else:
            self.btn_lmb.setText("ЛКМ")
        if os.path.exists(mmb_path):
            self.btn_mmb.setIcon(QIcon(mmb_path)); self.btn_mmb.setIconSize(QSize(75, 100))
        else:
            self.btn_mmb.setText("Колесо")
        if os.path.exists(rmb_path):
            self.btn_rmb.setIcon(QIcon(rmb_path)); self.btn_rmb.setIconSize(QSize(75, 100))
        else:
            self.btn_rmb.setText("ПКМ")

    def change_autonomous_mode(self, new_mode):
        if self.chk_2k_combo.isChecked():
            if new_mode in ["left", "right"]:
                self.combo_buttons_selected[new_mode] = not self.combo_buttons_selected[new_mode]
        elif self.chk_scroll_mode.isChecked():
            return
        else:
            self.advanced_clicker.click_type = new_mode
            self.update_button_styles()

    def execute_system_app_call(self):
        """Кнопка 'Программа': Принудительно разворачивает и выдергивает окно трекера поверх всех игр"""
        if self.main_win:
            self.main_win.setWindowFlags(self.main_win.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
            if self.main_win.isMinimized():
                self.main_win.showNormal()
            else:
                self.main_win.show()
            self.main_win.raise_()
            self.main_win.activateWindow()
            screen = QApplication.primaryScreen().geometry()
            self.main_win.move((screen.width() - self.main_win.width()) // 2, (screen.height() - self.main_win.height()) // 2)

    def execute_system_win_call(self):
        """Кнопка 'Windows': Эмулирует железное нажатие клавиши Win на клавиатуре для открытия Пуска"""
        ctypes.windll.user32.keybd_event(0x5B, 0, 0, 0)
        time.sleep(0.05)
        ctypes.windll.user32.keybd_event(0x5B, 0, 0x0002, 0)

    def execute_system_kbd_call(self):
        """Кнопка 'Клава': Безопасно запускает встроенную экранную клавиатуру Windows"""
        try:
            subprocess.Popen(os.path.join(os.environ['SystemRoot'], 'System32', 'osk.exe'), shell=True)
        except Exception as e:
            print(f"Ошибка запуска экранной клавиатуры: {e}")

    def hideEvent(self, event):
        """🔥 СУПЕР-ОПТИМИЗАЦИЯ: убрано дисковое чтение JSON при закрытии панели макросов"""
        super().hideEvent(event)
        if hasattr(self.advanced_clicker, 'reset_drag_hold_state'):
            self.advanced_clicker.reset_drag_hold_state()
        if hasattr(self.advanced_clicker, 'reset_2k_combo_state'):
            self.advanced_clicker.reset_2k_combo_state()
            
        # Прямо из ОЗУ MainWindow проверяем, активен ли тулбар, разгружая жесткий диск
        if hasattr(self.main_win, 'mod_mouse') and self.main_win.mod_mouse.toolbar_window:
            t_win = self.main_win.mod_mouse.toolbar_window
            if t_win.isVisible() or (hasattr(t_win, 'trigger_dot') and t_win.trigger_dot.isVisible()):
                screen = QApplication.primaryScreen().geometry()
                if t_win.is_expanded:
                    t_win.register_windows_appbar(t_win.x(), t_win.y(), screen.width(), screen.height())
                    t_win.show()
                else:
                    t_win.trigger_dot.show()

    def save_advanced_timers_config(self):
        """Мгновенно сохраняет выставленные секунды ЛКМ и ПКМ в текущий профиль config.json"""
        try:
            config = config_manager.load_config()
            current_prof = config.get("current_profile", "Default Profile")
            if "mouse" in config["profiles"][current_prof]:
                if "advanced_timers" not in config["profiles"][current_prof]["mouse"]:
                    config["profiles"][current_prof]["mouse"]["advanced_timers"] = {}
                config["profiles"][current_prof]["mouse"]["advanced_timers"]["left_hold_sec"] = self.spin_hold_left.value()
                config["profiles"][current_prof]["mouse"]["advanced_timers"]["right_hold_sec"] = self.spin_hold_right.value()
                config_manager.save_config(config)
        except Exception as e:
            print(f"Ошибка сохранения таймеров панели: {e}")

    def load_advanced_timers_config(self):
        """Считывает сохраненные секунды ЛКМ и ПКМ из config.json и выставляет их в спинбоксы"""
        try:
            config = config_manager.load_config()
            current_prof = config.get("current_profile", "Default Profile")
            mouse_cfg = config["profiles"][current_prof].get("mouse", {})
            timers_cfg = mouse_cfg.get("advanced_timers", {})
            left_sec = timers_cfg.get("left_hold_sec", 1)
            right_sec = timers_cfg.get("right_hold_sec", 4)
            self.spin_hold_left.blockSignals(True)
            self.spin_hold_left.setValue(left_sec)
            self.spin_hold_left.blockSignals(False)
            self.spin_hold_right.blockSignals(True)
            self.spin_hold_right.setValue(right_sec)
            self.spin_hold_right.blockSignals(False)
        except Exception as e:
            print(f"Ошибка загрузки таймеров панели: {e}")

    def showEvent(self, event):
        """ОРИГИНАЛЬНЫЙ СИНХРОНИЗИРОВАННЫЙ МЕТОД SHOWEVENT С АВТОЗАГРУЗКОЙ ДАННЫХ"""
        super().showEvent(event)
        self.advanced_clicker.click_type = "left"
        self.load_advanced_timers_config()
        if hasattr(self.main_win, 'mod_mouse') and self.main_win.mod_mouse.toolbar_window:
            t_win = self.main_win.mod_mouse.toolbar_window
            if hasattr(t_win, 'trigger_dot') and t_win.trigger_dot:
                t_win.trigger_dot.hide()
            t_win.unregister_windows_appbar()
            t_win.hide()
        self.update_button_styles()

    def update_button_styles(self):
        current_mode = self.advanced_clicker.click_type
        is_2k_active = self.chk_2k_combo.isChecked()
        is_scroll_active = self.chk_scroll_mode.isChecked()
        is_held_by_time = getattr(self.advanced_clicker, 'currently_held_button', None)
        is_held_by_drag = getattr(self.advanced_clicker, 'is_drag_holding', False)
        is_held_by_2k = getattr(self.advanced_clicker, 'is_2k_holding', False)
        is_held_by_scroll = getattr(self.advanced_clicker, 'is_scroll_joystick_active', False)
        
        held_button = None
        if is_held_by_time: held_button = is_held_by_time
        elif is_held_by_drag: held_button = getattr(self.advanced_clicker, 'drag_held_button_type', None)
        elif is_held_by_2k: held_button = getattr(self.advanced_clicker, 'combo_lead_button', None)
        elif is_held_by_scroll: held_button = "middle"
        
        held_style = "QPushButton { background-color: #ffffff; border: 3px solid #ff4d4d; border-radius: 6px; }"
        combo_style = "QPushButton { background-color: #ffffff; border: 2.5px solid #ffca28; border-radius: 6px; }"
        active_style = "QPushButton { background-color: #fa05f2; border: 2px solid #fa05f2; border-radius: 6px; } QPushButton:hover { background-color: #ffffff; }"
        inactive_style = "QPushButton { background-color: #36fa05; border: 1px solid #10381f; border-radius: 6px; } QPushButton:hover { border-color: #2ed573; background-color: #f0f0f0; }"
        
        if held_button == "left":
            self.btn_lmb.setStyleSheet(held_style)
        elif is_2k_active and self.combo_buttons_selected.get("left", False):
            self.btn_lmb.setStyleSheet(combo_style)
        else:
            self.btn_lmb.setStyleSheet(active_style if (current_mode == "left" and not is_2k_active and not is_scroll_active) else inactive_style)
            
        if held_button == "middle":
            self.btn_mmb.setStyleSheet(held_style)
        elif is_scroll_active and not is_held_by_scroll:
            self.btn_mmb.setStyleSheet(combo_style)
        else:
            self.btn_mmb.setStyleSheet(active_style if (current_mode == "middle" or is_scroll_active) else inactive_style)
            
        if held_button == "right":
            self.btn_rmb.setStyleSheet(held_style)
        elif is_2k_active and self.combo_buttons_selected.get("right", False):
            self.btn_rmb.setStyleSheet(combo_style)
        else:
            self.btn_rmb.setStyleSheet(active_style if (current_mode == "right" and not is_2k_active and not is_scroll_active) else inactive_style)

