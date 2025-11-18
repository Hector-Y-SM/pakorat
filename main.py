#!/usr/bin/env python3
from interfaz import InterfazBaccarat
import sys

def mostrar_banner():
    banner = """
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║              🎰  PAKKORAT UNO  🎰                        ║
    ║                                                          ║
    ║          Juego de Baccarat con Cartas UNO                ║
    ║            y Detección por Código QR                     ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """
    print(banner)

def configurar_tamano_ventana():
    """Configura el tamaño de la ventana del juego"""
    print("\nCONFIGURACIÓN DE VENTANA")
    print("=" * 60)
    print("\n¿Qué tamaño quieres para la ventana?")
    print("  1. Pequeña (800 x 480) - Para dos pantallas")
    print("  2. Mediana (1024 x 600) - Tamaño intermedio")
    print("  3. Grande (1280 x 720) - Pantalla completa")
    print("  4. Personalizado")
    print()
    
    while True:
        opcion = input("Selecciona opción (1-4): ").strip()
        
        if opcion == "1":
            print("\n📺 Tamaño: 800 x 480")
            return 800, 480
        elif opcion == "2":
            print("\n📺 Tamaño: 1024 x 600")
            return 1024, 600
        elif opcion == "3":
            print("\n📺 Tamaño: 1280 x 720")
            return 1280, 720
        elif opcion == "4":
            try:
                ancho = int(input("Ancho (píxeles): "))
                alto = int(input("Alto (píxeles): "))
                print(f"\n📺 Tamaño personalizado: {ancho} x {alto}")
                return ancho, alto
            except:
                print("valores inválidos. Intenta de nuevo.")
        else:
            print("opción inválida. Ingresa 1-4.")

def configurar_camara():
    """Configura la conexión de la cámara"""
    print("\n📷 CONFIGURACIÓN DE CÁMARA")
    print("=" * 60)
    print("\n¿Qué tipo de cámara vas a usar?")
    print("  1. IP Webcam")
    print("  2. Cámara local (laptop/PC)")
    print()
    
    while True:
        opcion = input("Selecciona opción (1/2): ").strip()
        
        if opcion == "1":            
            url = 'http://192.168.1.67:8080'
            return url
        
        elif opcion == "2":
            print("\n💻 Usando cámara local")
            return None
        
        else:
            print("❌ Opción inválida. Ingresa 1 o 2.")

def mostrar_instrucciones():
    """Muestra las instrucciones del juego"""
    print("\n" + "=" * 60)
    print("📖 INSTRUCCIONES DEL JUEGO")
    print("=" * 60)
    print("""
🎯 OBJETIVO:
   Predecir qué mano tendrá un puntaje más cercano a 9

📋 REGLAS:
   • Cartas 0-9 valen su valor nominal
   • Solo se cuenta la última cifra (ej: 15 = 5 puntos)
   • 8 o 9 con 2 cartas = "Natural" (gana automáticamente)
   
🎮 CONTROLES:
   ESPACIO  → Iniciar nueva ronda
   R        → Reiniciar después de terminar
   D        → Activar/desactivar modo debug
   Q        → Salir del juego

🃏 FLUJO DEL JUEGO:
   1. Presiona ESPACIO para iniciar
   2. Muestra cartas del JUGADOR cuando se pida (2 cartas)
   3. Muestra cartas de la BANCA cuando se pida (2 cartas)
   4. El sistema decide automáticamente si se necesita tercera carta
   5. Se declara el ganador
   6. Presiona R para nueva ronda
    """)
    print("=" * 60)
    input("\npresiona enter para jugar")

def main():
    """Función principal"""
    mostrar_banner()
    
    # Configurar tamaño de ventana
    ancho, alto = configurar_tamano_ventana()
    
    # Configurar cámara
    url_camara = configurar_camara()
    
    # Mostrar instrucciones
    mostrar_instrucciones()
    
    # Crear e iniciar el juego
    print("\niniciando PAKKORAT")
    print("conectando con la camara\n")
    
    try:
        interfaz = InterfazBaccarat(ip_webcam_url=url_camara, 
                                   ancho_ventana=ancho, 
                                   alto_ventana=alto)
        interfaz.ejecutar()
    except Exception as e:
        print(f"\nerror al ejecutar el juego: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
   

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)