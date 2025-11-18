import cv2
import json
import numpy as np
from pyzbar.pyzbar import decode
import requests
from io import BytesIO

class DetectorCartas:
    """Detector de cartas UNO mediante códigos QR"""
    
    def __init__(self, ip_webcam_url=None):
        """
        Inicializa el detector
        
        Args:
            ip_webcam_url: URL de IP Webcam
        """
        self.ip_webcam_url = ip_webcam_url
        self.cap = None
        self.ultima_carta_detectada = None
        self.frames_sin_deteccion = 0

    def conectar_camara(self):
        if self.ip_webcam_url:
            # Usar /shot.jpg para obtener frames individuales
            self.video_url = f"{self.ip_webcam_url}/shot.jpg"
            try:
                # Verificar conexión
                response = requests.get(self.ip_webcam_url, timeout=3)
                if response.status_code == 200:
                    print("conexion exitosa con IP Webcam")
                    # Probar obtener un frame
                    test_frame = requests.get(self.video_url, timeout=3)
                    if test_frame.status_code == 200:
                        print("video funcionando")
                        return True
                    else:
                        print("eror en el video")
                        return False
                else:
                    print("no se pudo conectar a IP Webcam")
                    return False
            except Exception as e:
                print(f"Error al conectar: {e}")
                return False
        else:
            # Modo cámara local
            self.cap = cv2.VideoCapture(0)
            if self.cap.isOpened():
                return True
            else:
                return False
    
    def obtener_frame(self):
        """Obtiene un frame de la cámara"""
        if self.ip_webcam_url:
            # Obtener frame desde IP Webcam usando /shot.jpg
            try:
                img_resp = requests.get(self.video_url, timeout=1)
                if img_resp.status_code != 200:
                    return False, None
                img_arr = np.array(bytearray(img_resp.content), dtype=np.uint8)
                frame = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)
                if frame is not None:
                    return True, frame
                else:
                    return False, None
            except Exception as e:
                print(f"error al obtener frame: {e}")
                return False, None
        else:
            # Obtener frame de cámara local
            return self.cap.read()
    
    def detectar_cartas_rectangulos(self, frame):
        """
        Detecta rectángulos blancos (cartas UNO) en el frame
        
        Returns:
            list: Lista de contornos de cartas detectadas
        """
        # Convertir a escala de grises
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Aplicar blur para reducir ruido
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Detectar bordes blancos (cartas UNO tienen borde blanco)
        # Umbral para detectar áreas blancas
        _, thresh = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY)
        
        # Encontrar contornos
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        cartas_detectadas = []
        
        for contour in contours:
            # Filtrar por área (cartas deben ser suficientemente grandes)
            area = cv2.contourArea(contour)
            if area < 5000:  # Área mínima
                continue
            
            # Aproximar contorno a polígono
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
            
            # Verificar que sea aproximadamente rectangular (4 esquinas)
            if len(approx) >= 4 and len(approx) <= 6:
                # Verificar relación de aspecto similar a carta UNO (5.6 x 8.7)
                x, y, w, h = cv2.boundingRect(approx)
                aspect_ratio = float(w) / h if h > 0 else 0
                
                # Cartas UNO tienen relación ~0.64 (pueden estar rotadas)
                if 0.4 < aspect_ratio < 1.8:  # Rango amplio para rotaciones
                    cartas_detectadas.append({
                        'contorno': approx,
                        'bbox': (x, y, w, h),
                        'area': area
                    })
        
        return cartas_detectadas
    
    def detectar_qr_en_region(self, frame, bbox, debug=False):
        """
        Busca códigos QR en una región específica del frame
        
        Args:
            frame: Frame completo
            bbox: Tupla (x, y, w, h) de la región
            debug: Si True, muestra ventana con ROI para depuración
            
        Returns:
            dict o None: Datos de la carta encontrada
        """
        x, y, w, h = bbox
        
        # Extraer región de interés (ROI)
        roi = frame[y:y+h, x:x+w]
        
        # DEBUG: Mostrar la región donde busca QR
        if debug:
            cv2.imshow('DEBUG - Region buscando QR', roi)
            print(f"Buscando QR en región: {w}x{h} pixels")
        
        # Intentar con imagen original
        codigos = decode(roi)
        
        # Si no encuentra, intentar con diferentes procesamientos
        if not codigos:
            # Intentar con escala de grises
            gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            codigos = decode(gray_roi)
            
            if debug and not codigos:
                print("no se detectó QR en ROI")
        
        if codigos:
            if debug:
                print(f"{len(codigos)} QR(s) detectado(s)")
            
            for codigo in codigos:
                try:
                    # Decodificar JSON del QR
                    data = codigo.data.decode('utf-8')
                    if debug:
                        print(f"data: {data}")
                    
                    carta_data = json.loads(data)
                    
                    # Validar estructura
                    if 'color' in carta_data and 'valor' in carta_data:
                        if debug:
                            print(f"carta válida: {carta_data}")
                        return carta_data
                        
                except json.JSONDecodeError:
                    if debug:
                        print(f"error JSON: {data}")
                    continue
                except Exception as e:
                    if debug:
                        print(f"error: {e}")
                    continue
        
        return None
    
    def detectar_cartas_completo(self, frame, debug=False):
        """
        Detecta cartas por sus bordes blancos y luego busca QR dentro
        
        Args:
            frame: Frame de video
            debug: Si True, muestra información de debug
        
        Returns:
            tuple: (carta_data, frame_anotado)
        """
        frame_anotado = frame.copy()
        
        # Detectar rectángulos blancos (cartas)
        cartas = self.detectar_cartas_rectangulos(frame)
        
        if not cartas:
            self.frames_sin_deteccion += 1
            return None, frame_anotado
        
        # Buscar QR en cada carta detectada
        for carta in cartas:
            x, y, w, h = carta['bbox']
            
            # Dibujar contorno de carta detectada (azul)
            cv2.drawContours(frame_anotado, [carta['contorno']], -1, (255, 0, 0), 2)
            cv2.putText(frame_anotado, "Carta", (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            
            # Buscar QR en esta carta
            carta_data = self.detectar_qr_en_region(frame, carta['bbox'], debug=debug)
            
            if carta_data:
                # QR encontrado! Dibujar en verde
                cv2.rectangle(frame_anotado, (x, y), (x+w, y+h), (0, 255, 0), 3)
                texto = f"{carta_data['color'].capitalize()} {carta_data['valor']}"
                cv2.putText(frame_anotado, texto, (x, y - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                
                self.frames_sin_deteccion = 0
                return carta_data, frame_anotado
        
        self.frames_sin_deteccion += 1
        return None, frame_anotado
    
    def detectar_carta_estable(self, frame, frames_requeridos=10):
        """
        Detecta una carta solo si aparece consistentemente
        Evita lecturas falsas o accidentales
        
        Args:
            frame: Frame de video
            frames_requeridos: Número de frames consecutivos para confirmar
            
        Returns:
            tuple: (dict o None, frame_anotado)
        """
        carta_actual, frame_anotado = self.detectar_cartas_completo(frame)
        
        if carta_actual:
            if self.ultima_carta_detectada == carta_actual:
                # Misma carta detectada consecutivamente
                if self.frames_sin_deteccion == 0:
                    # Carta estable detectada
                    return carta_actual, frame_anotado
            else:
                # Nueva carta, reiniciar contador
                self.ultima_carta_detectada = carta_actual
                self.frames_sin_deteccion = 0
        else:
            # No hay detección
            if self.frames_sin_deteccion > frames_requeridos:
                self.ultima_carta_detectada = None
        
        return None, frame_anotado
    
    def dibujar_interfaz(self, frame, mensaje="Muestra una carta UNO frente a la cámara"):
        """Dibuja elementos de interfaz en el frame"""
        # Solo mensaje, sin cuadro guía
        cv2.putText(frame, mensaje, (20, 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Instrucciones
        cv2.putText(frame, "La carta se detectara automaticamente", (20, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        return frame
    
    def liberar(self):
        """Libera recursos de la cámara"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("camara desconectada")


# Código de prueba
if __name__ == "__main__":
    IP_WEBCAM = "http://192.168.1.67:8080" 
    
    # Preguntar modo
    print("\n¿Qué cámara quieres usar?")
    print("1. IP Webcam (celular)")
    print("2. Cámara local (laptop)")
    opcion = input("Opción (1/2): ").strip()
    
    if opcion == "1":
        url = IP_WEBCAM
        detector = DetectorCartas(ip_webcam_url=url)
    else:
        detector = DetectorCartas()
    
    # Conectar
    if not detector.conectar_camara():
        print("❌ No se pudo conectar a la cámara")
        exit(1)
    
    try:
        while True:
            ret, frame = detector.obtener_frame()
            
            if not ret or frame is None:
                print("No se pudo obtener frame")
                continue
            
            # Detectar carta (ahora retorna carta y frame anotado)
            carta, frame_procesado = detector.detectar_carta_estable(frame, frames_requeridos=5)
            
            if carta:
                print(f"Carta detectada: {carta['color'].upper()} {carta['valor']}")
            
            # Dibujar interfaz sobre el frame procesado
            frame_final = detector.dibujar_interfaz(frame_procesado)
            
            # Mostrar
            cv2.imshow('Detector de Cartas UNO', frame_final)
            
            # Salir con 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    except KeyboardInterrupt:
        print("\nInterrumpido por usuario")
    
    finally:
        detector.liberar()