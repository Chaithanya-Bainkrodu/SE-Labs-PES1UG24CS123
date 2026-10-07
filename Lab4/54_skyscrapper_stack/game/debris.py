import pygame


class Debris:
    def __init__(self, x, y, width, height, color, vx):
        self.width = float(width)
        self.height = float(height)

        # Center anchor coordinates
        self.x = float(x) + self.width / 2.0
        self.y = float(y) + self.height / 2.0

        self.color = color
        self.vx = float(vx)
        self.vy = -2.0  # Slight upward initial hop
        self.gravity = 0.4
        self.angle = 0.0
        self.rot_speed = 4.0 if self.vx >= 0 else -4.0

        # Subpixel handling: Ensure Pygame surface dimensions are valid positive integers (>= 1 px)
        surf_w = max(1, int(round(self.width)))
        surf_h = max(1, int(round(self.height)))

        # Pre-render base surface
        self.base_surface = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
        self.base_surface.fill(self.color)
        pygame.draw.rect(
            self.base_surface,
            (245, 245, 250),
            (0, 0, surf_w, surf_h),
            width=2,
            border_radius=2,
        )

    def update(self):
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy
        self.angle = (self.angle + self.rot_speed) % 360.0

    def render(self, surface):
        # Rotate pre-rendered base surface around its center anchor
        rotated_surf = pygame.transform.rotate(self.base_surface, self.angle)
        rect = rotated_surf.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(rotated_surf, rect)

    def is_offscreen(self, screen_height):
        # Account for potential rotated extent radius
        max_extent = max(self.width, self.height)
        return (self.y - max_extent) > screen_height