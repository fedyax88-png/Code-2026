from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

class PlaceholderPage(QFrame):
    def __init__(self, title_text, parent=None):
        super().__init__(parent)
        self.setObjectName("MainSettingsCard")
        
        # Индивидуальный темный фон карточки в тон левой панели
        self.setStyleSheet("""
            QFrame#MainSettingsCard {
                background-color: #040314;
                border: 2px solid #1a153a;
                border-radius: 12px;
            }
        """)
        
        # Задаем вертикальный слой и выравниваем текст по центру
        layout = QVBoxLayout(self)
        
        label = QLabel(title_text)
        label.setStyleSheet("color: #ffffff; font-size: 16px; font-weight: bold; background: transparent; border: none;")
        
        layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)

