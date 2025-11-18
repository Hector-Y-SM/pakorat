class Baccarat:
    """Implementación del juego de Baccarat con reglas tradicionales"""
    
    def __init__(self):
        self.mano_jugador = []
        self.mano_banca = []
        self.estado = "inicio"  # inicio, jugador_carta1, jugador_carta2, banca_carta1, banca_carta2, jugador_tercera, banca_tercera, finalizado
        self.ganador = None
        self.puntos_jugador = 0
        self.puntos_banca = 0
        self.mensaje = "Bienvenido al Baccarat"
        
    def reiniciar(self):
        """Reinicia el juego para una nueva ronda"""
        self.mano_jugador = []
        self.mano_banca = []
        self.estado = "inicio"
        self.ganador = None
        self.puntos_jugador = 0
        self.puntos_banca = 0
        self.mensaje = "Nueva ronda iniciada"
    
    def calcular_puntos(self, mano):
        """
        Calcula los puntos de una mano (suma % 10)
        
        Args:
            mano: Lista de cartas [{"color": "rojo", "valor": 7}, ...]
            
        Returns:
            int: Puntos de la mano (0-9)
        """
        suma = sum(carta["valor"] for carta in mano)
        return suma % 10
    
    def agregar_carta_jugador(self, carta):
        """Agrega una carta al jugador"""
        if self.estado not in ["jugador_carta1", "jugador_carta2", "jugador_tercera"]:
            return False, "No es momento de agregar carta al jugador"
        
        self.mano_jugador.append(carta)
        self.puntos_jugador = self.calcular_puntos(self.mano_jugador)
        
        # Avanzar estado
        if self.estado == "jugador_carta1":
            self.estado = "jugador_carta2"
            self.mensaje = f"Jugador: {carta['color']} {carta['valor']} (1/2). Muestra segunda carta del jugador"
        elif self.estado == "jugador_carta2":
            self.estado = "banca_carta1"
            self.mensaje = f"Jugador: {carta['color']} {carta['valor']} (2/2). Total: {self.puntos_jugador}. Ahora la banca"
        elif self.estado == "jugador_tercera":
            self.mensaje = f"Jugador pidió tercera: {carta['color']} {carta['valor']}. Total: {self.puntos_jugador}"
            self._evaluar_tercera_banca()
        
        return True, self.mensaje
    
    def agregar_carta_banca(self, carta):
        """Agrega una carta a la banca"""
        if self.estado not in ["banca_carta1", "banca_carta2", "banca_tercera"]:
            return False, "No es momento de agregar carta a la banca"
        
        self.mano_banca.append(carta)
        self.puntos_banca = self.calcular_puntos(self.mano_banca)
        
        # Avanzar estado
        if self.estado == "banca_carta1":
            self.estado = "banca_carta2"
            self.mensaje = f"Banca: {carta['color']} {carta['valor']} (1/2). Muestra segunda carta de la banca"
        elif self.estado == "banca_carta2":
            self.mensaje = f"Banca: {carta['color']} {carta['valor']} (2/2). Total: {self.puntos_banca}"
            self._evaluar_reparto_inicial()
        elif self.estado == "banca_tercera":
            self.mensaje = f"Banca pidió tercera: {carta['color']} {carta['valor']}. Total: {self.puntos_banca}"
            self._determinar_ganador()
        
        return True, self.mensaje
    
    def iniciar_reparto(self):
        """Inicia el reparto de cartas"""
        if self.estado != "inicio":
            return False, "El juego ya está en curso"
        
        self.estado = "jugador_carta1"
        self.mensaje = "Muestra la primera carta del JUGADOR"
        return True, self.mensaje
    
    def _evaluar_reparto_inicial(self):
        """Evalúa si hay natural (8 o 9) o si se necesita tercera carta"""
        # Verificar naturales
        if self.puntos_jugador >= 8 or self.puntos_banca >= 8:
            self.mensaje += " | ¡NATURAL!"
            self._determinar_ganador()
            return
        
        # Evaluar tercera carta del jugador
        if self.puntos_jugador <= 5:
            # Jugador pide tercera carta
            self.estado = "jugador_tercera"
            self.mensaje += " | Jugador necesita tercera carta"
        else:
            # Jugador se planta (6 o 7)
            self.mensaje += " | Jugador se planta"
            self._evaluar_tercera_banca_sin_tercera_jugador()
    
    def _evaluar_tercera_banca_sin_tercera_jugador(self):
        """Evalúa tercera carta de la banca cuando jugador se plantó"""
        if self.puntos_banca <= 5:
            self.estado = "banca_tercera"
            self.mensaje += " | Banca necesita tercera carta"
        else:
            # Banca se planta
            self.mensaje += " | Banca se planta"
            self._determinar_ganador()
    
    def _evaluar_tercera_banca(self):
        """Evalúa si la banca pide tercera carta según reglas complejas"""
        # Tercera carta del jugador (última carta agregada)
        tercera_jugador = self.mano_jugador[-1]["valor"]
        
        # Reglas de la banca según su puntaje y tercera del jugador
        if self.puntos_banca <= 2:
            # Banca 0-2: siempre pide
            self.estado = "banca_tercera"
            self.mensaje += " | Banca necesita tercera carta"
        elif self.puntos_banca == 3:
            # Banca 3: pide excepto si tercera del jugador = 8
            if tercera_jugador == 8:
                self.mensaje += " | Banca se planta (tercera jugador = 8)"
                self._determinar_ganador()
            else:
                self.estado = "banca_tercera"
                self.mensaje += " | Banca necesita tercera carta"
        elif self.puntos_banca == 4:
            # Banca 4: pide si tercera del jugador = 2,3,4,5,6,7
            if tercera_jugador in [2, 3, 4, 5, 6, 7]:
                self.estado = "banca_tercera"
                self.mensaje += " | Banca necesita tercera carta"
            else:
                self.mensaje += " | Banca se planta"
                self._determinar_ganador()
        elif self.puntos_banca == 5:
            # Banca 5: pide si tercera del jugador = 4,5,6,7
            if tercera_jugador in [4, 5, 6, 7]:
                self.estado = "banca_tercera"
                self.mensaje += " | Banca necesita tercera carta"
            else:
                self.mensaje += " | Banca se planta"
                self._determinar_ganador()
        elif self.puntos_banca == 6:
            # Banca 6: pide si tercera del jugador = 6,7
            if tercera_jugador in [6, 7]:
                self.estado = "banca_tercera"
                self.mensaje += " | Banca necesita tercera carta"
            else:
                self.mensaje += " | Banca se planta"
                self._determinar_ganador()
        else:
            # Banca 7: siempre se planta
            self.mensaje += " | Banca se planta"
            self._determinar_ganador()
    
    def _determinar_ganador(self):
        """Determina el ganador final"""
        self.estado = "finalizado"
        
        if self.puntos_jugador > self.puntos_banca:
            self.ganador = "jugador"
            self.mensaje = f"🎉 ¡GANA EL JUGADOR! ({self.puntos_jugador} vs {self.puntos_banca})"
        elif self.puntos_banca > self.puntos_jugador:
            self.ganador = "banca"
            self.mensaje = f"🏦 ¡GANA LA BANCA! ({self.puntos_banca} vs {self.puntos_jugador})"
        else:
            self.ganador = "empate"
            self.mensaje = f"🤝 ¡EMPATE! (ambos con {self.puntos_jugador})"
    
    def obtener_estado(self):
        """Retorna el estado actual del juego"""
        return {
            "estado": self.estado,
            "mano_jugador": self.mano_jugador,
            "mano_banca": self.mano_banca,
            "puntos_jugador": self.puntos_jugador,
            "puntos_banca": self.puntos_banca,
            "ganador": self.ganador,
            "mensaje": self.mensaje,
            "necesita_carta": self._que_carta_necesita()
        }
    
    def _que_carta_necesita(self):
        """Determina qué carta necesita el juego en este momento"""
        if self.estado == "inicio":
            return None
        elif "jugador" in self.estado:
            return "jugador"
        elif "banca" in self.estado:
            return "banca"
        else:
            return None
