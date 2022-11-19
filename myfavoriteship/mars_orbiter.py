import os
import math
import random
import pygame as pg

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
LT_BLUE = (173, 216, 230)

class Satellite(pg.sprite.Sprite):
    #Спутниковый объект, который вращается лицом к планете, разбивается и горит
    
    def __init__(self, background):
        super().__init__()
        self.background = background
        self.image_sat = pg.image.load("satellite.png").convert()
        self.image_crash = pg.image.load("satellite_crash_40x33.png").convert()
        self.image = self.image_sat
        self.rect = self.image.get_rect()
        self.image.set_colorkey(BLACK)  # задает прозрачный цвет
        self.x = random.randrange(315, 425)
        self.y = random.randrange(70, 180) 
        self.dx = random.choice([-3, 3])
        self.dy = 0
        self.heading = 0  # инициализирует ориентацию тарелки
        self.fuel = 100
        self.mass = 1
        self.distance = 0  # инициализирует расстояние между спутником и планетой
        self.thrust = pg.mixer.Sound('thrust_audio.ogg')
        self.thrust.set_volume(0.07)  # допустимые значения: 0-1

    def thruster(self, dx, dy):
        #Выполнение действий, связанных с стрельбой подруливающих устройств
        self.dx += dx
        self.dy += dy
        self.fuel -= 2
        self.thrust.play()     

    def check_keys(self):
        #Проверьте, нажимает ли пользователь клавиши со стрелками и вызывает метод thruster(").
        keys = pg.key.get_pressed()       
        # fire thrusters
        if keys[pg.K_RIGHT]:
            self.thruster(dx=0.05, dy=0)
        elif keys[pg.K_LEFT]:
            self.thruster(dx=-0.05, dy=0)
        elif keys[pg.K_UP]:
            self.thruster(dx=0, dy=-0.05)  
        elif keys[pg.K_DOWN]:
            self.thruster(dx=0, dy=0.05)
            
    def locate(self, planet):
        #Рассчитайте расстояние и направляйтесь к планете
        px, py = planet.x, planet.y
        dist_x = self.x - px
        dist_y = self.y - py
        # получить направление на планету к точечному блюду
        planet_dir_radians = math.atan2(dist_x, dist_y)
        self.heading = planet_dir_radians * 180 / math.pi
        self.heading -= 90  # спрайт путешествует хвостом первым
        self.distance = math.hypot(dist_x, dist_y)

    def rotate(self):
        #Вращайте спутник, используя градусы, чтобы тарелка была обращена к планете
        self.image = pg.transform.rotate(self.image_sat, self.heading)
        self.rect = self.image.get_rect()

    def path(self):
        #Обновите положение спутника и проведите линию, чтобы проследить орбитальный путь
        last_center = (self.x, self.y)
        self.x += self.dx
        self.y += self.dy
        pg.draw.line(self.background, WHITE, last_center, (self.x, self.y))

    def update(self):
        #Обновление спутникового объекта во время игры
        self.check_keys()
        self.rotate()
        self.path()
        self.rect.center = (self.x, self.y)        
        # изменить изображение на огненно-красный, если в атмосфере
        if self.dx == 0 and self.dy == 0:
            self.image = self.image_crash
            self.image.set_colorkey(BLACK)
            
class Planet(pg.sprite.Sprite):
    #Планетарный объект, который вращается и проецирует гравитационное поле
    
    def __init__(self):
        super().__init__()
        self.image_mars = pg.image.load("mars.png").convert()
        self.image_water = pg.image.load("mars_water.png").convert() 
        self.image_copy = pg.transform.scale(self.image_mars, (100, 100)) 
        self.image_copy.set_colorkey(BLACK) 
        self.rect = self.image_copy.get_rect()
        self.image = self.image_copy
        self.mass = 2000 
        self.x = 400 
        self.y = 320
        self.rect.center = (self.x, self.y)
        self.angle = math.degrees(0)
        self.rotate_by = math.degrees(0.01)

    def rotate(self):
        #Поворачивайте изображение планеты с каждым игровым циклом
        last_center = self.rect.center
        self.image = pg.transform.rotate(self.image_copy, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = last_center
        self.angle += self.rotate_by

    def gravity(self, satellite):
        #Рассчитать воздействие силы тяжести на спутник
        G = 1.0  # gravitational constant for game
        dist_x = self.x - satellite.x
        dist_y = self.y - satellite.y
        distance = math.hypot(dist_x, dist_y)     
        # нормализовать до единичного вектора
        dist_x /= distance
        dist_y /= distance
        # применить гравитацию
        force = G * (satellite.mass * self.mass) / (math.pow(distance, 2))
        satellite.dx += (dist_x * force)
        satellite.dy += (dist_y * force)
        
    def update(self):
        #Вызов метода поворота
        self.rotate()

def calc_eccentricity(dist_list):
    #Вычислить и вернуть эксцентриситет из списка радиусов
    apoapsis = max(dist_list)
    periapsis = min(dist_list)
    eccentricity = (apoapsis - periapsis) / (apoapsis + periapsis)
    return eccentricity

def instruct_label(screen, text, color, x, y):
    #Возьмите экран, список строк, цвета и происхождения и отобразите текст на экране
    instruct_font = pg.font.SysFont(None, 25)
    line_spacing = 22
    for index, line in enumerate(text):
        label = instruct_font.render(line, True, color, BLACK)
        screen.blit(label, (x, y + index * line_spacing))

def box_label(screen, text, dimensions):
    #Сделайте метку фиксированного размера из экрана, текста и слева, сверху, ширины, высоты
    readout_font = pg.font.SysFont(None, 27)
    base = pg.Rect(dimensions)
    pg.draw.rect(screen, WHITE, base, 0)
    label = readout_font.render(text, True, BLACK)
    label_rect = label.get_rect(center=base.center)
    screen.blit(label, label_rect)

def mapping_on(planet):
    #Показать изображение влажности почвы на Марсе
    last_center = planet.rect.center
    planet.image_copy = pg.transform.scale(planet.image_water, (100, 100))
    planet.image_copy.set_colorkey(BLACK)
    planet.rect = planet.image_copy.get_rect()
    planet.rect.center = last_center

def mapping_off(planet):
    #Восстановить нормальное изображение планеты
    planet.image_copy = pg.transform.scale(planet.image_mars, (100, 100))
    planet.image_copy.set_colorkey(BLACK)

def cast_shadow(screen):
    #Добавить необязательный терминатор и тень за планетой на экран
    shadow = pg.Surface((400, 100), flags=pg.SRCALPHA)  # кортеж w,h
    shadow.fill((0, 0, 0, 210))  # прозрачность последних наборов чисел
    screen.blit(shadow, (0, 270))  # Кортеж - координаты слева сверху

def main():
    #Настройте метки и инструкции, создайте объекты и запустите игровой цикл
    pg.init()  # инициализировать pygame
    
    # настроенный дисплей
    os.environ['SDL_VIDEO_WINDOW_POS'] = '700, 100'  # установить происхождение окна игры
    screen = pg.display.set_mode((800, 645), pg.FULLSCREEN) 
    pg.display.set_caption("Mars Orbiter")
    background = pg.Surface(screen.get_size())

    # включить звуковой микшер
    pg.mixer.init()

    intro_text = [
        ' The Mars Orbiter experienced an error during Orbit insertion.',
        ' Use thrusters to correct to a circular mapping orbit without',
        ' running out of propellant or burning up in the atmosphere.'
        ]
 
    instruct_text1 = [
        'Orbital altitude must be within 69-120 miles',
        'Orbital Eccentricity must be < 0.05',
        'Avoid top of atmosphere at 68 miles'    
        ]

    instruct_text2 = [
        'Left Arrow = Decrease Dx', 
        'Right Arrow = Increase Dx', 
        'Up Arrow = Decrease Dy', 
        'Down Arrow = Increase Dy', 
        'Space Bar = Clear Path',
        'Escape = Exit Full Screen'        
        ]  

    # создание экземпляров планет и спутниковых объектов
    planet = Planet()
    planet_sprite = pg.sprite.Group(planet)
    sat = Satellite(background)    
    sat_sprite = pg.sprite.Group(sat)

    # для верификации круговой орбиты
    dist_list = []  
    eccentricity = 1
    eccentricity_calc_interval = 5  # оптимизирован для высоты 120 миль
    
    # хронометраж
    clock = pg.time.Clock()
    fps = 30
    tick_count = 0

    # для функции картирования влажности почвы
    mapping_enabled = False
    
    running = True
    while running:
        clock.tick(fps)
        tick_count += 1
        dist_list.append(sat.distance)
        
        # получить ввод с клавиатуры
        for event in pg.event.get():
            if event.type == pg.QUIT:  # закрыть окно
                running = False
            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                screen = pg.display.set_mode((800, 645))  # выход из полноэкранного режима
            elif event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                background.fill(BLACK)  # четкий путь
            elif event.type == pg.KEYUP:
                sat.thrust.stop()  # стоп-звук
                mapping_off(planet)  # выключить вид карты влажности
            elif mapping_enabled:
                if event.type == pg.KEYDOWN and event.key == pg.K_m:
                    mapping_on(planet)

        # получить направление и расстояние до планеты и применить гравитацию
        sat.locate(planet)  
        planet.gravity(sat)

        # рассчитать эксцентриситет орбиты
        if tick_count % (eccentricity_calc_interval * fps) == 0:
            eccentricity = calc_eccentricity(dist_list)
            dist_list = []              

        # re-blit фон для команды рисования - предотвращает очистку контура
        screen.blit(background, (0, 0))
        
        # Условия отказа топлива/высоты
        if sat.fuel <= 0:
            instruct_label(screen, ['Fuel Depleted!'], RED, 340, 195)
            sat.fuel = 0
            sat.dx = 2
        elif sat.distance <= 68:
            instruct_label(screen, ['Atmospheric Entry!'], RED, 320, 195)
            sat.dx = 0
            sat.dy = 0

        # включить функцию сопоставления
        if eccentricity < 0.05 and sat.distance >= 69 and sat.distance <= 120:
            map_instruct = ['Press & hold M to map soil moisture']
            instruct_label(screen, map_instruct, LT_BLUE, 250, 175)
            mapping_enabled = True
        else:
            mapping_enabled = False

        planet_sprite.update()
        planet_sprite.draw(screen)
        sat_sprite.update()
        sat_sprite.draw(screen)

        # отображать вводный текст в течение 15 секунд
        if pg.time.get_ticks() <= 15000:  # время в миллисекундах
            instruct_label(screen, intro_text, GREEN, 145, 100)

        # отображение телеметрии и инструкций
        box_label(screen, 'Dx', (70, 20, 75, 20))
        box_label(screen, 'Dy', (150, 20, 80, 20))
        box_label(screen, 'Altitude', (240, 20, 160, 20))
        box_label(screen, 'Fuel', (410, 20, 160, 20))
        box_label(screen, 'Eccentricity', (580, 20, 150, 20))
        
        box_label(screen, '{:.1f}'.format(sat.dx), (70, 50, 75, 20))     
        box_label(screen, '{:.1f}'.format(sat.dy), (150, 50, 80, 20))
        box_label(screen, '{:.1f}'.format(sat.distance), (240, 50, 160, 20))
        box_label(screen, '{}'.format(sat.fuel), (410, 50, 160, 20))
        box_label(screen, '{:.8f}'.format(eccentricity), (580, 50, 150, 20))
          
        instruct_label(screen, instruct_text1, WHITE, 10, 575)
        instruct_label(screen, instruct_text2, WHITE, 570, 510)
      
        # добавить терминатор и границу
        cast_shadow(screen)
        pg.draw.rect(screen, WHITE, (1, 1, 798, 643), 1)

        pg.display.flip()

if __name__ == "__main__":
    main()
