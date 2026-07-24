# modules/kb_sett1.py - ЧАСТЬ 1 ИЗ 3
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider, QScrollArea, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import styles
import config_manager

class KeyboardSettingBlock1(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingCard")
        
        self.config = config_manager.load_config()
        self.current_prof = self.config.get("current_profile", "Default Profile")
        self.kb_data = self.config["profiles"][self.current_prof]["kb"]
        
        # КЭШ В ОЗУ ДЛЯ СВЕРХБЫСТРОГО ДОСТУПА К ПОРОГАМ БЕЗ ТОРМОЗОВ ДИСКА
        self.cached_thresholds = self.kb_data.get("thresholds", {})
        self.cached_smooth_factor = self.kb_data.get("smooth_factor", 50)
        
        # РОДНАЯ СТИЛИЗАЦИЯ КАРТОЧКИ И НЕОНОВОГО СКРОЛЛБАРА (РАСШИРЕНО В 2 РAЗА ДО 24PX)
        self.setStyleSheet("""
            QFrame#SettingCard { background-color: #04030d; border: 1px solid #1a1038; border-radius: 10px; }
            QLabel { color: #ffffff; font-family: 'Segoe UI', sans-serif; font-size: 11px; background: transparent; border: none; }
            
            /* Фирменная стилизация вертикального бегунка прокрутки списка жестов */
            QScrollBar:vertical {
                border: 1px solid #1a1038; 
                background-color: #0b0617; 
                width: 24px; /* УВЕЛИЧЕНО С 10PX ДО 24PX СТРОГО ПО ТЗ ДЛЯ УДОБСТВА ЕVIACAM! */
                margin: 0px; 
                border-radius: 12px; /* Закругляем под новую ширину */
            }
            QScrollBar::handle:vertical { 
                background-color: #401970; 
                border: 2px solid #8a2be2; 
                min-height: 20px; 
                border-radius: 10px; /* Сделали сам ползунок шире и круглее */
            }
            QScrollBar::handle:vertical:hover { background-color: #8a2be2; border-color: #ffffff; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; height: 0px; }
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical { border: none; background: none; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
            
            /* Стили ползунков калибровки жестов и главного ползунка плавности */
            QSlider::groove:horizontal { border: 1px solid #401970; height: 4px; background: #0b0617; border-radius: 2px; }
            QSlider::sub-page:horizontal { background: #8a2be2; border-radius: 2px; }
            QSlider::handle:horizontal {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0 #ffffff, stop:0.3 #8a2be2, stop:1 rgba(138,43,226,0));
                width: 14px; height: 14px; margin: -5px 0; border-radius: 7px;
            }
            QLabel#StatusDot { border-radius: 6px; border: none; }
        """)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(12, 10, 12, 12)
        self.main_layout.setSpacing(8)
        
        top_layout = QHBoxLayout(); top_layout.setSpacing(10)
        ico = QLabel()
        ico.setStyleSheet("background: transparent; border: none;")
        pix = QPixmap(styles.get_image("kb1.png"))
        if not pix.isNull():
            ico.setPixmap(pix.scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        top_layout.addWidget(ico)
        
        title = QLabel("ИИ-Калибровка и Мониторинг Мимики")
        title.setStyleSheet("color: #ffffff; font-size: 13px; font-weight: bold;")
        top_layout.addWidget(title)
        top_layout.addStretch()
        
        # ВОЗВРАЩАЕМ ВАШ КРАСИВЫЙ РОДНОЙ СВИТЧ ДЛЯ СВОРАЧИВАНИЯ ОКНА
        self.toggle = QPushButton("●")
        self.toggle.setCheckable(True)
        saved_open_state = self.kb_data.get("setting_1", True)
        self.toggle.setChecked(saved_open_state)
        self.toggle.setFixedSize(44, 20)
        self.toggle.clicked.connect(self.on_setting_toggle_clicked)
        top_layout.addWidget(self.toggle)
        self.main_layout.addLayout(top_layout)
        
        self.line = QFrame(); self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setStyleSheet("background-color: #1a1038; min-height: 1px; max-height: 1px; border: none;")
        self.main_layout.addWidget(self.line)

# modules/kb_sett1.py - ЧАСТЬ 2 ИЗ 3
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; } QWidget { background: transparent; }")
        
        scroll_content = QWidget()
        self.list_layout = QVBoxLayout(scroll_content)
        self.list_layout.setContentsMargins(0, 0, 5, 0)
        self.list_layout.setSpacing(6)
        
        self.gesture_list = [
            ("brows_up", "Брови (Подняты вверх)"),
            ("brows_down", "Брови (Нахмурены вниз)"),
            ("blink_left", "Моргание (Левый глаз зажмурен)"),
            ("blink_right", "Моргание (Правый глаз зажмурен)"),
            ("mouth_jaw", "Рот (Закрыт / Половина / Открыт)"),
            ("smile", "Улыбка (Влево или вправо)"),
            ("pucker", "Губы трубочкой / Поцелуй"),
            ("turn_left", "Голова (Поворот влево)"),
            ("turn_right", "Голова (Поворот вправо)"),
            ("tilt_up", "Голова (Наклон вверх)"),
            ("tilt_down", "Голова (Наклон вниз)"),
            ("zoom_in", "Расстояние (Приближение головы)"),
            ("zoom_out", "Расстояние (Отдаление головы)")
        ]
        
        self.ui_live_labels = {}
        self.ui_sliders = {}
        self.ui_dots = {}
        self.ui_thresh_labels = {}
        
        for internal_id, readable_name in self.gesture_list:
            row_frame = QFrame()
            row_frame.setStyleSheet("QFrame { background-color: #0b0617; border: 1px solid #1a1038; border-radius: 6px; }")
            row_layout = QVBoxLayout(row_frame)
            row_layout.setContentsMargins(10, 6, 10, 6)
            row_layout.setSpacing(4)
            
            info_hbox = QHBoxLayout()
            lbl_name = QLabel(readable_name)
            lbl_name.setStyleSheet("font-weight: bold; color: #ffffff;")
            
            lbl_live = QLabel("ИИ: 0%")
            lbl_live.setFixedWidth(65)
            lbl_live.setStyleSheet("color: #a347ff; font-weight: bold;")
            self.ui_live_labels[internal_id] = lbl_live
            
            saved_thresh = self.cached_thresholds.get(internal_id, 35)
            lbl_thresh = QLabel(f"Порог: {saved_thresh}%")
            lbl_thresh.setFixedWidth(65)
            lbl_thresh.setStyleSheet("color: #8a2be2;")
            self.ui_thresh_labels[internal_id] = lbl_thresh
            
            dot = QLabel()
            dot.setObjectName("StatusDot")
            dot.setFixedSize(12, 12)
            dot.setStyleSheet("background-color: #ffcc00; border-radius: 6px;")
            self.ui_dots[internal_id] = dot
            
            info_hbox.addWidget(lbl_name)
            info_hbox.addStretch()
            info_hbox.addWidget(lbl_live)
            info_hbox.addWidget(lbl_thresh)
            info_hbox.addWidget(dot)
            row_layout.addLayout(info_hbox)
            
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(5, 95)
            slider.setValue(saved_thresh)
            slider.valueChanged.connect(lambda v, iid=internal_id: self.on_gesture_slider_changed(iid, v))
            self.ui_sliders[internal_id] = slider
            row_layout.addWidget(slider)
            
            self.list_layout.addWidget(row_frame)
            
        self.scroll_area.setWidget(scroll_content)
        self.main_layout.addWidget(self.scroll_area)
        
        # --- ФРЕЙМ ПОЛЗУНКА ПЛАВНОСТИ ---
        self.smooth_row_frame = QFrame()
        self.smooth_row_frame.setStyleSheet("QFrame { background-color: #080410; border: 1px solid #1a1038; border-radius: 8px; }")
        smooth_vbox = QVBoxLayout(self.smooth_row_frame)
        smooth_vbox.setContentsMargins(10, 8, 10, 8)
        smooth_vbox.setSpacing(4)
        
        smooth_hbox = QHBoxLayout()
        lbl_smooth_title = QLabel("Сглаживание и плавность мимики:")
        lbl_smooth_title.setStyleSheet("font-weight: bold; color: #00f0ff; background: transparent;")
        
        self.lbl_smooth_val = QLabel(f"{self.cached_smooth_factor}%")
        self.lbl_smooth_val.setStyleSheet("color: #00f0ff; font-weight: bold; background: transparent;")
        
        smooth_hbox.addWidget(lbl_smooth_title)
        smooth_hbox.addStretch()
        smooth_hbox.addWidget(self.lbl_smooth_val)
        smooth_vbox.addLayout(smooth_hbox)
        
        self.slider_smooth = QSlider(Qt.Orientation.Horizontal)
        self.slider_smooth.setRange(0, 95) 
        self.slider_smooth.setValue(self.cached_smooth_factor)
        self.slider_smooth.valueChanged.connect(self.on_smooth_factor_changed)
        
        self.slider_smooth.setStyleSheet("""
            QSlider::groove:horizontal { border: 1px solid #401970; height: 4px; background: #0b0617; border-radius: 2px; }
            QSlider::sub-page:horizontal { background: #8a2be2; border-radius: 2px; }
            QSlider::handle:horizontal {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0 #ffffff, stop:0.3 #8a2be2, stop:1 rgba(138,43,226,0));
                width: 14px; height: 14px; margin: -5px 0; border-radius: 7px;
            }
        """)
        smooth_vbox.addWidget(self.slider_smooth)
        self.main_layout.addWidget(self.smooth_row_frame)

        # ЖЕСТКАЯ ДИРЕКТИВА: Инициализируем геометрию и стили свитча ДО отрисовки окна на экране
        self.apply_visibility_layout_state(saved_open_state)
        
        # Даем принудительный пинок рендерингу кнопки, чтобы вернуть белый кругляшок на фиолетовом фоне
        self.toggle.update()
        self.toggle.repaint()

# modules/kb_sett1.py - ЧАСТЬ 3 ИЗ 3
    def on_setting_toggle_clicked(self, checked):
        self.apply_visibility_layout_state(checked)
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        config["profiles"][current_prof]["kb"]["setting_1"] = checked
        config_manager.save_config(config)

    def on_gesture_slider_changed(self, gesture_id, value):
        """Обновление значения слайдера: пишем в UI и моментально кэшируем в ОЗУ"""
        self.ui_thresh_labels[gesture_id].setText(f"Порог: {value}%")
        self.cached_thresholds[gesture_id] = int(value) 
        
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        if "thresholds" not in config["profiles"][current_prof]["kb"]:
            config["profiles"][current_prof]["kb"]["thresholds"] = {}
        config["profiles"][current_prof]["kb"]["thresholds"][gesture_id] = int(value)
        config_manager.save_config(config)

    def on_smooth_factor_changed(self, value):
        """Слот изменения ползунка плавности: кэширует в ОЗУ и пишет в JSON"""
        self.lbl_smooth_val.setText(f"{value}%")
        self.cached_smooth_factor = int(value)
        
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        config["profiles"][current_prof]["kb"]["smooth_factor"] = int(value)
        config_manager.save_config(config)

    def apply_visibility_layout_state(self, is_open):
        """
        Вспомогательный метод: мгновенно сворачивает или распахивает сетку ползунков.
        СТРОГО ПО ТЗ: Меняет графику родного свитча (прямоугольник + белый кругляшок)!
        """
        has_smooth_block = hasattr(self, 'smooth_row_frame') and self.smooth_row_frame is not None

        if is_open:
            self.scroll_area.show()
            if has_smooth_block: self.smooth_row_frame.show()
            self.line.show()
            
            # РОДНОЙ ИГРОВОЙ ДИЗАЙН: Белый кругляшок сдвинут ВПРАВО (Фиолетовый фон)
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
            self.scroll_area.hide()
            if has_smooth_block: self.smooth_row_frame.hide()
            self.line.hide()
            
            # РОДНОЙ ИГРОВОЙ ДИЗАЙН: Белый кругляшок сдвинут ВЛЕВО (Тёмно-фиолетовый фон)
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

        self.toggle.update()
        self.toggle.repaint()

    def process_live_gestures(self, gestures):
        """ЖИВОЙ ИИ-ДИСПЕТЧЕР КАЛИБРОВКИ С ОПТИМИЗИРОВАННЫМИ ФАЗАМИ И СКОРОСТЬЮ РАБОТЫ ИЗ ОЗУ"""
        if not self.toggle.isChecked():
            return

        for gesture_id, _ in self.gesture_list:
            if gesture_id not in gestures:
                continue

            live_val = float(gestures[gesture_id])
            
            if gesture_id in self.ui_live_labels:
                self.ui_live_labels[gesture_id].setText(f"ИИ: {int(live_val)}%")

            thresh = self.cached_thresholds.get(gesture_id, 35)
            
            if gesture_id in self.ui_dots:
                dot = self.ui_dots[gesture_id]
                
                if gesture_id == "mouth_jaw":
                    if live_val >= thresh:
                        dot.setStyleSheet("background-color: #8a2be2; border-radius: 6px;") 
                    elif live_val >= 5.0:
                        dot.setStyleSheet("background-color: #2ed573; border-radius: 6px;") 
                    else:
                        dot.setStyleSheet("background-color: #ffcc00; border-radius: 6px;") 
                
                elif gesture_id == "zoom_out":
                    if live_val >= thresh:
                        dot.setStyleSheet("background-color: #8a2be2; border-radius: 6px;") 
                    else:
                        dot.setStyleSheet("background-color: #ffcc00; border-radius: 6px;") 
                        
                else:
                    if live_val >= thresh:
                        dot.setStyleSheet("background-color: #2ed573; border-radius: 6px;") 
                    else:
                        dot.setStyleSheet("background-color: #ffcc00; border-radius: 6px;")
