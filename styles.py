# styles.py
import os

# Автоматический и точный поиск папки images относительно этого файла
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "images")

def get_image(filename):
    """Возвращает абсолютный и точный путь к картинке"""
    return os.path.join(IMAGES_DIR, filename)

# Цветовая палитра интерфейса
BG_MAIN = "#040320"        # Глубокий темно-фиолетовый (фон всего окна и верхней панели)
TEXT_WHITE = "#ffffff"     # Основной текст
TEXT_MUTED = "#a1a3b5"     # Приглушенный текст

# Акцентные цвета состояний
COLOR_PINK = "#ff007f"     # Розовая полосочка переключателя
COLOR_PURPLE = "#8a2be2"   # Фиолетовый оттенок
COLOR_GREEN = "#2ed573"    # Зеленый (Включено, Старт)
COLOR_RED = "#ff4757"      # Красный (Отключено, Стоп)

# === 1. ИНДИВИДУАЛЬНЫЙ СТИЛЬ ЛЕВОЙ ПАНЕЛИ (SIDEBAR) ===
# Сделан отдельным темным настраиваемым квадратом
STYLE_SIDEBAR_PANEL = """
    QFrame#Sidebar {
        background-color: #000308;       /* Темный независимый цвет фона */
        border: 2px solid #1a153a;       /* Своя обводка */
        border-radius: 12px;
    }
    QPushButton {
        background-color: #09071c;
        color: #a1a3b5;
        border: 1px solid #1c1742;
        border-radius: 6px;
        padding: 6px 12px;
        font-family: 'Segoe UI', sans-serif;
        font-size: 12px;
    }
    QPushButton:hover {
        background-color: #120e2e;
        color: #ffffff;
        border-color: #ff007f;
    }
    QComboBox {
        background-color: #09071c;
        color: #ffffff;
        border: 1px solid #1c1742;
        border-radius: 6px;
        padding: 4px;
    }
"""

# === 2. ИНДИВИДУАЛЬНЫЙ СТИЛЬ МОДУЛЯ 1 (ВИДЕО) ===
STYLE_VIDEO_MODULE = """
    QFrame#Card {
        background-color: #040B1E;       /* Индивидуальный фон внутренностей */
        border: 2px solid #00d2ff;       /* Своя обводка (например, голубой неон) */
        border-radius: 10px;
    }
    QPushButton {
        background-color: #0f0e26;
        color: #00d2ff;
        border: 1px solid #005f73;
        border-radius: 5px;
        padding: 5px 10px;
    }
    QPushButton:hover {
        background-color: #00d2ff;
        color: #000000;
        border-color: #ffffff;
    }
"""

# === 3. ИНДИВИДУАЛЬНЫЙ СТИЛЬ МОДУЛЯ 2 (МЫШЬ) ===
STYLE_MOUSE_MODULE = """
    QFrame#Card {
        background-color: #0C1D24;       /* Индивидуальный фон внутренностей */
        border: 2px solid #0CC61B;       /* Своя обводка (например, желтый неон) */
        border-radius: 10px;
    }
    QPushButton {
        background-color: #1a0f2b;
        color: #ffb703;
        border: 1px solid #946500;
        border-radius: 5px;
        padding: 5px 10px;
    }
    QPushButton:hover {
        background-color: #ffb703;
        color: #000000;
        border-color: #ffffff;
    }
"""

# === 4. ИНДИВИДУАЛЬНЫЙ СТИЛЬ МОДУЛЯ 3 (КЛАВИАТУРА) ===
STYLE_KB_MODULE = """
    QFrame#Card {
        background-color: #140D30;       /* Индивидуальный фон внутренностей */
        border: 2px solid #7F61E5;       /* Своя обводка (например, зеленый неон) */
        border-radius: 10px;
    }
    QPushButton {
        background-color: #0c182b;
        color: #2ed573;
        border: 1px solid #124024;
        border-radius: 5px;
        padding: 5px 10px;
    }
    QPushButton:hover {
        background-color: #2ed573;
        color: #000000;
        border-color: #ffffff;
    }
"""

# === 5. ИНДИВИДУАЛЬНЫЙ СТИЛЬ МОДУЛЯ 4 (ГОЛОСОВОЕ УПРАВЛЕНИЕ) ===
STYLE_VOICE_MODULE = """
    QFrame#Card {
        background-color:  #1F0D2B;       /* Индивидуальный фон внутренностей */
        border: 2px solid  #502548;       /* Своя обводка (розовый неон) */
        border-radius: 10px;
    }
    QPushButton {
        background-color: #210c24;
        color: #ff007f;
        border: 1px solid #800040;
        border-radius: 5px;
        padding: 5px 10px;
    }
    QPushButton:hover {
        background-color: #ff007f;
        color: #ffffff;
        border-color: #ffffff;
    }
"""

# Глобальные базовые стили для окна и текста (чтобы не ломать внутренности)
STYLE_SHEET = f"""
    QMainWindow {{
        background-color: {BG_MAIN};
    }}
    QLabel {{
        color: {TEXT_WHITE};
        font-family: 'Segoe UI', 'Arial', sans-serif;
    }}
"""
