# config_manager.py
import os
import json
import copy  # Подключаем модуль для создания изолированных копий памяти, защищая от рассинхрона модулей

# Определяем путь к файлу сохранения настроек в корне проекта
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

# Глобальная переменная модуля для хранения кэша настроек в оперативной памяти (ОЗУ)
_CONFIG_RAM_CACHE = None

# Базовая структура настроек по умолчанию (Дополнили вашими параметрами мыши и Оверлеев)
DEFAULT_CONFIG = {
    "current_profile": "Default Profile",
    "window_settings": {
        "opacity": 100,
        "position_x": 100,
        "position_y": 100
    },
    "profiles": {
        "Default Profile": {
            "video": {
                "main_toggle": True,
                "online_mode": True,
                "tracking_mode": True,
                "tracking_alpha": 0.15,
                "tracking_show_dot": True,
                "tracking_show_box": True,
                "resolution": "640x480",
                "fps": 30,
                "video_format": "MJPG",
                "setting_1": True,
                "setting_2": True,
                "setting_3": True,
                "setting_4": True
            },
            "mouse": {
                "main_toggle": True,
                "autoclicker": False,
                "panel_on_screen": False,
                "move_mode": True,
                "click_mode": True,
                "speed": 25.0,
                "smooth": 0.12,
                "threshold": 0.15,
                
                "use_win_mouse": True,
                "show_custom_cursor": False,
                "show_click_circle": True,
                "click_sound_enabled": True,
                "click_delay": 0.6,
                "click_radius": 15,
                "click_hold_ms": 50,
                "selected_sound_file": "default",
                
                # НАШИ НОВЫЕ ИИ-ПАРАМЕТРЫ ПАНЕЛИ ИЗ 8 КНОПОК И ДВУХУРОВНЕВОЙ ФИКСАЦИИ:
                "toolbar_enabled": False,       
                "toolbar_auto_hide": True,      
                "toolbar_size_cm": 5,           
                "toolbar_anchor_x": -1,         
                "toolbar_anchor_y": 0,          
                
                "setting_1": True,
                "setting_2": True,
                "setting_3": True,
                "setting_4": True
            },

            "kb": {
                "main_toggle": True,
                "gestures_enabled": True,
                "hotkeys_enabled": False,
                "overlay_opacity": 100,
                "overlay_size": 60,
                "overlay_press_enabled": True,
                "overlay_selected_keys": [],
                # ИСПРАВЛЕНО: Добавляем словарь для хранения четырех кастомных режимов нажатия оверлейных кнопок
                "overlay_modes": {}, 
                "cross_enabled": False,
                "setting_1": True,
                "setting_2": True,
                "setting_3": True,
                "setting_4": True
            },
            "voice": {
                "main_toggle": True,
                "mode": "Стандартный",
                "setting_1": True,
                "setting_2": True,
                "setting_3": True,
                "setting_4": True
            }
        },
        "Gaming": {},
        "Work": {}
    }
}

# Заполняем пустые профили копией дефолтного для бесконфликтного старта
DEFAULT_CONFIG["profiles"]["Gaming"] = json.loads(json.dumps(DEFAULT_CONFIG["profiles"]["Default Profile"]))
DEFAULT_CONFIG["profiles"]["Work"] = json.loads(json.dumps(DEFAULT_CONFIG["profiles"]["Default Profile"]))

def load_config():
    """Загружает конфигурацию из ОЗУ. Отдает изолированную копию, защищая от рассинхрона."""
    global _CONFIG_RAM_CACHE
    
    # Если данные уже есть в ОЗУ, мгновенно отдаем их независимую глубокую копию (диск = 0% нагрузки)
    if _CONFIG_RAM_CACHE is not None:
        return copy.deepcopy(_CONFIG_RAM_CACHE)
        
    # Если кэш пуст (первый запуск программы), проверяем и читаем файл на диске
    if not os.path.exists(CONFIG_FILE):
        _CONFIG_RAM_CACHE = DEFAULT_CONFIG
        save_config(DEFAULT_CONFIG)
        return copy.deepcopy(_CONFIG_RAM_CACHE)
        
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            
            # ЗАЩИТА СТАРЫХ КОНФИГОВ: гарантируем, что новые параметры добавятся без поломки файла
            for prof_name in data.get("profiles", {}):
                # Проверка для секции мыши
                mouse_conf = data["profiles"][prof_name].get("mouse", {})
                for key, def_val in DEFAULT_CONFIG["profiles"]["Default Profile"]["mouse"].items():
                    if key not in mouse_conf:
                        mouse_conf[key] = def_val
                        
                # Проверка для секции клавиатуры (гарантируем наличие overlay_modes)
                kb_conf = data["profiles"][prof_name].get("kb", {})
                for key, def_val in DEFAULT_CONFIG["profiles"]["Default Profile"]["kb"].items():
                    if key not in kb_conf:
                        kb_conf[key] = def_val
            
            # Сохраняем обработанную конфигурацию в кэш ОЗУ
            _CONFIG_RAM_CACHE = data
            return copy.deepcopy(_CONFIG_RAM_CACHE)
    except Exception:
        _CONFIG_RAM_CACHE = DEFAULT_CONFIG
        return copy.deepcopy(_CONFIG_RAM_CACHE)

def save_config(config_data):
    """Записывает переданный словарь настроек в файл config.json и мгновенно обновляет кэш ОЗУ"""
    global _CONFIG_RAM_CACHE
    # Сохраняем глубокую копию в оперативную память для предотвращения взаимного влияния потоков
    _CONFIG_RAM_CACHE = copy.deepcopy(config_data)
    
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"Ошибка при сохранении файла конфигурации: {e}")
        return False
