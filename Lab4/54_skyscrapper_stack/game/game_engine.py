import random
import pygame
from game.block import Block
from game.debris import Debris


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.block_height = 28
        self.base_width = 180
        self.alignment_tolerance = 5.0

        self.font_title = pygame.font.SysFont(None, 38)
        self.font_hud = pygame.font.SysFont(None, 28)
        self.font_big = pygame.font.SysFont(None, 46)

        # Pre-allocate gradient background surface for efficient rendering
        self.bg_surface = pygame.Surface((1, self.height))

        self.reset()

    def get_color(self, index):
        palette = [
            (230, 75, 75),   # Crimson
            (240, 140, 45),  # Orange
            (245, 210, 50),  # Gold
            (60, 195, 110),  # Green
            (50, 150, 240),  # Blue
            (165, 80, 225),  # Purple
        ]
        return palette[index % len(palette)]

    def reset(self):
        self.score = 0
        self.points = 0
        self.perfect_streak = 0
        self.game_over = False

        self.feedback_text = ""
        self.feedback_timer = 0
        self.debris = []

        base_x = (self.width - self.base_width) // 2
        base_y = self.height - 60
        base_block = Block(base_x, base_y, self.base_width, self.block_height, self.get_color(0), speed=0)
        self.stack = [base_block]

        self.spawn_active_block()

    def spawn_active_block(self):
        top_block = self.stack[-1]
        next_y = top_block.y - self.block_height - 4
        speed = min(10.0, 4.5 + (len(self.stack) * 0.35))
        color = self.get_color(len(self.stack))

        start_x = 25 if random.choice([True, False]) else self.width - 25 - top_block.width
        self.active_block = Block(start_x, next_y, top_block.width, self.block_height, color, speed=speed)

    def drop_block(self):
        if self.game_over:
            return

        top_block = self.stack[-1]
        act = self.active_block

        left = max(act.x, top_block.x)
        right = min(act.x + act.width, top_block.x + top_block.width)
        overlap = right - left
        
        is_successful_drop = overlap > 0
        
        if is_successful_drop:
            offset = abs(act.x - top_block.x)
            is_perfect = offset <= self.alignment_tolerance

            if is_perfect:
                self.perfect_streak += 1
                base_points = 1 + 5
                self.points += base_points

                new_width = act.width
                if self.perfect_streak % 3 == 0 and new_width < self.base_width:
                    new_width = min(self.base_width, new_width + 10.0)
                    self.feedback_text = f"PERFECT! +5 (Streak {self.perfect_streak} - Width Restored!)"
                else:
                    self.feedback_text = f"PERFECT! +5"

                self.feedback_timer = 60

                new_x = top_block.x + (top_block.width - new_width) / 2.0
                new_x = max(20.0, min(self.width - 20.0 - new_width, new_x))

                new_block = Block(new_x, act.y, new_width, self.block_height, act.color, speed=0)
            else:
                self.perfect_streak = 0
                self.points += 1

                # Generate Debris for off-cut portions
                if act.x < top_block.x:
                    off_width = top_block.x - act.x
                    self.debris.append(Debris(act.x, act.y, off_width, self.block_height, act.color, vx=-2.0))
                
                if act.x + act.width > top_block.x + top_block.width:
                    off_width = (act.x + act.width) - (top_block.x + top_block.width)
                    off_x = top_block.x + top_block.width
                    self.debris.append(Debris(off_x, act.y, off_width, self.block_height, act.color, vx=2.0))

                trimmed_width = overlap
                new_block = Block(left, act.y, trimmed_width, self.block_height, act.color, speed=0)

            self.stack.append(new_block)
            self.score += 1

            if new_block.y < 180:
                shift_amount = self.block_height + 4
                for b in self.stack:
                    b.y += shift_amount
                for d in self.debris:
                    d.y += shift_amount

            self.spawn_active_block()
        else:
            self.game_over = True

    def handle_event(self, event):
        if self.game_over:
            if (event.type == pygame.KEYDOWN and event.key in (pygame.K_r, pygame.K_SPACE)) or \
               (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
                self.reset()
            return

        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.drop_block()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.drop_block()

    def update(self):
        if not self.game_over:
            self.active_block.update(self.width)
            if self.feedback_timer > 0:
                self.feedback_timer -= 1

        for d in self.debris:
            d.update()

        self.debris = [d for d in self.debris if not d.is_offscreen(self.height)]

    def _get_sky_colors(self):
        # Color milestones: (top_color, bottom_color)
        phases = [
            (0,  (100, 180, 240), (210, 235, 255)),  # Day
            (10, (220, 90, 50),   (250, 180, 80)),   # Sunset
            (25, (60, 30, 90),    (170, 70, 120)),   # Twilight
            (45, (10, 12, 30),    (30, 40, 75)),     # High Atmosphere / Night
        ]

        h = self.score
        if h <= phases[0][0]:
            return phases[0][1], phases[0][2]
        if h >= phases[-1][0]:
            return phases[-1][1], phases[-1][2]

        for i in range(len(phases) - 1):
            h1, top1, bot1 = phases[i]
            h2, top2, bot2 = phases[i + 1]
            if h1 <= h <= h2:
                t = (h - h1) / float(h2 - h1)
                
                def lerp(c1, c2):
                    return tuple(int(max(0, min(255, c1[j] + (c2[j] - c1[j]) * t))) for j in range(3))

                return lerp(top1, top2), lerp(bot1, bot2)

        return phases[0][1], phases[0][2]

    def render(self, screen):
        top_color, bot_color = self._get_sky_colors()

        # Render gradient to 1-pixel wide vertical surface and scale up
        for y in range(self.height):
            t = y / float(self.height)
            r = int(top_color[0] + (bot_color[0] - top_color[0]) * t)
            g = int(top_color[1] + (bot_color[1] - top_color[1]) * t)
            b = int(top_color[2] + (bot_color[2] - top_color[2]) * t)
            self.bg_surface.set_at((0, y), (r, g, b))

        scaled_bg = pygame.transform.scale(self.bg_surface, (self.width, self.height))
        screen.blit(scaled_bg, (0, 0))

        title_surf = self.font_title.render("Skyscraper Stack", True, (245, 245, 245))
        screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 16))

        score_surf = self.font_hud.render(f"Height: {self.score}  |  Points: {self.points}", True, (255, 220, 80))
        screen.blit(score_surf, (self.width // 2 - score_surf.get_width() // 2, 54))

        if self.feedback_timer > 0 and self.feedback_text:
            feed_surf = self.font_hud.render(self.feedback_text, True, (80, 240, 120))
            screen.blit(feed_surf, (self.width // 2 - feed_surf.get_width() // 2, 84))

        for b in self.stack:
            b.render(screen)

        for d in self.debris:
            d.render(screen)

        if not self.game_over:
            self.active_block.render(screen)

        if self.game_over:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 195))
            screen.blit(overlay, (0, 0))

            over_surf = self.font_big.render("TOWER COLLAPSED!", True, (240, 75, 75))
            screen.blit(over_surf, (self.width // 2 - over_surf.get_width() // 2, self.height // 2 - 60))

            final_surf = self.font_hud.render(f"Final Height: {self.score}  |  Points: {self.points}", True, (255, 255, 255))
            screen.blit(final_surf, (self.width // 2 - final_surf.get_width() // 2, self.height // 2 - 10))

            restart_surf = self.font_hud.render("Press [Space] or [R] to Play Again", True, (200, 200, 200))
            screen.blit(restart_surf, (self.width // 2 - restart_surf.get_width() // 2, self.height // 2 + 30))