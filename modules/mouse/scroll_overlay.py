# modules/mouse/scroll_overlay.py
import sys
import ctypes
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QRectF, QPoint
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush

class ScrollJoystickOverlay(QWidget):
    def __init__(self, advanced_clicker_ref=None):
        super().__init__()
        self.clicker_ref = advanced_clicker_ref
        
        # ЖЕСТКИЙ ФИКС ДЛЯ 4K: Отключаем автоматический пересчет геометрии окон операционной системой,
        # чтобы Windows не сдвигала координаты move() в противоположные углы экрана при 200% масштабе.
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool |
            Qt.WindowType.WindowTransparentForInput
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        
        # Запрашиваем точный масштаб системы Windows (200% = 2.0)
        self.dpi_scale = self.get_windows_dpi_scale()
        
        # Задаем фиксированные размеры оверлея (400 пикселей в высоту, 60 в ширину)
        self.panel_width = 60
        self.panel_height = 400
        self.setFixedSize(self.panel_width, self.panel_height)
        
        # Координаты центра спавна
        self.center_screen_x = 0
        self.center_screen_y = 0
        self.yellow_circle_radius = 20

    def get_windows_dpi_scale(self):
        """Прямой Win32-запрос к ОС Windows: узнаем реальный масштаб High DPI экрана"""
        try:
            hdc = ctypes.windll.user32.GetDC(0)
            LOGPIXELSX = 88
            dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, LOGPIXELSX)
            ctypes.windll.user32.ReleaseDC(0, hdc)
            return dpi / 96.0
        except:
            return 1.0
    def activate_joystick_at(self, start_x, start_y):
        """4K High-DPI ЦЕНТРИРОВАНИЕ: Корректирует координаты с учетом масштаба 200%"""
        self.center_screen_x = start_x
        self.center_screen_y = start_y
        
        # Вычисляем логический центр окна с учетом DPI, чтобы убрать улет полосы в другой угол
        pos_x = int(start_x - (self.panel_width / 2))
        pos_y = int(start_y - (self.panel_height / 2))
        
        # Если в Windows стоит 200%, принудительно делим геометрию на масштаб
        # Это заставит Qt приземлить центр желтого круга ровно под курсор мыши
        if self.dpi_scale > 1.0:
            pos_x = int(pos_x / self.dpi_scale)
            pos_y = int(pos_y / self.dpi_scale)
            
        self.move(pos_x, pos_y)
        self.show()
        self.update()

    def paintEvent(self, event):
        """Рендеринг полупрозрачной полосы и желтого круга"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        cx = self.panel_width / 2.0
        cy = self.panel_height / 2.0

        # 1. СИНЯЯ ПОЛОСА
        painter.setPen(QPen(QColor(0, 0, 0, 50), 1.5))
        painter.setBrush(QBrush(QColor(135, 206, 235, 130)))
        painter.drawRect(QRectF(0, 0, self.panel_width, self.panel_height))

        # 2. ЖЕЛТЫЙ КРУГ
        painter.setPen(QPen(QColor(0, 0, 0, 200), 1.5))
        painter.setBrush(QBrush(QColor(255, 255, 0, 230)))
        painter.drawEllipse(QPoint(int(cx), int(cy)), self.yellow_circle_radius, self.yellow_circle_radius)

        # 3. ОТМЕТКИ СКОРОСТЕЙ
        painter.setPen(QPen(QColor(0, 0, 0, 180), 2))
        offsets = [45, 100, 160]
        
        for offset in offsets:
            painter.drawLine(int(cx - 15), int(cy - offset), int(cx + 15), int(cy - offset))
            painter.drawLine(int(cx - 15), int(cy + offset), int(cx + 15), int(cy + offset))

        painter.end()
    def calculate_speed_and_direction(self, global_mouse_x, global_mouse_y):
        """ЖЕСТКИЙ ИИ-ФИКС ДЛЯ 4K: Считает скорости и боковой выход в единой логической системе координат"""
        
        # Получаем чистое смещение курсора ИИ относительно центра спавна в логических пикселях Windows
        local_x = global_mouse_x - self.center_screen_x
        local_y = global_mouse_y - self.center_screen_y
        
        # УВЕЛИЧИВАЕМ ЗАЗОР ДЛЯ БОКОВОГО ВЫХОДА ДО 120 ПИКСЕЛЕЙ (Защита от микро-колебаний головы)
        # Теперь полоса не закроется случайно, если вы ведете голову строго вверх или вниз
        if abs(local_x) > (self.panel_width / 2.0 + 120):
            return "trigger_stop", 0
            
        # ПРОВЕРКА ВЕРТИКАЛЬНОГО ВЫХОДА ЗА ПРЕДЕЛЫ ПОЛОСЫ ВЫСОТОЙ 400px
        if abs(local_y) > (self.panel_height / 2.0 + 40):
            return "trigger_stop", 0

        abs_dy = abs(local_y)
        direction = "up" if local_y < 0 else "down"

        # Идеальное распределение 3-х скоростей скроллинга внутри полосы высотой 400 пикселей (200px вверх и 200px вниз)
        if abs_dy <= self.yellow_circle_radius + 15:
            return "neutral", 0 # Мертвая зона внутри жёлтого круга покоя
        elif abs_dy <= 75:
            return direction, 1 # Зона скорости 1 (Медленный шаг)
        elif abs_dy <= 140:
            return direction, 2 # Зона скорости 2 (Средний шаг)
        else:
            return direction, 3 # Зона скорости 3 (Максимальный шаг)
