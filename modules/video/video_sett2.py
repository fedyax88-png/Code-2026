# modules/video/video_sett2.py - ЧАСТЬ 1 ИЗ 2
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCheckBox, QSlider
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import styles
import config_manager

class VideoSettingBlock2(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingCard")
        
        self.config = config_manager.load_config()
        self.current_prof = self.config.get("current_profile", "Default Profile")
        self.video_data = self.config["profiles"][self.current_prof]["video"]
        
        # Переводим сохраненный float (например, 0.15) в целое число для слайдера (15)
        saved_alpha = int(self.video_data.get("tracking_alpha", 0.15) * 100)
        # Ограничиваем рамками нового диапазона (от 1 до 20)
        saved_alpha = max(1, min(20, saved_alpha))
        
        self.setStyleSheet("""
            QFrame#SettingCard { background-color: #03060f; border: 1px solid #101f38; border-radius: 10px; }
            QLabel { color: #ffffff; font-family: 'Segoe UI', sans-serif; font-size: 12px; background: transparent; border: none; }
            QCheckBox { color: #ffffff; font-size: 12px; spacing: 8px; background: transparent; border: none; }
            QCheckBox::indicator { width: 14px; height: 14px; border: 1px solid #162e54; border-radius: 3px; background-color: #071224; }
            QCheckBox::indicator:checked { background-color: #00d2ff; border-color: #ffffff; }
            QCheckBox::indicator:hover { border-color: #00d2ff; }
            
            /* Стилизация фирменного голубого неонового ползунка плавности видео */
            QSlider::groove:horizontal { border: 1px solid #162e54; height: 4px; background: #071224; border-radius: 2px; }
            QSlider::sub-page:horizontal { background: #00d2ff; border-radius: 2px; }
            QSlider::handle:horizontal {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0 #ffffff, stop:0.3 #00d2ff, stop:1 rgba(0,210,255,0));
                width: 14px; height: 14px; margin: -5px 0; border-radius: 7px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(12)
        
        top_layout = QHBoxLayout(); top_layout.setSpacing(10)
        ico = QLabel()
        pix = QPixmap(styles.get_image("video1.png"))
        if not pix.isNull():
            ico.setPixmap(pix.scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        top_layout.addWidget(ico)
        
        title = QLabel("Настройки ИИ-Трекинга")
        title.setStyleSheet("font-size: 13px; font-weight: bold; color: #ffffff;")
        top_layout.addWidget(title)
        top_layout.addStretch()
        
        self.toggle = QPushButton("●")
        self.toggle.setCheckable(True)
        self.toggle.setChecked(self.video_data.get("setting_2", True))
        self.toggle.setFixedSize(44, 20)
        self.toggle.setStyleSheet("background-color: #00d2ff; border: none; border-radius: 10px; text-align: right; color: white; font-size: 34px; font-weight: bold; padding-top: -10px;")
        top_layout.addWidget(self.toggle)
        layout.addLayout(top_layout)
        
        line = QFrame(); line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #162e54; min-height: 1px; max-height: 1px; border: none;")
        layout.addWidget(line)
        
        # 1. Флажок точки на носу
        saved_show_dot = self.video_data.get("tracking_show_dot", True)
        self.chk_show_dot = QCheckBox("Отображать зелёную точку на носу")
        self.chk_show_dot.setChecked(saved_show_dot)
        self.chk_show_dot.stateChanged.connect(self.on_show_dot_changed)
        layout.addWidget(self.chk_show_dot)
        
        # 2. Флажок авторамки головы
        saved_show_box = self.video_data.get("tracking_show_box", True)
        self.chk_show_box = QCheckBox("Отображать рамку вокруг головы")
        self.chk_show_box.setChecked(saved_show_box)
        self.chk_show_box.stateChanged.connect(self.on_show_box_changed)
        layout.addWidget(self.chk_show_box)
        
        # 3. НОВЫЙ ФЛАЖОК ДЛЯ КЛАВИАТУРНЫХ ЖЕСТОВ МИМИКИ (ПО НАШЕМУ ПЛАНУ)
        saved_blendshapes = self.video_data.get("tracking_blendshapes", True)
        self.chk_blendshapes = QCheckBox("Включить ИИ-анализ жестов лица (Blendshapes)")
        self.chk_blendshapes.setChecked(saved_blendshapes)
        self.chk_blendshapes.stateChanged.connect(self.on_blendshapes_changed)
        layout.addWidget(self.chk_blendshapes)
        
        # --- БЛОК ПОЛЗУНКА ПЛАВНОСТИ ТОЧКИ НА НОСУ ---
        smooth_hbox = QHBoxLayout()
        lbl_smooth_title = QLabel("Плавность слежения (Альфа-фильтр):")
        lbl_smooth_title.setStyleSheet("font-weight: bold; color: #a1a3b5; background: transparent;")
        
        float_val = float(saved_alpha / 100.0)
        self.lbl_alpha_val = QLabel(f"{float_val}")
        if saved_alpha == 15: self.lbl_alpha_val.setText("0.15 (Эталон)")
        elif saved_alpha == 20: self.lbl_alpha_val.setText("0.20 (Быстро)")
        elif saved_alpha == 1: self.lbl_alpha_val.setText("0.01 (Макс. плавно)")
        self.lbl_alpha_val.setStyleSheet("color: #00d2ff; font-weight: bold; background: transparent;")
        
        smooth_hbox.addWidget(lbl_smooth_title)
        smooth_hbox.addStretch()
        smooth_hbox.addWidget(self.lbl_alpha_val)
        layout.addLayout(smooth_hbox)
        
        self.slider_alpha = QSlider(Qt.Orientation.Horizontal)
        self.slider_alpha.setRange(1, 20) # НАШ НОВЫЙ ДИАПАЗОН ОТ 0.01 ДО 0.20
        self.slider_alpha.setValue(saved_alpha)
        self.slider_alpha.valueChanged.connect(self.on_alpha_slider_changed)
        layout.addWidget(self.slider_alpha)
        
        layout.addStretch()


# modules/video/video_sett2.py - ЧАСТЬ 2 ИЗ 2
    def on_show_dot_changed(self, state):
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        config["profiles"][current_prof]["video"]["tracking_show_dot"] = (state == 2)
        config_manager.save_config(config)

    def on_show_box_changed(self, state):
        """Сохранение состояния видимости рамки вокруг головы в JSON"""
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        config["profiles"][current_prof]["video"]["tracking_show_box"] = (state == 2)
        config_manager.save_config(config)

    def on_blendshapes_changed(self, state):
        """Сохранение главного рубильника ИИ-анализа мимики (Blendshapes) в JSON"""
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        config["profiles"][current_prof]["video"]["tracking_blendshapes"] = (state == 2)
        config_manager.save_config(config)

    def on_alpha_slider_changed(self, value):
        """Слот изменения ползунка сглаживания видео: переводит шкалу в float и сохраняет"""
        float_alpha = float(value / 100.0)
        
        if value == 7: alpha_text = "0.07 (Эталон)"
        elif value == 2: alpha_text = "0.02 (Макс. плавно)"
        elif value == 15: alpha_text = "0.15 (Быстро)"
        else: alpha_text = f"{float_alpha}"
        
        self.lbl_alpha_val.setText(alpha_text)
        
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        config["profiles"][current_prof]["video"]["tracking_alpha"] = float_alpha
        config_manager.save_config(config)
