import pygame as pg

class ScrollManager:
    def __init__(self, view_height):
        self.view_h = view_height
        self.content_h = 0
        self.scroll_y = 0

    def clamp(self):
        """Prevents scrolling too far up or down."""
        # 1. Figure out the maximum distance we can scroll
        max_scroll = max(0, self.content_h - self.view_h)
        
        # 2. Force scroll_y to stay between 0 (top) and max_scroll (bottom)
        self.scroll_y = max(0, min(self.scroll_y, max_scroll))

    def scroll(self, amount):
        """Moves the scroll position and clamps it."""
        self.scroll_y += amount
        self.clamp()
    


class Message:
    def __init__(self, text, sender="undefined", color=(255,255,255), max_width=200, 
                 max_height=0,border_width=0,shape: str = "undefined", bg_color=(255, 255, 255, 0)) -> None:
        self.sender = sender
        if isinstance(color, tuple) and len(color) >= 3:
            self.color = (int(color[0]), int(color[1]), int(color[2]))
        else:
            self.color = (255, 255, 255)
        if isinstance(bg_color, tuple) and len(bg_color) >= 3:
            self.bg_color = tuple(int(c) for c in bg_color)
        else:
            self.bg_color = (255, 255, 255, 0)
        self.shape = shape
        self.font = pg.font.SysFont("consolas", 14)
        self.name_font = pg.font.SysFont("consolas", 14, bold=True)
        self.max_width, self.max_height, self.border_width, shape = max_width, max_height, border_width, shape
        if self.max_height > 0:
            self.max_width -= 10 # space for scroll if height is limited
        self.lines = self._word_wrap(str(text), max_width)

        self.height = (len(self.lines) * self.font.get_linesize()) + 20
        if self.sender != "undefined":
            self.height += 15
    
    def _word_wrap(self, text, max_width) -> list:
        words = text.split(' ')
        lines = []
        current_line = []

        for word in words:
            current_line.append(word)
            test_line = " ".join(current_line)
            if self.font.size(test_line)[0] > max_width - 20:
                current_line.pop()
                lines.append(" ".join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(" ".join(current_line))
        return lines
    
    def render(self, surface, x, y):
        draw_height = self.height
        if self.max_height > 0 and self.height > self.max_height:
            draw_height = self.max_height
        
        rect = pg.Rect(x,y, self.max_width, draw_height)
        
        # want to add more shapes later
        radius = 15 if self.shape == "rounded" else (25 if self.shape == "oval" else 0)

        if len(self.bg_color) == 4 and self.bg_color[3] < 255:
            temp_surf = pg.Surface((rect.width, rect.height), pg.SRCALPHA)
            pg.draw.rect(temp_surf, self.bg_color, temp_surf.get_rect(), border_radius=radius)
            if self.border_width > 0:
                pg.draw.rect(temp_surf, self.color, temp_surf.get_rect(), self.border_width, border_radius=radius)
            surface.blit(temp_surf, rect.topleft)
        else:
            pg.draw.rect(surface, self.bg_color, rect, border_radius=radius)
            if self.border_width > 0:
                pg.draw.rect(surface, self.color, rect, self.border_width, border_radius=radius)
        
        old_clip = surface.get_clip()
        surface.set_clip(rect.clip(old_clip))

        text_y = y + 10
        text_x = x + 10

        if self.sender != "undefined":
            name_surf = self.name_font.render(f"[{self.sender}]", True, self.color)
            surface.blit(name_surf, (text_x, text_y))
            text_y += 15
        
        for line in self.lines:
            text_surf = self.font.render(line, True, (220, 220, 220))
            surface.blit(text_surf, (text_x, text_y))
            text_y += self.font.get_linesize()
        
        surface.set_clip(old_clip)

class ChatBox:
    def __init__(self, x, y, width, height, mode="chat", on_submit=None) -> None:
        self.rect = pg.Rect(x, y, width, height)
        self.msgs = []
        self.on_submit = on_submit
        self.buttons = []
        self.mode = mode
        
        self.input_text = ""
        self.input_active = False
        self.input_font = pg.font.SysFont("consolas", 16)

        view_h = height - (40 if mode == 'chat' else 60)
        self.scroller = ScrollManager(view_height=view_h)

        self.dev_msgs = []
    
    def add_button(self, text, callback):
        self.buttons.append({"text": text, "callback": callback})
    
    def add_message(self, message: Message, is_dev: bool=False):
        if is_dev:
            self.dev_msgs.append(message)
            if len(self.dev_msgs) > 50:
                self.dev_msgs.pop(0)
        else:
            if len(self.msgs) > 50:
                self.msgs.pop(0)
            self.msgs.append(message)

        active_list = self.dev_msgs if is_dev else self.msgs

        self.scroller.content_h = sum(msg.height + 10 for msg in active_list)

        self.scroller.scroll_y = float('inf')
        self.scroller.clamp()
    
    def handle_event(self, event):
        consumed = False
        mouse_pos = pg.mouse.get_pos()
        hovering = self.rect.collidepoint(mouse_pos)

        if event.type == pg.MOUSEWHEEL:
            if hovering or (self.mode == "chat" and self.input_active):
                self.scroller.scroll(event.y * -25)
                return True

        if self.mode == "chat":
            if event.type == pg.KEYDOWN:
                if self.input_active and event.key == pg.K_PAGEUP:
                    self.scroller.scroll(-50)
                    return True
                if self.input_active and event.key == pg.K_PAGEDOWN:
                    self.scroller.scroll(50)
                    return True

                if not self.input_active and (event.key == pg.K_RETURN or event.key == pg.K_SLASH):
                    self.input_active = True
                    self.input_text = "/" if event.key == pg.K_SLASH else ""
                    consumed = True
                elif self.input_active:
                    if event.key == pg.K_RETURN:
                        if self.input_text.strip() and self.on_submit:
                            self.on_submit(self.input_text)
                        self.input_text = ""
                        self.input_active = False
                    elif event.key == pg.K_ESCAPE:
                        self.input_active = False
                    elif event.key == pg.K_BACKSPACE:
                        if len(self.input_text) >= 1: self.input_text = self.input_text[:-1]
                    else:
                        self.input_text += event.unicode
                    consumed = True
        elif self.mode == "popup":
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                for btn in self.buttons:
                    if "rect" in btn and btn["rect"].collidepoint(event.pos):
                        btn["callback"]()
                        consumed = True
        return consumed

    def render(self, surface, dev_mode=False):
        bg_color = (40, 20, 20) if dev_mode else (20, 20, 25)
        pg.draw.rect(surface, bg_color, self.rect)
        
        old_clip = surface.get_clip()
        view_rect = pg.Rect(self.rect.x, self.rect.y, self.rect.width, self.scroller.view_h)
        if old_clip:
            surface.set_clip(view_rect.clip(old_clip))
        else:
            surface.set_clip(view_rect)

        current_y = self.rect.y - self.scroller.scroll_y + 10
        active_list = self.dev_msgs if dev_mode else self.msgs
        for msg in active_list:
            if current_y + msg.height > self.rect.y and current_y < self.rect.y + self.scroller.view_h:
                msg.render(surface, self.rect.x + 10, current_y)
            current_y += msg.height + 10
        
        surface.set_clip(old_clip)

        input_h = 40 if self.mode == 'chat' else 60
        input_rect = pg.Rect(self.rect.x, self.rect.bottom - input_h, self.rect.width, input_h)
        pg.draw.rect(surface, bg_color, input_rect)

        pg.draw.rect(surface, (150, 150, 150), self.rect, 2) # main border

        if self.mode == 'chat':
            pg.draw.line(surface, (150, 150, 150), (self.rect.x, self.rect.bottom - 40), (self.rect.right, self.rect.bottom - 40))
            if self.input_active:
                cursor = "_" if (pg.time.get_ticks() // 500) % 2 == 0 else " "
                txt_surf = self.input_font.render(f"> {self.input_text}{cursor}", True, (50, 255, 50))
            else:
                txt_surf = self.input_font.render("Press 'Enter' to chat...", True, (150, 150, 150))
            surface.blit(txt_surf, (self.rect.x + 10, self.rect.bottom - 30))
        elif self.mode == "popup":
            pg.draw.line(surface, (150, 150, 150), (self.rect.x, self.rect.bottom -60), (self.rect.right, self.rect.bottom - 60))
            if len(self.buttons) > 0:
                button_w = (self.rect.width - 20) // len(self.buttons)
                for i, btn in enumerate(self.buttons):
                    bx = self.rect.x + 10 + (i * button_w)
                    by = self.rect.bottom - 50
                    btn_rect = pg.Rect(bx + 5, by, button_w - 10, 40)
                    btn["rect"] = btn_rect
                    color = (80, 80, 100) if btn_rect.collidepoint(pg.mouse.get_pos()) else (50, 50, 60)
                    pg.draw.rect(surface, color, btn_rect, border_radius=8)
                    pg.draw.rect(surface, (150, 150, 150), btn_rect, 1, border_radius=8)
                    txt_surf = self.input_font.render(btn["text"], True, (255, 255, 255))
                    surface.blit(txt_surf, txt_surf.get_rect(center=btn_rect.center))

    def log_msg(self, dev_mode, *args, color=None, sender="System"):
        msg_text = " ".join(str(arg) for arg in args)
        txt_color = color if color else (255, 255, 255)

        new_msg = Message(text= msg_text, sender=sender, color=txt_color, 
                          max_width=self.rect.width - 20, shape="rounded", 
                          bg_color=(50, 50, 60, 200))
        self.add_message(new_msg, is_dev=dev_mode)
    
    def resize(self, screen_width, screen_height):
        self.rect.x = screen_width - self.rect.width
        self.rect.y = int(screen_height * 0.5)
        self.rect.height = int(screen_height * 0.3)
        self.scroller.view_h = self.rect.height - (40 if self.mode == 'chat' else 60)
        self.scroller.clamp()
                
