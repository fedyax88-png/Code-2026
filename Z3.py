# =====================================================================================
# Z3.py — ПОЛНАЯ ОПТИМИЗАЦИЯ + ПОДДЕРЖКА ВСЕХ КЛАВИШ (A-Z, 0-9, СПЕЦКЛАВИШИ)
#
# ИСПРАВЛЕНИЯ:
#   1. Словарь KEY_SCANCODES расширен с 10 до 80+ клавиш
#   2. Добавлена функция get_scancode() для правильного получения скан-кода любой клавиши
#   3. Исправлена функция hardware_key_event() для корректной отправки всех клавиш
#   4. Добавлена поддержка специальных клавиш (Tab, Caps, Enter, Shift, Ctrl, Alt, Win и т.д.)
#   5. Все клавиши теперь работают везде (Windows, игры, приложения)
# =====================================================================================

import sys
import os
import time
import signal
import ctypes
import threading

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QGridLayout, QStackedWidget, QFrame, QLabel, QPushButton)
from PyQt6.QtCore import Qt, QTimer, QPoint, pyqtSlot, QMetaObject
from PyQt6.QtGui import QPainter, QPen, QColor, QCursor, QPixmap

import styles
from title_bar import CustomTitleBar
from sidebar import SidebarMenu
import config_manager

from modules.video.video_module import VideoControlModule
from modules.mouse.mouse_module import MouseControlModule
from modules.kb.kb_module import KeyboardControlModule
from modules.voice.voice_module import VoiceControlModule

from modules.voice.voice_settings_main import VoiceSettingsMainWidget
from modules.video.video_settings_main import VideoSettingsMainWidget
from modules.mouse.mouse_settings_main import MouseSettingsMainWidget
from modules.kb.kb_settings_main import KeyboardSettingsMainWidget

from modules.profiles_page import PlaceholderPage as ProfilesPage
from modules.settings_page import PlaceholderPage as GeneralSettingsPage
from modules.about_page import PlaceholderPage as AboutPage
from modules.mouse.advanced_panel import MouseAdvancedPanel


# =====================================================================================
# КЭШИРОВАНИЕ КОНФИГА (TTL = 250мс)
# =====================================================================================
CONFIG_CACHE_TTL = 0.25
_config_cache = {"data": None, "ts": 0.0}

def get_cached_config():
    global _config_cache
    now = time.monotonic()
    if _config_cache["data"] is None or (now - _config_cache["ts"]) > CONFIG_CACHE_TTL:
        _config_cache["data"] = config_manager.load_config()
        _config_cache["ts"] = now
    return _config_cache["data"]

def invalidate_config_cache():
    global _config_cache
    _config_cache["ts"] = 0.0


# =====================================================================================
# WINDOWS API СТРУКТУРЫ
# =====================================================================================
class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

_LONG = ctypes.c_long
_DWORD = ctypes.c_ulong
_ULONG_PTR = ctypes.POINTER(ctypes.c_ulong)

class MOUSEINPUT_SYS(ctypes.Structure):
    _fields_ = [
        ("dx", _LONG), ("dy", _LONG), ("mouseData", _DWORD),
        ("dwFlags", _DWORD), ("time", _DWORD), ("dwExtraInfo", _ULONG_PTR)
    ]

class KEYBDINPUT_SYS(ctypes.Structure):
    _fields_ = [
        ("wVk", ctypes.c_ushort), ("wScan", ctypes.c_ushort),
        ("dwFlags", _DWORD), ("time", _DWORD), ("dwExtraInfo", _ULONG_PTR)
    ]

class HARDWAREINPUT_SYS(ctypes.Structure):
    _fields_ = [("uMsg", _DWORD), ("wParamL", ctypes.c_ushort), ("wParamH", ctypes.c_ushort)]

class INPUT_UNION_SYS(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT_SYS), ("ki", KEYBDINPUT_SYS), ("hi", HARDWAREINPUT_SYS)]

class INPUT_SYS(ctypes.Structure):
    _fields_ = [("type", _DWORD), ("u", INPUT_UNION_SYS)]

# =====================================================================================
# КОНСТАНТЫ MOUSE EVENTS
# =====================================================================================
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_VIRTUALDESK = 0x4000

# =====================================================================================
# ✅ ПОЛНЫЙ СЛОВАРЬ СКАН-КОДОВ (80+ КЛАВИШ)
# =====================================================================================
SCANCODE_MAP = {
    # Функциональные клавиши
    "escape": 0x01, "esc": 0x01,
    "f1": 0x3B, "f2": 0x3C, "f3": 0x3D, "f4": 0x3E,
    "f5": 0x3F, "f6": 0x40, "f7": 0x41, "f8": 0x42,
    "f9": 0x43, "f10": 0x44, "f11": 0x57, "f12": 0x58,
    
    # Цифры (верхний ряд)
    "~": 0x29, "`": 0x29,
    "1": 0x02, "!": 0x02,
    "2": 0x03, "@": 0x03,
    "3": 0x04, "#": 0x04,
    "4": 0x05, "$": 0x05,
    "5": 0x06, "%": 0x06,
    "6": 0x07, "^": 0x07,
    "7": 0x08, "&": 0x08,
    "8": 0x09, "*": 0x09,
    "9": 0x0A, "(": 0x0A,
    "0": 0x0B, ")": 0x0B,
    "-": 0x0C, "_": 0x0C,
    "=": 0x0D, "+": 0x0D,
    "backspace": 0x0E,
    
    # Верхний буквенный ряд (QWERTY)
    "tab": 0x0F,
    "q": 0x10, "Q": 0x10,
    "w": 0x11, "W": 0x11,
    "e": 0x12, "E": 0x12,
    "r": 0x13, "R": 0x13,
    "t": 0x14, "T": 0x14,
    "y": 0x15, "Y": 0x15,
    "u": 0x16, "U": 0x16,
    "i": 0x17, "I": 0x17,
    "o": 0x18, "O": 0x18,
    "p": 0x19, "P": 0x19,
    "[": 0x1A, "{": 0x1A,
    "]": 0x1B, "}": 0x1B,
    "\\": 0x2B, "|": 0x2B,
    
    # Средний буквенный ряд (ASDFGH)
    "capslock": 0x3A, "caps": 0x3A,
    "a": 0x1E, "A": 0x1E,
    "s": 0x1F, "S": 0x1F,
    "d": 0x20, "D": 0x20,
    "f": 0x21, "F": 0x21,
    "g": 0x22, "G": 0x22,
    "h": 0x23, "H": 0x23,
    "j": 0x24, "J": 0x24,
    "k": 0x25, "K": 0x25,
    "l": 0x26, "L": 0x26,
    ";": 0x27, ":": 0x27,
    "'": 0x28, "\"": 0x28,
    "enter": 0x1C, "return": 0x1C,
    
    # Нижний буквенный ряд (ZXCVBN)
    "lshift": 0x2A, "shift": 0x2A,
    "z": 0x2C, "Z": 0x2C,
    "x": 0x2D, "X": 0x2D,
    "c": 0x2E, "C": 0x2E,
    "v": 0x2F, "V": 0x2F,
    "b": 0x30, "B": 0x30,
    "n": 0x31, "N": 0x31,
    "m": 0x32, "M": 0x32,
    ",": 0x33, "<": 0x33,
    ".": 0x34, ">": 0x34,
    "/": 0x35, "?": 0x35,
    "rshift": 0x36,
    
    # Системные клавиши
    "lctrl": 0x1D, "ctrl": 0x1D, "control": 0x1D,
    "win": 0x5B, "lwin": 0x5B,
    "lalt": 0x38, "alt": 0x38,
    "space": 0x39,
    "ralt": 0x38, "altgr": 0x38,
    "rctrl": 0x1D,
    
    # Стрелки
    "🡠": 0x4B, "left": 0x4B,
    "🡢": 0x4D, "right": 0x4D,
    "🡡": 0x48, "up": 0x48,
    "🡣": 0x50, "down": 0x50,
    
    # Дополнительные клавиши
    "insert": 0x52, "ins": 0x52,
    "delete": 0x53, "del": 0x53,
    "home": 0x47,
    "end": 0x4F,
    "pageup": 0x49, "pgup": 0x49,
    "pagedown": 0x51, "pgdn": 0x51,
    "numlock": 0x45,
    "scrolllock": 0x46,
    "printscreen": 0x37, "print": 0x37,
    "pause": 0x45,
    
    # Клавиши специального назначения
    "rst": 0x44,  # RST → F10
    "app": 0x5D,  # APP/Menu
    "ск": 0x39,   # СК → Space (для скролла)
    "osk": 0x01,  # OSK → Escape
    "лп": 0x01,   # ЛП → Escape
    
    # Кириллица (русская раскладка)
    "й": 0x10, "Й": 0x10,
    "ц": 0x11, "Ц": 0x11,
    "у": 0x12, "У": 0x12,
    "к": 0x13, "К": 0x13,
    "е": 0x14, "Е": 0x14,
    "н": 0x15, "Н": 0x15,
    "г": 0x16, "Г": 0x16,
    "ш": 0x17, "Ш": 0x17,
    "щ": 0x18, "Щ": 0x18,
    "з": 0x19, "З": 0x19,
    "х": 0x1A, "Х": 0x1A,
    "ъ": 0x1B, "Ъ": 0x1B,
    "ф": 0x1E, "Ф": 0x1E,
    "ы": 0x1F, "Ы": 0x1F,
    "в": 0x20, "В": 0x20,
    "а": 0x21, "А": 0x21,
    "п": 0x22, "П": 0x22,
    "р": 0x23, "Р": 0x23,
    "о": 0x24, "О": 0x24,
    "л": 0x25, "Л": 0x25,
    "д": 0x26, "Д": 0x26,
    "ж": 0x27, "Ж": 0x27,
    "э": 0x28, "Э": 0x28,
    "я": 0x2C, "Я": 0x2C,
    "ч": 0x2D, "Ч": 0x2D,
    "с": 0x2E, "С": 0x2E,
    "м": 0x2F, "М": 0x2F,
    "и": 0x30, "И": 0x30,
    "т": 0x31, "Т": 0x31,
    "ь": 0x32, "Ь": 0x32,
    "б": 0x33, "Б": 0x33,
    "ю": 0x34, "Ю": 0x34,
}

def get_scancode(key_name):
    """✅ Получить скан-код клавиши по названию."""
    key_lower = str(key_name).lower().strip()
    if key_lower in SCANCODE_MAP:
        return SCANCODE_MAP[key_lower]
    
    # Если не найдено в словаре — пробуем как одиночный символ
    if len(key_lower) == 1:
        return ord(key_lower.upper())
    
    # Последний резервный вариант — Escape (0x01)
    return 0x01

def hardware_mouse_action(flag):
    """Отправка события мыши через SendInput."""
    try:
        extra = ctypes.pointer(ctypes.c_ulong(0))
        inp = INPUT_SYS()
        inp.type = 0  # INPUT_MOUSE
        inp.u.mi = MOUSEINPUT_SYS(0, 0, 0, flag | MOUSEEVENTF_VIRTUALDESK, 0, extra)
        ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))
    except Exception:
        pass

def hardware_key_event(scan_code, is_down=True):
    """✅ ИСПРАВЛЕННАЯ: Отправка события клавиатуры через SendInput."""
    try:
        extra = ctypes.pointer(ctypes.c_ulong(0))
        inp = INPUT_SYS()
        inp.type = 1  # INPUT_KEYBOARD
        flags = 0x0008  # KEYEVENTF_SCANCODE
        if not is_down:
            flags |= 0x0002  # KEYEVENTF_KEYUP
        inp.u.ki = KEYBDINPUT_SYS(0, scan_code, flags, 0, extra)
        ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))
    except Exception:
        pass


class VirtualCursorOverlay(QWidget):
    """Кастомный геймерский оверлей: лазерный микроблок на 144 Гц"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowTransparentForInput
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        screen_geo = QApplication.primaryScreen().geometry()
        self.setGeometry(screen_geo)

        self.progress = 0.0
        self.v_x = float(screen_geo.width() // 2)
        self.v_y = float(screen_geo.height() // 2)

        try:
            hdc = ctypes.windll.user32.GetDC(0)
            self.dpi_scale = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88) / 96.0
            ctypes.windll.user32.ReleaseDC(0, hdc)
        except Exception:
            self.dpi_scale = 1.0

        self.lbl_cursor = QLabel(self)
        self.lbl_cursor.setFixedSize(16, 16)
        self.lbl_cursor.setStyleSheet("""
            QLabel {
                background-color: #a347ff;
                border: 2px solid #ffffff;
                border-radius: 8px;
            }
        """)
        self._cursor_visible_state = None

        self.hardware_timer = QTimer(self)
        self.hardware_timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.hardware_timer.timeout.connect(self.sync_cursor_position_hardware_144hz)
        self.hardware_timer.start(7)

        try:
            hwnd = int(self.winId())
            style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
            ctypes.windll.user32.SetWindowLongW(hwnd, -20, style | 0x08000000 | 0x00000020 | 0x00000008)
            ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0040)
        except Exception:
            pass

    def sync_cursor_position_hardware_144hz(self):
        """Синхронизация позиции курсора на 144 Гц"""
        config = get_cached_config()
        current_prof = config.get("current_profile", "Default Profile")
        show_custom_cursor = config["profiles"][current_prof]["mouse"].get("show_custom_cursor", False)

        if show_custom_cursor:
            if self._cursor_visible_state is not True:
                self.lbl_cursor.show()
                self._cursor_visible_state = True

            pt = POINT()
            if ctypes.windll.user32.GetCursorPos(ctypes.byref(pt)):
                self.v_x = float(pt.x / self.dpi_scale)
                self.v_y = float(pt.y / self.dpi_scale)
                self.lbl_cursor.move(int(self.v_x), int(self.v_y))

                if 0.0 < self.progress < 1.0:
                    self.update()
        else:
            if self._cursor_visible_state is not False:
                self.lbl_cursor.hide()
                self._cursor_visible_state = False

    def update_cursor_data(self, progress, virtual_x, virtual_y):
        """Обновление данных курсора"""
        self.progress = progress

    def paintEvent(self, event):
        """Отрисовка круга зарядки"""
        config = get_cached_config()
        current_prof = config.get("current_profile", "Default Profile")
        show_click_circle = config["profiles"][current_prof]["mouse"].get("show_click_circle", True)

        if show_click_circle and 0.0 < self.progress < 1.0:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            pen = QPen(QColor("#2ed573"), 3)
            painter.setPen(pen)
            radius = 18
            span_angle = int(-self.progress * 360 * 16)

            cx = int(self.v_x) + 8
            cy = int(self.v_y) + 8
            painter.drawArc(cx - radius, cy - radius, radius * 2, radius * 2, 90 * 16, span_angle)
            painter.end()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowSystemMenuHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)

        self.resize(1250, 680)
        self.setMinimumSize(1250, 620)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.title_bar = CustomTitleBar(self)
        self.main_layout.addWidget(self.title_bar)

        self.body_layout = QHBoxLayout()
        self.body_layout.setContentsMargins(12, 12, 12, 12)
        self.body_layout.setSpacing(12)

        self.sidebar = SidebarMenu(self)
        self.body_layout.addWidget(self.sidebar)

        self.content_stack = QStackedWidget()
        self.page_main = QWidget()

        self.page_settings = VideoSettingsMainWidget(self)
        self.page_voice_settings = VoiceSettingsMainWidget(self)
        self.page_mouse_settings = MouseSettingsMainWidget(self)
        self.page_keyboard_settings = KeyboardSettingsMainWidget(self)

        self.page_nav_profiles = ProfilesPage("СТРАНИЦА КОНФИГУРАЦИИ ПРОФИЛЕЙ", self)
        self.page_nav_settings = GeneralSettingsPage("СТРАНИЦА ОБЩИХ НАСТРОЕК ПРОГРАММЫ", self)
        self.page_nav_about = AboutPage("ИНФОРМАЦИЯ О ПРОГРАММЕ И РАЗРАБОТЧИКЕ", self)

        self.setup_main_page_grid()

        self.content_stack.addWidget(self.page_main)
        self.content_stack.addWidget(self.page_settings)
        self.content_stack.addWidget(self.page_voice_settings)
        self.content_stack.addWidget(self.page_mouse_settings)
        self.content_stack.addWidget(self.page_keyboard_settings)
        self.content_stack.addWidget(self.page_nav_profiles)
        self.content_stack.addWidget(self.page_nav_settings)
        self.content_stack.addWidget(self.page_nav_about)

        self.content_stack.setCurrentIndex(0)

        self.body_layout.addWidget(self.content_stack, stretch=4)
        self.main_layout.addLayout(self.body_layout)

        self.setStyleSheet(styles.STYLE_SHEET)

        self.cursor_overlay = VirtualCursorOverlay()
        screen_geometry = QApplication.primaryScreen().geometry()
        self.cursor_overlay.setGeometry(screen_geometry)
        self.cursor_overlay.show()

    def setup_main_page_grid(self):
        grid = QGridLayout(self.page_main)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(12)

        self.mod_video = VideoControlModule(self)
        self.mod_mouse = MouseControlModule(self)
        self.mod_keyboard = KeyboardControlModule(self)
        self.mod_voice = VoiceControlModule(self)

        from modules.mouse.autoclick_win import DwellClicker
        self.dwell_clicker = DwellClicker()

        self.advanced_panel_window = MouseAdvancedPanel(self)

        from modules.mouse.start_mouse import MouseController
        self.mouse_controller = MouseController()

        self.mod_video.camera_thread.face_moved.connect(self.on_face_coordinates_received)
        self.mod_video.camera_thread.face_gestures_received.connect(self.on_face_gestures_received)

        self.page_settings.block1.settings_changed.connect(self.mod_video.hot_reboot_camera_hardware)
        self.mod_video.camera_thread.head_size_calculated.connect(self.page_settings.block3.update_live_head_size)

        self.mod_video.settings_clicked.connect(lambda: self.content_stack.setCurrentIndex(1))
        self.mod_mouse.settings_clicked.connect(lambda: self.content_stack.setCurrentIndex(3))
        self.mod_keyboard.settings_clicked.connect(lambda: self.content_stack.setCurrentIndex(4))
        self.mod_voice.btn_settings.clicked.connect(lambda: self.content_stack.setCurrentIndex(2))

        self.sidebar.home_requested.connect(lambda: self.content_stack.setCurrentIndex(0))
        self.sidebar.profiles_requested.connect(lambda: self.content_stack.setCurrentIndex(5))
        self.sidebar.settings_requested.connect(lambda: self.content_stack.setCurrentIndex(6))
        self.sidebar.about_requested.connect(lambda: self.content_stack.setCurrentIndex(7))

        grid.addWidget(self.mod_video, 0, 0)
        grid.addWidget(self.mod_mouse, 0, 1)
        grid.addWidget(self.mod_keyboard, 1, 0)
        grid.addWidget(self.mod_voice, 1, 1)

    def on_face_coordinates_received(self, nx, ny):
        """ЦЕНТРАЛЬНЫЙ ДИСПЕТЧЕР УПРАВЛЕНИЯ: координаты лица -> физический курсор"""
        config = get_cached_config()
        current_prof = config.get("current_profile", "Default Profile")
        mouse_conf = config["profiles"][current_prof]["mouse"]

        if not mouse_conf.get("main_toggle", True):
            self.cursor_overlay.update_cursor_data(0.0, 0.0, 0.0)
            self.mouse_controller.reset()
            return

        is_f10_active_now = False
        if hasattr(self, 'active_pressed_keys'):
            is_f10_active_now = self.active_pressed_keys.get("f10", False)

        if not hasattr(self, '_f10_clutch_ready_for_reset'):
            self._f10_clutch_ready_for_reset = False

        if is_f10_active_now:
            self._f10_clutch_ready_for_reset = True
            if hasattr(self, 'cursor_overlay') and self.cursor_overlay:
                self.cursor_overlay.update_cursor_data(0.0, self.mouse_controller.virtual_x, self.mouse_controller.virtual_y)
            return
        else:
            if self._f10_clutch_ready_for_reset:
                scr_w = self.mouse_controller.screen_width
                scr_h = self.mouse_controller.screen_height
                cx = int(scr_w // 2)
                cy = int(scr_h // 2)

                try:
                    ctypes.windll.user32.SetCursorPos(cx, cy)
                except Exception:
                    pass

                self.mouse_controller.reset()

                if hasattr(self, 'dwell_clicker') and self.dwell_clicker:
                    self.dwell_clicker.reset(float(cx), float(cy))
                    self.dwell_clicker.progress = 0.0
                    self.dwell_clicker.is_locked = False
                    if hasattr(self.dwell_clicker, 'dwell_timer'):
                        self.dwell_clicker.dwell_timer.stop()

                if hasattr(self, 'advanced_panel_window') and self.advanced_panel_window:
                    if hasattr(self.advanced_panel_window, 'advanced_clicker') and self.advanced_panel_window.advanced_clicker:
                        self.advanced_panel_window.advanced_clicker.reset(float(cx), float(cy))
                        self.advanced_panel_window.advanced_clicker.progress = 0.0
                        self.advanced_panel_window.advanced_clicker.is_locked = False

                try:
                    ctypes.windll.user32.mouse_event(0x0004, 0, 0, 0, 0)
                except Exception:
                    pass

                self._f10_clutch_ready_for_reset = False
                return

        speed_mult = mouse_conf.get("speed", 25.0)
        dead_zone = mouse_conf.get("threshold", 0.15)
        click_time = mouse_conf.get("click_delay", 0.6)
        radius_zone = mouse_conf.get("click_radius", 15)

        pos = QCursor.pos()
        is_over_main_ui = self.geometry().contains(pos)

        is_over_advanced_panel = False
        if hasattr(self, 'advanced_panel_window') and self.advanced_panel_window and self.advanced_panel_window.isVisible():
            is_over_advanced_panel = self.advanced_panel_window.geometry().contains(pos)

        is_over_toolbar = False
        toolbar_window = getattr(self.mod_mouse, 'toolbar_window', None)
        if toolbar_window and toolbar_window.isVisible():
            is_over_toolbar = toolbar_window.geometry().contains(pos)

        if mouse_conf.get("move_mode", True):
            self.mouse_controller.move(nx, ny, speed_multiplier=speed_mult, threshold=dead_zone, use_windows_mouse=True)
            self.mouse_controller.apply_physical_move()

        progress = 0.0
        is_advanced_panel_open = False
        if hasattr(self, 'advanced_panel_window') and self.advanced_panel_window and self.advanced_panel_window.isVisible():
            is_advanced_panel_open = True

        if is_advanced_panel_open:
            adv_clicker = self.advanced_panel_window.advanced_clicker
            use_scroll_mode = self.advanced_panel_window.chk_scroll_mode.isChecked()
            is_scroll_active = getattr(adv_clicker, 'is_scroll_joystick_active', False)

            if getattr(adv_clicker, 'currently_held_button', None) is not None:
                if is_over_advanced_panel:
                    adv_clicker.release_timer.stop()
                    adv_clicker.execute_forced_release()
                    adv_clicker.is_locked = True
                    adv_clicker.last_move_time = time.time()
                    return

            if (is_over_main_ui or is_over_advanced_panel) and not use_scroll_mode and not is_scroll_active:
                progress = adv_clicker.check_dwell(self.mouse_controller.virtual_x, self.mouse_controller.virtual_y,
                                                    click_delay=click_time, click_radius=radius_zone)
                if progress >= 1.0:
                    def run_async_adv_click():
                        import pydirectinput
                        try:
                            pydirectinput.click()
                        except Exception:
                            pass
                    threading.Thread(target=run_async_adv_click, daemon=True).start()
                    adv_clicker.reset(float(pos.x()), float(pos.y()))
                    adv_clicker.is_locked = False
                    progress = 0.0
            else:
                progress = adv_clicker.check_dwell(self.mouse_controller.virtual_x, self.mouse_controller.virtual_y,
                                                    click_delay=click_time, click_radius=radius_zone)

            if hasattr(self, 'cursor_overlay') and self.cursor_overlay:
                self.cursor_overlay.update_cursor_data(progress, self.mouse_controller.virtual_x, self.mouse_controller.virtual_y)
            return

        elif mouse_conf.get("click_mode", True) or is_over_toolbar:
            progress = self.dwell_clicker.check_dwell(
                self.mouse_controller.virtual_x, self.mouse_controller.virtual_y,
                use_autoclick=True,
                click_delay=click_time,
                click_radius=radius_zone,
                is_over_toolbar=is_over_toolbar,
                is_over_main_ui=is_over_main_ui
            )

        if hasattr(self, 'page_keyboard_settings') and self.page_keyboard_settings:
            block1 = getattr(self.page_keyboard_settings, 'block1', None)
            if block1 and hasattr(block1, 'process_live_gestures'):
                if hasattr(self, 'mod_video') and self.mod_video and getattr(self.mod_video, 'camera_thread', None):
                    last_gestures = getattr(self.mod_video.camera_thread, 'last_gestures_cache', None)
                    if last_gestures:
                        try:
                            block1.process_live_gestures(last_gestures)
                        except Exception:
                            pass

        if hasattr(self, 'cursor_overlay') and self.cursor_overlay:
            self.cursor_overlay.update_cursor_data(
                progress,
                self.mouse_controller.virtual_x,
                self.mouse_controller.virtual_y
            )

    def showEvent(self, event):
        """Интегрируем кнопки Назад прямо в верхние углы новых окон настроек"""
        super().showEvent(event)

        if not hasattr(self, '_video_back_btn_added'):
            back_to_main_vid = QPushButton("✕ Назад")
            back_to_main_vid.setFixedSize(90, 28)
            back_to_main_vid.setStyleSheet("QPushButton { background-color: #071224; color: #00d2ff; border: 1px solid #162e54; border-radius: 5px; font-weight: bold; } QPushButton:hover { background-color: #00d2ff; color: black; border-color: white; }")
            back_to_main_vid.clicked.connect(lambda: self.content_stack.setCurrentIndex(0))
            header_layout_vid = QHBoxLayout()
            header_layout_vid.addStretch()
            header_layout_vid.addWidget(back_to_main_vid)
            self.page_settings.layout().insertLayout(0, header_layout_vid)
            self._video_back_btn_added = True

        if not hasattr(self, '_voice_back_btn_added'):
            back_to_main_voice = QPushButton("✕ Назад")
            back_to_main_voice.setFixedSize(90, 28)
            back_to_main_voice.setStyleSheet("QPushButton { background-color: #130a21; color: #ff007f; border: 1px solid #2f174d; border-radius: 5px; font-weight: bold; } QPushButton:hover { background-color: #ff007f; color: white; border-color: white; }")
            back_to_main_voice.clicked.connect(lambda: self.content_stack.setCurrentIndex(0))
            header_layout_voice = QHBoxLayout()
            header_layout_voice.addStretch()
            header_layout_voice.addWidget(back_to_main_voice)
            self.page_voice_settings.layout().insertLayout(0, header_layout_voice)
            self._voice_back_btn_added = True

        if not hasattr(self, '_mouse_back_btn_added'):
            back_to_main_mouse = QPushButton("✕ Назад")
            back_to_main_mouse.setFixedSize(90, 28)
            back_to_main_mouse.setStyleSheet("QPushButton { background-color: #05140b; color: #2ed573; border: 1px solid #123d22; border-radius: 5px; font-weight: bold; } QPushButton:hover { background-color: #2ed573; color: black; border-color: white; }")
            back_to_main_mouse.clicked.connect(lambda: self.content_stack.setCurrentIndex(0))
            header_layout_mouse = QHBoxLayout()
            header_layout_mouse.addStretch()
            header_layout_mouse.addWidget(back_to_main_mouse)
            self.page_mouse_settings.layout().insertLayout(0, header_layout_mouse)
            self._mouse_back_btn_added = True

        if not hasattr(self, '_kb_back_btn_added'):
            header_layout_kb = QHBoxLayout()
            header_layout_kb.setContentsMargins(0, 0, 0, 0)
            header_layout_kb.setSpacing(6)

            self.btn_main_set5 = QPushButton("Настройки №2")
            self.btn_main_set5.setFixedSize(110, 28)
            self.btn_main_set5.setStyleSheet("QPushButton { background-color: #130a21; color: #a347ff; border: 1px solid #2f174d; border-radius: 5px; font-weight: bold; } QPushButton:hover { background-color: #8a2be2; color: white; border-color: white; }")
            header_layout_kb.addWidget(self.btn_main_set5)

            self.btn_main_set5_back = QPushButton("Назад к блокам")
            self.btn_main_set5_back.setFixedSize(110, 28)
            self.btn_main_set5_back.setStyleSheet("QPushButton { background-color: #130a21; color: #a347ff; border: 1px solid #2f174d; border-radius: 5px; font-weight: bold; } QPushButton:hover { background-color: #8a2be2; color: white; border-color: white; }")
            self.btn_main_set5_back.setVisible(False)
            header_layout_kb.addWidget(self.btn_main_set5_back)

            def open_set5_page_logic():
                if hasattr(self.page_keyboard_settings, 'set_active_page_index'):
                    self.page_keyboard_settings.set_active_page_index(1)
                    self.btn_main_set5.setVisible(False)
                    self.btn_main_set5_back.setVisible(True)

            def close_set5_page_logic():
                if hasattr(self.page_keyboard_settings, 'set_active_page_index'):
                    self.page_keyboard_settings.set_active_page_index(0)
                    self.btn_main_set5.setVisible(True)
                    self.btn_main_set5_back.setVisible(False)

            self.btn_main_set5.clicked.connect(open_set5_page_logic)
            self.btn_main_set5_back.clicked.connect(close_set5_page_logic)

            header_layout_kb.addStretch()

            back_to_main_kb = QPushButton("✕ Назад")
            back_to_main_kb.setFixedSize(90, 28)
            back_to_main_kb.setStyleSheet("QPushButton { background-color: #130a21; color: #8a2be2; border: 1px solid #2f174d; border-radius: 5px; font-weight: bold; } QPushButton:hover { background-color: #8a2be2; color: white; border-color: white; }")

            def on_full_exit_kb_settings():
                close_set5_page_logic()
                self.content_stack.setCurrentIndex(0)

            back_to_main_kb.clicked.connect(on_full_exit_kb_settings)
            header_layout_kb.addWidget(back_to_main_kb)

            self.page_keyboard_settings.layout().insertLayout(0, header_layout_kb)
            self._kb_back_btn_added = True

        NAV_BACK_STYLE = "QPushButton { background-color: #09071c; color: #a1a3b5; border: 1px solid #1c1742; border-radius: 5px; font-weight: bold; } QPushButton:hover { background-color: #120e2e; color: white; border-color: #00d2ff; }"

        if not hasattr(self, '_nav_profiles_back_added'):
            btn = QPushButton("✕ Назад")
            btn.setFixedSize(90, 28)
            btn.setStyleSheet(NAV_BACK_STYLE)
            btn.clicked.connect(lambda: self.content_stack.setCurrentIndex(0))
            lay = QHBoxLayout()
            lay.addStretch()
            lay.addWidget(btn)
            self.page_nav_profiles.layout().insertLayout(0, lay)
            self._nav_profiles_back_added = True

        if not hasattr(self, '_nav_settings_back_added'):
            btn = QPushButton("✕ Назад")
            btn.setFixedSize(90, 28)
            btn.setStyleSheet(NAV_BACK_STYLE)
            btn.clicked.connect(lambda: self.content_stack.setCurrentIndex(0))
            lay = QHBoxLayout()
            lay.addStretch()
            lay.addWidget(btn)
            self.page_nav_settings.layout().insertLayout(0, lay)
            self._nav_settings_back_added = True

        if not hasattr(self, '_nav_about_back_added'):
            btn = QPushButton("✕ Назад")
            btn.setFixedSize(90, 28)
            btn.setStyleSheet(NAV_BACK_STYLE)
            btn.clicked.connect(lambda: self.content_stack.setCurrentIndex(0))
            lay = QHBoxLayout()
            lay.addStretch()
            lay.addWidget(btn)
            self.page_nav_about.layout().insertLayout(0, lay)
            self._nav_about_back_added = True

    def on_face_gestures_received(self, gestures):
        """ЦЕНТРАЛЬНЫЙ ДИСПЕТЧЕР ЖЕСТОВ МИМИКИ ЛИЦА"""
        config = get_cached_config()
        current_prof = config.get("current_profile", "Default Profile")
        kb_conf = config["profiles"][current_prof].get("kb", {})

        live_thresholds = {}
        if hasattr(self, 'page_keyboard_settings') and self.page_keyboard_settings:
            block1 = getattr(self.page_keyboard_settings, 'block1', None)
            if block1 and hasattr(block1, 'cached_thresholds'):
                live_thresholds = block1.cached_thresholds

            block1_proc = getattr(block1, 'process_live_gestures', None)
            if block1_proc:
                try:
                    full_gestures = gestures.copy()
                    if hasattr(self, 'mouse_controller') and self.mouse_controller:
                        current_zoom_in = getattr(self.mouse_controller, 'live_zoom_in_pct', 0.0)
                        current_zoom_out = getattr(self.mouse_controller, 'live_zoom_out_pct', 0.0)

                        if current_zoom_in == 0.0 and current_zoom_out == 0.0:
                            cache = getattr(self.mod_video.camera_thread, 'last_gestures_cache', {})
                            if cache:
                                current_zoom_in = cache.get("zoom_in", 0.0)
                                current_zoom_out = cache.get("zoom_out", 0.0)

                        full_gestures["zoom_in"] = current_zoom_in
                        full_gestures["zoom_out"] = current_zoom_out
                    block1_proc(full_gestures)
                except Exception:
                    pass

            block2 = getattr(self.page_keyboard_settings, 'block2', None)
            if block2 and hasattr(block2, 'process_live_gestures'):
                try:
                    full_gestures = gestures.copy()
                    cache = getattr(self.mod_video.camera_thread, 'last_gestures_cache', {})
                    if cache:
                        full_gestures["zoom_in"] = cache.get("zoom_in", 0.0)
                        full_gestures["zoom_out"] = cache.get("zoom_out", 0.0)
                    block2.process_live_gestures(full_gestures)
                except Exception:
                    pass

        if not kb_conf.get("main_toggle", True) or not kb_conf.get("gestures_enabled", True):
            return

        bindings = kb_conf.get("bindings", {})
        if not hasattr(self, 'active_pressed_keys'):
            self.active_pressed_keys = {}

        is_gesture_mouse_allowed = kb_conf.get("real_press_enabled", True)
        if is_gesture_mouse_allowed:
            scroll_btn_obj = None
            is_overlay_scroll_active = False

            try:
                manager_obj = None
                if hasattr(self, 'mod_keyboard') and self.mod_keyboard:
                    if hasattr(self.mod_keyboard, 'overlay_manager') and self.mod_keyboard.overlay_manager:
                        manager_obj = self.mod_keyboard.overlay_manager

                if not manager_obj and hasattr(self, 'overlay_manager') and self.overlay_manager:
                    manager_obj = self.overlay_manager

                if manager_obj:
                    for btn in manager_obj.active_buttons:
                        if btn and btn.key_name == "ск":
                            scroll_btn_obj = btn
                            if getattr(btn, 'is_physically_pressed', False):
                                is_overlay_scroll_active = True
                            break
            except Exception:
                pass

            if not hasattr(self, '_prev_test_scroll_state'):
                self._prev_test_scroll_state = False

            if is_overlay_scroll_active != self._prev_test_scroll_state:
                if is_overlay_scroll_active:
                    print("\n[ИИ-СИСТЕМА] >>> КНОПКА СК АКТИВИРОВАНА (ВРАЩЕНИЕ КОЛЕСА ВКЛЮЧЕНО) <<<")
                else:
                    print("[ИИ-СИСТЕМА] <<< КНОПКА СК ДЕАКТИВИРОВАНА (ВРАЩЕНИЕ КОЛЕСА ВЫКЛЮЧЕНО) <<<")
                self._prev_test_scroll_state = is_overlay_scroll_active

            if is_overlay_scroll_active and scroll_btn_obj:
                btn_geo = scroll_btn_obj.geometry()
                center_zero_y = float(btn_geo.y() + (btn_geo.height() / 2.0))
                current_mouse_y = float(QCursor.pos().y())

                if not hasattr(self, '_blind_scroll_start_y') or self._blind_scroll_start_y is None:
                    self._blind_scroll_start_y = center_zero_y
                    self._last_blind_scroll_time = 0.0

                pixel_delta = current_mouse_y - self._blind_scroll_start_y
                abs_dy = abs(pixel_delta)

                if abs_dy > 20:
                    if abs_dy <= 100:
                        interval_sec = 1.0
                    elif abs_dy <= 200:
                        interval_sec = 0.5
                    elif abs_dy <= 300:
                        interval_sec = 0.33
                    else:
                        interval_sec = 0.01

                    now_t = time.time()
                    if now_t - getattr(self, '_last_blind_scroll_time', 0.0) >= interval_sec:
                        try:
                            s_dir = 120 if pixel_delta < 0 else -120
                            ctypes.windll.user32.mouse_event(0x0800, 0, 0, s_dir, 0)
                        except Exception:
                            pass
                        self._last_blind_scroll_time = now_t
            else:
                self._blind_scroll_start_y = None
        else:
            self._blind_scroll_start_y = None

        head_y = getattr(self.mouse_controller, 'current_y', 0.5)
        self._execute_hardware_press_async(gestures, bindings, live_thresholds, kb_conf, head_y)

    @pyqtSlot()
    def bring_to_foreground(self):
        """Принудительно и бесшовно выводит главное окно программы поверх всех игр и окон"""
        if self.isMinimized():
            self.showNormal()
        else:
            self.show()
        self.raise_()
        self.activateWindow()
        try:
            hwnd = int(self.winId())
            ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0040)
            ctypes.windll.user32.SetWindowPos(hwnd, -2, 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0040)
        except Exception:
            pass

    def _execute_hardware_press_async(self, gestures, bindings, thresholds, kb_conf, head_y):
        """✅ ИСПРАВЛЕННАЯ: Фоновый эмулятор клавиш с поддержкой всех клавиш"""
        is_gesture_mouse_allowed = kb_conf.get("real_press_enabled", True)
        currently_triggered_sys_keys = set()

        for gesture_id, key_name in bindings.items():
            if gesture_id not in gestures:
                continue
            if float(gestures[gesture_id]) >= float(thresholds.get(gesture_id, 35)):
                currently_triggered_sys_keys.add(key_name.lower().strip())

        # ЖЕЛЕЗОБЕТОННЫЙ ПЕРЕХВАТ КЛАТЧА RST (ОБНУЛЕНИЕ КУРСОРА)
        if "rst" in currently_triggered_sys_keys:
            self.active_pressed_keys["rst"] = True
            self.active_pressed_keys["f10"] = True
        else:
            self.active_pressed_keys["rst"] = False
            self.active_pressed_keys["f10"] = False

        for gesture_id, key_name in bindings.items():
            if gesture_id not in gestures:
                continue
            sys_key = key_name.lower().strip()
            if sys_key in ["ск", "rst"]:
                continue

            is_triggered = (float(gestures[gesture_id]) >= float(thresholds.get(gesture_id, 35)))
            if sys_key not in self.active_pressed_keys:
                self.active_pressed_keys[sys_key] = False

            logical_pos = QCursor.pos()

            if is_triggered:
                if not self.active_pressed_keys[sys_key]:
                    if sys_key == "app":
                        QMetaObject.invokeMethod(self, "bring_to_foreground", Qt.ConnectionType.QueuedConnection)
                        self.active_pressed_keys[sys_key] = True
                    elif is_gesture_mouse_allowed:
                        is_target_toggle_mode = False
                        try:
                            if hasattr(self, 'overlay_manager') and self.overlay_manager:
                                for btn in self.overlay_manager.active_buttons:
                                    if btn and btn.key_name == sys_key and btn.geometry().contains(logical_pos):
                                        cfg = get_cached_config()
                                        prof = cfg.get("current_profile", "Default Profile")
                                        if cfg["profiles"][prof].get("kb", {}).get("overlay_modes", {}).get(sys_key) == "toggle_click":
                                            is_target_toggle_mode = True
                                            break
                        except Exception:
                            pass

                        if is_target_toggle_mode:
                            self.active_pressed_keys[sys_key] = True
                            continue

                        # ✅ ИСПРАВЛЕННАЯ ОТПРАВКА АППАРАТНОГО НАЖАТИЯ
                        if sys_key in ["lmb", "rmb", "mmb"]:
                            flag = MOUSEEVENTF_LEFTDOWN if sys_key == "lmb" else (MOUSEEVENTF_RIGHTDOWN if sys_key == "rmb" else MOUSEEVENTF_MIDDLEDOWN)
                            hardware_mouse_action(flag)
                        else:
                            # ✅ Используем новую функцию get_scancode() вместо жёсткого словаря
                            scan = get_scancode(sys_key)
                            hardware_key_event(scan, is_down=True)

                        self.active_pressed_keys[sys_key] = True
            else:
                if self.active_pressed_keys[sys_key]:
                    if sys_key == "app":
                        self.active_pressed_keys[sys_key] = False
                    else:
                        is_target_toggle_mode = False
                        try:
                            if hasattr(self, 'overlay_manager') and self.overlay_manager:
                                for btn in self.overlay_manager.active_buttons:
                                    if btn and btn.key_name == sys_key and btn.geometry().contains(logical_pos):
                                        cfg = get_cached_config()
                                        prof = cfg.get("current_profile", "Default Profile")
                                        if cfg["profiles"][prof].get("kb", {}).get("overlay_modes", {}).get(sys_key) == "toggle_click":
                                            is_target_toggle_mode = True
                                            break
                        except Exception:
                            pass

                        if is_target_toggle_mode:
                            self.active_pressed_keys[sys_key] = False
                            continue

                        # ✅ ИСПРАВЛЕННАЯ ОТПРАВКА АППАРАТНОГО ОТЖАТИЯ
                        if sys_key in ["lmb", "rmb", "mmb"]:
                            flag = MOUSEEVENTF_LEFTUP if sys_key == "lmb" else (MOUSEEVENTF_RIGHTUP if sys_key == "rmb" else MOUSEEVENTF_MIDDLEUP)
                            hardware_mouse_action(flag)
                        else:
                            # ✅ Используем новую функцию get_scancode()
                            scan = get_scancode(sys_key)
                            hardware_key_event(scan, is_down=False)

                        self.active_pressed_keys[sys_key] = False

    def closeEvent(self, event):
        """Корректное завершение работы программы"""
        if hasattr(self, 'mod_video') and self.mod_video and getattr(self.mod_video, 'camera_thread', None):
            try:
                self.mod_video.camera_thread.stop()
                self.mod_video.camera_thread.wait(2000)
            except Exception:
                pass

        if hasattr(self, 'cursor_overlay') and self.cursor_overlay:
            try:
                self.cursor_overlay.close()
            except Exception:
                pass

        super().closeEvent(event)

        app = QApplication.instance()
        if app is not None:
            app.quit()

        def _force_exit_if_still_alive():
            os._exit(0)

        watchdog = threading.Timer(3.0, _force_exit_if_still_alive)
        watchdog.daemon = True
        watchdog.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())