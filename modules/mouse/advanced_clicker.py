# modules/mouse/advanced_clicker.py - ЧАСТЬ 1 ИЗ 4 (СТРУКТУРЫ WINAPI И ИНЖЕКТОРЫ СЕТКИ В ОЗУ)
import time
import math
import ctypes
import config_manager
from PyQt6.QtCore import QTimer

# =========================================================================
# НИЗКОУРОВНЕВАЯ АППАРАТНАЯ СИСТЕМА ВВОДА WINAPI ЧЕРЕЗ SENDINPUT
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
MOUSEEVENTF_WHEEL = 0x0800
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_VIRTUALDESK = 0x4000  # Стабилизатор 4K координатной сетки под масштабирование Windows 11

def hardware_mouse_action_raw(flag):
    """Шлет атомарное событие зажима/отжатия клика на аппаратном уровне WinAPI"""
    extra = ctypes.pointer(ctypes.c_ulong(0))
    inp = INPUT()
    inp.type = INPUT_MOUSE
    inp.u.mi = MOUSEINPUT(0, 0, 0, flag | MOUSEEVENTF_VIRTUALDESK, 0, extra)
    ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))

def hardware_mouse_wheel_raw(amount):
    """Шлет аппаратный тик колеса мыши, стабильно работающий в шутерах и 3D играх"""
    extra = ctypes.pointer(ctypes.c_ulong(0))
    inp = INPUT()
    inp.type = INPUT_MOUSE
    inp.u.mi = MOUSEINPUT(0, 0, amount, MOUSEEVENTF_WHEEL | MOUSEEVENTF_VIRTUALDESK, 0, extra)
    ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))
# modules/mouse/advanced_clicker.py - ЧАСТЬ 2 ИЗ 4 (ОПТИМИЗАЦИЯ ПАМЯТИ И СБРОСЫ СОСТОЯНИЙ МАКРОСОВ)
class AdvancedDwellClicker:
    def __init__(self):
        self.last_move_time = time.time()
        self.anchor_x = 0.0
        self.anchor_y = 0.0
        self.is_locked = False
        self.click_type = "left"
        self.panel_ref = None
        
        # 🔥 ВЫСШАЯ ОПТИМИЗАЦИЯ ОЗУ: Считываем масштаб экрана ровно ОДИН РАЗ при старте класса!
        # Убирает тяжелую нагрузку GetDC из циклов 144 Гц, сбивая загрузку ЦП обратно к 6%
        try:
            hdc = ctypes.windll.user32.GetDC(0)
            self.cached_dpi_scale = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88) / 96.0
            ctypes.windll.user32.ReleaseDC(0, hdc)
        except:
            self.cached_dpi_scale = 2.0
            
        # Загружаем физическую матрицу монитора один раз в оперативную память (3840x2160)
        self.cached_scr_w = ctypes.windll.user32.GetSystemMetrics(0)
        self.cached_scr_h = ctypes.windll.user32.GetSystemMetrics(1)
        
        self.release_timer = QTimer()
        self.release_timer.setSingleShot(True)
        self.release_timer.timeout.connect(self.execute_forced_release)
        self.currently_held_button = None
        
        self.is_drag_holding = False
        self.drag_held_button_type = None
        
        self.is_2k_holding = False
        self.combo_lead_button = None
        self.combo_attack_button = None
        self.timer_2k = QTimer()
        self.timer_2k.setSingleShot(True)
        self.timer_2k.timeout.connect(self.reset_2k_combo_state)
        
        self.is_scroll_joystick_active = False
        self.scroll_start_y = 0.0
        self.scroll_last_pos_time = time.time()
        self.scroll_hardware_timer = QTimer()
        self.scroll_hardware_timer.timeout.connect(self.execute_scroll_wheel_tick)
        self.current_scroll_direction = "neutral"
        self.current_scroll_speed = 0

    def execute_forced_release(self):
        button_type = self.currently_held_button
        if button_type == "left":
            hardware_mouse_action_raw(MOUSEEVENTF_LEFTUP)
        elif button_type == "right":
            hardware_mouse_action_raw(MOUSEEVENTF_RIGHTUP)
        self.currently_held_button = None
        if self.panel_ref and button_type:
            self.panel_ref.uncheck_hold_visuals(button_type)

    def reset_drag_hold_state(self):
        if self.is_drag_holding and self.drag_held_button_type:
            if self.drag_held_button_type == "left":
                hardware_mouse_action_raw(MOUSEEVENTF_LEFTUP)
            elif self.drag_held_button_type == "middle":
                hardware_mouse_action_raw(MOUSEEVENTF_MIDDLEUP)
            elif self.drag_held_button_type == "right":
                hardware_mouse_action_raw(MOUSEEVENTF_RIGHTUP)
            self.is_drag_holding = False
            self.drag_held_button_type = None

    def reset_2k_combo_state(self):
        if self.is_2k_holding and self.combo_lead_button:
            if self.combo_lead_button == "left":
                hardware_mouse_action_raw(MOUSEEVENTF_LEFTUP)
            elif self.combo_lead_button == "right":
                hardware_mouse_action_raw(MOUSEEVENTF_RIGHTUP)
            self.is_2k_holding = False
            self.combo_lead_button = None
            self.combo_attack_button = None
            self.click_type = "left"
            if self.panel_ref:
                self.panel_ref.uncheck_hold_visuals("2k_combo_finished")

    def close_scroll_joystick_hardware(self):
        self.scroll_hardware_timer.stop()
        self.is_scroll_joystick_active = False
        self.current_scroll_direction = "neutral"
        self.current_scroll_speed = 0
        import win32con
        ctypes.windll.user32.SystemParametersInfoW(win32con.SPI_SETCURSORS, 0, None, 0)

    def execute_scroll_wheel_tick(self):
        if not self.is_scroll_joystick_active:
            return
        if self.current_scroll_direction == "up":
            hardware_mouse_wheel_raw(120)
        elif self.current_scroll_direction == "down":
            hardware_mouse_wheel_raw(-120)

# modules/mouse/advanced_clicker.py - ЧАСТЬ 3 ИЗ 4 (МЕТОД CHECK_DWELL И ВЫРАВНИВАНИЕ СЕТКИ ИЗ ОЗУ)
    def check_dwell(self, current_virtual_x, current_virtual_y, click_delay=0.6, click_radius=15):
        # НЕВИДИМЫЙ ИГРОВОЙ СКРОЛЛ: Перехват ИИ-координат лица в реальном времени
        if self.is_scroll_joystick_active:
            local_y = current_virtual_y - self.scroll_start_y
            abs_dy = abs(local_y)
            
            # 1. АВТО-ОТКЛЮЧЕНИЕ ПРИ ОСТАНОВКЕ ГОЛОВЫ
            dist_moved = math.hypot(current_virtual_x - self.anchor_x, current_virtual_y - self.anchor_y)
            if dist_moved > 5:
                self.scroll_last_pos_time = time.time()
                self.anchor_x = current_virtual_x
                self.anchor_y = current_virtual_y
            else:
                if time.time() - self.scroll_last_pos_time > 1.0:
                    self.close_scroll_joystick_hardware()
                    self.is_locked = True
                    self.last_move_time = time.time()
                    if self.panel_ref:
                        self.panel_ref.uncheck_hold_visuals("scroll_mode_finished")
                    return 0.0
                    
            # 2. ЖЕЛЕЗНЫЙ РАСЧЕТ НАПРАВЛЕНИЯ И 3-Х ИГРОВЫХ СКОРОСТЕЙ ЗУМА
            direction = "up" if local_y < 0 else "down"
            if abs_dy <= 25:  # Мертвая зона покоя
                self.scroll_hardware_timer.stop()
                self.current_scroll_direction = "neutral"
                self.current_scroll_speed = 0
            else:
                self.current_scroll_direction = direction
                if abs_dy <= 80:
                    interval_ms = 700
                elif abs_dy <= 180:
                    interval_ms = 300
                else:
                    interval_ms = 90
                if not self.scroll_hardware_timer.isActive() or self.scroll_hardware_timer.interval() != interval_ms:
                    self.scroll_hardware_timer.start(interval_ms)
            return 0.0

        if getattr(self, 'currently_held_button', None) is not None:
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
                # 🔥 ВЫСШАЯ ОПТИМИЗАЦИЯ СЕТКИ 4K: Читаем готовые коэффициенты из ОЗУ без GetDC вызовов!
                physical_x = int(current_virtual_x * self.cached_dpi_scale)
                physical_y = int(current_virtual_y * self.cached_dpi_scale)

                # Пересчитываем в абсолютную сетку Win32 (0 - 65535) по кэшированным метрикам экрана
                nx = int((physical_x * 65536) / self.cached_scr_w)
                ny = int((physical_y * 65536) / self.cached_scr_h)

                # Аппаратно удерживаем мышь на месте перед генерацией макроса
                extra = ctypes.pointer(ctypes.c_ulong(0))
                move_inp = INPUT()
                move_inp.type = INPUT_MOUSE
                move_inp.u.mi = MOUSEINPUT(nx, ny, 0, MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_VIRTUALDESK, 0, extra)
                ctypes.windll.user32.SendInput(1, ctypes.byref(move_inp), ctypes.sizeof(move_inp))
                time.sleep(0.005)
# modules/mouse/advanced_clicker.py - ЧАСТЬ 4 ИЗ 4 (ОПТИМИЗИРОВАННОЕ ВЫПОЛНЕНИЕ МАКРОСОВ И ЗАВЕРШЕНИЕ ФАЙЛА)
                fired_mode = self.click_type
                use_left_hold = False
                left_seconds = 1
                use_right_hold = False
                right_seconds = 4
                use_drag_hold = False
                use_double_click = False
                use_2k_combo = False
                use_scroll_mode = False

                if self.panel_ref:
                    use_left_hold = self.panel_ref.chk_hold_left.isChecked()
                    left_seconds = self.panel_ref.spin_hold_left.value()
                    use_right_hold = self.panel_ref.chk_hold_right.isChecked()
                    right_seconds = self.panel_ref.spin_hold_right.value()
                    use_drag_hold = self.panel_ref.chk_drag_hold.isChecked()
                    use_double_click = self.panel_ref.chk_double_click.isChecked()
                    use_2k_combo = self.panel_ref.chk_2k_combo.isChecked()
                    use_scroll_mode = self.panel_ref.chk_scroll_mode.isChecked()

                # РЕЖИМ 1: ДЖОЙСТИК-СКРОЛЛ ДЛЯ ИГР
                if use_scroll_mode:
                    self.scroll_start_y = current_virtual_y
                    self.scroll_last_pos_time = time.time()
                    self.is_scroll_joystick_active = True
                    self.current_scroll_direction = "neutral"
                    self.current_scroll_speed = 0
                    
                    h_cursor = ctypes.windll.user32.LoadCursorW(0, 32645)
                    ctypes.windll.user32.SetSystemCursor(h_cursor, 32512)
                    
                    if self.panel_ref:
                        self.panel_ref.update_button_styles()
                    self.is_locked = True
                    return 0.0

                # РЕЖИМ 2: ИГРОВОЙ КОМБО-МАКРОС «2К»
                if use_2k_combo:
                    is_lmb_selected = self.panel_ref.combo_buttons_selected.get("left", False)
                    is_rmb_selected = self.panel_ref.combo_buttons_selected.get("right", False)
                    lead_btn = "right" if use_right_hold else ("left" if use_left_hold else None)
                    if not lead_btn and is_rmb_selected:
                        lead_btn = "right"
                    attack_btn = "left" if lead_btn == "right" else "right"
                    hold_duration = right_seconds if lead_btn == "right" else left_seconds
                    
                    if not self.is_2k_holding:
                        self.combo_lead_button = lead_btn
                        self.combo_attack_button = attack_btn
                        if lead_btn == "right":
                            hardware_mouse_action_raw(MOUSEEVENTF_RIGHTDOWN)
                        elif lead_btn == "left":
                            hardware_mouse_action_raw(MOUSEEVENTF_LEFTDOWN)
                        self.is_2k_holding = True
                        self.timer_2k.start(hold_duration * 1000)
                        
                    if attack_btn == "left" and is_lmb_selected:
                        hardware_mouse_action_raw(MOUSEEVENTF_LEFTDOWN); hardware_mouse_action_raw(MOUSEEVENTF_LEFTUP)
                    elif attack_btn == "right" and is_rmb_selected:
                        hardware_mouse_action_raw(MOUSEEVENTF_RIGHTDOWN); hardware_mouse_action_raw(MOUSEEVENTF_RIGHTUP)
                    if self.panel_ref:
                        self.panel_ref.update_button_styles()
                    self.is_locked = True
                    return 0.0

                # РЕЖИМ 3: ДВОЙНОЙ КЛИК «2х»
                if use_double_click:
                    if fired_mode == "left":
                        hardware_mouse_action_raw(MOUSEEVENTF_LEFTDOWN); hardware_mouse_action_raw(MOUSEEVENTF_LEFTUP)
                        time.sleep(0.05)
                        hardware_mouse_action_raw(MOUSEEVENTF_LEFTDOWN); hardware_mouse_action_raw(MOUSEEVENTF_LEFTUP)
                    elif fired_mode == "right":
                        hardware_mouse_action_raw(MOUSEEVENTF_RIGHTDOWN); hardware_mouse_action_raw(MOUSEEVENTF_RIGHTUP)
                        time.sleep(0.05)
                        hardware_mouse_action_raw(MOUSEEVENTF_RIGHTDOWN); hardware_mouse_action_raw(MOUSEEVENTF_RIGHTUP)
                    elif fired_mode == "middle":
                        hardware_mouse_action_raw(MOUSEEVENTF_MIDDLEDOWN); hardware_mouse_action_raw(MOUSEEVENTF_MIDDLEUP)
                        time.sleep(0.05)
                        hardware_mouse_action_raw(MOUSEEVENTF_MIDDLEDOWN); hardware_mouse_action_raw(MOUSEEVENTF_MIDDLEUP)
                    self.click_type = "left"
                    if self.panel_ref:
                        self.panel_ref.uncheck_hold_visuals("double_click_finished")
                        self.panel_ref.update_button_styles()
                    self.is_locked = True
                    return 0.0

                # РЕЖИМ 4: ЗАЖИМ ДЛЯ ПЕРЕТАСКИВАНИЯ ПАПОК «УДЕРЖ»
                if use_drag_hold:
                    if not self.is_drag_holding:
                        self.drag_held_button_type = fired_mode
                        if fired_mode == "left":
                            hardware_mouse_action_raw(MOUSEEVENTF_LEFTDOWN)
                        elif fired_mode == "middle":
                            hardware_mouse_action_raw(MOUSEEVENTF_MIDDLEDOWN)
                        elif fired_mode == "right":
                            hardware_mouse_action_raw(MOUSEEVENTF_RIGHTDOWN)
                        self.is_drag_holding = True
                        if self.panel_ref:
                            self.panel_ref.update_button_styles()
                    else:
                        if self.drag_held_button_type == "left":
                            hardware_mouse_action_raw(MOUSEEVENTF_LEFTUP)
                        elif self.drag_held_button_type == "middle":
                            hardware_mouse_action_raw(MOUSEEVENTF_MIDDLEUP)
                        elif self.drag_held_button_type == "right":
                            hardware_mouse_action_raw(MOUSEEVENTF_RIGHTUP)
                        self.is_drag_holding = False
                        self.drag_held_button_type = None
                        self.click_type = "left"
                        if self.panel_ref:
                            self.panel_ref.uncheck_hold_visuals("drag_hold_finished")
                            self.panel_ref.update_button_styles()
                    self.is_locked = True
                    return 0.0

                # РЕЖИМ 5: ДЛИТЕЛЬНЫЕ ЗАЖИМЫ НА СЕКУНДЫ ПО ТАЙМЕРУ
                if fired_mode == "left" and use_left_hold:
                    if self.currently_held_button:
                        self.execute_forced_release()
                    hardware_mouse_action_raw(MOUSEEVENTF_LEFTDOWN)
                    self.currently_held_button = "left"
                    self.release_timer.start(left_seconds * 1000)
                elif fired_mode == "right" and use_right_hold:
                    if self.currently_held_button:
                        self.execute_forced_release()
                    hardware_mouse_action_raw(MOUSEEVENTF_RIGHTDOWN)
                    self.currently_held_button = "right"
                    self.release_timer.start(right_seconds * 1000)
                else:
                    if fired_mode == "left":
                        hardware_mouse_action_raw(MOUSEEVENTF_LEFTDOWN); hardware_mouse_action_raw(MOUSEEVENTF_LEFTUP)
                    elif fired_mode == "right":
                        hardware_mouse_action_raw(MOUSEEVENTF_RIGHTDOWN); hardware_mouse_action_raw(MOUSEEVENTF_RIGHTUP)
                    elif fired_mode == "middle":
                        hardware_mouse_action_raw(MOUSEEVENTF_MIDDLEDOWN); hardware_mouse_action_raw(MOUSEEVENTF_MIDDLEUP)
                        
                if fired_mode in ["right", "middle"]:
                    self.click_type = "left"
                if self.panel_ref:
                    self.panel_ref.update_button_styles()
                self.is_locked = True
                return 0.0
                
        return progress

    def reset(self, start_x, start_y):
        if getattr(self, 'currently_held_button', None):
            self.execute_forced_release()
        if getattr(self, 'is_drag_holding', False):
            self.reset_drag_hold_state()
        if self.panel_ref:
            self.panel_ref.uncheck_hold_visuals("drag_hold_finished")
        if getattr(self, 'is_2k_holding', False):
            self.timer_2k.stop()
            self.reset_2k_combo_state()
        self.last_move_time = time.time()
        self.anchor_x = start_x
        self.anchor_y = start_y
        self.click_type = "left"
        self.is_locked = True
