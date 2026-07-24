# modules/mouse/mouse_sett1.py
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import styles
import config_manager

class MouseSettingBlock1(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingCard")
        
        self.config = config_manager.load_config()
        self.current_prof = self.config.get("current_profile", "Default Profile")
        self.mouse_data = self.config["profiles"][self.current_prof]["mouse"]
        
        # Загружаем значение альфы напрямую из блока видео, где живет ИИ-трекер
        self.video_data = self.config["profiles"][self.current_prof]["video"]
        
        self.setStyleSheet("""
            QFrame#SettingCard { background-color: #030a06; border: 1px solid #10381f; border-radius: 10px; }
            QLabel { color: #ffffff; font-family: 'Segoe UI', sans-serif; font-size: 12px; background: transparent; border: none; }
            QSlider::groove:horizontal { border: 1px solid #123d22; height: 4px; background: #05140b; border-radius: 2px; }
            QSlider::sub-page:horizontal { background: #2ed573; border-radius: 2px; }
            QSlider::handle:horizontal {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0 #ffffff, stop:0.3 #2ed573, stop:1 rgba(46,213,115,0));
                width: 16px; height: 16px; margin: -6px 0; border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(10)
        
        top_layout = QHBoxLayout(); top_layout.setSpacing(10)
        ico = QLabel()
        pix = QPixmap(styles.get_image("mouse1.png"))
        if not pix.isNull():
            ico.setPixmap(pix.scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        top_layout.addWidget(ico)
        
        title = QLabel("Настройка Движения")
        title.setStyleSheet("color: #ffffff; font-size: 13px; font-weight: bold; background: transparent; border: none;")
        top_layout.addWidget(title)
        top_layout.addStretch()
        
        self.toggle = QPushButton("●")
        self.toggle.setCheckable(True)
        self.toggle.setChecked(self.mouse_data.get("setting_1", True))
        self.toggle.setFixedSize(44, 20)
        self.toggle.setStyleSheet("background-color: #2ed573; border: none; border-radius: 10px; text-align: right; color: white; font-size: 34px; font-weight: bold; padding-top: -10px;")
        top_layout.addWidget(self.toggle)
        layout.addLayout(top_layout)
        
        line = QFrame(); line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #123d22; min-height: 1px; max-height: 1px; border: none;")
        layout.addWidget(line)
        
        # 1. Ползунок Скорости (ПО ВАШЕМУ ТЗ: УВЕЛИЧЕН ДО 200 МАКСИМУМ)
        saved_speed = float(self.mouse_data.get("speed", 25.0))
        if saved_speed > 200.0: saved_speed = 200.0
        
        speed_txt_layout = QHBoxLayout()
        speed_lbl = QLabel("Скорость перемещения курсора:")
        self.lbl_speed_val = QLabel(f"{round(saved_speed, 1)}")
        self.lbl_speed_val.setStyleSheet("color: #2ed573; font-weight: bold;")
        speed_txt_layout.addWidget(speed_lbl)
        speed_txt_layout.addStretch()
        speed_txt_layout.addWidget(self.lbl_speed_val)
        layout.addLayout(speed_txt_layout)
        
        self.slider_speed = QSlider(Qt.Orientation.Horizontal)
        self.slider_speed.setRange(1, 200)  # Меняем верхнюю планку диапазона на 200
        self.slider_speed.setValue(int(saved_speed))
        self.slider_speed.valueChanged.connect(self.on_speed_changed)
        layout.addWidget(self.slider_speed)
        
        layout.addSpacing(5)
        
        # 2. Ползунок Сглаживания (от 1% до 30%)
        saved_alpha = float(self.video_data.get("tracking_alpha", 0.15))
        if saved_alpha > 0.30: saved_alpha = 0.30
        if saved_alpha < 0.01: saved_alpha = 0.01
        alpha_slider_val = int(saved_alpha * 100)
        
        smooth_txt_layout = QHBoxLayout()
        smooth_lbl = QLabel("Плавность движения (Сглаживание):")
        self.lbl_smooth_val = QLabel(f"{alpha_slider_val}%")
        self.lbl_smooth_val.setStyleSheet("color: #2ed573; font-weight: bold;")
        smooth_txt_layout.addWidget(smooth_lbl)
        smooth_txt_layout.addStretch()
        smooth_txt_layout.addWidget(self.lbl_smooth_val)
        layout.addLayout(smooth_txt_layout)
        
        self.slider_smooth = QSlider(Qt.Orientation.Horizontal)
        self.slider_smooth.setRange(1, 30)
        self.slider_smooth.setValue(alpha_slider_val)
        self.slider_smooth.valueChanged.connect(self.on_smooth_changed)
        layout.addWidget(self.slider_smooth)
        
        layout.addSpacing(5)

        # 3. Ползунок Мёртвой зоны (0.00 - 0.40)
        saved_threshold = float(self.mouse_data.get("threshold", 0.15))
        if saved_threshold > 0.40: saved_threshold = 0.40
        thresh_slider_val = int(saved_threshold * 100)
        
        thresh_txt_layout = QHBoxLayout()
        thresh_lbl = QLabel("Порог чувствительности (Мёртвая зона):")
        self.lbl_thresh_val = QLabel(f"{round(saved_threshold, 2)}")
        self.lbl_thresh_val.setStyleSheet("color: #2ed573; font-weight: bold;")
        thresh_txt_layout.addWidget(thresh_lbl)
        thresh_txt_layout.addStretch()
        thresh_txt_layout.addWidget(self.lbl_thresh_val)
        layout.addLayout(thresh_txt_layout)
        
        self.slider_threshold = QSlider(Qt.Orientation.Horizontal)
        self.slider_threshold.setRange(0, 40)
        self.slider_threshold.setValue(thresh_slider_val)
        self.slider_threshold.valueChanged.connect(self.on_threshold_changed)
        layout.addWidget(self.slider_threshold)

        layout.addStretch()

    def on_speed_changed(self, value):
        self.lbl_speed_val.setText(f"{round(float(value), 1)}")
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        config["profiles"][current_prof]["mouse"]["speed"] = float(value)
        config_manager.save_config(config)

    def on_smooth_changed(self, value):
        float_val = value / 100.0
        self.lbl_smooth_val.setText(f"{value}%")
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        config["profiles"][current_prof]["video"]["tracking_alpha"] = float_val
        config_manager.save_config(config)

    def on_threshold_changed(self, value):
        float_val = value / 100.0
        self.lbl_thresh_val.setText(f"{round(float_val, 2)}")
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        config["profiles"][current_prof]["mouse"]["threshold"] = float_val
        config_manager.save_config(config)
