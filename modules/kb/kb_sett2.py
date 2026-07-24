# modules/kb_sett2.py - ЧАСТЬ 1 ИЗ 6
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDialog, QComboBox, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import styles
import config_manager

class KeyboardSettingBlock2(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingCard2")
        self.config = config_manager.load_config()
        self.current_prof = self.config.get("current_profile", "Default Profile")
        self.kb_data = self.config["profiles"][self.current_prof]["kb"]
        
        # КЭШ В ОЗУ ДЛЯ СВЕРХБЫСТРОГО ДОСТУПА БЕЗ ТОРМОЗОВ ДИСКА
        self.cached_bindings = self.kb_data.get("bindings", {})
        self.cached_thresholds = self.kb_data.get("thresholds", {})
        
        # Словарь для хранения ссылок на физические объекты кнопок по их именам
        self.key_buttons = {}
        
        # Фирменная темно-фиолетовая кибер-стилизация
        self.setStyleSheet("""
            QFrame#SettingCard2 {
                background-color: #04030d;
                border: 1px solid #1a1038;
                border-radius: 10px;
            }
            QLabel {
                color: #ffffff;
                font-family: 'Segoe UI', sans-serif;
                font-size: 11px;
                background: transparent;
                border: none;
            }
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
        
        # Назначение клавиш
        title = QLabel("Назначение клавиш")
        title.setStyleSheet("color: #ffffff; font-size: 13px; font-weight: bold;")
        top_layout.addWidget(title)
        top_layout.addStretch()
        
        # СТРОГО ПО ТЗ: Добавлена интерактивная кнопка физического переключения нажатий клавиш в ОС
        self.btn_real_press = QPushButton()
        self.btn_real_press.setCheckable(True)
        
        # Загружаем сохраненный статус эмуляции (по дефолту True — нажимать кнопки в Windows)
        saved_press_state = self.kb_data.get("real_press_enabled", True)
        self.btn_real_press.setChecked(saved_press_state)
        self.btn_real_press.setFixedSize(105, 22)
        self.btn_real_press.clicked.connect(self.on_real_press_toggle_clicked)
        top_layout.addWidget(self.btn_real_press)
        
        # БЕГУНОК СВОРАЧИВАНИЯ КЛАВИАТУРЫ
        self.toggle = QPushButton("●")
        self.toggle.setCheckable(True)
        saved_open_state = self.kb_data.get("setting_2", True)
        self.toggle.setChecked(saved_open_state)
        self.toggle.setFixedSize(44, 20)
        self.toggle.setStyleSheet("background-color: #8a2be2; border: none; border-radius: 10px; text-align: right; color: white; font-size: 34px; font-weight: bold; padding-top: -10px;")
        self.toggle.clicked.connect(self.on_setting_toggle_clicked)
        top_layout.addWidget(self.toggle)
        self.main_layout.addLayout(top_layout)
        
        self.line = QFrame()
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setStyleSheet("background-color: #1a1038; min-height: 1px; max-height: 1px; border: none;")
        self.main_layout.addWidget(self.line)
        
        # Контейнер для клавиатуры, который будет сворачиваться
        self.keyboard_container = QWidget()
        self.kb_vbox = QVBoxLayout(self.keyboard_container)
        self.kb_vbox.setContentsMargins(0, 0, 0, 0)
        self.kb_vbox.setSpacing(4)
        self.main_layout.addWidget(self.keyboard_container)
# modules/kb_sett2.py - ЧАСТЬ 2 ИЗ 6 (ИСПРАВЛЕННАЯ С ВНЕДРЕНИЕМ КНОПКИ RST ВМЕСТО СИСТЕМНОЙ F10)
        # Отрисовка рядов виртуальной клавиатуры строго по физической сетке
        # РЯД 0: Функциональные клавиши (Esc, LMB, RMB, MMB, OSK, ЛП, СК, APP, F8, F9, RST, F11, F12)
        row0_layout = QHBoxLayout()
        row0_layout.setSpacing(3)
        self.create_key("Esc", 35, row0_layout)
        row0_layout.addSpacing(15)
        
        # ИИ-кнопки мыши, утилиты, ИИ-Скролл головы и кнопка APP на месте F7
        self.create_key("LMB", 30, row0_layout)
        self.create_key("RMB", 30, row0_layout)
        self.create_key("MMB", 30, row0_layout)
        self.create_key("OSK", 30, row0_layout)
        self.create_key("ЛП", 30, row0_layout)
        self.create_key("СК", 30, row0_layout)
        self.create_key("APP", 30, row0_layout) # Внедрена кнопка APP вместо F7
        row0_layout.addSpacing(10)
        
        self.create_key("F8", 30, row0_layout) # Сместилась левее на пустой слот
        row0_layout.addSpacing(10)
        
        # СТРОГО ПО ТЗ: Вырезаем системную клавишу F10 и врезаем на её законное место чистую кнопку RST (Reset)
        for f_key in ["F9", "RST", "F11", "F12"]:
            self.create_key(f_key, 30, row0_layout)
            
        self.kb_vbox.addLayout(row0_layout)
        self.kb_vbox.addSpacing(4)
        
        # РЯД 1: Цифры и спецсимволы
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(3)
        num_keys = ["~", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", "Backspace"]
        for key in num_keys:
            w = 55 if key == "Backspace" else 30
            self.create_key(key, w, row1_layout)
        self.kb_vbox.addLayout(row1_layout)
        
        # РЯД 2: Буквенный ряд QWERTY с кнопкой Tab
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(3)
        self.create_key("Tab", 45, row2_layout)
        q_keys = ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "[", "]", "\\"]
        for key in q_keys:
            self.create_key(key, 30, row2_layout)
        self.kb_vbox.addLayout(row2_layout)
        
        # РЯД 3: Буквенный ряд ASDFG с кнопками Caps и Enter
        row3_layout = QHBoxLayout()
        row3_layout.setSpacing(3)
        self.create_key("Caps", 52, row3_layout)
        a_keys = ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";", "'"]
        for key in a_keys:
            self.create_key(key, 30, row3_layout)
        self.create_key("Enter", 58, row3_layout)
        self.kb_vbox.addLayout(row3_layout)
        
        # РЯД 4: Буквенный ряд ZXCVB с кнопками Shift
        row4_layout = QHBoxLayout()
        row4_layout.setSpacing(3)
        self.create_key("LShift", 70, row4_layout)
        z_keys = ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"]
        for key in z_keys:
            self.create_key(key, 30, row4_layout)
        self.create_key("RShift", 75, row4_layout)
        self.kb_vbox.addLayout(row4_layout)
        
        # РЯД 5: Системные клавиши (Ctrl, Alt, Пробел) и Стрелочки управления
        row5_layout = QHBoxLayout()
        row5_layout.setSpacing(3)
        self.create_key("LCtrl", 40, row5_layout)
        self.create_key("Win", 35, row5_layout)
        self.create_key("LAlt", 40, row5_layout)
        self.create_key("Space", 185, row5_layout)
        self.create_key("RAlt", 40, row5_layout)
        self.create_key("RCtrl", 40, row5_layout)
        row5_layout.addSpacing(10)
        self.create_key("🡠", 30, row5_layout)
        
        arrow_vbox = QVBoxLayout()
        arrow_vbox.setSpacing(2)
        self.create_key("🡡", 30, arrow_vbox, height=14)
        self.create_key("🡣", 30, arrow_vbox, height=14)
        row5_layout.addLayout(arrow_vbox)
        self.create_key("🡢", 30, row5_layout)
        self.kb_vbox.addLayout(row5_layout)
        
        self.apply_visibility_layout_state(saved_open_state)
        self.update_real_press_button_style()


# modules/kb_sett2.py - ЧАСТЬ 3 ИЗ 6 (ИСПРАВЛЕННАЯ С ПОДДЕРЖКОЙ КНОПКИ RST)
    def create_key(self, text, width, target_layout, height=30):
        """Создает кнопку клавиатуры, сохраняя ссылку на нее для последующей динамической ИИ-подсветки"""
        btn = QPushButton(text)
        btn.setObjectName("VisualKey")
        btn.setFixedSize(width, height)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #0b0617;
                color: #a347ff;
                border: 1px solid #401970;
                border-radius: 4px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8a2be2;
                color: #ffffff;
                border-color: #ffffff;
            }
        """)
        btn.clicked.connect(lambda checked, t=text: self.open_gesture_binding_dialog(t))
        self.key_buttons[text] = btn
        target_layout.addWidget(btn)

    def apply_visibility_layout_state(self, is_open):
        """Вспомогательный метод: плавно схлопывает клавиатурную матрицу"""
        if is_open:
            self.keyboard_container.show()
            self.line.show()
            self.toggle.setStyleSheet("background-color: #8a2be2; border: none; border-radius: 10px; text-align: right; color: white; font-size: 34px; font-weight: bold; padding-top: -10px;")
            self.toggle.setText("●")
            self.setMinimumHeight(0)
            self.setMaximumHeight(16777215)
        else:
            self.keyboard_container.hide()
            self.line.hide()
            self.toggle.setStyleSheet("background-color: #1a1038; border: 1px solid #401970; border-radius: 10px; text-align: left; color: white; font-size: 34px; font-weight: bold; padding-top: -10px;")
            self.toggle.setText("●")
            self.setFixedHeight(42)

    def on_setting_toggle_clicked(self, checked):
        self.apply_visibility_layout_state(checked)
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        config["profiles"][current_prof]["kb"]["setting_2"] = checked
        config_manager.save_config(config)

    def on_real_press_toggle_clicked(self, checked):
        """Слот обработки клика по кнопке 'Вкл нажатия' с защитным окном по вашему ТЗ"""
        if not checked:
            # Если пользователь ВЫКЛЮЧАЕТ физический зажим кнопок клавиатуры в ОС — выводим QMessageBox
            from PyQt6.QtWidgets import QMessageBox
            msg = QMessageBox(self)
            msg.setWindowTitle("Предупреждение системы")
            msg.setText("ВНИМАНИЕ!\n\nВы отключаете физическую эмуляцию нажатий КЛАВИАТУРЫ in Windows.\n\nБуквы на экране перестанут печататься в играх и блокноте (останется только визуальная подсветка).\n\nВы уверены?")
            msg.setIcon(QMessageBox.Icon.Warning)
            yes_btn = msg.addButton("Да, отключить", QMessageBox.ButtonRole.YesRole)
            no_btn = msg.addButton("Отмена", QMessageBox.ButtonRole.NoRole)
            msg.setDefaultButton(no_btn)
            msg.setStyleSheet("QMessageBox { background-color: #04030d; border: 2px solid #8a2be2; border-radius: 10px; } QLabel { color: #ffffff; font-family: 'Segoe UI', sans-serif; font-size: 12px; font-weight: bold; } QPushButton { background-color: #0b0617; color: #a347ff; border: 1px solid #401970; border-radius: 4px; padding: 5px 12px; font-weight: bold; } QPushButton:hover { background-color: #8a2be2; color: white; border-color: white; }")
            msg.exec()
            
            if msg.clickedButton() != yes_btn:
                # Отмена: принудительно возвращаем кнопку в активное включенное положение
                self.btn_real_press.blockSignals(True)
                self.btn_real_press.setChecked(True)
                self.btn_real_press.blockSignals(False)
                self.update_real_press_button_style()
                return
                
        # Фиксируем и сохраняем подтвержденный статус
        self.update_real_press_button_style()
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        config["profiles"][current_prof]["kb"]["real_press_enabled"] = self.btn_real_press.isChecked()
        config_manager.save_config(config)

    def update_real_press_button_style(self):
        """Обновляет стиль кнопки 'Вкл нажатия'"""
        if self.btn_real_press.isChecked():
            self.btn_real_press.setText("Включено нажатия")
            self.btn_real_press.setStyleSheet("QPushButton { background-color: #0c2414; color: #2ed573; border: 1px solid #2ed573; border-radius: 4px; font-size: 10px; font-weight: bold; } QPushButton:hover { background-color: #2ed573; color: black; border-color: white; }")
        else:
            self.btn_real_press.setText("Выключено нажатия")
            self.btn_real_press.setStyleSheet("QPushButton { background-color: #160a0f; color: #ff4757; border: 1px solid #ff4757; border-radius: 4px; font-size: 10px; font-weight: bold; } QPushButton:hover { background-color: #ff4757; color: white; border-color: white; }")

# modules/kb_sett2.py - ЧАСТЬ 4 ИЗ 6 (ИСПРАВЛЕННАЯ С КОРРЕКТНЫМ ИМЕНЕМ RST)
    def open_gesture_binding_dialog(self, key_name):
        """Всплывающее КАСТОМНОЕ безрамочное окно калибровки жеста для выбранной клавиши клавиатуры"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"ИИ-Настройка клавиши [{key_name}]")
        dialog.setFixedSize(340, 190)
        
        # УБИРАЕМ РАМКУ WINDOWS ПО ТЗ И ДЕЛАЕМ ОКНО СТРОГО СТИЛЬНЫМ И БЕЗОПАСНЫМ
        dialog.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        
        # ТОТАЛЬНЫЙ ОФИЦИАЛЬНЫЙ СБРОС: Наш собственный крестик гарантированно тушит все зажимы мыши
        def force_clean_all_mouse_states():
            import ctypes
            try:
                ctypes.windll.user32.mouse_event(0x0004, 0, 0, 0, 0) # LEFTUP
                ctypes.windll.user32.mouse_event(0x0010, 0, 0, 0, 0) # RIGHTUP
            except Exception:
                pass
            main_win = self.window()
            if main_win and hasattr(main_win, 'mod_keyboard') and main_win.mod_keyboard:
                mod = main_win.mod_keyboard
                if hasattr(mod, 'overlay_manager') and mod.overlay_manager:
                    for btn in mod.overlay_manager.active_buttons:
                        # АППАРАТНЫЙ ПРЕДОХРАНИТЕЛЬ: Проверяем наличие атрибута key_name, чтобы новые полосы фокуса не вызывали вылет!
                        if hasattr(btn, 'key_name'):
                            if btn.key_name in ["lmb", "rmb", "mmb"]:
                                btn.is_physically_pressed = False
                                btn.click_processed_in_this_hover = False
                                btn.set_neon_style(is_active=False)
                                
        dialog.destroyed.connect(force_clean_all_mouse_states)
        
        # СТИЛИЗАЦИЯ С ТОЛСТОЙ НЕОНОВОЙ ФИОЛЕТОВОЙ РАМКОЙ ДЛЯ ВСЕГО ОКНА (ПОЛОСА ПРОКРУТКИ УВЕЛИЧЕНА ДО 24PX)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #04030d;
                border: 2px solid #8a2be2;
                border-radius: 12px;
            }
            QLabel {
                color: #ffffff;
                font-family: 'Segoe UI', sans-serif;
                font-size: 12px;
                font-weight: bold;
                background: transparent;
                border: none;
            }
            QComboBox {
                background-color: #0b0617;
                color: #ffffff;
                border: 1px solid #401970;
                border-radius: 4px;
                padding-left: 5px;
                font-size: 11px;
                font-weight: bold;
                height: 26px;
            }
            QComboBox QAbstractItemView {
                background-color: #0b0617;
                color: #ffffff;
                border: 1px solid #401970;
                selection-background-color: #8a2be2;
                selection-color: #ffffff;
                outline: none;
            }
            /* ФИРМЕННЫЙ ШИРОКИЙ СКРОЛЛБАР ЕVIACAM (УВЕЛИЧЕН ДО 24PX) */
            QComboBox QAbstractItemView QScrollBar:vertical {
                border: 1px solid #1a1038;
                background-color: #04030d;
                width: 24px;
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
            QComboBox QAbstractItemView QScrollBar::add-line:vertical, 
            QComboBox QAbstractItemView QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            QComboBox QAbstractItemView QScrollBar::add-page:vertical, 
            QComboBox QAbstractItemView QScrollBar::sub-page:vertical {
                background-color: #04030d;
                border-radius: 12px;
            }
            QPushButton {
                background-color: #0b0617;
                color: #a347ff;
                border: 1px solid #401970;
                border-radius: 4px;
                font-size: 11px;
                font-weight: bold;
                height: 28px;
            }
            QPushButton:hover {
                background-color: #8a2be2;
                color: white;
                border-color: white;
            }
        """)
        
        dlg_layout = QVBoxLayout(dialog)
        dlg_layout.setContentsMargins(15, 12, 15, 15)
        dlg_layout.setSpacing(10)

# modules/kb_sett2.py - ЧАСТЬ 5 ИЗ 6 (ИСПРАВЛЕННАЯ С ТОЧНОЙ СИНХРОНИЗАЦИЕЙ СТРОКИ RST)
        # НАШ СОБСТВЕННЫЙ КИБЕР-КРЕСТИК В ВЕРХНЕМ LAYOUT РЯДУ ПО ТЗ
        title_hbox = QHBoxLayout()
        lbl_title = QLabel(f"ИИ-Настройка клавиши [{key_name.upper()}]")
        title_hbox.addWidget(lbl_title)
        title_hbox.addStretch()
        
        btn_close_cross = QPushButton("✕")
        btn_close_cross.setFixedSize(22, 22)
        btn_close_cross.setStyleSheet("QPushButton { background-color: #160a0f; color: #ff4757; border: 1px solid #ff4757; border-radius: 5px; font-size: 11px; font-weight: bold; height: 22px; } QPushButton:hover { background-color: #ff4757; color: white; border-color: white; }")
        btn_close_cross.clicked.connect(dialog.reject) # Закрывает диалог нативно внутри PyQt6
        title_hbox.addWidget(btn_close_cross)
        dlg_layout.addLayout(title_hbox)
        
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        bindings = config["profiles"][current_prof]["kb"].get("bindings", {})
        
        current_gesture = "none"
        # СТРОГО ПО ТЗ: Сравниваем через нижний регистр для 100% совместимости с RST
        for g_id, bound_key in bindings.items():
            if str(bound_key).lower() == str(key_name).lower():
                current_gesture = g_id
                break
                
        combo_gestures = QComboBox()
        gesture_items = [
            ("none", "нет жеста"),
            ("brows_up", "Брови (Подняты вверх)"),
            ("brows_down", "Брови (Нахмурены вниз)"),
            ("blink_left", "Моргание (Левый глаз зажмурен)"),
            ("blink_right", "Моргание (Правый глаз зажмурен)"),
            ("mouth_jaw", "Рот (Полное открытие челюсти)"),
            ("smile", "Улыбка (Влево или вправо)"),
            ("pucker", "Губы трубочкой / Поцелуй"),
            ("turn_left", "Голова (Поворот влево)"),
            ("turn_right", "Голова (Поворот вправо)"),
            ("tilt_up", "Голова (Наклон вверх)"),
            ("tilt_down", "Голова (Наклон вниз)"),
            ("zoom_in", "Расстояние (Приближение головы)"),
            ("zoom_out", "Расстояние (Отдаление головы)")
        ]
        
        for internal_id, readable_name in gesture_items:
            if internal_id != "none" and internal_id in bindings and bindings[internal_id] != key_name:
                display_text = f"{readable_name} [Занято клавишей {bindings[internal_id]}]"
            else:
                display_text = readable_name
            combo_gestures.addItem(display_text, internal_id)
            
        for idx in range(combo_gestures.count()):
            if combo_gestures.itemData(idx) == current_gesture:
                combo_gestures.setCurrentIndex(idx)
                break
                
        dlg_layout.addWidget(combo_gestures)
        dlg_layout.addSpacing(2)
        
        btn_save = QPushButton("Сохранить ИИ-привязку")
        
        def save_binding_logic():
            selected_gesture_id = combo_gestures.itemData(combo_gestures.currentIndex())
            cfg = config_manager.load_config()
            prof = cfg.get("current_profile", "Default Profile")
            
            if "bindings" not in cfg["profiles"][prof]["kb"]:
                cfg["profiles"][prof]["kb"]["bindings"] = {}
                
            current_bindings = cfg["profiles"][prof]["kb"]["bindings"]
            
            # Очищаем старые привязки, приводя к единому регистру во избежание дубликатов RST
            for gid, kname in list(current_bindings.items()):
                if str(kname).lower() == str(key_name).lower():
                    del current_bindings[gid]
                    
            if selected_gesture_id != "none":
                current_bindings[selected_gesture_id] = key_name
                
            config_manager.save_config(cfg)
            self.cached_bindings = current_bindings
            self.cached_thresholds = cfg["profiles"][prof]["kb"].get("thresholds", {})
            dialog.accept()
            
        btn_save.clicked.connect(save_binding_logic)
        dlg_layout.addWidget(btn_save)
        dialog.open()




# modules/kb_sett2.py - ЧАСТЬ 6 ИЗ 6 (ИСПРАВЛЕННАЯ С ПОЛНЫМ КЭШЕМ СОСТОЯНИЙ ДЛЯ RST)
    def process_live_gestures(self, gestures):
        """
        ЖИВАЯ ИИ-ПОДСВЕТКА КЛAВИШ С АППАРАТНЫМ КЭШЕМ СОСТОЯНИЙ:
        Считывает актуальные геймерские пороги из block1 в ОЗУ в реальном времени.
        Полностью убирает хардкод 5% для рта, выравнивая отклик с лампами!
        """
        if not self.toggle.isChecked():
            return
            
        if not hasattr(self, '_ui_pressed_states'):
            self._ui_pressed_states = {name: False for name in self.key_buttons}
            
        # Вытаскиваем живые значения порогов из ОЗУ соседнего блока (block1) во избежание рассинхрона
        main_win = self.window()
        active_thresholds = self.cached_thresholds
        if main_win and hasattr(main_win, 'page_keyboard_settings') and main_win.page_keyboard_settings:
            block1 = getattr(main_win.page_keyboard_settings, 'block1', None)
            if block1 and hasattr(block1, 'cached_thresholds'):
                active_thresholds = block1.cached_thresholds
                
        currently_active_keys = set()
        
        # СТРОГО ПО ТЗ: Подсвечиваем клавиши в реальном времени, обеспечивая 100% совместимость с кнопкой RST
        for gesture_id, key_name in self.cached_bindings.items():
            if gesture_id not in gestures or key_name not in self.key_buttons:
                continue
            live_val = float(gestures[gesture_id])
            thresh = float(active_thresholds.get(gesture_id, 35))
            if live_val >= thresh:
                currently_active_keys.add(key_name)
                
        for btn_name, btn_obj in self.key_buttons.items():
            is_now_pressed = (btn_name in currently_active_keys)
            if is_now_pressed != self._ui_pressed_states[btn_name]:
                if is_now_pressed:
                    btn_obj.setStyleSheet("""
                        QPushButton {
                            background-color: #2ed573;
                            color: #ffffff;
                            border: 1px solid #ffffff;
                            border-radius: 4px;
                            font-family: 'Segoe UI', sans-serif;
                            font-size: 10px;
                            font-weight: bold;
                        }
                    """)
                else:
                    btn_obj.setStyleSheet("""
                        QPushButton {
                            background-color: #0b0617;
                            color: #a347ff;
                            border: 1px solid #401970;
                            border-radius: 4px;
                            font-family: 'Segoe UI', sans-serif;
                            font-size: 10px;
                            font-weight: bold;
                        }
                        QPushButton:hover {
                            background-color: #8a2be2;
                            color: #ffffff;
                            border-color: #ffffff;
                        }
                    """)
                self._ui_pressed_states[btn_name] = is_now_pressed
