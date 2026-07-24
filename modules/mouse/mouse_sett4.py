# modules/mouse_sett4.py
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import styles

class MouseSettingBlock4(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingCard")
        self.setStyleSheet("QFrame#SettingCard { background-color: #030a06; border: 1px solid #10381f; border-radius: 10px; }")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(10)
        
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)
        
        ico = QLabel()
        ico.setStyleSheet("background: transparent; border: none;")
        pix = QPixmap(styles.get_image("mouse1.png"))
        if not pix.isNull():
            ico.setPixmap(pix.scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        top_layout.addWidget(ico)
        
        title = QLabel("Настройки 4")
        title.setStyleSheet("color: #ffffff; font-size: 14px; font-weight: 500; background: transparent; border: none;")
        top_layout.addWidget(title)
        top_layout.addStretch()
        
        self.toggle = QPushButton("●")
        self.toggle.setCheckable(True)
        self.toggle.setChecked(True)
        self.toggle.setFixedSize(44, 20)
        self.toggle.setStyleSheet("background-color: #2ed573; border: none; border-radius: 10px; text-align: right; padding-right: 0px; color: white; font-size: 34px; font-weight: bold; padding-top: -10px;")
        top_layout.addWidget(self.toggle)
        layout.addLayout(top_layout)
        
        layout.addStretch()

