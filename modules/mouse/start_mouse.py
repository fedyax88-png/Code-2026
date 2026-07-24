# modules/mouse/start_mouse.py - СИНХРОНИЗАЦИЯ СКОРОСТЕЙ И ИИ-ОПЕРЕЖЕНИЕ КАДРА (ПОЛНАЯ ИСПРАВЛЕННАЯ ВЕРСИЯ ДЛЯ 4K DPI 200%)
import math
import ctypes

# Низкоуровневые структуры WinAPI для аппаратного управления курсором без двойного ускорения
LONG = ctypes.c_long
DWORD = ctypes.c_ulong
ULONG_PTR = ctypes.POINTER(ctypes.c_ulong)

class POINT(ctypes.Structure):
    _fields_ = [("x", LONG), ("y", LONG)]

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", LONG),
        ("dy", LONG),
        ("mouseData", DWORD),
        ("dwFlags", DWORD),
        ("time", DWORD),
        ("dwExtraInfo", ULONG_PTR)
    ]

class INPUT_UNION(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT)]

class INPUT(ctypes.Structure):
    _fields_ = [("type", DWORD), ("u", INPUT_UNION)]

INPUT_MOUSE = 0
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_VIRTUALDESK = 0x4000  # Стабилизатор координатной сетки под масштабирование Windows 11

class MouseController:
    def __init__(self):
        self.prev_x = None
        self.prev_y = None
        self.dpi_scale = self.get_windows_dpi_scale()
        
        # Получаем истинное физическое разрешение матрицы 4K монитора (3840x2160)
        # Полностью отказываемся от pyautogui.size(), который ломал разметку
        self.screen_width = ctypes.windll.user32.GetSystemMetrics(0)
        self.screen_height = ctypes.windll.user32.GetSystemMetrics(1)
        
        # Задаем виртуальный центр в логических координатах интерфейса PyQt6
        self.virtual_x = float((self.screen_width / self.dpi_scale) // 2)
        self.virtual_y = float((self.screen_height / self.dpi_scale) // 2)
        
        self.sub_x = 0.0
        self.sub_y = 0.0

    def get_windows_dpi_scale(self):
        try:
            hdc = ctypes.windll.user32.GetDC(0)
            LOGPIXELSX = 88
            dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, LOGPIXELSX)
            ctypes.windll.user32.ReleaseDC(0, hdc)
            return dpi / 96.0
        except:
            return 1.0

    def reset(self):
        self.prev_x = None
        self.prev_y = None
        self.virtual_x = float((self.screen_width / self.dpi_scale) // 2)
        self.virtual_y = float((self.screen_height / self.dpi_scale) // 2)
        self.sub_x = 0.0
        self.sub_y = 0.0

    def move(self, current_x, current_y, speed_multiplier=25.0, use_windows_mouse=True, threshold=0.15):
        """Перемещает мышь на аппаратном уровне WinAPI SendInput, убирая микро-прыжки"""
        if self.prev_x is None or self.prev_y is None:
            self.prev_x, self.prev_y = current_x, current_y
            return

        dx = current_x - self.prev_x
        dy = current_y - self.prev_y
        distance = math.hypot(dx, dy)

        current_step_x = 0
        current_step_y = 0

        if distance >= threshold:
            acceleration = math.pow(distance, 1.5) / distance
            move_x = dx * acceleration * speed_multiplier
            move_y = dy * acceleration * speed_multiplier

            if use_windows_mouse:
                self.sub_x += move_x
                self.sub_y += move_y
                current_step_x = int(self.sub_x)
                current_step_y = int(self.sub_y)

                if current_step_x != 0 or current_step_y != 0:
                    # Отправляем один чистый хардверный сдвиг в ядро Windows (работает в 3D играх)
                    extra = ctypes.pointer(ctypes.c_ulong(0))
                    inp = INPUT()
                    inp.type = INPUT_MOUSE
                    inp.u.mi = MOUSEINPUT(current_step_x, current_step_y, 0, MOUSEEVENTF_MOVE | MOUSEEVENTF_VIRTUALDESK, 0, extra)
                    ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))

                self.sub_x -= current_step_x
                self.sub_y -= current_step_y

        # ИИ-ОПЕРЕЖЕНИЕ КАДРА БЕЗ РАССИНХРОНИЗАЦИИ ТУЛБАРА:
        if use_windows_mouse:
            pt = POINT()
            if ctypes.windll.user32.GetCursorPos(ctypes.byref(pt)):
                # Переводим физические пиксели Windows в логическую сетку интерфейса PyQt6
                base_x = float(pt.x / self.dpi_scale)
                base_y = float(pt.y / self.dpi_scale)
                
                # Приводим ИИ-опережение к правильному логическому масштабу оверлея
                self.virtual_x = base_x + (current_step_x / self.dpi_scale)
                self.virtual_y = base_y + (current_step_y / self.dpi_scale)
        else:
            if distance >= threshold:
                self.virtual_x += move_x
                self.virtual_y += move_y
            
            logical_w = float(self.screen_width / self.dpi_scale)
            logical_h = float(self.screen_height / self.dpi_scale)
            self.virtual_x = max(0.0, min(self.virtual_x, logical_w))
            self.virtual_y = max(0.0, min(self.virtual_y, logical_h))

        self.prev_x = current_x
        self.prev_y = current_y

    def apply_physical_move(self):
        pass
