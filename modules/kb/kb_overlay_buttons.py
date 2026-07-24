import os
import ctypes
import threading

import pydirectinput
import config_manager

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication
from PyQt6.QtCore import Qt, QTimer, QPoint, QMetaObject
from PyQt6.QtGui import QMouseEvent, QCursor

pydirectinput.FAILSAFE = False


# ---------------------------------------------------------------------------
# Константы Win32
# ---------------------------------------------------------------------------
GWL_EXSTYLE = -20
WS_EX_NOACTIVATE = 0x08000000
WS_EX_TRANSPARENT = 0x00000020

MOUSE_LEFT_DOWN, MOUSE_LEFT_UP = 0x0002, 0x0004
MOUSE_RIGHT_DOWN, MOUSE_RIGHT_UP = 0x0008, 0x0010
MOUSE_MID_DOWN, MOUSE_MID_UP = 0x0020, 0x0040
MOUSE_MOVE = 0x0001
MOUSE_ABSOLUTE = 0x8000

KEYEVENTF_SCANCODE = 0x0008
KEYEVENTF_KEYUP = 0x0002

VK_CONTROL = 0x11
VK_LWIN = 0x5B
VK_LBUTTON = 0x01


# ---------------------------------------------------------------------------
# ctypes-структуры (определяются ОДИН РАЗ)
# ---------------------------------------------------------------------------
class _MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long), ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong), ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]


class _KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort), ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong), ("time", ctypes.c_ulong),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]


class _INPUT_UNION(ctypes.Union):
    _fields_ = [("mi", _MOUSEINPUT), ("ki", _KEYBDINPUT)]


class _INPUT(ctypes.Structure):
    _anonymous_ = ("u",)
    _fields_ = [("type", ctypes.c_ulong), ("u", _INPUT_UNION)]


class _POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


# ---------------------------------------------------------------------------
# Хелперы уровня модуля
# ---------------------------------------------------------------------------
_MOUSE_FLAGS = {
    ("lmb", True): MOUSE_LEFT_DOWN, ("lmb", False): MOUSE_LEFT_UP,
    ("rmb", True): MOUSE_RIGHT_DOWN, ("rmb", False): MOUSE_RIGHT_UP,
    ("mmb", True): MOUSE_MID_DOWN, ("mmb", False): MOUSE_MID_UP,
}

_HW_CODES = {
    "w": (0x57, 0x11), "ц": (0x57, 0x11),
    "a": (0x41, 0x1E), "ф": (0x41, 0x1E),
    "s": (0x53, 0x1F), "ы": (0x53, 0x1F),
    "d": (0x44, 0x20), "в": (0x44, 0x20),
    "🡠": (0x25, 0x4B), "🡡": (0x26, 0x48),
    "🡢": (0x27, 0x4D), "🡣": (0x28, 0x50),
    "space": (0x20, 0x39),
    "shift": (0x10, 0x2A), "ctrl": (0x11, 0x1D), "alt": (0x12, 0x38),
}

_ARROWS = {"🡠": "left", "🡢": "right", "🡡": "up", "🡣": "down"}


def _normalize_key(raw_name):
    k = raw_name.lower().strip()
    if k in _ARROWS:
        return _ARROWS[k]
    if k in ("shift", "lshift", "rshift"):
        return "shift"
    if k in ("ctrl", "lctrl", "rctrl"):
        return "ctrl"
    if k in ("alt", "lalt", "ralt"):
        return "alt"
    if k in ("backspace", "tab", "esc", "enter"):
        return k
    if k in ("caps", "capslock", "caps lock"):
        return "capslock"
    return k


def _hardware_codes(raw_name):
    k = raw_name.lower().strip()
    if k in _HW_CODES:
        return _HW_CODES[k]
    if len(k) == 1:
        return (ord(k.upper()), 0)
    return (0, 0)


def _send_mouse(flag):
    """Отправка клика мыши через SendInput с живыми координатами курсора (для DX-игр)."""
    try:
        pt = _POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
        scr_w = ctypes.windll.user32.GetSystemMetrics(0) or 1
        scr_h = ctypes.windll.user32.GetSystemMetrics(1) or 1
        abs_x = int((pt.x * 65536) / scr_w)
        abs_y = int((pt.y * 65536) / scr_h)
        extra = ctypes.pointer(ctypes.c_ulong(0))
        inp = _INPUT()
        inp.type = 0  # INPUT_MOUSE
        inp.u.mi = _MOUSEINPUT(abs_x, abs_y, 0, flag | MOUSE_MOVE | MOUSE_ABSOLUTE, 0, extra)
        ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))
    except Exception:
        pass


def _set_ex_style(hwnd, add=0, remove=0):
    try:
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, (style | add) & ~remove)
    except Exception:
        pass


def _find_main_window():
    for widget in QApplication.topLevelWidgets():
        if widget.__class__.__name__ == "MainWindow":
            return widget
    return None


def _start_file(exe):
    try:
        os.startfile(exe)
    except Exception:
        pass


def _keyboard_worker(key, is_down):
    try:
        if is_down:
            pydirectinput.keyDown(key)
        else:
            pydirectinput.keyUp(key)
    except Exception:
        pass


def _resolve_position(saved, key, default):
    if key not in saved:
        return default
    pos = saved[key]
    if isinstance(pos, dict):
        return (int(pos.get("x", default[0])), int(pos.get("y", default[1])))
    if isinstance(pos, (list, tuple)) and len(pos) >= 2:
        return (int(pos[0]), int(pos[1]))
    return default


def _build_button_sheet(c_bg, c_border, c_bg_active, c_border_active, font_size):
    return f"""
        QLabel {{
            background-color: {c_bg};
            color: {c_border};
            border: 2px solid {c_border};
            border-radius: 8px;
            font-family: 'Segoe UI', sans-serif;
            font-size: {font_size}px;
            font-weight: bold;
        }}
        QLabel[active="true"] {{
            background-color: {c_bg_active};
            color: {c_border_active};
            border: 2px solid {c_border_active};
        }}
    """


FOCUS_LINE_SHEET = """
    QLabel {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1a0826, stop:1 #0b0314);
        color: #8a2be2;
        border: 1px solid #401970;
        border-radius: 4px;
        font-family: 'Segoe UI', sans-serif;
        font-size: 9px;
        font-weight: bold;
    }
    QLabel[active="hover_active"] {
        background-color: #2ed573;
        color: #000000;
        border: 1px solid #ffffff;
    }
    QLabel[active="click_active"] {
        background-color: #00d2ff;
        color: #000000;
        border: 1px solid #ffffff;
    }
"""


# ---------------------------------------------------------------------------
# Базовый класс: общая логика окна, перетаскивания и покраски через Qt-свойство
# ---------------------------------------------------------------------------
class FloatingButtonBase(QWidget):
    def __init__(self, key_text, width, height, opacity_pct, position_key, parent=None):
        super().__init__(parent)
        self.key_name = key_text.lower()
        self.display_text = key_text.upper()
        self._position_key = position_key

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint
                            | Qt.WindowType.WindowStaysOnTopHint
                            | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(width, height)
        self.setWindowOpacity(opacity_pct / 100.0)

        self.drag_position = QPoint()
        self.is_dragging = False
        self.is_physically_pressed = False

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.lbl = QLabel(self.display_text)
        self.lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.lbl)

        self.hover_timer = QTimer(self)
        self.hover_timer.timeout.connect(self.check_mouse_hover_trigger)
        self.hover_timer.start(50)

    # --- покраска: меняем только Qt-свойство, QSS слушает [active="true"] ---
    def set_neon_style(self, is_active=False):
        if self.lbl.property("active") != is_active:
            self.lbl.setProperty("active", is_active)
            self.lbl.style().unpolish(self.lbl)
            self.lbl.style().polish(self.lbl)

    def _ensure(self, name, default):
        if not hasattr(self, name):
            setattr(self, name, default)
        return getattr(self, name)

    # --- перетаскивание с Ctrl + сохранение позиции ---
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and \
                (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.is_dragging = True
            event.accept()
            return
        event.ignore()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() & Qt.MouseButton.LeftButton and self.is_dragging:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if not self.is_dragging:
            return
        self.is_dragging = False
        geo = self.geometry()
        config = config_manager.load_config()
        prof = config.get("current_profile", "Default Profile")
        kb = config["profiles"][prof]["kb"]
        kb.setdefault("overlay_positions", {})[self._position_key] = [geo.x(), geo.y()]
        config_manager.save_config(config)
        event.accept()

    # переопределяется в подклассах
    def check_mouse_hover_trigger(self):
        pass


# ---------------------------------------------------------------------------
# Кнопка матрицы (Set 3) — 5 режимов ховера/клика
# ---------------------------------------------------------------------------
class FloatingOverlayKey(FloatingButtonBase):
    def __init__(self, key_text, initial_x=300, initial_y=300, parent=None):
        config = config_manager.load_config()
        prof = config.get("current_profile", "Default Profile")
        kb = config["profiles"][prof].get("kb", {})
        size = kb.get("overlay_size", 60)
        opacity = kb.get("overlay_opacity", 100)

        super().__init__(key_text, size, size, opacity, key_text.lower(), parent)
        self.move(initial_x, initial_y)
        _set_ex_style(int(self.winId()), add=WS_EX_NOACTIVATE)

        self.lbl.setStyleSheet(_build_button_sheet(
            kb.get("clr_bg", "#0b0617"),
            kb.get("clr_border", "#401970"),
            kb.get("clr_bg_active", "#2ed573"),
            kb.get("clr_border_active", "#ffffff"),
            max(10, int(size * 0.26)),
        ))

        if self.key_name == "k+":
            self.is_physically_pressed = kb.get("cross_enabled", False)
        self.set_neon_style(is_active=self.is_physically_pressed)

    # --- покраска + точечная реакция кнопки K+ (перерождает/убивает крест) ---
    def set_neon_style(self, is_active=False):
        if self.lbl.property("active") != is_active:
            self.lbl.setProperty("active", is_active)
            self.lbl.style().unpolish(self.lbl)
            self.lbl.style().polish(self.lbl)

        if self.key_name == "k+":
            config = config_manager.load_config()
            prof = config.get("current_profile", "Default Profile")
            kb = config["profiles"][prof].get("kb", {})
            if kb.get("cross_enabled", False) != is_active:
                config["profiles"][prof]["kb"]["cross_enabled"] = is_active
                config_manager.save_config(config)

                main_win = _find_main_window()
                mod = getattr(main_win, "mod_keyboard", None) if main_win else None
                mgr = getattr(mod, "overlay_manager", None) if mod else None
                if mgr:
                    if is_active:
                        mgr.spawn_only_cross_buttons()
                    else:
                        mgr.destroy_only_cross_buttons()

                page = getattr(main_win, "page_keyboard_settings", None) if main_win else None
                block4 = getattr(page, "block4", None) if page else None
                chk = getattr(block4, "chk_cross_enable", None) if block4 else None
                if chk:
                    chk.blockSignals(True)
                    chk.setChecked(is_active)
                    chk.blockSignals(False)

    # --- исполнение системного действия (мышь / утилиты / клавиатура) ---
    def _execute_action(self, press_down, press_enabled, sys_key, clean_key):
        if not press_enabled:
            return

        if sys_key in ("lmb", "rmb", "mmb"):
            hwnd = int(self.winId())
            if press_down:
                _set_ex_style(hwnd, add=WS_EX_TRANSPARENT)
            else:
                _set_ex_style(hwnd, remove=WS_EX_TRANSPARENT)
            _send_mouse(_MOUSE_FLAGS[(sys_key, press_down)])

        elif sys_key == "ск":
            if press_down:
                main_win = _find_main_window()
                mc = getattr(main_win, "mouse_controller", None) if main_win else None
                self.scroll_start_y = float(getattr(mc, "current_y", 0.5)) if mc else 0.5
            else:
                self.scroll_start_y = None

        elif sys_key in ("osk", "лп", "app") and press_down:
            if sys_key == "app":
                main_win = _find_main_window()
                if main_win and main_win.metaObject().indexOfMethod("bring_to_foreground()") != -1:
                    QMetaObject.invokeMethod(main_win, "bring_to_foreground",
                                              Qt.ConnectionType.QueuedConnection)
            else:
                exe = "osk.exe" if sys_key == "osk" else "magnify.exe"
                threading.Thread(target=_start_file, args=(exe,), daemon=True).start()

        elif sys_key != "ctr":
            threading.Thread(target=_keyboard_worker,
                             args=(clean_key, press_down), daemon=True).start()

    # --- калибровка CTR: автономный обратный отсчёт ---
    def _run_ctr_calibration(self):
        if getattr(self, "calibration_active", False):
            return
        self.calibration_active = True
        self.calibration_ticks = 3
        self.set_neon_style(is_active=True)

        def countdown():
            if not getattr(self, "calibration_active", False):
                return
            if self.calibration_ticks > 0:
                self.lbl.setText(f"{self.calibration_ticks}...")
                self.calibration_ticks -= 1
                QTimer.singleShot(1000, countdown)
            else:
                self.lbl.setText("OK!")
                main_win = _find_main_window()
                cam = getattr(main_win, "mod_video", None) if main_win else None
                thread = getattr(cam, "camera_thread", None) if cam else None
                tracker = getattr(thread, "tracker", None) if thread else None
                if tracker:
                    tracker.calibrate_zero()
                QTimer.singleShot(1000, lambda: self.lbl.setText("CTR"))
                QTimer.singleShot(1000, lambda: self.set_neon_style(is_active=False))
                self.calibration_active = False

        countdown()

    # --- общий зажим/отжим LMB для toggle_click и click_on_hover_off ---
    # --- общий зажим/отжим для toggle_click и click_on_hover_off ---
    def _toggle_click_press(self, press_enabled, sys_key, clean_key):
        is_mouse_key = sys_key in ("lmb", "rmb", "mmb")

        if is_mouse_key:
            # МЫШЬ (LMB/RMB/MBB): отложенный железный зажим как у LMB.
            # Зелёный цвет сразу, реальный DOWN — через 1с, таймер на 500мс,
            # _mimic_hold_timer_active блокирует преждевременный сброс.
            if not self.is_physically_pressed:
                self.is_physically_pressed = True
                self.set_neon_style(is_active=True)
                self._mimic_hold_timer_active = True

                def hold_after_1s():
                    if self.is_physically_pressed:
                        self._hardware_lmb_is_locking = True
                        self._execute_action(True, press_enabled, sys_key, clean_key)
                        self.hover_timer.setInterval(500)
                    self._mimic_hold_timer_active = False

                QTimer.singleShot(1000, hold_after_1s)
            else:
                self.is_physically_pressed = False
                self._hardware_lmb_is_locking = False
                self._execute_action(False, press_enabled, sys_key, clean_key)
                self.hover_timer.setInterval(50)
                self.set_neon_style(is_active=False)
        else:
            # КЛАВИАТУРА (буквы/WASD/утилиты): мгновенный toggle без отложенного зажима.
            if not self.is_physically_pressed:
                self.set_neon_style(is_active=True)
                self._execute_action(True, press_enabled, sys_key, clean_key)
                self.is_physically_pressed = True
            else:
                self.set_neon_style(is_active=False)
                self._execute_action(False, press_enabled, sys_key, clean_key)
                self.is_physically_pressed = False

    def _release_lmb(self, press_enabled, clean_key):
        self.is_physically_pressed = False
        self._hardware_lmb_is_locking = False
        self._execute_action(False, press_enabled, "lmb", clean_key)
        self.hover_timer.setInterval(50)
        self._toggle_click_lock = False
        self._toggle_hover_processed = False
        self._click_hover_off_lock = False
        self.set_neon_style(is_active=False)

    # --- диспетчер ховера ---
    def check_mouse_hover_trigger(self):
        if self.is_dragging:
            return

        config = config_manager.load_config()
        prof = config.get("current_profile", "Default Profile")
        kb = config["profiles"][prof].get("kb", {})
        active_mode = kb.get("overlay_modes", {}).get(self.key_name, "hover")
        press_enabled = kb.get("overlay_press_enabled", True)
        sys_key = self.key_name
        clean_key = _normalize_key(self.key_name)

        is_hovered = self.geometry().contains(QCursor.pos())

        if sys_key == "ctr" and is_hovered:
            self._run_ctr_calibration()
            return

        if is_hovered:
            self._handle_hover(active_mode, sys_key, clean_key, press_enabled)
        else:
            self._handle_leave(active_mode, sys_key, clean_key, press_enabled)

    def _handle_hover(self, active_mode, sys_key, clean_key, press_enabled):
        self._ensure("_toggle_hover_processed", False)
        self._ensure("_click_once_processed", False)
        self._ensure("_toggle_click_lock", False)
        self._ensure("_click_hover_off_lock", False)
        self._ensure("_last_mimic_state", False)
        self._ensure("_last_dwell_state", False)
        self._ensure("_was_outside_after_click", False)
        self._ensure("_mimic_hold_timer_active", False)
        self._ensure("_hardware_lmb_is_locking", False)

        main_win = _find_main_window()

        # [РЕЖИМ 1] HOVER
        if active_mode == "hover":
            if not self.is_physically_pressed:
                self._hardware_lmb_is_locking = False
                self.set_neon_style(is_active=True)
                self._execute_action(True, press_enabled, sys_key, clean_key)
                self.is_physically_pressed = True

        # [РЕЖИМ 2] TOGGLE_HOVER
        elif active_mode == "toggle_hover" and not self._toggle_hover_processed:
            self._toggle_hover_processed = True
            if sys_key == "lmb":
                if not self._hardware_lmb_is_locking:
                    self._hardware_lmb_is_locking = True
                    self.is_physically_pressed = True
                    self.set_neon_style(is_active=True)
                    self._execute_action(True, press_enabled, sys_key, clean_key)
                    self.hover_timer.setInterval(500)
                else:
                    self.is_physically_pressed = False
                    self._hardware_lmb_is_locking = False
                    self._execute_action(False, press_enabled, sys_key, clean_key)
                    self.hover_timer.setInterval(50)
                    self.set_neon_style(is_active=False)
            else:
                self.is_physically_pressed = not self.is_physically_pressed
                self.set_neon_style(is_active=self.is_physically_pressed)
                self._execute_action(self.is_physically_pressed, press_enabled, sys_key, clean_key)

        # --- детекция клика по тулбару (мимик / dwell) ---
        mimic_click_active = bool(ctypes.windll.user32.GetAsyncKeyState(VK_LBUTTON) & 0x8000)
        if (sys_key == "lmb" and self._hardware_lmb_is_locking
                and active_mode in ("toggle_click", "click_on_hover_off")):
            mimic_click_active = False

        dwell_click_active = False
        dc = getattr(main_win, "dwell_clicker", None) if main_win else None
        if dc:
            dwell_click_active = getattr(dc, "is_locked", False) or getattr(dc, "progress", 0.0) >= 0.98

        mimic_triggered = mimic_click_active and not self._last_mimic_state
        dwell_triggered = dwell_click_active and not self._last_dwell_state
        is_toolbar_clicked = mimic_triggered or dwell_triggered

        if (not mimic_click_active and self._last_mimic_state) or \
           (not dwell_click_active and self._last_dwell_state):
            self._click_once_processed = False
            self._toggle_click_lock = False
            self._click_hover_off_lock = False

        self._last_mimic_state = mimic_click_active
        self._last_dwell_state = dwell_click_active

        # [РЕЖИМ 5] CLICK_ON_HOVER_OFF: выключение чистым наведением (только LMB)
        if (active_mode == "click_on_hover_off" and sys_key == "lmb"
                and self.is_physically_pressed and not self._mimic_hold_timer_active):
            self._release_lmb(press_enabled, clean_key)

        # --- действия по клику на тулбаре (режимы 3/4/5) ---
        if is_toolbar_clicked:
            if active_mode == "click_once" and not self._click_once_processed:
                self._click_once_processed = True
                self.set_neon_style(is_active=True)
                self._execute_action(True, press_enabled, sys_key, clean_key)
                QTimer.singleShot(50, lambda: self._execute_action(False, press_enabled, sys_key, clean_key))
                QTimer.singleShot(50, lambda: self.set_neon_style(is_active=False))

            elif active_mode == "toggle_click" and not self._toggle_click_lock:
                self._toggle_click_lock = True
                self._toggle_click_press(press_enabled, sys_key, clean_key)

            elif active_mode == "click_on_hover_off" and not self._click_hover_off_lock:
                self._click_hover_off_lock = True
                self._toggle_click_press(press_enabled, sys_key, clean_key)

        # [РЕЖИМ 5] CLICK_ON_HOVER_OFF: сброс, если был уход и возврат без клика
        if (active_mode == "click_on_hover_off" and self.is_physically_pressed
                and not is_toolbar_clicked and self._was_outside_after_click):
            self.set_neon_style(is_active=False)
            self._execute_action(False, press_enabled, sys_key, clean_key)
            self.is_physically_pressed = False
            self._was_outside_after_click = False

    def _handle_leave(self, active_mode, sys_key, clean_key, press_enabled):
            self._toggle_hover_processed = False
            self._click_once_processed = False
            self._toggle_click_lock = False
            self._click_hover_off_lock = False

            if sys_key == "lmb":
                # БЕЗОПАСНОЕ ЧТЕНИЕ: _hardware_lmb_is_locking инициализируется только в _handle_hover,
                # поэтому при уходе курсора с LMB-кнопки, которая ещё ни разу не была "ховернута",
                # используем getattr с дефолтом False, чтобы не падать с AttributeError.
                is_lmb_locking = getattr(self, "_hardware_lmb_is_locking", False)

                if (self.is_physically_pressed
                        and active_mode in ("toggle_click", "toggle_hover", "click_on_hover_off")
                        and not getattr(self, "_mimic_hold_timer_active", False)):
                    raw_os_click = bool(ctypes.windll.user32.GetAsyncKeyState(VK_LBUTTON) & 0x8000)
                    keep_holding = raw_os_click and is_lmb_locking
                    if not keep_holding and not getattr(self, "_last_mimic_state", False):
                        self._release_lmb(press_enabled, clean_key)
                current_raw = bool(ctypes.windll.user32.GetAsyncKeyState(VK_LBUTTON) & 0x8000)
                self._last_mimic_state = False if is_lmb_locking else current_raw
                self._last_dwell_state = False
            else:
                if self.is_physically_pressed and active_mode == "click_on_hover_off":
                    self._was_outside_after_click = True

                if active_mode == "hover" and self.is_physically_pressed:
                    self.set_neon_style(is_active=False)
                    self._execute_action(False, press_enabled, sys_key, clean_key)
                    self.is_physically_pressed = False
                elif active_mode == "toggle_hover":
                    self.set_neon_style(is_active=self.is_physically_pressed)
                else:
                    if not self.is_physically_pressed:
                        self.set_neon_style(is_active=False)
                        if self.hover_timer.interval() != 50:
                            self.hover_timer.setInterval(50)


# ---------------------------------------------------------------------------
# Кнопка креста-пульта (Set 4) — DirectX-сканкоды
# ---------------------------------------------------------------------------
class FloatingCrossKey(FloatingButtonBase):
    def __init__(self, position_id, key_text, initial_x, initial_y, parent=None):
        config = config_manager.load_config()
        prof = config.get("current_profile", "Default Profile")
        kb = config["profiles"][prof].get("kb", {})
        bind = kb.get("cross_custom_binds", {}).get(position_id, {"w": 60, "h": 40})
        w = bind.get("w", 60)
        h = bind.get("h", 40)
        opacity = kb.get("cross_opacity", 100)

        super().__init__(key_text, w, h, opacity, f"cross_4v_{position_id}", parent)
        self.position_id = position_id
        self.move(initial_x, initial_y)
        _set_ex_style(int(self.winId()), add=WS_EX_NOACTIVATE | WS_EX_TRANSPARENT)

        self.lbl.setStyleSheet(_build_button_sheet(
            kb.get("clr_bg", "#0b0617"),
            kb.get("clr_border", "#401970"),
            kb.get("clr_bg_active", "#2ed573"),
            kb.get("clr_border_active", "#ffffff"),
            max(9, int(min(w, h) * 0.35)),
        ))
        self.set_neon_style(is_active=False)

    def _inject_cross_key(self, press_down, sys_key, vk, scan, press_enabled):
        if not press_enabled:
            return
        if sys_key in ("lmb", "rmb", "mmb"):
            _send_mouse(_MOUSE_FLAGS[(sys_key, press_down)])
        elif sys_key == "ск":
            if press_down:
                main_win = _find_main_window()
                mc = getattr(main_win, "mouse_controller", None) if main_win else None
                self.scroll_start_y = float(getattr(mc, "current_y", 0.5)) if mc else 0.5
            else:
                self.scroll_start_y = None
        elif sys_key in ("osk", "лп", "app"):
            if press_down:
                if sys_key == "app":
                    main_win = _find_main_window()
                    if main_win and main_win.metaObject().indexOfMethod("bring_to_foreground()") != -1:
                        QMetaObject.invokeMethod(main_win, "bring_to_foreground",
                                                  Qt.ConnectionType.QueuedConnection)
                else:
                    exe = "osk.exe" if sys_key == "osk" else "magnify.exe"
                    threading.Thread(target=_start_file, args=(exe,), daemon=True).start()
        elif sys_key == "win":
            try:
                ctypes.windll.user32.keybd_event(VK_LWIN, 0,
                                                  0 if press_down else KEYEVENTF_KEYUP, 0)
            except Exception:
                pass
        elif vk != 0:
            try:
                flags = KEYEVENTF_SCANCODE
                if not press_down:
                    flags |= KEYEVENTF_KEYUP
                ctypes.windll.user32.keybd_event(vk, scan, flags, 0)
            except Exception:
                pass

    def _release_cross_key(self):
        self.set_neon_style(is_active=False)
        config = config_manager.load_config()
        prof = config.get("current_profile", "Default Profile")
        kb = config["profiles"][prof].get("kb", {})
        press_enabled = kb.get("overlay_press_enabled", True)
        vk, scan = _hardware_codes(self.key_name)
        self._inject_cross_key(False, self.key_name, vk, scan, press_enabled)
        self.is_physically_pressed = False

    def check_mouse_hover_trigger(self):
        is_ctrl = bool(ctypes.windll.user32.GetAsyncKeyState(VK_CONTROL) & 0x8000)
        hwnd = int(self.winId())
        try:
            current = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            if is_ctrl:
                # Ctrl зажат: режим перетаскивания — клик-сквозь выключаем,
                # отпускаем зажатую клавишу и НЕ эмулируем ховер.
                if current & WS_EX_TRANSPARENT:
                    _set_ex_style(hwnd, remove=WS_EX_TRANSPARENT)
                if self.is_physically_pressed:
                    self._release_cross_key()
                return
            else:
                if not (current & WS_EX_TRANSPARENT):
                    _set_ex_style(hwnd, add=WS_EX_TRANSPARENT)
        except Exception:
            pass

        if self.is_dragging:
            return

        config = config_manager.load_config()
        prof = config.get("current_profile", "Default Profile")
        kb = config["profiles"][prof].get("kb", {})
        press_enabled = kb.get("overlay_press_enabled", True)
        vk, scan = _hardware_codes(self.key_name)

        is_hovered = self.geometry().contains(QCursor.pos())
        if is_hovered and not self.is_physically_pressed:
            self.set_neon_style(is_active=True)
            self._inject_cross_key(True, self.key_name, vk, scan, press_enabled)
            self.is_physically_pressed = True
        elif not is_hovered and self.is_physically_pressed:
            self._release_cross_key()


# ---------------------------------------------------------------------------
# Полоса фокуса (Технология №4)
# ---------------------------------------------------------------------------
class FloatingFocusLine(QWidget):
    def __init__(self, position_id, line_name, initial_x, initial_y, w, h):
        super().__init__(None)
        self.position_id = position_id
        self.line_name = line_name
        self.is_dragging = False
        self.drag_position = QPoint()

        cfg = config_manager.load_config()
        prof = cfg.get("current_profile", "Default Profile")
        kb = cfg["profiles"][prof].get("kb", {})
        opacity_pct = kb.get("focus_lines_opacity", 40)
        self.active_mode = kb.get("focus_lines_binds", {}).get(position_id, {}).get("mode", "hover")

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint
                            | Qt.WindowType.WindowStaysOnTopHint
                            | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(int(w), int(h))
        self.setWindowOpacity(opacity_pct / 100.0)
        self.move(int(initial_x), int(initial_y))
        _set_ex_style(int(self.winId()), add=WS_EX_NOACTIVATE)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.lbl = QLabel(self.line_name)
        self.lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl.setStyleSheet(FOCUS_LINE_SHEET)
        self.layout.addWidget(self.lbl)

        self.focus_timer = QTimer(self)
        self.focus_timer.timeout.connect(self.check_focus_line_hover)
        self.focus_timer.start(50)

    def _set_active(self, state):
        if self.lbl.property("active") != state:
            self.lbl.setProperty("active", state)
            self.lbl.style().unpolish(self.lbl)
            self.lbl.style().polish(self.lbl)

    def check_focus_line_hover(self):
        if self.is_dragging:
            return
        is_hovered = self.geometry().contains(QCursor.pos())
        if is_hovered and self.active_mode == "hover":
            self.raise_()
            self.activateWindow()
            self._set_active("hover_active")
        elif not is_hovered:
            # сброс любого визуального состояния (hover И click) при уходе курсора
            self._set_active("")

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                self.is_dragging = True
                event.accept()
                return
            if self.active_mode == "click":
                self.raise_()
                self.activateWindow()
                self._set_active("click_active")
                event.accept()
                return
        event.ignore()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() & Qt.MouseButton.LeftButton and self.is_dragging:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if not self.is_dragging:
            return
        self.is_dragging = False
        geo = self.geometry()
        config = config_manager.load_config()
        prof = config.get("current_profile", "Default Profile")
        kb = config["profiles"][prof]["kb"]
        kb.setdefault("overlay_positions", {})[f"focus_line_4v_{self.position_id}"] = [geo.x(), geo.y()]
        config_manager.save_config(config)
        event.accept()


# ---------------------------------------------------------------------------
# Глобальный контроллер оверлеев
# ---------------------------------------------------------------------------
class OverlayKeysManager:
    def __init__(self):
        self.active_buttons = []

    def spawn_overlay_buttons(self, keys_list):
        self.destroy_all_buttons()
        config = config_manager.load_config()
        prof = config.get("current_profile", "Default Profile")
        kb = config["profiles"][prof].get("kb", {})
        saved = kb.get("overlay_positions", {})
        btn_size = kb.get("overlay_size", 60)

        start_x, start_y = 200, 150
        spacing = int(btn_size + 10)

        for idx, key_text in enumerate(keys_list):
            pure_key_id = key_text.lower()
            default = (start_x + idx * spacing, start_y)
            current_x, current_y = _resolve_position(saved, pure_key_id, default)
            button_window = FloatingOverlayKey(key_text, current_x, current_y)
            button_window.show()
            self.active_buttons.append(button_window)

        if kb.get("cross_enabled", False):
            self.spawn_only_cross_buttons()
        if kb.get("focus_lines_enabled", False):
            self.spawn_focus_lines_hardware()

    def spawn_only_cross_buttons(self):
        self.destroy_only_cross_buttons()
        config = config_manager.load_config()
        prof = config.get("current_profile", "Default Profile")
        kb = config["profiles"][prof].get("kb", {})
        binds = kb.get("cross_custom_binds", {})
        saved = kb.get("overlay_positions", {})

        cx, cy = 800, 450

        def dim(pos, default_w, default_h):
            b = binds.get(pos, {})
            return b.get("w", default_w), b.get("h", default_h)

        t_w, t_h = dim("top", 60, 40)
        b_w, b_h = dim("bottom", 60, 40)
        l_w, l_h = dim("left", 60, 40)
        r_w, r_h = dim("right", 60, 40)
        c_w, c_h = dim("center", 60, 40)

        blueprint = [
            ("top",    binds.get("top", {}).get("key", "🡡"),    cx - t_w // 2,     cy - t_h - 75),
            ("bottom", binds.get("bottom", {}).get("key", "🡣"), cx - b_w // 2,     cy + 75),
            ("left",   binds.get("left", {}).get("key", "🡠"),   cx - l_w - 75,     cy - l_h // 2),
            ("right",  binds.get("right", {}).get("key", "🡢"),  cx + 75,           cy - r_h // 2),
            ("center", binds.get("center", {}).get("key", "Space"), cx - c_w // 2, cy + 35),
        ]

        for pos_id, key_char, def_x, def_y in blueprint:
            if not binds.get(pos_id, {}).get("visible", True):
                continue
            uid = f"cross_4v_{pos_id}"
            target_x, target_y = _resolve_position(saved, uid, (def_x, def_y))
            cross_window = FloatingCrossKey(pos_id, key_char, target_x, target_y)

            # ЮВЕЛИРНОЕ ДОСПАВНИВАНИЕ позиции без перезапуска клавиатуры
            def make_release(win_obj, key_id):
                def actual_release(event):
                    win_obj.is_dragging = False
                    cfg = config_manager.load_config()
                    p = cfg.get("current_profile", "Default Profile")
                    cfg["profiles"][p]["kb"].setdefault("overlay_positions", {})[key_id] = [
                        int(win_obj.geometry().x()), int(win_obj.geometry().y())
                    ]
                    config_manager.save_config(cfg)
                    event.accept()
                return actual_release

            cross_window.mouseReleaseEvent = make_release(cross_window, uid)
            cross_window.show()
            self.active_buttons.append(cross_window)

    def spawn_focus_lines_hardware(self):
        config = config_manager.load_config()
        prof = config.get("current_profile", "Default Profile")
        kb = config["profiles"][prof].get("kb", {})
        binds = kb.get("focus_lines_binds", {})
        saved = kb.get("overlay_positions", {})

        screen = QApplication.primaryScreen().geometry()
        cx = screen.width() // 2
        cy = screen.height() // 2
        offset = 120

        blueprint = [
            ("top",    "Вверх", cx - 150,         cy - offset - 40),
            ("bottom", "Вниз",  cx - 150,         cy + offset),
            ("left",   "Лево",  cx - offset - 40, cy - 150),
            ("right",  "Право", cx + offset,      cy - 150),
            ("nw",     "СЗ",    cx - offset - 80,  cy - offset - 40),
            ("ne",     "СВ",    cx + offset,      cy - offset - 40),
            ("sw",     "ЮЗ",    cx - offset - 80,  cy + offset),
            ("se",     "ЮВ",    cx + offset,       cy + offset),
        ]

        for pos_id, name, def_x, def_y in blueprint:
            bd = binds.get(pos_id, {"w": 100, "h": 20, "visible": True})
            if not bd.get("visible", True):
                continue
            w = bd.get("w", 100)
            h = bd.get("h", 20)
            uid = f"focus_line_4v_{pos_id}"
            target_x, target_y = _resolve_position(saved, uid, (def_x, def_y))
            line_window = FloatingFocusLine(pos_id, name, target_x, target_y, w, h)
            line_window.show()
            self.active_buttons.append(line_window)

    def destroy_only_cross_buttons(self):
        kept = []
        for btn in self.active_buttons:
            if (hasattr(btn, "position_id")
                    and btn.position_id in ("top", "bottom", "left", "right", "center")
                    and not hasattr(btn, "line_name")):
                try:
                    btn.close()
                    btn.deleteLater()
                except Exception:
                    pass
            else:
                kept.append(btn)
        self.active_buttons = kept

    def destroy_all_buttons(self):
        for btn in self.active_buttons:
            try:
                btn.close()
                btn.deleteLater()
            except Exception:
                pass
        self.active_buttons.clear()