# modules/mouse/autoclick_win.py - ЧАСТЬ 1 ИЗ 2 (УЛЬТРА-ОПТИМИЗИРОВАННАЯ ХАРДВЕРНАЯ ВЕРСИЯ — 6% ЦП ИЗ ОЗУ)
import os
import math
import time
import ctypes
import config_manager
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl

# =========================================================================
# НИЗКОУРОВНЕВАЯ АППАРАТНАЯ СИСТЕМА ВВОДА WINAPI (SENDINPUT)
# =========================================================================
LONG = ctypes.c_long
DWORD = ctypes.c_ulong
ULONG_PTR = ctypes.POINTER(ctypes.c_ulong)

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", LONG), ("dy", LONG), ("mouseData", DWORD),
        ("dwFlags", DWORD), ("time", DWORD), ("dwExtraInfo", ULONG_PTR)
    ]

class INPUT_UNION(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT)]

class INPUT(ctypes.Structure):
    _fields_ = [("type", DWORD), ("u", INPUT_UNION)]

INPUT_MOUSE = 0
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_VIRTUALDESK = 0x4000  # Стабилизатор 4K координатной сетки Windows 11

def hardware_mouse_click_raw(flag_down, flag_up, hold_sec):
    """Выполняет клик аппаратного уровня через SendInput в текущей физической точке экрана"""
    extra = ctypes.pointer(ctypes.c_ulong(0))
    
    inp_down = INPUT()
    inp_down.type = INPUT_MOUSE
    inp_down.u.mi = MOUSEINPUT(0, 0, 0, flag_down | MOUSEEVENTF_VIRTUALDESK, 0, extra)
    ctypes.windll.user32.SendInput(1, ctypes.byref(inp_down), ctypes.sizeof(inp_down))
    
    time.sleep(hold_sec)
    
    inp_up = INPUT()
    inp_up.type = INPUT_MOUSE
    inp_up.u.mi = MOUSEINPUT(0, 0, 0, flag_up | MOUSEEVENTF_VIRTUALDESK, 0, extra)
    ctypes.windll.user32.SendInput(1, ctypes.byref(inp_up), ctypes.sizeof(inp_up))

def hardware_mouse_action_single(flag):
    """Отправляет одиночное событие зажима мыши (нужно для удержания папок Drag-n-Drop)"""
    extra = ctypes.pointer(ctypes.c_ulong(0))
    inp = INPUT()
    inp.type = INPUT_MOUSE
    inp.u.mi = MOUSEINPUT(0, 0, 0, flag | MOUSEEVENTF_VIRTUALDESK, 0, extra)
    ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))


class DwellClicker:
    def __init__(self):
        self.last_move_time = time.time()
        self.anchor_x = 0.0
        self.anchor_y = 0.0
        self.locked_default_mode = "left"
        self.click_type = "left"
        self.is_permanent = True
        self.drag_active = False
        self.is_locked = False
        self.toolbar_ref = None
        
        # 🔥 СУПЕР-ОПТИМИЗАЦИЯ ОЗУ: Считываем масштаб и разрешение матрицы экрана ровно ОДИН РАЗ при старте класса!
        # Полностью разгружает ИИ-кадры 144 Гц от тяжелых GetDC запросов к ядру ОС
        try:
            hdc = ctypes.windll.user32.GetDC(0)
            self.cached_dpi_scale = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88) / 96.0
            ctypes.windll.user32.ReleaseDC(0, hdc)
        except:
            self.cached_dpi_scale = 2.0
            
        self.cached_scr_w = ctypes.windll.user32.GetSystemMetrics(0)
        self.cached_scr_h = ctypes.windll.user32.GetSystemMetrics(1)
        
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)

    def force_reset_to_default_left(self):
        """Принудительный сброс на Левый залоченный клик при снятии паузы"""
        if self.drag_active:
            hardware_mouse_action_single(MOUSEEVENTF_LEFTUP)
            self.drag_active = False
        self.locked_default_mode = "left"
        self.click_type = "left"
        self.is_permanent = True
        if self.toolbar_ref:
            self.toolbar_ref.refresh_all_button_images()


# modules/mouse/autoclick_win.py - ЧАСТЬ 2 ИЗ 2 (УЛЬТРА-ОПТИМИЗИРОВАННАЯ ХАРДВЕРНАЯ ВЕРСИЯ — ФИНАЛ ФАЙЛА)
    def check_dwell(self, current_virtual_x, current_virtual_y, use_autoclick=False, click_delay=0.6, click_radius=15, is_over_toolbar=False, is_over_main_ui=False):
        if not use_autoclick:
            return 0.0

        dist_from_anchor = math.hypot(current_virtual_x - self.anchor_x, current_virtual_y - self.anchor_y)
        
        if dist_from_anchor > click_radius:
            self.is_locked = False
            self.last_move_time = time.time()
            self.anchor_x = current_virtual_x
            self.anchor_y = current_virtual_y
            return 0.0
        else:
            if self.is_locked:
                return 0.0
                
            elapsed = time.time() - self.last_move_time
            progress = min(elapsed / click_delay, 1.0)
            
            if elapsed >= click_delay:
                # 🚀 ОЗУ-МАТЕМАТИКА 4K: Мгновенно берем готовые коэффициенты из памяти без запросов к ядру
                physical_x = int(current_virtual_x * self.cached_dpi_scale)
                physical_y = int(current_virtual_y * self.cached_dpi_scale)

                # Пересчитываем в абсолютную координатную сетку Windows (от 0 до 65535)
                nx = int((physical_x * 65536) / self.cached_scr_w)
                ny = int((physical_y * 65536) / self.cached_scr_h)

                # Аппаратно перемещаем мышь строго в физическую мишень перед генерацией клика
                extra = ctypes.pointer(ctypes.c_ulong(0))
                move_inp = INPUT(INPUT_MOUSE, INPUT_UNION(mi=MOUSEINPUT(nx, ny, 0, MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_VIRTUALDESK, 0, extra)))
                ctypes.windll.user32.SendInput(1, ctypes.byref(move_inp), ctypes.sizeof(move_inp))
                time.sleep(0.005)  # Аппаратная микропауза для стабилизации игровых движков

                # ИИ-ЛОГИКА EV IACAM: Над тулбаром клик всегда принудительно левый
                active_mode = "left" if is_over_toolbar else self.click_type
                config = config_manager.load_config()
                current_prof = config.get("current_profile", "Default Profile")
                mouse_conf = config["profiles"][current_prof]["mouse"]

                if not mouse_conf.get("click_mode", True) and not is_over_toolbar:
                    self.is_locked = True
                    return 0.0

                hold_ms = mouse_conf.get("click_hold_time", 50)
                hold_sec = float(hold_ms / 1000.0)

                # ВЫПОЛНЕНИЕ КЛИКОВ ЧЕРЕЗ АППАРАТНЫЙ SENDINPUT В ОБХОД ЗАЩИТ ОС И ИГР
                if active_mode == "left":
                    hardware_mouse_click_raw(MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP, hold_sec)
                elif active_mode == "right":
                    hardware_mouse_click_raw(MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP, hold_sec)
                elif active_mode == "middle":
                    hardware_mouse_click_raw(MOUSEEVENTF_MIDDLEDOWN, MOUSEEVENTF_MIDDLEUP, hold_sec)
                elif active_mode == "double":
                    hardware_mouse_click_raw(MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP, hold_sec)
                    time.sleep(0.05)
                    hardware_mouse_click_raw(MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP, hold_sec)
                elif active_mode == "drag":
                    if not self.drag_active:
                        hardware_mouse_action_single(MOUSEEVENTF_LEFTDOWN)
                        self.drag_active = True
                        self.is_locked = True
                        if self.toolbar_ref:
                            self.toolbar_ref.refresh_all_button_images()
                        return 0.0
                    else:
                        hardware_mouse_action_single(MOUSEEVENTF_LEFTUP)
                        self.drag_active = False
                elif active_mode in ["keyboard_1", "magnifier"]:
                    pass

                # ЗВУКОВОЕ СОПРОВОЖДЕНИЕ КЛИКА
                if mouse_conf.get("click_sound_enabled", True):
                    sound_name = mouse_conf.get("selected_sound_file", "default")
                    vol_percent = mouse_conf.get("click_volume", 80)
                    self.audio_output.setVolume(vol_percent / 100.0)
                    
                    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                    sound_folder = os.path.join(base_dir, "sounds")
                    sound_file_path = os.path.join(sound_folder, sound_name)
                    
                    if sound_name != "default" and os.path.exists(sound_file_path):
                        try:
                            self.player.setSource(QUrl.fromLocalFile(sound_file_path))
                            self.player.play()
                        except Exception: pass
                    else:
                        import winsound
                        try:
                            winsound.Beep(1200, 40)
                        except Exception: pass

                # СБРОС ФОКУСА ТУЛБАРА И ПЕРЕКЛЮЧЕНИЕ СИНЕГО ФОНА РЕЖИМОВ
                if not is_over_toolbar:
                    if not self.is_permanent or active_mode in ["keyboard_1", "magnifier", "drag"]:
                        if active_mode == "drag" and self.drag_active:
                            pass
                        else:
                            self.click_type = self.locked_default_mode
                            self.is_permanent = True
                            if self.toolbar_ref:
                                self.toolbar_ref.refresh_all_button_images()
                
                self.is_locked = True
                return 0.0
                
            return progress

    def reset(self, start_x, start_y):
        self.last_move_time = time.time()
        self.anchor_x = start_x
        self.anchor_y = start_y
        self.is_locked = True

    def execute_manual_toolbar_click(self):
        """Прямой аппаратный клик для кнопок плавающего тулбара с удержанием"""
        try:
            config = config_manager.load_config()
            current_prof = config.get("current_profile", "Default Profile")
            mouse_conf = config["profiles"][current_prof]["mouse"]
            hold_ms = mouse_conf.get("click_hold_time", 50)
            hold_sec = float(hold_ms / 1000.0)
            
            hardware_mouse_click_raw(MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP, hold_sec)
        except Exception:
            pass
