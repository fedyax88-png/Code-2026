# modules/mouse/click_toolbar.py 1 часть из 6
import os
import ctypes
import config_manager
import styles
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QApplication, QFrame
from PyQt6.QtCore import Qt, QTimer, QSize, QPoint
from PyQt6.QtGui import QCursor, QIcon, QPixmap, QPainter, QColor

# Точная Win32 структура для SHAppBarMessage из shell32.dll
class APPBARDATA(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.c_ulong),
        ("hWnd", ctypes.c_void_p),
        ("uCallbackMessage", ctypes.c_uint),
        ("uEdge", ctypes.c_uint),
        ("rc", ctypes.wintypes.RECT),
        ("lParam", ctypes.c_long)
    ]

class ClickTypeToolbar(QWidget):
    def __init__(self, main_window_ref):
        super().__init__()
        self.main_win = main_window_ref
        
        # Переменные ИИ-автоскрытия и таймеров по ТЗ
        self.is_expanded = True
        self.idle_counter = 0  # Счетчик тактов по 100мс для исчезновения
        
        # СТРОГО ПО ТЗ EV IACAM: На старте всегда Левый залоченный клик!
        self.main_win.dwell_clicker.force_reset_to_default_left()
        
        # ЖЕСТКАЯ СВЯЗКА: Передаем ссылку на себя в движок кликов для мгновенного тушения фона
        self.main_win.dwell_clicker.toolbar_ref = self
        
        # Настройка флагов окна: без рамок, поверх всего, Tool-окно без забора фокуса Windows
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        
        # Считываем конфигурацию
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        self.mouse_data = config["profiles"][current_prof]["mouse"]
        
        # Размеры кнопок панели
        self.btn_size = 42  
        self.panel_long_dim = (self.btn_size + 4) * 8 + 30  
        self.panel_short_dim = self.btn_size + 8            
        
        screen = QApplication.primaryScreen().geometry()
        saved_x = self.mouse_data.get("toolbar_anchor_x", -1)
        saved_y = self.mouse_data.get("toolbar_anchor_y", 0)
        
        # Дефолтная посадка — Правый край экрана по вашему запросу
        if saved_x == -1:
            saved_x = screen.width() - self.panel_short_dim
            saved_y = (screen.height() - self.panel_long_dim) // 2
            
        self.is_vertical = self.determine_orientation(saved_x, saved_y, screen.width(), screen.height())
        
        # Светлый серо-зеленый контейнер-фон карточки тулбара из вашего ТЗ
        self.bg_frame = QFrame(self)
        self.bg_frame.setObjectName("ToolbarBG")
        self.bg_frame.setStyleSheet("""
            QFrame#ToolbarBG {
                background-color: rgba(25, 45, 30, 0.95);
                border: 1px solid #2ed573;
                border-radius: 6px;
            }
        """)
        
        if self.is_vertical:
            self.resize(self.panel_short_dim, self.panel_long_dim)
            self.bg_frame.setGeometry(0, 0, self.panel_short_dim, self.panel_long_dim)
            self.main_box_layout = QVBoxLayout(self.bg_frame)
            self.main_box_layout.setContentsMargins(4, 15, 4, 15)
        else:
            self.resize(self.panel_long_dim, self.panel_short_dim)
            self.bg_frame.setGeometry(0, 0, self.panel_long_dim, self.panel_short_dim)
            self.main_box_layout = QHBoxLayout(self.bg_frame)
            self.main_box_layout.setContentsMargins(15, 4, 15, 4)
            
        self.main_box_layout.setSpacing(4)
        self.move(saved_x, saved_y)
        
        # ПО ТЗ: СОЗДАЕМ ТРИГГЕР-ПРЯМОУГОЛЬНИК ВМЕСТО СТАРОГО КРУГЛЯШКА
        self.trigger_dot = QWidget()
        self.trigger_dot.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.trigger_dot.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        
        # Кнопка внутри прямоугольника (Её размеры и геометрия теперь полностью динамические)
        self.dot_btn = QPushButton(self.trigger_dot)
        
        # Первичный расчет размеров прямоугольника по JSON уставкам (длина, ширина, скругления)
        self.update_trigger_geometry_live()
        
        # Включаем Win32 AppBar бронирование места на экране
        self.register_windows_appbar(saved_x, saved_y, screen.width(), screen.height())
        
        self.drag_position = None
        self.modes = ["pause", "left", "middle", "right", "drag", "double", "keyboard_1", "magnifier"]
        self.buttons = {}
        
        # Кешируем базовые картинки иконок и замочка в память ОДИН РАЗ при старте
        self.base_pixmaps = {}
        for mode in self.modes:
            px = QPixmap(styles.get_image(f"{mode}.png"))
            self.base_pixmaps[mode] = px if not px.isNull() else None
            
        self.lock_pixmap = QPixmap(styles.get_image("lock.png"))
        if self.lock_pixmap.isNull():
            self.lock_pixmap = None
        
        for mode in self.modes:
            btn = QPushButton(self.bg_frame)
            btn.setFixedSize(self.btn_size, self.btn_size)
            btn.clicked.connect(lambda checked, m=mode: self.handle_single_click(m))
            self.main_box_layout.addWidget(btn)
            self.buttons[mode] = btn
            
        # Запуск первичных политик прозрачности и скрытия
        self.apply_opacity_sync_logic()
        self.refresh_all_button_images()
        
        # Высокоскоростной ИИ-таймер скрытия/раскрытия и синхронизации (Каждые 100 мс)
        self.sync_timer = QTimer(self)
        self.sync_timer.timeout.connect(self.monitor_mouse_and_sync)
        self.sync_timer.start(100)

# modules/mouse/click_toolbar.py - ЧАСТЬ 2 ИЗ 6 (ПОЛНОЕ ИСПРАВЛЕНИЕ ОРИЕНТАЦИИ И ВЕРТИКАЛЬНОЙ ПАЛКИ ДЛЯ ВЕРХНЕЙ СТОРОНЫ)
    def register_windows_appbar(self, x, y, scr_w, scr_h):
        """Аппаратно вырезает место на экране Windows, переводя логику 4K в физические пиксели"""
        try:
            hwnd = int(self.winId())
            abd = APPBARDATA()
            abd.cbSize = ctypes.sizeof(APPBARDATA)
            abd.hWnd = hwnd

            # Вычисляем системный DPI масштаб для точного перевода геометрии в пиксели Win32
            try:
                hdc = ctypes.windll.user32.GetDC(0)
                dpi_scale = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88) / 96.0  # 88 - LOGPIXELSX
                ctypes.windll.user32.ReleaseDC(0, hdc)
            except:
                dpi_scale = 2.0  # Дефолт для ваших 200%

            # Переводим логические размеры тулбара и экрана в реальные физические пиксели матрицы
            phys_panel_short = int(self.panel_short_dim * dpi_scale)
            phys_panel_long = int(self.panel_long_dim * dpi_scale)
            
            # Извлекаем честное физическое разрешение монитора из WinAPI (3840x2160)
            phys_scr_w = ctypes.windll.user32.GetSystemMetrics(0)
            phys_scr_h = ctypes.windll.user32.GetSystemMetrics(1)
            
            phys_x = int(x * dpi_scale)

            if self.is_vertical:
                abd.uEdge = 2 if x > (scr_w // 2) else 0  # 2 = ABE_RIGHT, 0 = ABE_LEFT
                abd.rc.left = phys_scr_w - phys_panel_short if abd.uEdge == 2 else 0
                abd.rc.right = phys_scr_w if abd.uEdge == 2 else phys_panel_short
                abd.rc.top = 0
                abd.rc.bottom = phys_scr_h
            else:
                abd.uEdge = 3  # 3 = ABE_TOP
                abd.rc.left = phys_x
                abd.rc.right = phys_x + phys_panel_long
                abd.rc.top = 0
                abd.rc.bottom = phys_panel_short

            # Передаем ядру Windows чистые физические координаты — рабочий стол сдвинется идеально ровно
            ctypes.windll.shell32.SHAppBarMessage(0, ctypes.byref(abd))  # ABM_NEW
            ctypes.windll.shell32.SHAppBarMessage(1, ctypes.byref(abd))  # ABM_QUERYPOS
            ctypes.windll.shell32.SHAppBarMessage(2, ctypes.byref(abd))  # ABM_SETPOS
        except Exception as e:
            print(f"Ошибка регистрации AppBar: {e}")

    def unregister_windows_appbar(self):
        """Освобождает зарезервированное место на экране и возвращает рабочий стол назад через shell32"""
        try:
            hwnd = int(self.winId())
            abd = APPBARDATA()
            abd.cbSize = ctypes.sizeof(APPBARDATA)
            abd.hWnd = hwnd
            ctypes.windll.shell32.SHAppBarMessage(1, ctypes.byref(abd))  # ABM_REMOVE
        except Exception:
            pass

    def determine_orientation(self, x, y, scr_w, scr_h):
        """Определяет ориентацию: ЖЁСТКИЙ ФИКС — если панель стоит вверху экрана (y==0), она ВСЕГДА горизонтальная"""
        if y == 0:
            return False  # False означает ГОРИЗОНТАЛЬНЫЙ тулбар, прижатый к верху
            
        # Для левой и правой сторон оставляем оригинальную заводскую проверку координат x
        if x < 120 or x > (scr_w - self.panel_long_dim - 120):
            return True   # True означает ВЕРТИКАЛЬНЫЙ тулбар
        return False

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position:
            new_pos = event.globalPosition().toPoint() - self.drag_position
            self.move(new_pos)
            if not self.is_expanded:
                self.trigger_dot.move(new_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = None
            x, y = self.x(), self.y()
            screen = QApplication.primaryScreen().geometry()
            new_orientation = self.determine_orientation(x, y, screen.width(), screen.height())
            config = config_manager.load_config()
            current_prof = config.get("current_profile", "Default Profile")
            mouse_conf = config["profiles"][current_prof]["mouse"]
            mouse_conf["toolbar_anchor_x"] = x
            mouse_conf["toolbar_anchor_y"] = y
            config_manager.save_config(config)
            self.unregister_windows_appbar()
            if new_orientation != self.is_vertical:
                self.is_vertical = new_orientation
                self.main_win.mod_mouse.hot_rebuild_toolbar_geometry()
            else:
                if self.is_expanded:
                    self.register_windows_appbar(x, y, screen.width(), screen.height())
            event.accept()


# modules/mouse/click_toolbar.py 3 часть из 6
    def closeEvent(self, event):
        # Останавливаем таймер перед закрытием, чтобы он больше не дергал функции геометрии
        if hasattr(self, 'sync_timer') and self.sync_timer:
            self.sync_timer.stop()
            
        self.unregister_windows_appbar()
        
        if hasattr(self, 'trigger_dot') and self.trigger_dot:
            self.trigger_dot.close()
            
        super().closeEvent(event)


    def handle_single_click(self, click_mode):
        """ЭТАЛОННЫЙ ЦИКЛИЧЕСКИЙ ПЕРЕКЛЮЧАТЕЛЬ EV IACAM (Защита от бардака и ложных замков)"""
        import subprocess
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        is_click_enabled = config["profiles"][current_prof]["mouse"].get("click_mode", True)

        if not is_click_enabled and click_mode != "pause":
            return

        self.idle_counter = 0  # Сброс таймера простоя

        if click_mode == "pause":
            config["profiles"][current_prof]["mouse"]["click_mode"] = not is_click_enabled
            config_manager.save_config(config)
            if not is_click_enabled:
                self.main_win.dwell_clicker.force_reset_to_default_left()
            self.main_win.mod_mouse.update_click_buttons_from_json()
            
        elif click_mode == "keyboard_1":
            try:
                subprocess.Popen("cmd /c start osk.exe", shell=True)
            except Exception:
                pass
            self.main_win.dwell_clicker.click_type = self.main_win.dwell_clicker.locked_default_mode
            self.main_win.dwell_clicker.is_permanent = True
            
        elif click_mode == "magnifier":
            try:
                hwnd = ctypes.windll.user32.FindWindowW("ScreenMagnifierWindow", None)
                if hwnd:
                    ctypes.windll.user32.ShowWindow(hwnd, 9)
                    ctypes.windll.user32.SetForegroundWindow(hwnd)
                else:
                    subprocess.Popen("cmd /c start magnify.exe", shell=True)
            except Exception:
                try:
                    subprocess.Popen("cmd /c start magnify.exe", shell=True)
                except Exception:
                    pass
            self.main_win.dwell_clicker.click_type = self.main_win.dwell_clicker.locked_default_mode
            self.main_win.dwell_clicker.is_permanent = True
            
        else:
            current_active = self.main_win.dwell_clicker.click_type
            current_locked = self.main_win.dwell_clicker.locked_default_mode
            is_perm = self.main_win.dwell_clicker.is_permanent

            if click_mode == current_active:
                if is_perm:
                    self.main_win.dwell_clicker.force_reset_to_default_left()
                else:
                    self.main_win.dwell_clicker.locked_default_mode = click_mode
                    self.main_win.dwell_clicker.is_permanent = True
            else:
                self.main_win.dwell_clicker.click_type = click_mode
                self.main_win.dwell_clicker.is_permanent = False
            
        self.refresh_all_button_images()

# modules/mouse/click_toolbar.py 4 часть из 6
    def refresh_all_button_images(self):
        """МАТРИЦА СЛОЕВ: Динамическое послойное рисование пирога иконок без чтения диска"""
        current_type = self.main_win.dwell_clicker.click_type
        default_locked_type = self.main_win.dwell_clicker.locked_default_mode
        is_permanently_locked = self.main_win.dwell_clicker.is_permanent
        
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        is_click_enabled = config["profiles"][current_prof]["mouse"].get("click_mode", True)

        for mode, btn in self.buttons.items():
            bg_color = "transparent"
            border_style = "none"

            if not is_click_enabled:
                if mode == "pause":
                    bg_color = "#ff4d4d"  
                    border_style = "1px solid #ffffff"
                else:
                    bg_color = "rgba(40, 45, 50, 0.6)"  
            else:
                if mode == "pause":
                    bg_color = "transparent"
                elif mode in ["keyboard_1", "magnifier"]:
                    if current_type == mode:
                        bg_color = "#00d2ff"
                        border_style = "1px solid #ffffff"
                else:
                    if current_type == mode:
                        bg_color = "#00d2ff"
                        border_style = "1px solid #ffffff"

                        # Мгновенно применяем пирог стилей к кнопке на уровне оперативной памяти
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg_color};
                    border: {border_style};
                    border-radius: 4px;
                    padding: 0px;
                }}
                /* ЖЕСТКИЙ ФИКС Е V I A C A M ДЛЯ ХОРОШЕЙ ВИДИМОСТИ ПРИ НАВЕДЕНИИ:
                   Когда мышь/взгляд зависают над кнопкой, включается сочный светло-салатовый неоновый фон */
                QPushButton:hover {{
                    background-color: rgba(175, 250, 250, 0.95); /* Светло-салатовый полупрозрачный блик */
                    border: 1px solid #2ed573;                 /* Яркая неоновая салатовая рамка */
                    border-radius: 4px;
                }}
            """)


            base_px = self.base_pixmaps.get(mode)
            if base_px and not base_px.isNull():
                canvas = QPixmap(base_px.size())
                canvas.fill(Qt.GlobalColor.transparent)
                
                painter = QPainter(canvas)
                painter.drawPixmap(0, 0, base_px)
                
                if is_click_enabled and mode not in ["pause", "keyboard_1", "magnifier"]:
                    if mode == default_locked_type and is_permanently_locked:
                        if self.lock_pixmap and not self.lock_pixmap.isNull():
                            painter.drawPixmap(0, 0, self.lock_pixmap.scaled(base_px.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                
                painter.end()
                btn.setIcon(QIcon(canvas))
                btn.setIconSize(QSize(self.btn_size - 10, self.btn_size - 10))
            else:
                btn.setText(mode[:3])

    def apply_opacity_sync_logic(self):
        """Задает прозрачность по ползунку от 10% до 100%"""
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        mouse_conf = config["profiles"][current_prof]["mouse"]
        
        if mouse_conf.get("toolbar_opacity_enabled", False):
            op_percent = mouse_conf.get("toolbar_opacity_value", 80)
            alpha = op_percent / 100.0
            self.setWindowOpacity(alpha)
            self.trigger_dot.setWindowOpacity(alpha)
        else:
            self.setWindowOpacity(1.0)
            self.trigger_dot.setWindowOpacity(0.8)

# modules/mouse/click_toolbar.py - ЗАМЕНА МЕТОДА ИЗ ЧАСТИ 5 ИЗ 6 (ПОЛНАЯ ВЕРСИЯ С МЕТОДАМИ GEOMETRY И EXPAND)
    def update_trigger_geometry_live(self):
        """ПО ТЗ: Пересчитывает длину, толщину (ширину) и скругления ПРЯМОУГОЛЬНИКА на лету"""
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        mouse_conf = config["profiles"][current_prof]["mouse"]
        trig_len = mouse_conf.get("toolbar_trigger_length", 60)
        thickness = mouse_conf.get("toolbar_trigger_width", 6)  # Новая динамическая толщина полоски
        if self.is_vertical:
            self.trigger_dot.setFixedSize(thickness, trig_len)
            self.dot_btn.setGeometry(0, 0, thickness, trig_len)
        else:
            self.trigger_dot.setFixedSize(trig_len, thickness)
            self.dot_btn.setGeometry(0, 0, trig_len, thickness)
        self.dot_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #2ed573;
                border: none;
                border-radius: 2px;
            }}
            QPushButton:hover {{
                background-color: #00d2ff;
            }}
        """)
        if not self.is_expanded:
            self.collapse_toolbar_panel()

    def update_hide_policy_from_json(self):
        """Обновляет политики скрытия панели на лету при изменении конфигурации JSON"""
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        self.mouse_data = config["profiles"][current_prof]["mouse"]
        self.idle_counter = 0
        self.expand_toolbar_panel()

    def expand_toolbar_panel(self):
        """Аппаратно разворачивает скрытую ИИ-панель ровно в той позиции, где находился триггер (Исправлено для 4K)"""
        if not self.is_expanded:
            config = config_manager.load_config()
            current_prof = config.get("current_profile", "Default Profile")
            mouse_conf = config["profiles"][current_prof]["mouse"]
            
            saved_x = mouse_conf.get("toolbar_anchor_x", 0)
            saved_y = mouse_conf.get("toolbar_anchor_y", 0)
            pos_idx = mouse_conf.get("toolbar_trigger_position_idx", 1)  # 0=Низ/Лево, 1=Центр, 2=Верх/Право
            
            # Получаем чистую логическую геометрию экрана для правильного позиционирования PyQt6
            screen = QApplication.primaryScreen().geometry()
            
            # Сначала скрываем прямоугольный триггер
            self.trigger_dot.hide()
            
            # Все расчеты проводим в логическом пространстве без накопления ошибок округления
            if self.is_vertical:
                # Фиксируем X кромки (Правый или Левый край монитора)
                target_x = screen.width() - self.panel_short_dim if saved_x > (screen.width() // 2) else 0
                
                # Рассчитываем Y координату тулбара строго по позиции триггера
                if pos_idx == 0:
                    target_y = screen.height() - self.panel_long_dim - 10
                elif pos_idx == 2:
                    target_y = 10
                else:
                    target_y = (screen.height() - self.panel_long_dim) // 2
            else:
                # Если панель горизонтальная вверху экрана
                target_y = 0
                
                # Рассчитываем X координату тулбара строго по позиции триггера
                if pos_idx == 0:
                    target_x = 10
                elif pos_idx == 2:
                    target_x = screen.width() - self.panel_long_dim - 10
                else:
                    target_x = (screen.width() - self.panel_long_dim) // 2
            
            # Записываем вычисленные логические координаты обратно в память
            mouse_conf["toolbar_anchor_x"] = target_x
            mouse_conf["toolbar_anchor_y"] = target_y
            
            # Вызываем AppBar (он сам внутри переведет логику в физические пиксели 4K матрицы)
            self.register_windows_appbar(target_x, target_y, screen.width(), screen.height())
            
            # Изменяем размер и перемещаем Qt окно в логических координатах интерфейса
            if self.is_vertical:
                self.resize(self.panel_short_dim, self.panel_long_dim)
            else:
                self.resize(self.panel_long_dim, self.panel_short_dim)
                
            self.move(target_x, target_y)
            self.show()
            self.is_expanded = True
            self.idle_counter = 0


# modules/mouse/click_toolbar.py - ЧАСТЬ 6 ИЗ 6 (УЛЬТРА-ОПТИМИЗИРОВАННАЯ ХАРДВЕРНАЯ ВЕРСИЯ БЕЗ НАГРУЗКИ НА ДИСК)
    def collapse_toolbar_panel(self):
        """Аппаратно сворачивает панель в прямоугольную полоску с учетом позиций 1, 2, 3 (Исправлено для 4K)"""
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        mouse_conf = config["profiles"][current_prof]["mouse"]
        
        saved_x = mouse_conf.get("toolbar_anchor_x", 0)
        saved_y = mouse_conf.get("toolbar_anchor_y", 0)
        trig_len = mouse_conf.get("toolbar_trigger_length", 60)
        thickness = mouse_conf.get("toolbar_trigger_width", 6)
        pos_idx = mouse_conf.get("toolbar_trigger_position_idx", 1)
        
        # Получаем чистую логическую геометрию экрана для PyQt6
        screen = QApplication.primaryScreen().geometry()
        
        if self.is_expanded:
            self.unregister_windows_appbar()
            self.hide()
            
        # Математика позиционирования прямоугольного триггера в логических координатах
        if self.is_vertical:
            dot_x = screen.width() - thickness if saved_x > (screen.width() // 2) else 0
            if pos_idx == 0:
                dot_y = screen.height() - trig_len - 10
            elif pos_idx == 2:
                dot_y = 10
            else:
                dot_y = saved_y + (self.panel_long_dim - trig_len) // 2
        else:
            dot_y = 0
            if pos_idx == 0:
                dot_x = 10
            elif pos_idx == 2:
                dot_x = screen.width() - trig_len - 10
            else:
                dot_x = saved_x + (self.panel_long_dim - trig_len) // 2
                
        self.trigger_dot.move(dot_x, dot_y)
        self.trigger_dot.show()
        self.is_expanded = False

    def monitor_mouse_and_sync(self):
        """Высокоскоростной мониторинг мыши (Полная синхронизация без лишнего дискового чтения)"""
        # 🔥 ВЫСШАЯ ОПТИМИЗАЦИЯ ТАЙМЕРА: Если открыта Advanced-панель макросов — тулбар мгновенно 
        # уходит в глубокий сон через чистый return, вообще не забивая ЦП дисковыми операциями!
        if hasattr(self.main_win, 'advanced_panel_window') and self.main_win.advanced_panel_window and self.main_win.advanced_panel_window.isVisible():
            if hasattr(self, 'trigger_dot') and self.trigger_dot:
                self.trigger_dot.hide()
            return

        # Метод прозрачности читает диск, но теперь он вызывается ТОЛЬКО когда панель макросов закрыта
        self.apply_opacity_sync_logic()
        
        config = config_manager.load_config()
        current_prof = config.get("current_profile", "Default Profile")
        mouse_conf = config["profiles"][current_prof]["mouse"]
        
        auto_hide_enabled = mouse_conf.get("toolbar_auto_hide", True)
        hide_delay_sec = mouse_conf.get("toolbar_hide_delay_sec", 5)
        max_idle_ticks = hide_delay_sec * 10
        
        # Получаем текущие логические координаты курсора
        pos = QCursor.pos()
        
        if self.is_expanded:
            is_mouse_inside = self.geometry().contains(pos)
            if is_mouse_inside:
                self.idle_counter = 0
            else:
                if auto_hide_enabled:
                    self.idle_counter += 1
                    if self.idle_counter >= max_idle_ticks:
                        self.collapse_toolbar_panel()
        else:
            if self.trigger_dot.geometry().contains(pos):
                self.expand_toolbar_panel()
