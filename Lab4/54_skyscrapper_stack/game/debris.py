import pygame


class Debris:
    def __init__(self, x, y, width, height, color, vx):
        self.width = float(width)
        self.height = float(height)
        self.x = float(x) + self.width / 2.0
        self.y = float(y) + self.height / 2.0
        self.color = color

        self.vx = float(vx)
        self.vy = -2.0  # slight upward hop on cut
        self.gravity = 0.4

        self.angle = 0.0
        self.rot_speed = 4.0 if vx >= 0 else -4.0

        # Pre-render base surface
        self.base_surface = pygame.Surface((int(self.width), int(self.height)), pygame.SRCALPHA)
        draw_rect = pygame.Rect(0, 0, int(self.width), int(self.height))
        pygame.draw.rect(self.base_surface, self.color, draw_rect, border_radius=2)
        pygame.draw.rect(self.base_surface, (245, 245, 250), draw_rect, width=2, border_radius=2)

    def update(self):
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy
        self.angle = (self.angle + self.rot_speed) % 360

    def render(self, surface):
        rotated_surf = pygame.transform.rotate(self.base_surface, self.angle)
        rect = rotated_surf.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(rotated_surf, rect)

    def is_offscreen(self, screen_height):
        return self.y - self.height / 2.0 > screen_height + 50