# title_bar.py ( 1 Часть из 3 ) (ФИКС ЗAГРУЗКИ ПОЗИЦИИ БЕГУНКА ИЗ ПРОФИЛЯ)
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QSlider
from PyQt6.QtCore import Qt, QSize, QPointF
from PyQt6.QtGui import QPixmap, QPainter, QLinearGradient, QFont, QPen, QColor
import styles
import config_manager  

class ChromedLabel(QLabel):
    """Кастомный класс для принудительного рисования букв в хромированно-зеленом градиенте"""
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.setText(text)
        self.setFixedHeight(18) 
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        font = QFont('Segoe UI', 14, QFont.Weight.Medium)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 0.5)
        painter.setFont(font)
        
        gradient = QLinearGradient(QPointF(0, 0), QPointF(0, self.height()))
        gradient.setColorAt(0.0, QColor("#ffffff")) 
        gradient.setColorAt(0.3, QColor("#d6dadf")) 
        gradient.setColorAt(0.58, QColor("#6fb8f7")) 
        gradient.setColorAt(0.75, QColor("#1a1c1e")) 
        gradient.setColorAt(0.75, QColor("#b1b7be")) 
        gradient.setColorAt(1.0, QColor("#ffffff")) 

        painter.setPen(QPen(gradient, 0))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self.text())
        painter.end()

class CustomTitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(50)  
        
        # ИСПРАВЛЕНО: Намертво привязали чтение позиции бегунка к активному профилю клавиатуры!
        self.config = config_manager.load_config()
        current_prof = self.config.get("current_profile", "Default Profile")
        kb_conf = self.config.get("profiles", {}).get(current_prof, {}).get("kb", {})
        
        # Читаем честную сохраненную прозрачность оверлеев Set 3 (по умолчанию 100%)
        self.saved_opacity = kb_conf.get("overlay_opacity", 100)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 0)
        layout.setSpacing(12)
        
        self.logo_img = QLabel()
        self.logo_img.setStyleSheet("background: transparent; border: none;")
        logo_pixmap = QPixmap(styles.get_image("logo.png"))
        if not logo_pixmap.isNull():
            self.logo_img.setPixmap(logo_pixmap.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        layout.addWidget(self.logo_img)
        
        text_container = QVBoxLayout()
        text_container.setSpacing(2)
        text_container.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        self.main_title = ChromedLabel("CONTROL CENTER")
        self.main_title.setStyleSheet("background: transparent; border: none;")
        
        self.sub_title = QLabel("Управляй. Настраивай. Контролируй.")
        self.sub_title.setStyleSheet("color: #a1a3b5; font-family: 'Segoe UI', sans-serif; font-size: 10px; background: transparent; border: none; padding-top: 1px;")
        
        text_container.addWidget(self.main_title)
        text_container.addWidget(self.sub_title)
        layout.addLayout(text_container)
        
        layout.addStretch()
        
        GREEN_BTN_STYLE = """
            QPushButton {
                background-color: #030f08;
                color: #2ed573;
                border: 1px solid qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2ed573, stop:0.5 #10381f, stop:1 #2ed573);
                border-radius: 5px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #2ed573;
                color: #000000;
                border-color: #ffffff;
            }
        """

        
# title_bar.py ( 2 Часть из 3 ) (СОХРАНЕНИЕ 16 КВАДРАТИКОВ ПАЛИТРЫ ПОЛЬЗОВАТЕЛЯ)
        # 3. Переименовали Кнопку 4 в "Цвет кнопок" и привязали к диалогу палитры
        self.btn_extra = QPushButton("Цвет кнопок")
        self.btn_extra.setFixedSize(90, 26)
        self.btn_extra.setStyleSheet(GREEN_BTN_STYLE)
        self.btn_extra.clicked.connect(self.open_color_picker_dialog)
        layout.addWidget(self.btn_extra)
        
        # 4. КНОПКА «Прозрачность»
        self.btn_opacity = QPushButton("Прозрачность")
        self.btn_opacity.setFixedSize(100, 26)
        self.btn_opacity.setStyleSheet(GREEN_BTN_STYLE)
        self.btn_opacity.clicked.connect(self.toggle_slider_visibility)
        layout.addWidget(self.btn_opacity)

        # 5. ПОЛЗУНОК ПРОЗРАЧНОСТИ 
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setFixedSize(240, 24) 
        self.opacity_slider.setRange(30, 100)
        self.opacity_slider.setValue(self.saved_opacity)
        self.opacity_slider.valueChanged.connect(self.on_slider_value_changed) 
        
        self.opacity_slider.setStyleSheet("""
            QSlider::groove:horizontal { border: 1px solid #10381f; height: 4px; background: #030f08; border-radius: 2px; }
            QSlider::sub-page:horizontal { background: #2ed573; border-radius: 2px; }
            QSlider::handle:horizontal {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0 #ffffff, stop:0.25 #00ff66, stop:0.6 rgba(46, 213, 115, 0.4), stop:1 rgba(46, 213, 115, 0));
                border: none; width: 24px; height: 24px; margin: -10px 0; border-radius: 12px;
            }
        """)
        self.opacity_slider.hide()
        layout.addWidget(self.opacity_slider)
        
        layout.addSpacing(100) 

        # 6. Кнопка "Свернуть"
        self.btn_minimize = QPushButton("—")
        self.btn_minimize.setFixedSize(28, 24)
        self.btn_minimize.setStyleSheet("""
            QPushButton { background-color: transparent; border: none; color: #ffffff; font-size: 14px; font-weight: bold; }
            QPushButton:hover { background-color: #1a153a; border-radius: 4px; color: #8a2be2; }
        """)
        self.btn_minimize.clicked.connect(self.minimize_window)
        layout.addWidget(self.btn_minimize)
        
        # 7. Кнопка "Закрыть" (Крестик)
        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(28, 24)
        self.btn_close.setStyleSheet(f"""
            QPushButton {{ background-color: transparent; border: none; color: #ffffff; font-size: 12px; font-weight: bold; }}
            QPushButton:hover {{ background-color: {styles.COLOR_RED}; border-radius: 4px; color: white; }}
        """)
        self.btn_close.clicked.connect(self.close_window)
        layout.addWidget(self.btn_close)
        
        self.drag_position = None

    def toggle_slider_visibility(self):
        """Метод интерактивного включения/выключения бегунка прозрачности при клике на кнопку"""
        if self.opacity_slider.isHidden():
            self.opacity_slider.show()
            self.btn_opacity.setStyleSheet("QPushButton { background-color: #2ed573; color: #000000; border: 1px solid #ffffff; border-radius: 5px; font-weight: bold; }")
        else:
            self.opacity_slider.hide()
            self.btn_opacity.setStyleSheet("QPushButton { background-color: #030f08; color: #2ed573; border: 1px solid qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2ed573, stop:0.5 #10381f, stop:1 #2ed573); border-radius: 5px; } QPushButton:hover { background-color: #2ed573; color: #000000; border-color: #ffffff; }")

    # Открывает кастомное безрамочное окно выбора 4-х параметров цвета кнопок
    def open_color_picker_dialog(self):
        from PyQt6.QtWidgets import QDialog, QColorDialog
        dialog = QDialog(self)
        dialog.setFixedSize(380, 210)
        dialog.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        
        dialog.setStyleSheet("""
            QDialog { background-color: #04030d; border: 2px solid #8a2be2; border-radius: 12px; }
            QLabel { color: #ffffff; font-family: 'Segoe UI', sans-serif; font-size: 12px; font-weight: bold; }
            QPushButton { background-color: #0b0617; color: #a347ff; border: 1px solid #401970; border-radius: 4px; font-size: 11px; font-weight: bold; height: 26px; }
            QPushButton:hover { background-color: #8a2be2; color: white; border-color: white; }
        """)
        
        dlg_layout = QVBoxLayout(dialog)
        dlg_layout.setContentsMargins(15, 12, 15, 15)
        dlg_layout.setSpacing(8)
        
        title_hbox = QHBoxLayout()
        lbl_title = QLabel("Управление цветом наэкранных клавиш")
        title_hbox.addWidget(lbl_title); title_hbox.addStretch()
        
        btn_close = QPushButton("✕")
        btn_close.setFixedSize(22, 22)
        btn_close.setStyleSheet("QPushButton { background-color: #160a0f; color: #ff4757; border: 1px solid #ff4757; border-radius: 5px; font-size: 11px; font-weight: bold; height: 22px; } QPushButton:hover { background-color: #ff4757; color: white; border-color: white; }")
        btn_close.clicked.connect(dialog.reject)
        title_hbox.addWidget(btn_close)
        dlg_layout.addLayout(title_hbox)
        
        config = config_manager.load_config()
        prof = config.get("current_profile", "Default Profile")
        kb_conf = config["profiles"][prof].get("kb", {})
        
        c_border = kb_conf.get("clr_border", "#401970")
        c_bg = kb_conf.get("clr_bg", "#0b0617")
        c_border_act = kb_conf.get("clr_border_active", "#ffffff")
        c_bg_act = kb_conf.get("clr_bg_active", "#2ed573")
        
        color_items = [
            ("clr_border", "Ободок и буквы по умолчанию:", c_border),
            ("clr_bg", "Внутренний фон по умолчанию:", c_bg),
            ("clr_border_active", "Ободок и буквы при нажатии:", c_border_act),
            ("clr_bg_active", "Внутренний фон при нажатии:", c_bg_act)
        ]
        
        def pick_color_logic(key_id, current_hex, button_indicator):
            color_dialog = QColorDialog(QColor(current_hex), dialog)
            color_dialog.setWindowTitle("Выберите цвет элемента")
            color_dialog.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
            
            # ШAГ 1 (ЗАГРУЗКА ИЗ ФAЙЛA): Перед открытием окна палитры считываем сохраненные кастомные квадратики пользователя
            cfg_init = config_manager.load_config()
            saved_palette = cfg_init.get("custom_palette_colors", ["#ffffff"] * 16)
            for i in range(min(16, len(saved_palette))):
                QColorDialog.setCustomColor(i, QColor(saved_palette[i]))
            
            color_dialog.setStyleSheet("""
                QColorDialog { background-color: #04030d; border: 2px solid #8a2be2; border-radius: 12px; }
                QPushButton { min-width: 90px; min-height: 30px; background-color: #0b0617; color: #a347ff; border: 1px solid #401970; border-radius: 4px; font-weight: bold; }
                QPushButton:hover { background-color: #8a2be2; color: white; border-color: white; }
            """)
            
            if color_dialog.exec() == QColorDialog.DialogCode.Accepted:
                color = color_dialog.selectedColor()
                new_hex = color.name()
                button_indicator.setStyleSheet(f"QPushButton {{ background-color: {new_hex}; border: 1px solid #ffffff; border-radius: 4px; }}")
                
                cfg = config_manager.load_config()
                p = cfg.get("current_profile", "Default Profile")
                cfg["profiles"][p]["kb"][key_id] = new_hex
                
                # ШAГ 2 (СОХРАНЕНИЕ КВАДРАТИКОВ): Вытаскиваем все 16 квадратиков из окна Windows, которые заполнил пользователь
                current_palette_list = []
                for i in range(16):
                    hex_color_from_grid = QColorDialog.customColor(i).name()
                    current_palette_list.append(hex_color_from_grid)
                
                # Записываем весь этот набор в корень конфигурационного JSON
                cfg["custom_palette_colors"] = current_palette_list
                
                if hasattr(config_manager, '_CONFIG_RAM_CACHE'):
                    config_manager._CONFIG_RAM_CACHE = cfg
                config_manager.save_config(cfg)
                
                if self.parent and hasattr(self.parent, 'mod_keyboard') and self.parent.mod_keyboard:
                    mod = self.parent.mod_keyboard
                    if hasattr(mod, 'overlay_manager') and mod.overlay_manager and mod.btn_2.isChecked():
                        selected_keys = cfg["profiles"][p]["kb"].get("overlay_selected_keys", [])
                        mod.overlay_manager.spawn_overlay_buttons(selected_keys)
        
        for k_id, label_text, hex_val in color_items:
            row = QHBoxLayout()
            lbl = QLabel(label_text)
            row.addWidget(lbl); row.addStretch()
            
            btn_color = QPushButton()
            btn_color.setFixedSize(50, 24)
            btn_color.setStyleSheet(f"QPushButton {{ background-color: {hex_val}; border: 1px solid #401970; border-radius: 4px; }}")
            btn_color.clicked.connect(lambda checked, kid=k_id, h=hex_val, b=btn_color: pick_color_logic(kid, h, b))
            
            row.addWidget(btn_color)
            dlg_layout.addLayout(row)
            
        dialog.open()



# title_bar.py ( ЧАСТЬ 3 ИЗ 3 ) (ОЧИЩЕННОЕ ЧИСТОЕ СОХРАНЕНИЕ ПРОЗРАЧНОСТИ SET 3)
    def on_slider_value_changed(self, value):
        """Обработчик изменения ползунка: МГНОВЕННО сохраняет её значение в JSON-файл без влияния на главное окно"""
        config = config_manager.load_config()
        if "profiles" in config:
            current_prof = config.get("current_profile", "Default Profile")
            if current_prof in config["profiles"]:
                # ИСПРАВЛЕНО: Записываем строго и только в overlay_opacity, разгружая ОЗУ от мусора!
                config["profiles"][current_prof]["kb"]["overlay_opacity"] = int(value)
                config_manager.save_config(config)
        
        # ЖИВОЙ ИИ-МОСТ: Находим менеджер оверлеев и приказываем кнопкам Set 3 мгновенно обновить яркость в ОС!
        if self.parent:
            if hasattr(self.parent, 'mod_keyboard') and self.parent.mod_keyboard:
                mod = self.parent.mod_keyboard
                if hasattr(mod, 'overlay_manager') and mod.overlay_manager and mod.btn_2.isChecked():
                    config = config_manager.load_config()
                    current_prof = config.get("current_profile", "Default Profile")
                    selected_keys = config["profiles"][current_prof]["kb"].get("overlay_selected_keys", [])
                    mod.overlay_manager.spawn_overlay_buttons(selected_keys)

    def minimize_window(self):
        if self.parent:
            self.parent.showMinimized()

    def close_window(self):
        """Логика крестика '✕' с безопасным перенаправлением закрытия в главное окно"""
        if self.parent:
            from PyQt6.QtWidgets import QMessageBox
            
            msg = QMessageBox(self)
            msg.setWindowTitle("Предупреждение")
            msg.setText("ВНИМАНИЕ!\n\nВы ЗАКРЫВАЕТЕ программу ИИ-управления.\nЭто приведет к ПОЛНОЙ ПОТЕРЕ КОНТРОЛЯ над компьютером через голову.\n\nВы уверены, что хотите завершить работу приложения?")
            msg.setIcon(QMessageBox.Icon.Warning)
            
            yes_btn = msg.addButton("Да, закрыть", QMessageBox.ButtonRole.YesRole)
            no_btn = msg.addButton("Отмена", QMessageBox.ButtonRole.NoRole)
            msg.setDefaultButton(no_btn)
            
            msg.setStyleSheet("""
                QMessageBox { background-color: #0c0f12; border: 2px solid #b1b7be; border-radius: 10px; }
                QLabel { color: #ffffff; font-family: 'Segoe UI', sans-serif; font-size: 12px; font-weight: bold; }
                QPushButton { background-color: #030f08; color: #2ed573; border: 1px solid #10381f; border-radius: 4px; padding: 6px 14px; font-weight: bold; min-width: 80px; }
                QPushButton:hover { background-color: #2ed573; color: black; border-color: white; }
            """)
            
            msg.exec()
            
            if msg.clickedButton() == yes_btn:
                self.parent.close()
            else:
                pass

    # Логика перетаскивания окна мышкой за верхнюю панель
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.parent:
                self.drag_position = event.globalPosition().toPoint() - self.parent.frameGeometry().topLeft()
                event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position:
            if self.parent:
                self.parent.move(event.globalPosition().toPoint() - self.drag_position)
                event.accept()
