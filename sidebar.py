# sidebar.py
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QPushButton, QComboBox, QLabel
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QIcon
import styles
import config_manager  # ПОДКЛЮЧАЕМ НАШ МЕНЕДЖЕР СОХРАНЕНИЙ

class SidebarMenu(QFrame):
    # Сигналы для отправки команд переключения страниц главному окну main.py
    home_requested = pyqtSignal()
    profiles_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    about_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setFixedWidth(210)  # Строго фиксированная ширина левой панели
        
        # СЧИТЫВАЕМ ИЗ JSON ТЕКУЩИЙ АКТИВНЫЙ ПРОФИЛЬ ПРИ СТАРТЕ:
        self.config = config_manager.load_config()
        self.saved_profile = self.config.get("current_profile", "Default Profile")
        
        # Применяем базовую структуру стилей
        self.setStyleSheet(styles.STYLE_SIDEBAR_PANEL)
        
        # Основной vertical слой меню
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 15, 12, 15)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # 1. Создаем кнопки навигации с вашими иконками
        self.btn_home = self.create_nav_button("Главная", styles.get_image("Home.png"))
        self.btn_profiles = self.create_nav_button("Профили", styles.get_image("Profile.png"))
        self.btn_settings = self.create_nav_button("Настройки", styles.get_image("Settings.png"))
        self.btn_about = self.create_nav_button("О программе", styles.get_image("About.png"))
        
        # Подключаем клики к отправке сигналов
        self.btn_home.clicked.connect(self.home_requested.emit)
        self.btn_profiles.clicked.connect(self.profiles_requested.emit)
        self.btn_settings.clicked.connect(self.settings_requested.emit)
        self.btn_about.clicked.connect(self.about_requested.emit)
        
        # Добавляем кнопки в слой
        layout.addWidget(self.btn_home)
        layout.addWidget(self.btn_profiles)
        layout.addWidget(self.btn_settings)
        layout.addWidget(self.btn_about)
        
        # Пружина-распорка: сдвигает всё, что ниже, к самому низу панели
        layout.addStretch()
        
        # 2. Нижний блок управления: Выбор профиля
        self.profile_box = QComboBox()
        self.profile_box.addItems(["Default Profile", "Gaming", "Work"])
        self.profile_box.setFixedHeight(30)
        
        # Автоматически выставляем тот профиль, который сохранен в JSON
        index = self.profile_box.findText(self.saved_profile)
        if index >= 0:
            self.profile_box.setCurrentIndex(index)
            
        # Подключаем смену профиля к методу сохранения в JSON
        self.profile_box.currentTextChanged.connect(self.on_profile_changed)
        
        layout.addWidget(self.profile_box)
        layout.addSpacing(180) 
        
        # 3. Кнопка запуска "▶ Start" (УМЕНЬШИЛИ ШИРИНУ И ИСПРАВИЛИ ЦВЕТ ХОВЕРА НА ЯРКО-ЗЕЛЕНЫЙ)
        self.btn_start = QPushButton("▶ Start")
        self.btn_start.setObjectName("BtnStart")
        self.btn_start.setFixedHeight(34)
        self.btn_start.setFixedWidth(120) # Сделали кнопку уже, чтобы появилось пространство по бокам
        
        # Динамический зеркальный градиент для рамки Start
        START_BORDER = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2ed573, stop:0.5 #112d1b, stop:1 #2ed573)"
        self.btn_start.setStyleSheet(f"""
            QPushButton#BtnStart {{
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1a4d2e, stop:0.4 #112d1b, stop:1 #06120b);
                color: #2ed573;
                border: 1px solid {START_BORDER};
                border-radius: 6px;
                font-weight: bold;
                text-align: center;
                padding-left: 0px;
                font-size: 13px;
            }}
            QPushButton#BtnStart:hover {{
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2ed573, stop:0.5 #1f6b3b, stop:1 #112d1b);
                color: #2ed573;
                border-color: #2ed573;
            }}
        """)
        # Добавляем кнопку в слой и выравниваем по центру панели (чтобы отступы справа и слева были одинаковыми)
        layout.addWidget(self.btn_start, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(20)  # Число 20 — это зазор в пикселях между Start и Stop.
        # 4. Кнопка остановки "■ Stop" (УМЕНЬШИЛИ ШИРИНУ И ИСПРАВИЛИ ЦВЕТ ХОВЕРА НА ЯРКО-КРАСНЫЙ)
        self.btn_stop = QPushButton("■ Stop")
        self.btn_stop.setObjectName("BtnStop")
        self.btn_stop.setFixedHeight(34)
        self.btn_stop.setFixedWidth(120) # Сделали кнопку уже, чтобы появилось пространство по бокам
        
        STOP_BORDER = f"qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {styles.COLOR_RED}, stop:0.5 #3d141d, stop:1 {styles.COLOR_RED})"
        self.btn_stop.setStyleSheet(f"""
            QPushButton#BtnStop {{
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5c1e29, stop:0.4 #3d141d, stop:1 #1a080c);
                color: {styles.COLOR_RED};
                border: 1px solid {STOP_BORDER};
                border-radius: 6px;
                font-weight: bold;
                text-align: center;
                padding-left: 0px;
                font-size: 13px;
            }}
            QPushButton#BtnStop:hover {{
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {styles.COLOR_RED}, stop:0.5 #8c1c2f, stop:1 #3d141d);
                color: {styles.COLOR_RED};
                border-color: {styles.COLOR_RED};
            }}
        """)
        layout.addWidget(self.btn_stop, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(30)  # Число 30 — это зазор в пикселях снизу. Он приподнимет Stop выше.
        
        # 5. Текстовый статус готовности системы в самом низу
        self.status_label = QLabel("● Система готова")
        self.status_label.setObjectName("StatusLabel")
        self.status_label.setStyleSheet(f"color: {styles.COLOR_GREEN}; font-size: 11px; margin-top: 5px; font-weight: 500; background: transparent; border: none;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

    def on_profile_changed(self, profile_name):
        """Метод обработки смены профиля: МГНОВЕННО сохраняет выбранное имя в JSON-файл"""
        config = config_manager.load_config()
        config["current_profile"] = profile_name
        config_manager.save_config(config)

    def create_nav_button(self, text, icon_path):
        """Вспомогательный метод для красивой сборки кнопок со световым излучением вправо"""
        btn = QPushButton(text)
        btn.setFixedHeight(38)
        
        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-left: 3px solid transparent;
                color: #a1a3b5;
                text-align: left;
                padding-left: 12px;
                font-size: 13px;
                font-weight: 500;
                border-radius: 0px;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(0, 210, 255, 0.55), stop:0.6 rgba(0, 210, 255, 0.15), stop:1 rgba(0, 210, 255, 0));
                color: #ffffff;
                border-left: 4px solid #00d2ff;
            }
            QPushButton:focus {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(0, 210, 255, 0.65), stop:0.7 rgba(0, 210, 255, 0.20), stop:1 rgba(0, 210, 255, 0));
                color: #ffffff;
                border-left: 4px solid #00d2ff;
            }
        """)
        
        # Загружаем иконку пользователя
        icon = QIcon(icon_path)
        if not icon.isNull():
            btn.setIcon(icon)
            btn.setIconSize(QSize(18, 18))
            
        return btn
