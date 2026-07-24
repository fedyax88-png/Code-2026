# modules/video/start_camera.py - ЧАСТЬ 1 ИЗ 2
import cv2
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QElapsedTimer
from PyQt6.QtGui import QImage, QPixmap
import styles
import config_manager
from modules.video.tracking import FaceTracker

class CameraWorker(QThread):
    frame_received = pyqtSignal(QPixmap)
    fps_received = pyqtSignal(int)
    face_moved = pyqtSignal(float, float)
    head_size_calculated = pyqtSignal(int)
    
    # НОВЫЙ ИИ-СИГНАЛ: Отправляет готовый словарь мимики (0-100%) в главное окно диспетчера
    face_gestures_received = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = False
        self.cap = None
        self.tracker = None
        self.target_width = 640
        self.target_height = 480
        self.target_fps = 30

    def run(self):
        self.running = True
        
        try:
            self.tracker = FaceTracker()
            # ЖЕСТКИЙ ФИКС АВТОКАЛИБРОВКИ: сбрасываем ноль при каждом новом старте потока камеры!
            self.tracker.reset()
        except Exception as e:
            print(f"[ОШИБКА ИНИЦИАЛИЗАЦИИ ИИ]: {e}")
            self.tracker = None


        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
            
        if not self.cap.isOpened():
            print("[ОШИБКА] Веб-камера Logitech недоступна.")
            self.running = False
            return

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.target_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.target_height)
        self.cap.set(cv2.CAP_PROP_FPS, self.target_fps)
        
        sleep_time = int(1000 / self.target_fps)
        
        fps_timer = QElapsedTimer()
        fps_timer.start()
        frame_count = 0
# modules/video/start_camera.py - ЧАСТЬ 2 ИЗ 2
        # Инициализируем ОЗУ-кэш жестов в самом начале цикла, чтобы ядро Z3 его видело
        self.last_gestures_cache = {}

        while self.running:
            if self.cap is None or not self.cap.isOpened():
                break
                
            ret, frame = self.cap.read()
            if not ret or frame is None:
                continue
                
            if not self.running:
                break
                
            frame_count += 1
            if fps_timer.elapsed() >= 1000:
                real_fps = int((frame_count * 1000) / fps_timer.elapsed())
                self.fps_received.emit(real_fps)
                frame_count = 0
                fps_timer.restart()


            frame = cv2.flip(frame, 1)
            
            config = config_manager.load_config()
            current_prof = config.get("current_profile", "Default Profile")
            video_conf = config["profiles"][current_prof]["video"]
            
            is_tracking_enabled = video_conf.get("tracking_mode", True)
            
            if is_tracking_enabled and self.tracker and self.running:
                # ИСПРАВЛЕНО: Динамически подхватываем из ОЗУ-кэша измененный ползунком параметр сглаживания альфа
                current_alpha = video_conf.get("tracking_alpha", 0.15)
                
                try:
                    # Извлекаем расширенные данные, включая словарь мимики gestures
                    success, nx, ny, box, gestures = self.tracker.process_frame(frame, alpha=current_alpha)
                    if success and self.running:
                        # СОХРАНЯЕМ В ОЗУ-КЭШ: Мгновенно обновляем глобальный слепок для Set 1 и Set 2
                        self.last_gestures_cache = gestures.copy()
                        
                        self.face_moved.emit(nx, ny)
                        
                        # Если общий рубильник ИИ-мимики включен — транслируем жесты в систему
                        if video_conf.get("tracking_blendshapes", True):
                            self.face_gestures_received.emit(gestures)
                        
                        head_width = box[2] - box[0]
                        self.head_size_calculated.emit(head_width)
                        
                        show_box = video_conf.get("tracking_show_box", True)
                        if show_box:
                            cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), (255, 210, 0), 2)
                            
                        show_dot = video_conf.get("tracking_show_dot", True)
                        if show_dot:
                            cv2.circle(frame, (int(nx), int(ny)), 5, (0, 255, 0), -1)
                except RuntimeError:
                    break
                except Exception as e:
                    print(f"[Уведомление трекера]: {e}")

            if not self.running:
                break

            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            scaled_pixmap = QPixmap.fromImage(qt_image).scaled(
                320, 240, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            
            if self.running:
                self.frame_received.emit(scaled_pixmap)
            
            self.msleep(sleep_time)

        video_pixmap = QPixmap(styles.get_image("video.jpg"))
        if not video_pixmap.isNull():
            self.frame_received.emit(video_pixmap.scaled(320, 240, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def stop(self):
        self.running = False
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.cap = None
        self.quit()
        self.wait()
