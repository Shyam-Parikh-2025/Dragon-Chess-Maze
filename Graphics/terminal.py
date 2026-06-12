import pygame as pg

class Terminal:
    def __init__(self, x, y, width, height):
        self.rect = pg.Rect(x,y, width, height)
        self.action_log = []
        self.dev_action_log = []

        self.font = pg.font.SysFont("consolas", 14)

        self.bg_color = (20, 20, 20)
        self.dev_border = (255, 50, 50)
        self.standard_border = (150, 150, 150)
        self.text_color = (220, 220, 220)
        self.line_height = 18
    
    def log_msg(self, dev_mode: bool, *args):

        raw_msg = " ".join([str(arg) for arg in args])

        max_chars_per_line = max(1, self.rect.width // 8 - 2)

        while len(raw_msg) > 0:
            line_part = raw_msg[:max_chars_per_line]
            raw_msg = raw_msg[max_chars_per_line:]
            if dev_mode:
                self.dev_action_log.append(line_part)
            else:
                self.action_log.append(line_part)
        max_lines = max(0, (self.rect.height - 10)//self.line_height)

        if dev_mode:
            while len(self.dev_action_log) > max_lines:
                self.dev_action_log.pop(0)
        else:
            while len(self.action_log) > max_lines:
                self.action_log.pop(0)
    
    def render(self, surface, dev_mode: bool):
        pg.draw.rect(surface, self.bg_color, self.rect)

        current_border = self.dev_border if dev_mode else self.standard_border
        pg.draw.rect(surface, current_border, self.rect, 2)

        y_offset = self.rect.y + 5
        for line in (self.action_log if not dev_mode else self.dev_action_log):
            text_surf = self.font.render(line, True, self.text_color)
            surface.blit(text_surf, (self.rect.x + 5, y_offset))
            y_offset += self.line_height
    
    def resize(self, screen_width, screen_height):
        self.rect.x = screen_width - 200
        self.rect.y = screen_height // 2
        self.rect.height = int(screen_height * 0.3)

        max_lines = max(0, (self.rect.height - 10) // self.line_height)
        while len(self.action_log) > max_lines:
            self.action_log.pop(0)
        while len(self.dev_action_log) > max_lines:
            self.dev_action_log.pop(0)

