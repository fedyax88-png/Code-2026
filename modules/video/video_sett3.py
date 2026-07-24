# modules/video/video_sett3.py
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import styles
import config_manager

class VideoSettingBlock3(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingCard")
        
        self.config = config_manager.load_config()
        self.current_prof = self.config.get("current_profile", "Default Profile")
        self.video_data = self.config["profiles"][self.current_prof]["video"]
        
        self.setStyleSheet("""
            QFrame#SettingCard { background-color: #03060f; border: 1px solid #101f38; border-radius: 10px; }
            QLabel { color: #ffffff; font-family: 'Segoe UI', sans-serif; font-size: 12px; background: transparent; border: none; }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(12)
        
        # Верхняя строка
        top_layout = QHBoxLayout(); top_layout.setSpacing(10)
        ico = QLabel()
        pix = QPixmap(styles.get_image("video1.png"))
        if not pix.isNull():
            ico.setPixmap(pix.scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        top_layout.addWidget(ico)
        
        title = QLabel("Дистанция и Калибровка")
        title.setStyleSheet("font-size: 13px; font-weight: bold; color: #ffffff;")
        top_layout.addWidget(title)
        top_layout.addStretch()
        
        self.toggle = QPushButton("●")
        self.toggle.setCheckable(True)
        self.toggle.setChecked(self.video_data.get("setting_3", True))
        self.toggle.setFixedSize(44, 20)
        self.toggle.setStyleSheet("background-color: #00d2ff; border: none; border-radius: 10px; text-align: right; color: white; font-size: 34px; font-weight: bold; padding-top: -10px;")
        top_layout.addWidget(self.toggle)
        layout.addLayout(top_layout)
        
        line = QFrame(); line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #162e54; min-height: 1px; max-height: 1px; border: none;")
        layout.addWidget(line)
        
        # ИНФОРМАЦИОННЫЕ ПОЛЯ ДЛЯ СЛЕЖЕНИЯ ЗА ДИСТАНЦИЕЙ ГОЛОВЫ
        info_label = QLabel("Текущие параметры кадра:")
        info_label.setStyleSheet("color: #a1a3b5; font-size: 11px;")
        layout.addWidget(info_label)
        
        size_layout = QHBoxLayout()
        size_title = QLabel("Размер силуэта лица:")
        # Сюда ИИ-поток будет выводить живые пиксели ширины головы
        self.lbl_head_size = QLabel("Камера спит")
        self.lbl_head_size.setStyleSheet("color: #00d2ff; font-weight: bold; font-size: 13px;")
        size_layout.addWidget(size_title)
        size_layout.addStretch()
        size_layout.addWidget(self.lbl_head_size)
        layout.addLayout(size_layout)
        
        desc_info = QLabel("Оптимальный размер: 140 - 220 px.<br>Если значение меньше — придвиньтесь ближе.<br>Если значение больше — сядьте дальше.")
        desc_info.setStyleSheet("color: #555e75; font-size: 11px; line-height: 1.3; padding-top: 5px;")
        layout.addWidget(desc_info)
        
        layout.addStretch()

    def update_live_head_size(self, pixels):
        """Живой метод перерисовки текста пикселей, вызываемый по сигналу из потока"""
        if self.toggle.isChecked():
            self.lbl_head_size.setText(f"{pixels} px")
