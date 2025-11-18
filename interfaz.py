import cv2
import numpy as np
from detector_cartas import DetectorCartas
from juego_baccarat import Baccarat

class InterfazBaccarat:
    """Interfaz gráfica para el juego de Baccarat con detección de cartas"""
    
    def __init__(self, ip_webcam_url=None, ancho_ventana=800, alto_ventana=480):
        """
        Inicializa la interfaz
        
        Args:
            ip_webcam_url: URL de la cámara IP (opcional)
            ancho_ventana: Ancho deseado de la ventana (default 800)
            alto_ventana: Alto deseado de la ventana (default 480)
        """
        self.detector = DetectorCartas(ip_webcam_url)
        self.juego = Baccarat()
        self.esperando_carta = False
        self.ultima_carta_leida = None
        self.modo_debug = False
        
        # Configuración de ventana
        self.ancho_ventana = ancho_ventana
        self.alto_ventana = alto_ventana
        
        # Marcador de partidas
        self.victorias_jugador = 0
        self.victorias_banca = 0
        self.empates = 0
        
    def conectar(self):
        """Conecta con la cámara"""
        return self.detector.conectar_camara()
    
    def dibujar_interfaz(self, frame):
        """Dibuja la interfaz del juego sobre el frame"""
        # Redimensionar frame según configuración
        frame_resizado = cv2.resize(frame, (self.ancho_ventana - 250, self.alto_ventana))
        h, w = frame_resizado.shape[:2]
        
        # Crear panel lateral derecho (más compacto)
        panel_width = 250
        panel = np.zeros((h, panel_width, 3), dtype=np.uint8)
        panel[:] = (40, 40, 40)  # Fondo gris oscuro
        
        y_offset = 15
        
        # Título (más pequeño)
        cv2.putText(panel, "BACCARAT UNO", (10, y_offset), 
                   cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)
        y_offset += 30
        
        # Línea separadora
        cv2.line(panel, (5, y_offset), (panel_width-5, y_offset), (100, 100, 100), 1)
        y_offset += 15
        
        # Estado del juego
        estado = self.juego.obtener_estado()
        
        # Marcador
        cv2.putText(panel, "=== MARCADOR ===", (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        y_offset += 20
        cv2.putText(panel, f"Jugador: {self.victorias_jugador}", (15, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        y_offset += 18
        cv2.putText(panel, f"Banca: {self.victorias_banca}", (15, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 100, 255), 1)
        y_offset += 18
        cv2.putText(panel, f"Empates: {self.empates}", (15, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)
        y_offset += 20
        
        # Línea separadora
        cv2.line(panel, (5, y_offset), (panel_width-5, y_offset), (100, 100, 100), 1)
        y_offset += 12
        
        # Mano del Jugador
        cv2.putText(panel, "JUGADOR", (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
        y_offset += 18
        
        if estado["mano_jugador"]:
            for i, carta in enumerate(estado["mano_jugador"], 1):
                texto = f"{i}. {carta['color'][:3].upper()} {carta['valor']}"
                cv2.putText(panel, texto, (15, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
                y_offset += 15
            
            cv2.putText(panel, f"Total: {estado['puntos_jugador']}", (15, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            y_offset += 18
        else:
            cv2.putText(panel, "Sin cartas", (15, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, (150, 150, 150), 1)
            y_offset += 18
        
        # Línea separadora
        cv2.line(panel, (5, y_offset), (panel_width-5, y_offset), (100, 100, 100), 1)
        y_offset += 12
        
        # Mano de la Banca
        cv2.putText(panel, "BANCA", (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 100, 255), 1)
        y_offset += 18
        
        if estado["mano_banca"]:
            for i, carta in enumerate(estado["mano_banca"], 1):
                texto = f"{i}. {carta['color'][:3].upper()} {carta['valor']}"
                cv2.putText(panel, texto, (15, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
                y_offset += 15
            
            cv2.putText(panel, f"Total: {estado['puntos_banca']}", (15, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 100, 255), 1)
            y_offset += 18
        else:
            cv2.putText(panel, "Sin cartas", (15, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, (150, 150, 150), 1)
            y_offset += 18
        
        # Línea separadora
        cv2.line(panel, (5, y_offset), (panel_width-5, y_offset), (100, 100, 100), 1)
        y_offset += 12
        
        # Mensaje del estado actual (compacto)
        cv2.putText(panel, "ESTADO:", (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        y_offset += 15
        
        # Dividir mensaje largo en múltiples líneas
        mensaje = estado["mensaje"]
        max_chars = 25
        palabras = mensaje.split()
        linea_actual = ""
        
        for palabra in palabras:
            if len(linea_actual + palabra) <= max_chars:
                linea_actual += palabra + " "
            else:
                cv2.putText(panel, linea_actual.strip(), (10, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 100), 1)
                y_offset += 14
                linea_actual = palabra + " "
        
        if linea_actual:
            cv2.putText(panel, linea_actual.strip(), (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 100), 1)
        
        # Controles en la parte inferior
        y_offset = h - 70
        cv2.line(panel, (5, y_offset), (panel_width-5, y_offset), (100, 100, 100), 1)
        y_offset += 12
        
        cv2.putText(panel, "CONTROLES:", (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        y_offset += 14
        cv2.putText(panel, "SPC - Ronda", (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        y_offset += 13
        cv2.putText(panel, "R - Reset", (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        y_offset += 13
        cv2.putText(panel, "D - Debug", (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        y_offset += 13
        cv2.putText(panel, "Q - Salir", (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        # Combinar frame de cámara con panel
        frame_combinado = np.hstack([frame_resizado, panel])
        
        # Mensaje principal en el frame de la cámara
        if self.esperando_carta:
            tipo_carta = estado["necesita_carta"]
            if tipo_carta:
                msg = f"Muestra carta de: {tipo_carta.upper()}"
                cv2.putText(frame_combinado, msg, (15, 35),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        return frame_combinado
    
    def procesar_carta_detectada(self, carta):
        """Procesa una carta detectada y la agrega al juego"""
        estado = self.juego.obtener_estado()
        
        # Evitar leer la misma carta múltiples veces
        if carta == self.ultima_carta_leida:
            return
        
        self.ultima_carta_leida = carta
        
        # Agregar carta según el estado
        if estado["necesita_carta"] == "jugador":
            exito, mensaje = self.juego.agregar_carta_jugador(carta)
            if exito:
                print(f"✅ {mensaje}")
                self.esperando_carta = True
        elif estado["necesita_carta"] == "banca":
            exito, mensaje = self.juego.agregar_carta_banca(carta)
            if exito:
                print(f"✅ {mensaje}")
                self.esperando_carta = True
        
        # Verificar si el juego terminó
        if self.juego.estado == "finalizado":
            self.esperando_carta = False
            self._actualizar_marcador()
    
    def _actualizar_marcador(self):
        """Actualiza el marcador de victorias"""
        if self.juego.ganador == "jugador":
            self.victorias_jugador += 1
        elif self.juego.ganador == "banca":
            self.victorias_banca += 1
        elif self.juego.ganador == "empate":
            self.empates += 1
    
    def iniciar_ronda(self):
        """Inicia una nueva ronda"""
        if self.juego.estado == "inicio":
            exito, mensaje = self.juego.iniciar_reparto()
            if exito:
                self.esperando_carta = True
                self.ultima_carta_leida = None
                print(f"🎰 {mensaje}")
        else:
            print("⚠️ Ya hay una ronda en curso")
    
    def nueva_ronda(self):
        """Reinicia el juego para una nueva ronda"""
        self.juego.reiniciar()
        self.esperando_carta = False
        self.ultima_carta_leida = None
        print("🔄 Nueva ronda lista")
    
    def ejecutar(self):
        """Bucle principal del juego"""
        if not self.conectar():
            print("❌ No se pudo conectar a la cámara")
            return
        
        print("\n" + "=" * 70)
        print("🎰 BACCARAT UNO - Juego iniciado")
        print("=" * 70)
        print("\n📋 INSTRUCCIONES:")
        print("   ESPACIO - Iniciar ronda")
        print("   R       - Nueva ronda (después de terminar)")
        print("   D       - Activar/desactivar debug")
        print("   Q       - Salir")
        print("\n" + "=" * 70 + "\n")
        
        try:
            while True:
                ret, frame = self.detector.obtener_frame()
                
                if not ret or frame is None:
                    continue
                
                # Detectar cartas si estamos esperando una
                if self.esperando_carta:
                    carta, frame_procesado = self.detector.detectar_cartas_completo(
                        frame, debug=self.modo_debug
                    )
                    
                    if carta:
                        self.procesar_carta_detectada(carta)
                        # Pequeña pausa después de detectar para evitar re-lecturas
                        cv2.waitKey(500)
                else:
                    frame_procesado = frame
                
                # Dibujar interfaz
                frame_final = self.dibujar_interfaz(frame_procesado)
                
                # Mostrar
                cv2.imshow('Baccarat UNO', frame_final)
                
                # Controles
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q'):
                    print("\n👋 Saliendo del juego...")
                    break
                elif key == ord(' '):  # Espacio
                    self.iniciar_ronda()
                elif key == ord('r'):
                    self.nueva_ronda()
                elif key == ord('d'):
                    self.modo_debug = not self.modo_debug
                    print(f"🔧 Modo DEBUG: {'ACTIVADO' if self.modo_debug else 'DESACTIVADO'}")
        
        except KeyboardInterrupt:
            print("\n⚠️ Interrumpido por usuario")
        
        finally:
            self.detector.liberar()
            print("\n" + "=" * 70)
            print("📊 ESTADÍSTICAS FINALES:")
            print(f"   Victorias Jugador: {self.victorias_jugador}")
            print(f"   Victorias Banca: {self.victorias_banca}")
            print(f"   Empates: {self.empates}")
            print("=" * 70)
            print("\n🎰 ¡Gracias por jugar!")


# Punto de entrada
if __name__ == "__main__":    
    print("🎮 Configuración de Baccarat UNO")
    print("=" * 50)
    
    # Tamaño de ventana
    print("\n¿Qué tamaño de ventana prefieres?")
    print("1. Pequeña (800x480)")
    print("2. Mediana (1024x600)")
    print("3. Grande (1280x720)")
    opcion_tamaño = input("Opción (1-3): ").strip()
    
    tamaños = {
        '1': (800, 480),
        '2': (1024, 600),
        '3': (1280, 720)
    }
    ancho, alto = tamaños.get(opcion_tamaño, (800, 480))
    
    # Preguntar modo de cámara
    print("\n¿Qué cámara quieres usar?")
    print("1. IP Webcam (celular)")
    print("2. Cámara local")
    opcion = input("Opción (1/2): ").strip()
    
    if opcion == "1":
        url = 'http://192.168.1.67:8080'
        interfaz = InterfazBaccarat(ip_webcam_url=url, 
                                   ancho_ventana=ancho, 
                                   alto_ventana=alto)
    else:
        interfaz = InterfazBaccarat(ancho_ventana=ancho, 
                                   alto_ventana=alto)
    
    # Ejecutar juego
    interfaz.ejecutar()