# modules/video_module.py 1 часть из 6
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QTimer
from PyQt6.QtGui import QPixmap, QIcon
import styles
import config_manager  # НАШ МЕНЕДЖЕР СОХРАНЕНИЙ

# Импортируем фоновый поток запуска камеры
from modules.video.start_camera import CameraWorker

class VideoControlModule(QFrame):
    # Сигнал для открытия окна детальных настроек
    settings_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        
        # ЗАГРУЖАЕМ сохраненные настройки из JSON файла при старте
        self.config = config_manager.load_config()
        self.current_prof = self.config.get("current_profile", "Default Profile")
        self.video_data = self.config["profiles"][self.current_prof]["video"]
        
        # Основной vertical слой карточки
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 1, 5, 10)
        self.main_layout.setSpacing(10)
        
        # ==========================================
        # 1. ВЕРХНЯЯ ПАНЕЛЬ ЗАГОЛОВКА
        # ==========================================
        self.header_panel = QFrame()
        self.header_panel.setStyleSheet("""
            QFrame {
                background-color: #050d1a;
                border: 1px solid #101f38;
                border-radius: 6px;
            }
        """)
        title_layout = QHBoxLayout(self.header_panel)
        title_layout.setContentsMargins(12, 6, 12, 6)
        title_layout.setSpacing(20)
        
        # Картинка video1.png
        self.video_icon = QLabel()
        self.video_icon.setStyleSheet("background: transparent; border: none;")
        vid_top_pixmap = QPixmap(styles.get_image("video1.png"))
        if not vid_top_pixmap.isNull():
            self.video_icon.setPixmap(vid_top_pixmap.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        title_layout.addWidget(self.video_icon)
        
        # Текст заголовка
        self.title_label = QLabel("1. ВИДЕО")
        self.title_label.setStyleSheet(f"font-weight: bold; font-size: 13px; color: {styles.TEXT_WHITE}; background: transparent; border: none;")
        title_layout.addWidget(self.title_label)
        
        title_layout.addStretch()
        
        # Кастомный крупный голубой переключатель
        self.toggle_btn = QPushButton()
        self.toggle_btn.setCheckable(True)
        
        # Считываем состояние главного бегунка
        saved_toggle_state = self.video_data.get("main_toggle", True)
        self.toggle_btn.setChecked(saved_toggle_state)
        
        self.toggle_btn.setFixedSize(44, 20)
        self.toggle_btn.clicked.connect(self.on_toggle_clicked)
        title_layout.addWidget(self.toggle_btn)
        
        self.main_layout.addWidget(self.header_panel)
# modules/video_module.py 2 часть из 6        
        # ==========================================
        # 2. ЦЕНТРАЛЬНАЯ ЧАСТЬ
        # ==========================================
        content_layout = QHBoxLayout()
        content_layout.setSpacing(5)
        
        self.video_img = QLabel()
        self.video_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_img.setStyleSheet("background: transparent; border: none;")
        
        # Инициализируем поток камеры
        self.camera_thread = CameraWorker(self)
        
        video_pixmap = QPixmap(styles.get_image("video.jpg"))
        if not video_pixmap.isNull():
            self.video_img.setPixmap(video_pixmap.scaled(320, 240, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        content_layout.addWidget(self.video_img, stretch=1)
        
        # Считываем сохраненный онлайн-режим отображения (по умолчанию True)
        self.saved_online_mode = self.video_data.get("online_mode", True)
        
        # СЧИТЫВАЕМ СОХРАНЕННЫЙ РЕЖИМ ИИ-ТРЕКИНГА ЛИЦА (по умолчанию True)
        self.saved_tracking_mode = self.video_data.get("tracking_mode", True)
        
        # Если главный бегунок включен — запускаем физический поток камеры в фоне ВСЕГДА
        if saved_toggle_state:
            self.camera_thread.start()
        # --- ПРАВАЯ СТОРОНА: Вертикальные блоки статуса и потока ---
        right_blocks_layout = QVBoxLayout()
        right_blocks_layout.setSpacing(5)
        
        # ПРЯМОУГОЛЬНИК А: Статус работы трансляции
        self.status_block = QFrame()
        status_lay = QHBoxLayout(self.status_block)
        status_lay.setContentsMargins(10, 10, 10, 10)
        status_lay.setSpacing(10)
        
        status_ico = QLabel()
        status_ico.setStyleSheet("background: transparent; border: none;")
        vid_status_pixmap = QPixmap(styles.get_image("video2.png"))
        if not vid_status_pixmap.isNull():
            status_ico.setPixmap(vid_status_pixmap.scaled(25, 25, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        status_lay.addWidget(status_ico)
        
        status_text_lay = QVBoxLayout()
        status_text_lay.setSpacing(2)
        status_title = QLabel("Трансляция<br>видео")
        status_title.setStyleSheet("color: #ffffff; font-size: 12px; font-weight: 500; background: transparent; border: none; line-height: 1.1;")
        
        self.status_value = QLabel()
        if saved_toggle_state:
            self.status_value.setText("Включена")
            self.status_value.setStyleSheet(f"color: {styles.COLOR_GREEN}; font-weight: bold; font-size: 11px; background: transparent; border: none; margin-top: 4px;")
        else:
            self.status_value.setText("Отключено")
            self.status_value.setStyleSheet(f"color: {styles.TEXT_MUTED}; font-size: 11px; background: transparent; border: none; margin-top: 4px;")
        
        status_text_lay.addWidget(status_title)
        status_text_lay.addWidget(self.status_value)
        status_lay.addLayout(status_text_lay)
        status_lay.addStretch()
        
        self.status_block.setFixedWidth(160)
        right_blocks_layout.addWidget(self.status_block)
        
        # ПРЯМОУГОЛЬНИК Б: Отображение потока в реальном времени
        self.mode_block = QFrame()
        mode_lay = QVBoxLayout(self.mode_block)
        mode_lay.setContentsMargins(12, 8, 12, 8)
        mode_lay.setSpacing(4)
        
        mode_title = QLabel("Отображение<br>потока")
        mode_title.setStyleSheet("color: #ffffff; font-size: 12px; font-weight: 500; background: transparent; border: none; line-height: 1.1;")
        
        self.mode_value = QLabel("в реальном времени")
        self.mode_value.setStyleSheet(f"color: {styles.TEXT_MUTED}; font-size: 13px; background: transparent; border: none; margin-top: 4px;")
        
        mode_lay.addWidget(mode_title)
        mode_lay.addWidget(self.mode_value)
        
        self.mode_block.setFixedWidth(160)
        right_blocks_layout.addWidget(self.mode_block)
        
        content_layout.addLayout(right_blocks_layout, stretch=1)
        self.main_layout.addLayout(content_layout)
        
        self.main_layout.addStretch()
# modules/video_module.py 3 часть из 6        
        # ==========================================
        # 3. НИЖНЯЯ ПАНЕЛЬ С КНОПКАМИ УПРАВЛЕНИЯ
        # ==========================================
        bottom_buttons = QHBoxLayout()
        bottom_buttons.setSpacing(6)
        
        # Переводим первую кнопку в режим тумблера (Checkable)
        self.btn_1 = QPushButton()
        self.btn_1.setCheckable(True)
        self.btn_1.setChecked(self.saved_online_mode)
        
        if self.saved_online_mode:
            self.btn_1.setText("Онлайн вкл")
        else:
            self.btn_1.setText("Онлайн выкл")
            
        # ПЕРЕВOДИМ ВТОРУЮ КНОПКУ ТРЕКИНГА В РЕЖИМ ТУМБЛЕРА (Checkable)
        self.btn_2 = QPushButton()
        self.btn_2.setCheckable(True)
        self.btn_2.setChecked(self.saved_tracking_mode)
        
        if self.saved_tracking_mode:
            self.btn_2.setText("Трекинг вкл")
        else:
            self.btn_2.setText("Трекинг выкл")
            
        self.btn_settings = QPushButton("Настройки видео")
        
        gear_icon = QIcon(styles.get_image("Settings.png"))
        if not gear_icon.isNull():
            self.btn_settings.setIcon(gear_icon)
            self.btn_settings.setIconSize(QSize(14, 14))
        
        for btn in [self.btn_1, self.btn_2, self.btn_settings]:
            btn.setFixedHeight(40)
            
        # Подключаем клики к интерактивным методам
        self.btn_1.clicked.connect(self.on_online_button_clicked)
        self.btn_2.clicked.connect(self.on_tracking_button_clicked)
        self.btn_settings.clicked.connect(self.settings_clicked.emit)
            
        bottom_buttons.addWidget(self.btn_1, stretch=1)
        bottom_buttons.addWidget(self.btn_2, stretch=1)
        bottom_buttons.addWidget(self.btn_settings, stretch=2)
        
        self.main_layout.addLayout(bottom_buttons)
        
        # Технические настройки для подсчета и вывода FPS
        self.current_fps_value = 0
        self.ui_fps_timer = QTimer(self)
        self.ui_fps_timer.setInterval(2000)
        self.ui_fps_timer.timeout.connect(self.update_fps_text_on_screen)
        
        self.camera_thread.fps_received.connect(self.store_fps_value)
        
        # Применяем неоновую обводку, настраиваемые фоны и обновляем стили
        self.update_module_colors()
        self.update_toggle_style()
        self.update_online_button_style()
        self.update_tracking_button_style()  # Вызов нового стиля для обводки трекинга
        
        # Если главный тумблер ВКЛЮЧЕН и Онлайн режим ТОЖЕ ВКЛЮЧЕН — запускаем отрисовку и таймер FPS
        if saved_toggle_state and self.saved_online_mode:
            self.camera_thread.frame_received.connect(self.video_img.setPixmap)
            self.ui_fps_timer.start()
    def update_module_colors(self):
        """
        ЗДЕСЬ НАСТРАИВАЮТСЯ ВСЕ ИНДИВИДУАЛЬНЫЕ ЦВЕTA МОДУЛЯ 1 (ВИДЕО):
        """
        CARD_BG = "#03060f"        # Очень темный фон внутри модуля (под картинкой и кнопками)
        
        # ПЛАВНЫЙ ДИAГОНАЛЬНЫЙ НЕОНОВЫЙ ГРАДИЕНТ РАМКИ
        BORDER_GRADIENT = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00d2ff, stop:0.2 #5d1b94, stop:1 #00d2ff)"
        
        BLOCK_BG = "#050d1a"       # Цвет внутри прямоугольников с правой стороны
        BLOCK_BORDER = "#101f38"   # Цвет тонкой обводки этих прямоугольников
        
        # Базовые стили для кнопок управления модуля видео (применяются ко всем кнопкам, кроме Онлайн вкл)
        self.btn_bg_color = "#071224"         
        self.btn_border_color = "#162e54"     
        self.btn_text_color = "#00d2ff"       
        
        self.setStyleSheet(f"""
            QFrame#Card {{
                background-color: {CARD_BG};
                border: 2px solid {BORDER_GRADIENT};
                border-radius: 12px;
             }}
            QPushButton {{
                background-color: {self.btn_bg_color};
                color: {self.btn_text_color};
                border: 1px solid {self.btn_border_color};
                border-radius: 6px;
                font-weight: 500;
             }}
            QPushButton:hover {{
                background-color: #00d2ff;
                color: #000000;
                border-color: #ffffff;
             }}
        """)
        
        block_style = f"QFrame {{ background-color: {BLOCK_BG}; border: 1px solid {BLOCK_BORDER}; border-radius: 8px; }}"
        self.status_block.setStyleSheet(block_style)
        self.mode_block.setStyleSheet(block_style)

# modules/video_module.py 4 часть из 6
    def store_fps_value(self, value):
        """Вспомогательный метод: сохраняет свежее значение FPS из потока в буфер"""
        self.current_fps_value = value

    def update_fps_text_on_screen(self):
        """Метод обновления экрана: вызывается раз в 2 секунды и выводит статус потока"""
        if self.toggle_btn.isChecked():
            if self.btn_1.isChecked():
                # А) Режим полной трансляции: Крупный и сочный зеленый FPS
                self.mode_value.setText(f"{self.current_fps_value} FPS")
                self.mode_value.setStyleSheet(f"color: {styles.COLOR_GREEN}; font-weight: bold; font-size: 18px; background: transparent; border: none; margin-top: 4px;")
            else:
                # Б) Режим фоновой обработки: Зеленая надпись + мелкие цифры FPS в конце
                self.mode_value.setText(f"Поток активен <span style='font-size: 10px; font-weight: normal;'>({self.current_fps_value} FPS)</span>")
                self.mode_value.setStyleSheet(f"color: {styles.COLOR_GREEN}; font-weight: bold; font-size: 11px; background: transparent; border: none; margin-top: 4px;")

    def hot_reboot_camera_hardware(self):
        """МЕТОД АВТОПЕPЕЗАПУСКА: На лету подхватывает новые параметры разрешения из JSON"""
        # Если в этот момент камера физически включена главным бегунком — делаем горячую перезагрузку
        if self.toggle_btn.isChecked():
            # Мягко тушим поток со старыми параметрами матрицы
            self.camera_thread.stop()
            # Сразу запускаем заново — поток считает из JSON новые ширину/высоту и FPS и применит к Logitech!
            self.camera_thread.start()

    def on_online_button_clicked(self, checked):
        """Логика интерактивной кнопки Онлайн вкл/выкл с экономией процессора и сохранением в JSON"""
        if checked:
            self.btn_1.setText("Онлайн вкл")
            
            # Если главный бегунок включен — подключаем вывод видео на экран
            if self.toggle_btn.isChecked():
                try:
                    self.camera_thread.frame_received.connect(self.video_img.setPixmap)
                except TypeError:
                    pass
        else:
            self.btn_1.setText("Онлайн выкл")
            
            # ОТКЛЮЧАЕМ отрисовку кадров на экране
            try:
                self.camera_thread.frame_received.disconnect(self.video_img.setPixmap)
            except TypeError:
                pass
                
            # Принудительно возвращаем JPEG-заглушку, очищая экран от зависшего кадра
            video_pixmap = QPixmap(styles.get_image("video.jpg"))
            if not video_pixmap.isNull():
                self.video_img.setPixmap(video_pixmap.scaled(320, 240, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

        self.update_fps_text_on_screen()
        self.update_online_button_style()
        
        # Сохраняем флаг онлайн режима в JSON базу
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        config["profiles"][current_prof]["video"]["online_mode"] = checked
        config_manager.save_config(config)

    def on_tracking_button_clicked(self, checked):
        """Логика кнопки Трекинг вкл/выкл с защитой от внезапной потери контроля над курсором"""
        # Если пользователь ВКЛЮЧАЕТ трекинг — делаем это сразу без подтверждений
        if checked:
            self.execute_tracking_logic(True)
        else:
            # Если пытается ВЫКЛЮЧИТЬ — блокируем и выводим фирменное сине-фиолетовое окно
            from PyQt6.QtWidgets import QMessageBox
            
            msg = QMessageBox(self)
            msg.setWindowTitle("Предупреждение")
            msg.setText("ВНИМАНИЕ!\n\nВы отключаете ИИ-ТРЕКИНГ лица.\nКурсор мыши ПЕРЕСТАНЕТ ходить за вашей головой.\n\nВы уверены, что хотите остановить трекинг?")
            msg.setIcon(QMessageBox.Icon.Warning)
            
            yes_btn = msg.addButton("Да, отключить", QMessageBox.ButtonRole.YesRole)
            no_btn = msg.addButton("Отмена", QMessageBox.ButtonRole.NoRole)
            msg.setDefaultButton(no_btn)
            
            # Стилизуем окно под неоновый интерфейс вашей видео-карточки
            msg.setStyleSheet("""
                QMessageBox { background-color: #03060f; border: 2px solid #00d2ff; border-radius: 10px; }
                QLabel { color: #ffffff; font-family: 'Segoe UI', sans-serif; font-size: 12px; font-weight: bold; }
                QPushButton { background-color: #071224; color: #00d2ff; border: 1px solid #162e54; border-radius: 4px; padding: 6px 14px; font-weight: bold; min-width: 80px; }
                QPushButton:hover { background-color: #00d2ff; color: black; border-color: white; }
            """)
            
            msg.exec()
            
            if msg.clickedButton() == yes_btn:
                self.execute_tracking_logic(False)
            else:
                # Отмена: принудительно возвращаем кнопку в нажатое (включенное) состояние
                self.btn_2.blockSignals(True)
                self.btn_2.setChecked(True)
                self.btn_2.blockSignals(False)
                self.btn_2.setText("Трекинг вкл")
                self.update_tracking_button_style()

# modules/video_module.py 5 часть из 6
    def execute_tracking_logic(self, checked):
        """Вспомогательный метод для сохранения состояния трекинга лица в JSON"""
        if checked:
            self.btn_2.setText("Трекинг вкл")
        else:
            self.btn_2.setText("Трекинг выкл")
            
        self.update_tracking_button_style()
        
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        config["profiles"][current_prof]["video"]["tracking_mode"] = checked
        config_manager.save_config(config)

    def update_online_button_style(self):
       """Отрисовка сочного ярко-синего неонового ободка на кнопке Онлайн при включении"""
       if self.btn_1.isChecked():
           self.btn_1.setStyleSheet(f"""
               QPushButton {{
                   background-color: #051224;
                   color: #00d2ff;
                   border: 1px solid #00d2ff;
                   border-radius: 6px;
                   font-weight: bold;
               }}
               QPushButton:hover {{
                   background-color: #00d2ff; color: #000000; border-color: #ffffff;
               }}
           """)
       else:
           self.btn_1.setStyleSheet(f"""
               QPushButton {{
                   background-color: {self.btn_bg_color};
                   color: #555e75;
                   border: 1px solid {self.btn_border_color};
                   border-radius: 6px;
                   font-weight: 500;
               }}
               QPushButton:hover {{
                   background-color: #00d2ff; color: #000000; border-color: #ffffff;
               }}
           """)

    def update_tracking_button_style(self):
       """Отрисовка сочного ярко-синего неонового ободка на кнопке Трекинг при включении"""
       if self.btn_2.isChecked():
           # ЯРКО-СИНИЙ/ГОЛУБОЙ НЕОНОВЫЙ ОБОДОК И ТЕКСТ ПРИ ВКЛЮЧЕНИИ ИИ ТРЕКИНГА
           self.btn_2.setStyleSheet(f"""
               QPushButton {{
                   background-color: #051224;
                   color: #00d2ff;
                   border: 1px solid #00d2ff;
                   border-radius: 6px;
                   font-weight: bold;
               }}
               QPushButton:hover {{
                   background-color: #00d2ff; color: #000000; border-color: #ffffff;
               }}
           """)
       else:
           # Базовый тёмный стиль, когда трекинг выключен
           self.btn_2.setStyleSheet(f"""
               QPushButton {{
                   background-color: {self.btn_bg_color};
                   color: #555e75;
                   border: 1px solid {self.btn_border_color};
                   border-radius: 6px;
                   font-weight: 500;
               }}
               QPushButton:hover {{
                   background-color: #00d2ff; color: #000000; border-color: #ffffff;
               }}
           """)

    def on_toggle_clicked(self, checked):
        """Переключатель логики главного статуса (Вкл/Выкл) с защитой от случайного отключения камеры"""
        # Если пользователь ВКЛЮЧАЕТ видео — запускаем мгновенно и без лишних вопросов!
        if checked:
            self.execute_video_toggle_logic(True)
        else:
            # Если пользователь пытается ВЫКЛЮЧИТЬ — блокируем и запрашиваем подтверждение,
            # чтобы защитить игрока от внезапной потери контроля над системой
            from PyQt6.QtWidgets import QMessageBox
            
            msg = QMessageBox(self)
            msg.setWindowTitle("Предупреждение")
            msg.setText("ВНИМАНИЕ!\n\nВы отключаете ГЛАВНЫЙ видеопоток камеры.\nИИ-трекинг лица полностью остановится.\n\nВы уверены, что хотите выключить камеру?")
            msg.setIcon(QMessageBox.Icon.Warning)
            
            yes_btn = msg.addButton("Да, отключить", QMessageBox.ButtonRole.YesRole)
            no_btn = msg.addButton("Отмена", QMessageBox.ButtonRole.NoRole)
            msg.setDefaultButton(no_btn)
            
            # Стилизуем окно под ваш фирменный неоновый сине-фиолетовый видео-интерфейс
            msg.setStyleSheet("""
                QMessageBox { background-color: #03060f; border: 2px solid #00d2ff; border-radius: 10px; }
                QLabel { color: #ffffff; font-family: 'Segoe UI', sans-serif; font-size: 12px; font-weight: bold; }
                QPushButton { background-color: #071224; color: #00d2ff; border: 1px solid #162e54; border-radius: 4px; padding: 6px 14px; font-weight: bold; min-width: 80px; }
                QPushButton:hover { background-color: #00d2ff; color: black; border-color: white; }
            """)
            
            msg.exec()
            
            if msg.clickedButton() == yes_btn:
                # Осознанное подтверждение выключения видеотрансляции
                self.execute_video_toggle_logic(False)
            else:
                # Отмена: принудительно возвращаем тумблер обратно в нажатое (активное) состояние
                self.toggle_btn.blockSignals(True)
                self.toggle_btn.setChecked(True)
                self.toggle_btn.blockSignals(False)
                self.update_toggle_style()

# modules/video_module.py 6 часть из 6
    def execute_video_toggle_logic(self, checked):
        """Вспомогательный метод для выполнения вашей оригинальной логики переключения видеотрансляции"""
        if checked:
            self.status_value.setText("Включена")
            self.status_value.setStyleSheet(f"color: {styles.COLOR_GREEN}; font-weight: bold; font-size: 11px; background: transparent; border: none; margin-top: 4px;")
            
            # Физически запускаем фоновый поток камеры и системный таймер обновления надписей
            self.camera_thread.start()
            self.ui_fps_timer.start()
            
            # Вывод на экран подключаем ТОЛЬКО если активна кнопка Онлайн
            if self.btn_1.isChecked():
                try:
                    self.camera_thread.frame_received.connect(self.video_img.setPixmap)
                except TypeError:
                    pass
        else:
            self.status_value.setText("Отключено")
            self.status_value.setStyleSheet(f"color: {styles.TEXT_MUTED}; font-size: 11px; background: transparent; border: none; margin-top: 4px;")
            
            # Полностью тушим таймер экрана, сбрасываем буфер и возвращаем дефолтную серую надпись
            self.ui_fps_timer.stop()
            self.current_fps_value = 0
            self.mode_value.setText("в реальном времени")
            self.mode_value.setStyleSheet(f"color: {styles.TEXT_MUTED}; font-size: 13px; background: transparent; border: none; margin-top: 4px;")
            
            # Блокируем сигналы отрисовки кадра
            try:
                self.camera_thread.frame_received.disconnect(self.video_img.setPixmap)
            except TypeError:
                pass
                
            # ПОЛНОСТЬЮ ОСТАНАВЛИВАЕМ камеру аппаратно
            self.camera_thread.stop()
            
            # Возвращаем JPEG-заглушку
            video_pixmap = QPixmap(styles.get_image("video.jpg"))
            if not video_pixmap.isNull():
                self.video_img.setPixmap(video_pixmap.scaled(320, 240, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                
        self.update_toggle_style()
        
        # Сохраняем положение бегунка в файл config.json
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        config["profiles"][current_prof]["video"]["main_toggle"] = checked
        config_manager.save_config(config)

    def update_toggle_style(self):
        """Отрисовка кастомной голубой/темной полоски переключателя строго по вашим размерам"""
        if self.toggle_btn.isChecked():
            self.toggle_btn.setStyleSheet("""
                QPushButton {
                    background-color: #00d2ff;
                    border: 1px solid #00b4d8;
                    border-radius: 10px;
                    text-align: right;
                    padding-right: 0px;
                    color: white;
                    font-size: 34px;
                    font-weight: bold;
                    padding-top: -10px;
                    padding-bottom: 0px;
                }
            """)
            self.toggle_btn.setText("●")
        else:
            self.toggle_btn.setStyleSheet("""
                QPushButton {
                    background-color: #101f38;
                    border: 1px solid #162e54;
                    border-radius: 10px;
                    text-align: left;
                    padding-left: 0px;
                    color: white;
                    font-size: 34px;
                    font-weight: bold;
                    padding-top: -10px;
                    padding-bottom: 0px;
                }
            """)
            self.toggle_btn.setText("●")
