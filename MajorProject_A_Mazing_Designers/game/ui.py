import pygame as pg
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
DARK_GRAY = (100, 100, 100)

class UI_MANAGER:
    def __init__(self):
        self.elements = []
        self.enable = True

    def handle_event(self, event):
        if self.enable:
            for element in self.elements:
                element.handle_event(event)

    def update(self):
        if self.enable:
            for element in self.elements:
                element.update()

    def draw(self):
        if self.enable:
            for element in self.elements:
                element.draw()

    def enable_disable(self):
        self.enable = not self.enable


class UI:
    def __init__(self, x, y, width, height, surface):
        self.rect = pg.Rect(x, y, width, height)
        self.hovered = False
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.surface = surface

    def update(self):
        self.hovered = self.rect.collidepoint(pg.mouse.get_pos())

class Slider(UI):
    def __init__(self, x, y, width, height, surface, initial_val=0.5):
        super().__init__(x, y, width, height, surface)
        self.value = initial_val
        self.dragging = False
        self.knob_width = 15
        self.knob = pg.Rect(x, y, self.knob_width, height + 10)
        self.update_knob_pos()

    def update_knob_pos(self):
        min_x, max_x = self.rect.left, self.rect.right
        center_x = self.rect.x + (self.rect.width * self.value)
        half = self.knob_width // 2
        center_x = max(min_x + half, min(center_x, max_x - half))
        self.knob.centerx = int(center_x)
        self.knob.centery = self.rect.centery

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.knob.collidepoint(event.pos) or self.rect.collidepoint(event.pos):
                self.dragging = True
                self.update_val(event.pos[0])

        elif event.type == pg.MOUSEBUTTONUP:
            self.dragging = False

        elif event.type == pg.MOUSEMOTION and self.dragging:
            self.update_val(event.pos[0])

    def update_val(self, mouse_x):
        x = mouse_x - self.rect.x
        x = max(0, min(x, self.rect.width))
        self.value = x / self.rect.width
        self.update_knob_pos()

    def get_val(self, min_val=0, max_val=100):
        return min_val + (max_val - min_val) * self.value

    def draw(self):
        pg.draw.rect(self.surface, GRAY, self.rect, border_radius=5)
        filled_width = int(self.rect.width * self.value)
        fill_rect = pg.Rect(self.rect.x, self.rect.y, filled_width, self.rect.height)
        pg.draw.rect(self.surface, BLUE, fill_rect, border_radius=5)
        pg.draw.rect(self.surface, WHITE, self.knob, border_radius=5)
        pg.draw.rect(self.surface, BLACK, self.knob, 2, border_radius=5)

class Button(UI):
    def __init__(self, x, y, width, height, surface, on_click,
                 ACTIVE_COLOR=(255, 255, 255), text="Button", toggle=False):
        super().__init__(x, y, width, height, surface)
        self.toggle = toggle
        self.is_active = False
        #self.button = pg.Rect(x, y, width*0.9, height*0.9)
        self.text = text
        self.font = pg.font.Font(None, 32)
        self.ACTIVE_COLOR = ACTIVE_COLOR
        self.on_click = on_click

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if self.toggle:
                    self.is_active = not self.is_active
                    self.on_click()
                else:
                    self.is_active = True

        if event.type == pg.MOUSEBUTTONUP:
            if not self.toggle and self.rect.collidepoint(event.pos):
                self.on_click()
            if not self.toggle:
                self.is_active = False

    def draw(self):
        if self.is_active:
            color = self.ACTIVE_COLOR
        elif self.hovered:
            color = DARK_GRAY
        else:
            color = GRAY
        pg.draw.rect(self.surface, color, self.rect, border_radius=5)
        pg.draw.rect(self.surface, BLACK, self.rect, 2, border_radius=5)
        txt_surface = self.font.render(self.text, True, BLACK)
        txt_rect = txt_surface.get_rect(center=self.rect.center)
        self.surface.blit(txt_surface, txt_rect)

class UserTxtInput(UI):
    def __init__(self, x, y, width, height, surface, txt_size=32, is_password=False,
                 b_color_active=(0, 100, 255), b_color_n=(0, 0, 0),
                 limits="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890 _-",
                 extendable=False):
        super().__init__(x, y, width, height, surface)
        self.active = False
        self.txt = ""
        self.limitations = limits
        self.is_password = is_password
        self.font = pg.font.Font(None, txt_size)
        self.b_color_active = b_color_active
        self.b_color_n = b_color_n
        self.extendable = extendable
        self.min_width = width

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)

        if event.type == pg.KEYDOWN and self.active:
            if event.key == pg.K_RETURN:
                self.active = False
            elif event.key == pg.K_BACKSPACE:
                self.txt = self.txt[:-1]
            else:
                space_allowed = self.surface.get_width() - self.x - 10
                n_txt = self.txt + event.unicode
                if self.font.size(n_txt)[0] <= space_allowed:
                    if event.unicode in self.limitations:
                        self.txt = n_txt

    def draw(self):
        b_color = self.b_color_active if self.active else self.b_color_n
        pg.draw.rect(self.surface, WHITE, self.rect)
        pg.draw.rect(self.surface, b_color, self.rect, 2)

        display_txt = "*" * len(self.txt) if self.is_password else self.txt
        if self.txt == "" and not self.active:
            txt_surface = self.font.render("Enter Here...", True, (211, 211, 211))
        else:
            txt_surface = self.font.render(display_txt, True, BLACK)

        if self.extendable:
            n_width = txt_surface.get_width() + 20
            self.rect.width = max(self.min_width, n_width)
            if self.x + self.rect.width > self.surface.get_width():
                self.rect.width = self.surface.get_width() - self.x

        self.surface.blit(txt_surface,
        (self.x + 5, self.rect.centery - txt_surface.get_height() // 2))

    def clear(self):
        self.txt = ""