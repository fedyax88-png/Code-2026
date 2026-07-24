# modules/video/tracking.py - ЧАСТЬ 1 ИЗ 2
import os
import cv2
import math
import mediapipe as mp
import config_manager

class FaceTracker:
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, "face_landmarker.task")
        
        options = mp.tasks.vision.FaceLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=model_path),
            running_mode=mp.tasks.vision.RunningMode.IMAGE,
            output_face_blendshapes=True
        )
        self.landmarker = mp.tasks.vision.FaceLandmarker.create_from_options(options)
        
        self.smooth_x = None
        self.smooth_y = None
        
        self.smooth_box_min_x = None
        self.smooth_box_min_y = None
        self.smooth_box_max_x = None
        self.smooth_box_max_y = None
        
        self.last_valid_box = [0, 0, 0, 0]
        self.frame_counter = 0
        
        # ЭТАЛОННАЯ РУЧНАЯ МАТРИЦА ЦЕНТРИРОВАНИЯ ГОЛОВЫ
        self.zero_yaw = 0.0
        self.zero_pitch = 0.0
        self.zero_zoom_width = 140.0 
        self.need_calibration = False

        # БУФЕР ДЛЯ ЖЕСТКОГО ИИ-ФИЛЬТРА СГЛАЖИВАНИЯ ШУМА МИМИКИ ПО ТЗ
        self.prev_gestures = {}

    def reset(self):
        self.smooth_x = None
        self.smooth_y = None
        self.smooth_box_min_x = None
        self.smooth_box_min_y = None
        self.smooth_box_max_x = None
        self.smooth_box_max_y = None
        self.prev_gestures.clear()

    def calibrate_zero(self):
        self.need_calibration = True

    def _calculate_head_angles_original(self, first_face, w, h, current_box_width):
        try:
            nose = first_face[4]
            chin = first_face[152]
            left_eye = first_face[33]
            right_eye = first_face[263]

            nx, ny, nz = nose.x * w, nose.y * h, nose.z * w
            cx, cy, cz = chin.x * w, chin.y * h, chin.z * w
            lx, ly, lz = left_eye.x * w, left_eye.y * h, left_eye.z * w
            rx, ry, rz = right_eye.x * w, right_eye.y * h, right_eye.z * w

            mid_eyes_x = (lx + rx) / 2.0
            mid_eyes_z = (lz + rz) / 2.0
            raw_yaw = (nx - mid_eyes_x) * 2.2

            mid_eyes_y = (ly + ry) / 2.0
            raw_pitch = (ny - mid_eyes_y) * 1.8 - (cy - ny) * 0.15

            if self.need_calibration:
                self.zero_yaw = raw_yaw
                self.zero_pitch = raw_pitch
                self.zero_zoom_width = float(current_box_width)
                self.need_calibration = False 

            yaw_delta = raw_yaw - self.zero_yaw
            pitch_delta = raw_pitch - self.zero_pitch
            zoom_delta = ((current_box_width - self.zero_zoom_width) / self.zero_zoom_width) * 100.0

            turn_left = max(0.0, min(100.0, -yaw_delta * 3.5))
            turn_right = max(0.0, min(100.0, yaw_delta * 3.5))
            tilt_up = max(0.0, min(100.0, -pitch_delta * 4.0))
            tilt_down = max(0.0, min(100.0, pitch_delta * 3.5))
            zoom_in = max(0.0, min(100.0, zoom_delta * 4.5))
            zoom_out = max(0.0, min(100.0, -zoom_delta * 4.5))

            return turn_left, turn_right, tilt_up, tilt_down, zoom_in, zoom_out
        except Exception:
            return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
# modules/video/tracking.py - ЧАСТЬ 2 ИЗ 2
    def process_frame(self, frame, alpha=0.15):
        """
        Лёгкий метод считывания ИИ-весов MediaPipe, интегрированный с 
        динамическим фильтром экспоненциального сглаживания шума по ТЗ.
        """
        self.frame_counter += 1
        h, w, _ = frame.shape
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        
        detection_result = self.landmarker.detect(mp_image)
        
        # Полный пакет выходных ИИ-жестов
        gestures = {
            "brows_up": 0.0, "brows_down": 0.0, "brow_up": 0.0, "brows": 0.0,
            "blink_left": 0.0, "blink_right": 0.0, 
            "mouth_jaw": 0.0, "jaw_open": 0.0, "smile": 0.0, "smile_left": 0.0, "smile_right": 0.0,
            "pucker": 0.0, "turn_left": 0.0, "turn_right": 0.0, "tilt_up": 0.0, "tilt_down": 0.0,
            "zoom_in": 0.0, "zoom_out": 0.0
        }
        
        if detection_result.face_landmarks and len(detection_result.face_landmarks) > 0:
            first_face = detection_result.face_landmarks[0]
            
            nose = first_face[4]
            raw_x = float(nose.x * w)
            raw_y = float(nose.y * h)
            
            if self.smooth_x is None or self.smooth_y is None:
                self.smooth_x, self.smooth_y = raw_x, raw_y
            else:
                self.smooth_x = alpha * raw_x + (1.0 - alpha) * self.smooth_x
                self.smooth_y = alpha * raw_y + (1.0 - alpha) * self.smooth_y

            if self.frame_counter % 3 == 0 or not self.last_valid_box:
                x_coords = [lm.x * w for lm in first_face]
                y_coords = [lm.y * h for lm in first_face]
                self.last_valid_box = [int(min(x_coords)), int(min(y_coords)), int(max(x_coords)), int(max(y_coords))]

            # ЖЕСТКИЙ ФИКС ГЕОМЕТРИИ: Считаем живую ширину лица из актуального прямоугольника (Правый край минус Левый край)
            current_box_width = float(self.last_valid_box[2] - self.last_valid_box[0]) if self.last_valid_box else 140.0

            # ПРЕДОХРАНИТЕЛЬ: Задаем начальный ноль, если калибровка ещё ни разу не прожималась
            if getattr(self, 'zero_zoom_width', 140.0) == 140.0 or self.zero_zoom_width == 0.0:
                self.zero_zoom_width = current_box_width

            # 3. СБОР СЫРЫХ ДАННЫХ ИЗ МЕДИAПАЙП БЛЕНДШЕЙПОВ
            if detection_result.face_blendshapes and len(detection_result.face_blendshapes) > 0:
                blendshapes_list = detection_result.face_blendshapes[0]

                total_brow_up = 0.0
                smile_l, smile_r = 0.0, 0.0
                
                for category in blendshapes_list:
                    name = category.category_name
                    val = max(0.0, min(100.0, float(category.score) * 100.0))
                    
                    if name == "eyeBlinkLeft": gestures["blink_left"] = val
                    elif name == "eyeBlinkRight": gestures["blink_right"] = val
                    elif name == "jawOpen":
                        gestures["mouth_jaw"] = val
                        gestures["jaw_open"] = val
                    elif name == "mouthPucker": gestures["pucker"] = val
                    elif name == "mouthSmileLeft": smile_l = val
                    elif name == "mouthSmileRight": smile_r = val
                    elif name in ["browDownLeft", "browDownRight"]:
                        if val > gestures["brows_down"]: gestures["brows_down"] = val
                    elif name in ["browInnerUp", "browOuterUpLeft", "browOuterUpRight"]:
                        if val > total_brow_up: total_brow_up = val
                        
                gestures["brows_up"] = total_brow_up
                gestures["brow_up"] = total_brow_up
                gestures["brows"] = total_brow_up
                gestures["smile_left"] = smile_l
                gestures["smile_right"] = smile_r
                gestures["smile"] = (smile_l + smile_r) / 2.0

            # 4. РАСЧЕТ ПОВОРОТОВ И НАКЛОНОВ ГОЛОВЫ
            t_left, t_right, t_up, t_down, z_in, z_out = self._calculate_head_angles_original(first_face, w, h, current_box_width)
            gestures["turn_left"] = t_left; gestures["turn_right"] = t_right
            gestures["tilt_up"] = t_up; gestures["tilt_down"] = t_down
            gestures["zoom_in"] = z_in; gestures["zoom_out"] = z_out

            # =========================================================================
            #   МАТЕМАТИЧЕСКИЙ ФИЛЬТР ЭКСПОНЕНЦИАЛЬНОГО СГЛАЖИВАНИЯ ПО ПОЛЗУНКУ ИЗ JSON
            # =========================================================================
            try:
                config = config_manager.load_config()
                current_prof = config.get("current_profile", "Default Profile")
                smooth_pct = config["profiles"][current_prof]["kb"].get("smooth_factor", 50)
            except Exception:
                smooth_pct = 50

            # Переводим проценты ползунка (0-95%) в коэффициент веса текущего кадра (от 1.0 до 0.05)
            k_weight = 1.0 - (smooth_pct / 100.0)

            for key in gestures:
                if key in self.prev_gestures:
                    gestures[key] = k_weight * gestures[key] + (1.0 - k_weight) * self.prev_gestures[key]
                self.prev_gestures[key] = gestures[key]

            return True, self.smooth_x, self.smooth_y, self.last_valid_box, gestures
        
        return False, 0.0, 0.0, [0, 0, 0, 0], gestures
