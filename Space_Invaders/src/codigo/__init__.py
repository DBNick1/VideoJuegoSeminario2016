
from pygame import *
import sys
from random import shuffle, randrange, choice

#           R    G    B
WHITE     = (255, 255, 255)
GREEN     = (78, 255, 87)
YELLOW     = (241, 255, 0)
BLUE     = (80, 255, 239)
PURPLE     = (203, 0, 255)
RED     = (237, 28, 36)

SCREEN         = display.set_mode((800,600))
FONT = "fuentes/space_invaders.ttf"
IMG_NAMES     = ["nave", "nave", "ufo", "enemigo1_1", "enemigo1_2", "enemigo2_1", "enemigo2_2",
                "enemigo3_1", "enemigo3_2", "explosionblue", "explosiongreen", "explosionpurple", "laser", "enemylaser"]
IMAGENES         = {name: image.load("imagenes/{}.png".format(name)).convert_alpha()
                for name in IMG_NAMES}

class NavedeCombate(sprite.Sprite):
    def __init__(self):
        sprite.Sprite.__init__(self)
        self.image = IMAGENES["nave"]
        self.rect = self.image.get_rect(topleft=(375, 540))
        self.velocidad = 5

    def update(self, keys, *args):
        if keys[K_LEFT] and self.rect.x > 10:
            self.rect.x -= self.velocidad
        if keys[K_RIGHT] and self.rect.x < 740:
            self.rect.x += self.velocidad
        game.screen.blit(self.image, self.rect)


class Municion(sprite.Sprite):
    def __init__(self, xpos, ypos, direccion, speed, filename, side):
        sprite.Sprite.__init__(self)
        self.image = IMAGENES[filename]
        self.rect = self.image.get_rect(topleft=(xpos, ypos))
        self.velocidad = speed
        self.direccion = direccion
        self.side = side
        self.filename = filename

    def update(self, keys, *args):
        game.screen.blit(self.image, self.rect)
        self.rect.y += self.velocidad * self.direccion
        if self.rect.y < 15 or self.rect.y > 600:
            self.kill()


class Enemigos(sprite.Sprite):
    def __init__(self, fila, columna):
        sprite.Sprite.__init__(self)
        self.fila = fila
        self.columna = columna
        self.images = []
        self.load_images()
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.direccion = 1
        self.movimientoDerecho = 15
        self.movimientoIzquierdo = 30
        self.cantidadMovimientos = 0
        self.moveTime = 600
        self.firstTime = True
        self.movedY = False;
        self.columnas = [False] * 10
        self.columnasVivas = [True] * 10
        self.derMovimiento = False
        self.izqMovimiento = False
        self.cantidadDerMov = 0
        self.cantidadIzqMov = 0
        self.timer = time.get_ticks()

    def update(self, keys, currentTime, killedRow, killedColumn, killedArray):
        self.check_column_deletion(killedRow, killedColumn, killedArray)
        if currentTime - self.timer > self.moveTime:
            self.movedY = False;
            if self.cantidadMovimientos >= self.movimientoDerecho and self.direccion == 1:
                self.direccion *= -1
                self.cantidadMovimientos = 0
                self.rect.y += 35
                self.movedY = True
                if self.derMovimiento:
                    self.movimientoDerecho += self.cantidadDerMov
                if self.firstTime:
                    self.movimientoDerecho = self.movimientoIzquierdo;
                    self.firstTime = False;
                self.addRightMovesAfterDrop = False
            if self.cantidadMovimientos >= self.movimientoIzquierdo and self.direccion == -1:
                self.direccion *= -1
                self.cantidadMovimientos = 0
                self.rect.y += 35
                self.movedY = True
                if self.izqMovimiento:
                    self.movimientoIzquierdo += self.cantidadIzqMov
                self.addLeftMovesAfterDrop = False
            if self.cantidadMovimientos < self.movimientoDerecho and self.direccion == 1 and not self.movedY:
                self.rect.x += 10
                self.cantidadMovimientos += 1
            if self.cantidadMovimientos < self.movimientoIzquierdo and self.direccion == -1 and not self.movedY:
                self.rect.x -= 10
                self.cantidadMovimientos += 1

            self.index += 1
            if self.index >= len(self.images):
                self.index = 0
            self.image = self.images[self.index]

            self.timer += self.moveTime
        game.screen.blit(self.image, self.rect)

    def check_column_deletion(self, filaDerrotada, killedColumn, matrizDerrotada):
        if filaDerrotada != -1 and killedColumn != -1:
            matrizDerrotada[filaDerrotada][killedColumn] = 1
            for column in range(10):
                if all([matrizDerrotada[row][column] == 1 for row in range(5)]):
                    self.columnas[column] = True

        for i in range(5):
            if all([self.columnas[x] for x in range(i + 1)]) and self.columnasVivas[i]:
                self.movimientoIzquierdo += 5
                self.columnasVivas[i] = False
                if self.direccion == -1:
                    self.movimientoDerecho += 5
                else:
                    self.derMovimiento = True
                    self.cantidadDerMov += 5
                    
        for i in range(5):
            if all([self.columnas[x] for x in range(9, 8 - i, -1)]) and self.columnasVivas[9 - i]:
                self.columnasVivas[9 - i] = False
                self.movimientoDerecho += 5
                if self.direccion == 1:
                    self.movimientoIzquierdo += 5
                else:
                    self.izqMovimiento = True
                    self.cantidadIzqMov += 5

    def load_images(self):
        images = {0: ["1_2", "1_1"],
                  1: ["2_2", "2_1"],
                  2: ["2_2", "2_1"],
                  3: ["3_1", "3_2"],
                  4: ["3_1", "3_2"],
                 }
        img1, img2 = (IMAGENES["enemigo{}".format(img_num)] for img_num in images[self.fila])
        self.images.append(transform.scale(img1, (40, 35)))
        self.images.append(transform.scale(img2, (40, 35)))


class Defensa(sprite.Sprite):
    def __init__(self, size, color, fila, columna):
       sprite.Sprite.__init__(self)
       self.height = size
       self.width = size
       self.color = color
       self.image = Surface((self.width, self.height))
       self.image.fill(self.color)
       self.rect = self.image.get_rect()
       self.fila = fila
       self.columna = columna

    def update(self, keys, *args):
        game.screen.blit(self.image, self.rect)


class UFO(sprite.Sprite):
    def __init__(self):
        sprite.Sprite.__init__(self)
        self.image = IMAGENES["ufo"]
        self.image = transform.scale(self.image, (75, 35))
        self.rect = self.image.get_rect(topleft=(-80, 45))
        self.fila = 5
        self.moveTime = 25000
        self.direccion = 1
        self.timer = time.get_ticks()
        self.mysteryEntered = mixer.Sound('sonidos/mysteryentered.wav')
        self.mysteryEntered.set_volume(0.3)
        self.playSound = True

    def update(self, keys, currentTime, *args):
        resetTimer = False
        if (currentTime - self.timer > self.moveTime) and (self.rect.x < 0 or self.rect.x > 800) and self.playSound:
            self.mysteryEntered.play()
            self.playSound = False
        if (currentTime - self.timer > self.moveTime) and self.rect.x < 840 and self.direccion == 1:
            self.mysteryEntered.fadeout(4000)
            self.rect.x += 2
            game.screen.blit(self.image, self.rect)
        if (currentTime - self.timer > self.moveTime) and self.rect.x > -100 and self.direccion == -1:
            self.mysteryEntered.fadeout(4000)
            self.rect.x -= 2
            game.screen.blit(self.image, self.rect)
        if (self.rect.x > 830):
            self.playSound = True
            self.direccion = -1
            resetTimer = True
        if (self.rect.x < -90):
            self.playSound = True
            self.direccion = 1
            resetTimer = True
        if (currentTime - self.timer > self.moveTime) and resetTimer:
            self.timer = currentTime

    
class Explosion(sprite.Sprite):
    def __init__(self, xpos, ypos, row, nave, mystery, score):
        sprite.Sprite.__init__(self)
        self.isMystery = mystery
        self.isShip = nave
        if mystery:
            self.text = Texto(FONT, 20, str(score), WHITE, xpos+20, ypos+6)
        elif nave:
            self.image = IMAGENES["nave"]
            self.rect = self.image.get_rect(topleft=(xpos, ypos))
        else:
            self.fila = row
            self.load_image()
            self.image = transform.scale(self.image, (40, 35))
            self.rect = self.image.get_rect(topleft=(xpos, ypos))
            game.screen.blit(self.image, self.rect)
            
        self.timer = time.get_ticks()
        
    def update(self, keys, currentTime):
        if self.isMystery:
            if currentTime - self.timer <= 200:
                self.text.draw(game.screen)
            if currentTime - self.timer > 400 and currentTime - self.timer <= 600:
                self.text.draw(game.screen)
            if currentTime - self.timer > 600:
                self.kill()
        elif self.isShip:
            if currentTime - self.timer > 300 and currentTime - self.timer <= 600:
                game.screen.blit(self.image, self.rect)
            if currentTime - self.timer > 900:
                self.kill()
        else:
            if currentTime - self.timer <= 100:
                game.screen.blit(self.image, self.rect)
            if currentTime - self.timer > 100 and currentTime - self.timer <= 200:
                self.image = transform.scale(self.image, (50, 45))
                game.screen.blit(self.image, (self.rect.x-6, self.rect.y-6))
            if currentTime - self.timer > 400:
                self.kill()
    
    def load_image(self):
        explosionesColores = ["purple", "blue", "blue", "green", "green"]
        self.image = IMAGENES["explosion{}".format(explosionesColores[self.fila])]

            
class Vidas_nave(sprite.Sprite):
    def __init__(self, xpos, ypos):
        sprite.Sprite.__init__(self)
        self.image = IMAGENES["nave"]
        self.image = transform.scale(self.image, (23, 23))
        self.rect = self.image.get_rect(topleft=(xpos, ypos))
        
    def update(self, keys, *args):
        game.screen.blit(self.image, self.rect)


class Texto(object):
    def __init__(self, textFont, size, message, color, xpos, ypos):
        self.font = font.Font(textFont, size)
        self.surface = self.font.render(message, True, color)
        self.rect = self.surface.get_rect(topleft=(xpos, ypos))

    def draw(self, surface):
        surface.blit(self.surface, self.rect)


class VentanaPrincipal(object):
    def __init__(self):
        mixer.pre_init(44100, -16, 1, 512)
        init()
        self.caption = display.set_caption('Space Invaders')
        self.screen = SCREEN
        self.fondo = image.load('imagenes/c.jpg').convert()
        self.fondo2 = image.load('imagenes/b.jpg').convert()
        self.comenzarPartida = False
        self.pantallaPrincipal = True
        self.gameOver = False
        self.enemyposition = 65
        
        
                                 

    def reset(self, score, lives):
        self.player = NavedeCombate()
        self.grupoColisiones = sprite.Group(self.player)
        self.explosionsGroup = sprite.Group()
        self.municion = sprite.Group()
        self.mysteryShip = UFO()
        self.ufoGrupo = sprite.Group(self.mysteryShip)
        self.enemigoMunicion = sprite.Group()
        self.reset_lives()
        self.generar_enemigos()
        self.todasLasDefensas = sprite.Group(self.defensa(0), self.defensa(1), self.defensa(2), self.defensa(3))
        self.keys = key.get_pressed()
        self.clock = time.Clock()
        self.timer = time.get_ticks()
        self.noteTimer = time.get_ticks()
        self.temporizador_nave = time.get_ticks()
        self.puntaje = score
        self.vidas = lives
        self.sonido()
        self.generar_texto()
        self.filaDerrotada = -1
        self.columnaDerrotada = -1
        self.naveNueva = False
        self.naveViva = True
        self.killedArray = [[0] * 10 for x in range(5)]

    def defensa(self, number):
       defensaGrupo = sprite.Group()
       for fila in range(4):
           for columna in range(9):
               defensa = Defensa(10, GREEN, fila, columna)
               defensa.rect.x = 50 + (200 * number) + (columna * defensa.width)
               defensa.rect.y = 450 + (fila * defensa.height)
               defensaGrupo.add(defensa)
       return defensaGrupo

    def reset_lives(self):
        self.vida1 = Vidas_nave(715, 3)
        self.vida2 = Vidas_nave(742, 3)
        self.vida3 = Vidas_nave(769, 3)
        self.vidasGrupo = sprite.Group(self.vida1, self.vida2, self.vida3)
        
    def sonido(self):
        self.sonidos = {}
        for sonido_nombre in ["shoot", "shoot2", "invaderkilled", "mysterykilled", "shipexplosion"]:
            self.sonidos[sonido_nombre] = mixer.Sound("sonidos/{}.wav".format(sonido_nombre))
            self.sonidos[sonido_nombre].set_volume(0.2)

        self.musicNotes = [mixer.Sound("sonidos/{}.wav".format(i)) for i in range(4)]
        for sonido in self.musicNotes:
            sonido.set_volume(0.5)

        self.noteIndex = 0

    def play_main_music(self, currentTime):
        moveTime = self.enemigos.sprites()[0].moveTime
        if currentTime - self.noteTimer > moveTime:
            self.note = self.musicNotes[self.noteIndex]
            if self.noteIndex < 3:
                self.noteIndex += 1
            else:
                self.noteIndex = 0

            self.note.play()
            self.noteTimer += moveTime

    def generar_texto(self):
        self.tituloTexto = Texto(FONT, 60, "Space Invaders", YELLOW, 120, 15)
        self.tituloTexto2 = Texto(FONT, 25, "Presiona cualquier tecla", YELLOW, 201, 500)
        self.tituloTexto3 = Texto(FONT, 12, "Desarrolladores Emanuel Chiesa Nicolas Espinosa Lucas Lopez Micaela Montero", RED, 105,580)
        self.gameOverText = Texto(FONT, 50, "Game Over", RED, 250, 270)
        self.nextRoundText = Texto(FONT, 50, "SIGUIENTE OLEADA", RED, 190, 270)
        self.enemigo1texto = Texto(FONT, 25, "   =   10 pts", GREEN, 368, 270)
        self.enemigo2texto = Texto(FONT, 25, "   =  20 pts", BLUE, 368, 320)
        self.enemigo3texto = Texto(FONT, 25, "   =  30 pts", PURPLE, 368, 370)
        self.enemigo4texto = Texto(FONT, 25, "   =   XXXX", RED, 368, 420)
        self.scoreText = Texto(FONT, 20, "Puntos", GREEN, 2, 5)
        self.livesText = Texto(FONT, 20, "Vidas ",GREEN, 640, 5)
        
    def controles_nave(self):
        self.keys = key.get_pressed()
        for e in event.get():
            if e.type == QUIT:
                sys.exit()
            if e.type == KEYDOWN:
                if e.key == K_SPACE:
                    if len(self.municion) == 0 and self.naveViva:
                        if self.puntaje < 1000:
                            municion = Municion(self.player.rect.x+23, self.player.rect.y+5, -1, 15, "laser", "center")
                            self.municion.add(municion)
                            self.sprites.add(self.municion)
                            self.sonidos["shoot"].play()
                        else:
                            leftbullet = Municion(self.player.rect.x+8, self.player.rect.y+5, -1, 15, "laser", "left")
                            rightbullet = Municion  (self.player.rect.x+38, self.player.rect.y+5, -1, 15, "laser", "right")
                            self.municion.add(leftbullet)
                            self.municion.add(rightbullet)
                            self.sprites.add(self.municion)
                            self.sonidos["shoot2"].play()

    def generar_enemigos(self):
        enemigos= sprite.Group()
        for row in range(5):
            for column in range(10):
                enemigo = Enemigos(row, column)
                enemigo.rect.x = 157 + (column * 50)
                enemigo.rect.y = self.enemyposition + (row * 45)
                enemigos.add(enemigo)
        
        self.enemigos = enemigos

        self.sprites = sprite.Group(self.player, self.enemigos, self.vidasGrupo, self.mysteryShip)

    def Generar_Disparo_Enemigo(self):
        columnList = []
        for enemigo in self.enemigos:
            columnList.append(enemigo.columna)

        columnSet = set(columnList)
        columnList = list(columnSet)
        shuffle(columnList)
        column = columnList[0]
        enemyList = []
        rowList = []

        for enemigo in self.enemigos:
            if enemigo.columna == column:
                rowList.append(enemigo.fila)
        row = max(rowList)
        for enemigo in self.enemigos:
            if enemigo.columna == column and enemigo.fila == row:
                if (time.get_ticks() - self.timer) > 700:
                    self.enemigoMunicion.add(Municion(enemigo.rect.x + 14, enemigo.rect.y + 20, 1, 5, "enemylaser", "center"))
                    self.sprites.add(self.enemigoMunicion)
                    self.timer = time.get_ticks() 

    def calcular_puntuacion(self, row):
        puntos = {0: 30,   
                  1: 20,
                  2: 20,
                  3: 10,
                  4: 10,
                  5: choice([50, 100, 150, 300])
                 }
                      
        puntos = puntos[row]
        self.puntaje += puntos
        return puntos

    def tablero(self):#contiene toda la pantalla principal de la partida del jugador(nave,enemigos,vidas,puntacio)
        self.enemigo1 = IMAGENES["enemigo3_1"]
        self.enemigo1 = transform.scale(self.enemigo1 , (40, 40))
        self.enemigo2 = IMAGENES["enemigo2_2"]
        self.enemigo2 = transform.scale(self.enemigo2 , (40, 40))
        self.enemigo3 = IMAGENES["enemigo1_2"]
        self.enemigo3 = transform.scale(self.enemigo3 , (40, 40))
        self.enemigo4 = IMAGENES["ufo"]
        self.enemigo4 = transform.scale(self.enemigo4 , (80, 40))
        self.screen.blit(self.enemigo1, (318, 270))
        self.screen.blit(self.enemigo2, (318, 320))
        self.screen.blit(self.enemigo3, (318, 370))
        self.screen.blit(self.enemigo4, (299, 420))

        for e in event.get():
            if e.type == QUIT:
                sys.exit()
            if e.type == KEYUP:
                self.comenzarPartida = True
                self.pantallaPrincipal = False
    
    def velocidad_del_enemigo(self):
        if len(self.enemigos) <= 10:#si la cantidad de enemigos es menor a diez o igual se incrementa un 400
            for enemigos in self.enemigos:
                enemigos.moveTime = 400
        if len(self.enemigos) == 1:# si la cantidad de enemigos es igual a 1  se incrementa en 200
            for enemigos in self.enemigos:
                enemigos.moveTime = 200
                
    def colisiones(self):
        colisionesdict = sprite.groupcollide(self.municion, self.enemigoMunicion, True, False)
        if colisionesdict:
            for value in colisionesdict.values():
                for spritesActuales in value:
                    self.enemigoMunicion.remove(spritesActuales)
                    self.sprites.remove(spritesActuales)

        enemigosdict = sprite.groupcollide(self.municion, self.enemigos, True, False)
        if enemigosdict:
            for value in enemigosdict.values():
                for spritesActuales in value:
                    self.sonidos["invaderkilled"].play()
                    self.filaDerrotada = spritesActuales.fila
                    self.columnaDerrotada = spritesActuales.columna
                    puntos = self.calcular_puntuacion(spritesActuales.fila)
                    explosion = Explosion(spritesActuales.rect.x, spritesActuales.rect.y, spritesActuales.fila, False, False, puntos)
                    self.explosionsGroup.add(explosion)
                    self.sprites.remove(spritesActuales)
                    self.enemigos.remove (spritesActuales)
                    self.gameTimer = time.get_ticks()
                    break
        
        ufodict = sprite.groupcollide(self.municion, self.ufoGrupo, True, True)
        if ufodict:
            for value in ufodict.values():
                for spritesActuales in value:
                    spritesActuales.mysteryEntered.stop()
                    self.sonidos["mysterykilled"].play()
                    puntos = self.calcular_puntuacion(spritesActuales.fila)
                    explosion = Explosion(spritesActuales.rect.x, spritesActuales.rect.y, spritesActuales.fila, False, True, puntos)
                    self.explosionsGroup.add(explosion)
                    self.sprites.remove(spritesActuales)
                    self.ufoGrupo.remove(spritesActuales)
                    newShip = UFO()
                    self.sprites.add(newShip)
                    self.ufoGrupo.add(newShip)
                    break

        municionesdict = sprite.groupcollide(self.enemigoMunicion, self.grupoColisiones, True, False)     
        if municionesdict:
            for value in municionesdict.values():
                for playerShip in value:
                    if self.vidas == 3:
                        self.vidas -= 1
                        self.vidasGrupo.remove(self.vida3)
                        self.sprites.remove(self.vida3)
                    elif self.vidas == 2:
                        self.vidas -= 1
                        self.vidasGrupo.remove(self.vida2)
                        self.sprites.remove(self.vida2)
                    elif self.vidas == 1:
                        self.vidas -= 1
                        self.vidasGrupo.remove(self.vida1)
                        self.sprites.remove(self.vida1)
                    elif self.vidas == 0:
                        self.gameOver = True
                        self.comenzarPartida = False
                    self.sonidos["shipexplosion"].play()
                    explosion = Explosion(playerShip.rect.x, playerShip.rect.y, 0, True, False, 0)
                    self.explosionsGroup.add(explosion)
                    self.sprites.remove(playerShip)
                    self.grupoColisiones.remove(playerShip)
                    self.naveNueva = True
                    self.temporizador_nave = time.get_ticks()
                    self.naveViva = False

        if sprite.groupcollide(self.enemigos, self.grupoColisiones, True, True):
            self.gameOver = True
            self.comenzarPartida = False

        sprite.groupcollide(self.municion, self.todasLasDefensas, True, True)
        sprite.groupcollide(self.enemigoMunicion, self.todasLasDefensas, True, True)
        sprite.groupcollide(self.enemigos, self.todasLasDefensas, False, True)

    def generar_nave_nueva(self, gameOverTexto, currentTime):
        if gameOverTexto and (currentTime - self.temporizador_nave > 900):
            self.player = NavedeCombate()
            self.sprites.add(self.player)
            self.grupoColisiones.add(self.player)
            self.naveNueva = False
            self.naveViva = True

    def game_over(self, currentTime):
        self.screen.blit(self.fondo2, (0,0))
        if currentTime - self.timer < 750:
            self.gameOverText.draw(self.screen)
        if currentTime - self.timer > 750 and currentTime - self.timer < 1500:
            self.screen.blit(self.fondo2, (0,0))
        if currentTime - self.timer > 1500 and currentTime - self.timer < 2250:
            self.gameOverText.draw(self.screen)
        if currentTime - self.timer > 2250 and currentTime - self.timer < 2750:
            self.screen.blit(self.fondo2, (0,0))
        if currentTime - self.timer > 3000:
            self.pantallaPrincipal = True
        
        for e in event.get():
            if e.type == QUIT:
                sys.exit()

    def main(self):
        while True:
            if self.pantallaPrincipal:
                self.reset(0, 3)
                self.screen.blit(self.fondo, (0,0))
                self.tituloTexto.draw(self.screen)
                self.tituloTexto2.draw(self.screen)
                self.tituloTexto3.draw(self.screen)
                self.enemigo1texto.draw(self.screen)
                self.enemigo2texto.draw(self.screen)
                self.enemigo3texto.draw(self.screen)
                self.enemigo4texto.draw(self.screen)
                self.tablero()

            elif self.comenzarPartida:
                if len(self.enemigos) == 0:
                    currentTime = time.get_ticks()
                    if currentTime - self.gameTimer < 3000:              
                        self.screen.blit(self.fondo2, (0,0))
                        self.puntosTexto2 = Texto(FONT, 20, str(self.puntaje), GREEN, 100, 5)
                        
                        self.puntosTexto2.draw(self.screen)
                        self.nextRoundText.draw(self.screen)
                        self.livesText.draw(self.screen)
                        self.vidasGrupo.update(self.keys)
                        self.controles_nave()
                    if currentTime - self.gameTimer > 3000:
                        self.reset(self.puntaje, self.vidas)
                        self.enemyposition += 35
                        self.generar_enemigos()
                        self.gameTimer += 3000
                else:
                    currentTime = time.get_ticks()
                    self.play_main_music(currentTime)              
                    self.screen.blit(self.fondo2, (0,0))
                    self.todasLasDefensas.update(self.screen)
                    self.puntosTexto2 = Texto(FONT, 20, str(self.puntaje), GREEN, 100, 5)
                    self.scoreText.draw(self.screen)
                    self.puntosTexto2.draw(self.screen)
                    self.livesText.draw(self.screen)
                    self.controles_nave()
                    self.sprites.update(self.keys, currentTime, self.filaDerrotada, self.columnaDerrotada, self.killedArray)
                    self.explosionsGroup.update(self.keys, currentTime)
                    self.colisiones()
                    self.generar_nave_nueva(self.naveNueva, currentTime)
                    self.velocidad_del_enemigo()

                    if len(self.enemigos) > 0:
                        self.Generar_Disparo_Enemigo()
    
            elif self.gameOver:
                currentTime = time.get_ticks()
                self.game_over(currentTime)

            display.update()
            self.clock.tick(60)
                

if __name__ == '__main__':
    game = VentanaPrincipal()
    game.main()

