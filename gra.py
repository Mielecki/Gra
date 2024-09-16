import pygame
from tkinter import Label, Entry, Button, Tk, BOTTOM, StringVar, OptionMenu
from random import choice
from time import sleep
import math
from enum import Enum

# Domyślne ustawienia
HEIGHT = 1000
triangle_size = 10
rect_width = rect_height = 10
hex_size = 60
oct_size = 100
colors_quant = 2
N = 10
M = 10
FPS = 30
grid = []

# Kolory
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (25, 25, 112)
DARKGREEN = (0, 100, 0)
PINK = (255, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 215, 0)
GREEN = (0, 255, 0)
LIGHTBLUE = (0, 191, 255)
DARKPINK = (176, 48, 96)

COLORS = [BLUE, DARKGREEN, PINK, RED, YELLOW, GREEN, LIGHTBLUE, DARKPINK]

# Kształy siatki
class Shape(Enum):
    RECTANGLE = "KWADRAT"
    TRIANGLE = "TRÓJKĄT"
    HEXAGON = "SZESCIOKAT"
    OCTAGON = "OSMIOKĄT + KWADRAT"

CHOOSE = Shape.TRIANGLE

# Klasa po której dziedziczą kształty. Rysuje ona figury.
class Element:
    def __init__(self, col, row, color):
        self.vertices = []
        self.neighbours = []
        self.col = col
        self.row = row
        self.color = color

    # Rysowanie odbywa się poprzez zmiane koloru obiektu
    def draw(self, screen):
        pygame.draw.polygon(screen, self.color, self.vertices, 0)
        pygame.draw.polygon(screen, (0, 0, 0), self.vertices, 1) # Rysowanie obwodu figury

# Funkcja liczy wyznacznik |(p1-p3)x(p2-p3)| aby określić po której stronie wektora p2p3 leży p1
# Funkcja potrzebna do określenia położenia punkty w figurze
def det(p1, p2, p3):
    return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])

# Klasa odpowiedziala za rysowanie trójkąta.
class Triangle(Element):
    # Obliczanie koorydnatów kolejnych wierzchołków
    def __init__(self, col, row, color):
        super().__init__(col, row, color)
        x_offset = col * triangle_size/2 + triangle_size/2
        y_offset = row * triangle_size

        if (col + row) % 2 == 0:
            v1 = (x_offset, y_offset)
            v2 = (x_offset + triangle_size / 2, y_offset + triangle_size)
            v3 = (x_offset - triangle_size / 2, y_offset + triangle_size)
        else:
            v1 = (x_offset, y_offset + triangle_size)
            v2 = (x_offset + triangle_size / 2, y_offset)
            v3 = (x_offset - triangle_size / 2, y_offset)

        self.vertices = [v1, v2, v3]
    
    # metoda opowiedzialna za obliczenie czy kliknięto wewnątrz figury
    def contains_point(self, point):
        b = [det(point, self.vertices[i], self.vertices[(i + 1) % 3]) < 0.0 for i in range(3)]
        return all(b) or not any(b)

    # metoda odpowiedziala za obliczenie które figury są sąsiadami tego obiektu
    def set_neighbours(self):
        x = self.col
        y = self.row
        if (x + y) % 2 == 0:
            if x-1 >= 0:
                self.neighbours.append((x-1, y))
            if x+1 < N:
                self.neighbours.append((x+1, y))
            if y+1 < M:
                self.neighbours.append((x, y+1))
        else:
            if x-1 >= 0:
                self.neighbours.append((x-1, y))
            if x+1 < N:
                self.neighbours.append((x+1, y))
            if y-1 >= 0:
                self.neighbours.append((x, y-1))

# Kolejne figury analogicznie jak trójkąt
class Rectangle(Element):
    def __init__(self, col, row, color):
        super().__init__(col, row, color)
        x_offset = col * rect_width
        y_offset = row * rect_height
        
        v1 = (x_offset, y_offset)
        v2 = (x_offset + rect_width, y_offset)
        v3 = (x_offset + rect_width, y_offset + rect_height)
        v4 = (x_offset, y_offset + rect_height)
        
        self.vertices = [v1, v2, v3, v4]

    def contains_point(self, point):
        px, py = point
        v1, v2, v3, v4 = self.vertices
        
        return v1[0] <= px <= v3[0] and v1[1] <= py <= v3[1]

    def set_neighbours(self):
        x = self.col
        y = self.row
        if x - 1 >= 0:
            self.neighbours.append((x - 1, y))
        if x + 1 < N:
            self.neighbours.append((x + 1, y))
        if y - 1 >= 0:
            self.neighbours.append((x, y - 1))
        if y + 1 < M:
            self.neighbours.append((x, y + 1))

class Hexagon(Element):
    def __init__(self, col, row, color):
        super().__init__(col, row, color)
        self.calculate_vertices()

    def calculate_vertices(self):
        x_offset = self.col * 3/2 * hex_size + hex_size
        y_offset = self.row * math.sqrt(3) * hex_size + (self.col % 2) * math.sqrt(3) / 2 * hex_size + hex_size

        self.vertices = [
            (x_offset + hex_size * math.cos(math.radians(60 * i)),
             y_offset + hex_size * math.sin(math.radians(60 * i)))
            for i in range(6)
        ]

    def contains_point(self, point):
        b = [det(point, self.vertices[i], self.vertices[(i + 1) % 6]) < 0.0 for i in range(6)]
        return all(b) or not any(b)

    def set_neighbours(self):
        x = self.col
        y = self.row

        if x % 2 == 0:
            potential_neighbours = [
                (x - 1, y), (x + 1, y), 
                (x, y - 1), (x - 1, y - 1), 
                (x, y + 1), (x + 1, y - 1)
            ]
        else:
            potential_neighbours = [
                (x - 1, y), (x + 1, y), 
                (x, y - 1), (x - 1, y + 1), 
                (x, y + 1), (x + 1, y + 1)
            ]

        for nx, ny in potential_neighbours:
            if 0 <= nx < N and 0 <= ny < M:
                self.neighbours.append((nx, ny))

class Octagon(Element):
    def __init__(self, col, row, color):
        super().__init__(col, row, color)
        self.calculate_vertices()

    def calculate_vertices(self):
        angle_step = math.pi / 4
        radius = oct_size * math.sqrt((2 + math.sqrt(2))/2)  # Promień ośmiokąta wpisanego w kwadrat

        x_offset = self.col * (2 * oct_size / math.sqrt(2) + oct_size) + (2 * oct_size / math.sqrt(2) + oct_size)/2
        y_offset = self.row * (2 * oct_size / math.sqrt(2) + oct_size) + (2 * oct_size / math.sqrt(2) + oct_size)/2

        self.vertices = [
            (x_offset + radius * math.cos(angle_step * i + math.pi/8), 
             y_offset + radius * math.sin(angle_step * i + math.pi/8))
            for i in range(8)
        ]

    def contains_point(self, point):
        b = [det(point, self.vertices[i], self.vertices[(i + 1) % 8]) < 0.0 for i in range(8)]
        return all(b) or not any(b)

    def set_neighbours(self):
        x = self.col
        y = self.row
        potential_neighbours = [
            (x - 1, y), (x + 1, y), 
            (x, y - 1), (x, y + 1)
        ]

        for nx, ny in potential_neighbours:
            if 0 <= nx < N and 0 <= ny < M:
                self.neighbours.append((nx, ny))

        potential_neighbours = [
            (x - 1, y + M - 1), (x-1, y+M), 
            (x, y + M - 1), (x, y+M)
        ]

        for nx, ny in potential_neighbours:
            if 0 <= nx < N-1 and M <= ny < 2*M-1:
                self.neighbours.append((nx, ny))

class Square(Element):
    def __init__(self, col, row, color):
        super().__init__(col, row, color)
        x_offset = (col) *(2 * oct_size / math.sqrt(2) + oct_size) + ( oct_size / math.sqrt(2) + oct_size)
        y_offset = (row - N) * (2 * oct_size / math.sqrt(2) + oct_size)+ (2 * oct_size / math.sqrt(2) + oct_size)
        
        v1 = (x_offset, y_offset)
        v2 = (x_offset + oct_size/math.sqrt(2), y_offset + oct_size/math.sqrt(2))
        v3 = (x_offset + oct_size/math.sqrt(2)*2, y_offset)
        v4 = (x_offset + oct_size/math.sqrt(2), y_offset - oct_size/math.sqrt(2))
        self.vertices = [v1, v2, v3, v4]
    def contains_point(self, point):
        b = [det(point, self.vertices[i], self.vertices[(i + 1) % 4]) < 0.0 for i in range(4)]
        return all(b) or not any(b)

    def set_neighbours(self):
        x = self.col
        y = self.row
        if y-M >= 0:
            self.neighbours.append((x, y-M))
        if 0 <= y-M+1 < M:
            self.neighbours.append((x, y-M+1))
        if y-M >= 0 and x + 1 < N:
            self.neighbours.append((x +1, y-M ))
        if 0 <= y-M+1 < M and x + 1 < N:
            self.neighbours.append((x +1, y-M+1 ))

# Główna pętla gry
def game_loop():
    # Tworzenie siatki z wybraną figurą
    def create_grid():
        global grid
        grid = []
        if CHOOSE == Shape.TRIANGLE:
            for x in range(N):
                grid.append([])
                for y in range(M):
                    elem = Triangle(x, y, choice(COLORS[:colors_quant]))
                    grid[x].append(elem)
        elif CHOOSE == Shape.RECTANGLE:
            for x in range(N):
                grid.append([])
                for y in range(M):
                    elem = Rectangle(x, y, choice(COLORS[:colors_quant]))
                    grid[x].append(elem)
        elif CHOOSE == Shape.HEXAGON:
            for x in range(N):
                grid.append([])
                for y in range(M):
                    elem = Hexagon(x, y, choice(COLORS[:colors_quant]))
                    grid[x].append(elem)
        elif CHOOSE == Shape.OCTAGON:
            for x in range(N):
                grid.append([])
                for y in range(M):
                    elem = Octagon(x, y, choice(COLORS[:colors_quant]))
                    grid[x].append(elem)
                if x < N-1:
                    for y in range(M-1):
                        elem = Square(x, N+y, choice(COLORS[:colors_quant]))
                        grid[x].append(elem)

        for x in range(N):
            for y in range(len(grid[x])):
                grid[x][y].set_neighbours()

    # Rysowanie siatki poprzez zmiane/pozostawienie koloru dla każdej figury
    def draw_grid():
        for x in range(N):
            for y in range(len(grid[x])):
                grid[x][y].draw(screen)

    # Zmiana koloru poprzez iterowanie po tablicy z kolorami z ograniczeniem modulo wybranej ilości kolorów
    def change_color(x, y):
        grid[x][y].color = COLORS[(COLORS.index(grid[x][y].color) + 1) % colors_quant ]

    # Kolorowanie sąsiadów figury
    def color_neighbours(x, y):
        change_color(x, y)
        for xn, yn in grid[x][y].neighbours:
            change_color(xn, yn)

    # Sprawdzenie czy koniec gry, gdy wszystkie figury mają ten sam kolor
    def check_game_over():
        color = grid[0][0].color
        for x in range(N):
            for y in range(M):
                if grid[x][y].color != color:
                    return False
        return True
    
    # Pętla odpowiedzialna za jedną klatke w grze
    def refresh():
        def victory_window():
            pygame.quit()

            root = Tk()
            root.title("WYGRANA")
            root.geometry("500x100")

            label = Label(root)
            label.pack()

            def change_colors():
                current_bg = root.cget("bg")
                new_fg = current_bg
                new_bg = 'yellow' if new_fg == "purple" else "purple"
                root.configure(bg=new_bg)
                label.config(text="Wygrana!", fg=new_fg, bg=new_bg, font=("Arial", 36))

                root.after(1000, change_colors)

            change_colors()

            root.mainloop()

        nonlocal running
        screen.fill(BLACK)

        draw_grid()  

        pygame.display.flip()
        if check_game_over():
            sleep(1)
            running = False
            victory_window()

    # "Wyłapywanie" wychodzenia z gry oraz kliknięcia lewym przyciskiem myszy
    def event_handler(event):
        nonlocal running

        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Jeżeli klinięto lewym przyciskiem myszy to sprawdzane jest czy kliknięto wewnątrz figury
            mouse_pos = pygame.mouse.get_pos()
            x = -1
            y = -1

            for row in grid:
                for elem in row:
                    if elem.contains_point(mouse_pos):
                        x = elem.col
                        y = elem.row

            if (x, y) != (-1, -1):
                color_neighbours(x, y)
            
    
    pygame.init()
    screen = pygame.display.set_mode((HEIGHT, HEIGHT))
    clock = pygame.time.Clock()
    create_grid()
    running = True

    # pętla odpowiedzalna za działanie gry
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            event_handler(event)

        refresh()

    pygame.quit()

# Funkcja tworząca okno początkowe
def start_window():
    # Funkcja ustawiająca odpowiednie zmienne względem wybranych wartości
    def set_values(size_val, shape_val, color_val):
        global N, M, HEIGHT, CHOOSE, triangle_size, rect_height, rect_width, hex_size, oct_size, colors_quant

        colors_quant = int(color_val)
        N = int(size_val)
        CHOOSE = Shape(shape_val)
        M = N

        if CHOOSE == Shape.RECTANGLE:
            rect_width = rect_height = HEIGHT // N
        elif CHOOSE == Shape.TRIANGLE:
            M //=2
            triangle_size = HEIGHT * 2/(N+1)
        elif CHOOSE == Shape.HEXAGON:
            hex_size = HEIGHT/(math.sqrt(3)*(N+1/2))
        elif CHOOSE == Shape.OCTAGON:
            oct_size = HEIGHT/(N + N*2/math.sqrt(2))

    # Funckja sprawdzająca czy wybrane właściwości gry są poprawne
    def check_values(size_val, shape_val, color_val):
        if int(size_val) <= 0: 
            error_window("N musi być większe niż 0")
            return False
        
        if int(color_val) < 2 or int(color_val) > 8:
            error_window("Liczba kolorów musi być z zakresu [2, 8]")
            return False
        
        if Shape(shape_val) not in Shape:
            error_window("Błąd wyboru kształtu")
            return False
        
        return True

    # Funkcja odpowiedzialna za okno błędu
    def error_window(msg):
        root = Tk()
        root.title("Błąd")

        root.geometry("600x60")

        root.configure(bg='red')

        label_input = Label(root, text=f"Błąd: {msg}!\n")
        label_input.config(fg="white")
        label_input.config(font=("Arial", 20))
        label_input.configure(bg='red')
        label_input.pack()

    # Funkcja tworząca i wypełniająca okno początkowe
    def setup():
        nonlocal root

        root.title("Gra")
        root.geometry("600x400")

        info_label = Label(root, text="Generowana jest siatka stworzona z wybranej figury o wymiarach NxN w wybranej liczbe kolorów. Celem gry jest osiągnięcie na każdym polu tego samego koloru. Aby zmienić kolor figury, należy kliknąć na nią, co w rezultacie zmieni kolor jej oraz sąsiednich figur.\n", wraplength=500, justify="center")
        info_label.pack(pady=(10, 0))

        size_input_label = Label(root, text="Wybierz liczbe figur w rzędzie: \n")
        size_input_label.pack(pady=(10, 0))

        size_input = Entry(root)
        size_input.pack(pady=(0, 10))


        shape_input_label = Label(root, text="Wybierz kształt: \n")
        shape_input_label.pack(pady=(10, 0))

        shapes = [e.value for e in Shape]
        shape_input = StringVar(root)
        shape_input.set(shapes[0])

        menu = OptionMenu(root, shape_input, *shapes)
        menu.pack(pady=(0, 10))

        color_input_label = Label(root, text="Wybierz liczbe kolorów z zakresu [2, 8]: \n")
        color_input_label.pack(pady=(10, 0))

        color_input = Entry(root)
        color_input.pack(pady=(0, 10))

        # Funkcja sprawdzająca poprawność zmiennych i je ustawiająca
        def check_input(event):
            try:
                if check_values(size_input.get(), shape_input.get(), color_input.get()): 
                    set_values(size_input.get(), shape_input.get(), color_input.get())
                    game_loop()
            except ValueError:
                error_window("Wprowadź liczbę całkowitą")

        start_button = Button(root, text="Start", command=lambda: check_input(None))
        start_button.pack(side=BOTTOM)
        
        root.bind("<Return>", check_input) # Klinięce enter jest tożsame z klinięciem przycisku Start

    root = Tk()
    setup()
    root.mainloop()


if __name__ == "__main__":
    start_window()