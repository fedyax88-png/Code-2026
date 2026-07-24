# modules/video/video_sett1.py
import cv2
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox
from PyQt6.QtCore import Qt, pyqtSignal  # Добавили pyqtSignal для автоперезапуска
from PyQt6.QtGui import QPixmap
import styles
import config_manager

class VideoSettingBlock1(QFrame):
    # НОВЫЙ СИГНАЛ: Сообщает модулю видео, что пользователь изменил параметры железа
    settings_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingCard")
        
        # ЗАГРУЖАЕМ сохраненные настройки из JSON файла при старте
        self.config = config_manager.load_config()
        self.current_prof = self.config.get("current_profile", "Default Profile")
        self.video_data = self.config["profiles"][self.current_prof]["video"]
        
        # УЛЬТРА-СТИЛИЗАЦИЯ: Исправили черный текст во всплывающем списке (QAbstractItemView)
        self.setStyleSheet("""
            QFrame#SettingCard {
                background-color: #03060f;
                border: 1px solid #101f38;
                border-radius: 10px;
            }
            QLabel { color: #ffffff; font-family: 'Segoe UI', sans-serif; font-size: 12px; background: transparent; border: none; }
            
            QComboBox {
                background-color: #071224; 
                color: #00d2ff; 
                border: 1px solid #162e54; 
                border-radius: 4px;
                padding-left: 5px; 
                font-size: 11px; 
                font-weight: 500;
            }
            QComboBox::drop-down { border: none; }
            
            /* ЖЕСТКО КРАСИМ ВСПЛЫВАЮЩИЙ СПИСОК: тёмный фон, БЕЛЫЙ ТЕКСТ */
            QComboBox QAbstractItemView {
                background-color: #071224;
                color: #ffffff; /* ТЕКСТ ТЕПЕРЬ ГАРАНТИРОВАННО БЕЛЫЙ */
                border: 1px solid #162e54;
                selection-background-color: #00d2ff; /* Голубой неон при наведении */
                selection-color: #000000; /* Черные буквы на ховере для читаемости */
                outline: none;
            }
        """)
        
        # Главный вертикальный слой блока настроек
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(12)
        
        # Верхняя строка: Иконка + Заголовок + Свитч включения этого блока
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)
        
        ico = QLabel()
        pix = QPixmap(styles.get_image("video1.png"))
        if not pix.isNull():
            ico.setPixmap(pix.scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        top_layout.addWidget(ico)
        
        title = QLabel("Формат и Разрешение")
        title.setStyleSheet("font-size: 13px; font-weight: bold; color: #ffffff;")
        top_layout.addWidget(title)
        top_layout.addStretch()
        
        # Крупный голубой переключатель (Toggle)
        self.toggle = QPushButton("●")
        self.toggle.setCheckable(True)
        self.toggle.setChecked(self.video_data.get("setting_1", True))
        self.toggle.setFixedSize(44, 20)
        self.toggle.setStyleSheet("background-color: #00d2ff; border: none; border-radius: 10px; text-align: right; color: white; font-size: 34px; font-weight: bold; padding-top: -10px;")
        top_layout.addWidget(self.toggle)
        layout.addLayout(top_layout)
        
        # Тонкая линия разделителя
        line = QFrame(); line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #162e54; min-height: 1px; max-height: 1px; border: none;")
        layout.addWidget(line)
        
        # --- СЕТКА ДЛЯ ВЫБОРА ПАРАМЕТРОВ КАМЕРЫ ---
        res_layout = QHBoxLayout()
        res_label = QLabel("Разрешение экрана:")
        self.combo_res = QComboBox()
        self.combo_res.setFixedSize(110, 22)
        res_layout.addWidget(res_label)
        res_layout.addStretch()
        res_layout.addWidget(self.combo_res)
        layout.addLayout(res_layout)
        
        fps_layout = QHBoxLayout()
        fps_label = QLabel("Частота кадров (FPS):")
        self.combo_fps = QComboBox()
        self.combo_fps.setFixedSize(110, 22)
        fps_layout.addWidget(fps_label)
        fps_layout.addStretch()
        fps_layout.addWidget(self.combo_fps)
        layout.addLayout(fps_layout)
        
        fmt_layout = QHBoxLayout()
        fmt_label = QLabel("Формат потака:")
        self.combo_fmt = QComboBox()
        self.combo_fmt.setFixedSize(110, 22)
        fmt_layout.addWidget(fmt_label)
        fmt_layout.addStretch()
        fmt_layout.addWidget(self.combo_fmt)
        layout.addLayout(fmt_layout)
        
        layout.addStretch()
        
        # Блокируем сигналы перед заполнением, чтобы не вызвать ложный автоперезапуск при старте
        self.combo_res.blockSignals(True)
        self.combo_fps.blockSignals(True)
        self.combo_fmt.blockSignals(True)
        
        self.scan_hardware_capabilities()
        
        # Разблокируем сигналы
        self.combo_res.blockSignals(False)
        self.combo_fps.blockSignals(False)
        self.combo_fmt.blockSignals(False)
        
        # Связываем изменение выбора в списках с сохранением и отправкой сигнала изменения
        self.combo_res.currentTextChanged.connect(self.save_current_settings)
        self.combo_fps.currentTextChanged.connect(self.save_current_settings)
        self.combo_fmt.currentTextChanged.connect(self.save_current_settings)

    def scan_hardware_capabilities(self):
        resolutions_to_test = ["1280x720", "1024x576", "960x540", "800x600", "640x480", "320x240"]
        fps_to_test = ["30", "25", "20", "15"]
        formats_to_test = ["MJPG", "YUY2"]
        
        self.combo_res.addItems(resolutions_to_test)
        self.combo_fps.addItems(fps_to_test)
        self.combo_fmt.addItems(formats_to_test)
        
        saved_res = self.video_data.get("resolution", "640x480")
        saved_fps = str(self.video_data.get("fps", 30))
        saved_fmt = self.video_data.get("video_format", "MJPG")
        
        idx_res = self.combo_res.findText(saved_res); self.combo_res.setCurrentIndex(idx_res if idx_res >= 0 else 4)
        idx_fps = self.combo_fps.findText(saved_fps); self.combo_fps.setCurrentIndex(idx_fps if idx_fps >= 0 else 0)
        idx_fmt = self.combo_fmt.findText(saved_fmt); self.combo_fmt.setCurrentIndex(idx_fmt if idx_fmt >= 0 else 0)

    def save_current_settings(self):
        """Метод сбора данных из выпадающих списков, записи в config.json и отправки триггера перезапуска"""
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        video_conf = config["profiles"][current_prof]["video"]
        
        video_conf["resolution"] = self.combo_res.currentText()
        try:
            video_conf["fps"] = int(self.combo_fps.currentText())
        except ValueError:
            video_conf["fps"] = 30
        video_conf["video_format"] = self.combo_fmt.currentText()
        
        config_manager.save_config(config)
        
        # ОТПРАВЛЯЕМ СИГНАЛ: Главное окно поймает его и мгновенно перезагрузит камеру
        self.settings_changed.emit()
