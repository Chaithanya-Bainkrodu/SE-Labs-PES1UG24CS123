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

        # Pre-allocate 1px wide background surface for fast scaling
        self.bg_surface = pygame.Surface((1, self.height))

        self.reset()

    def get_color(self, index):
        colors = [
            (230, 75, 75),
            (240, 140, 45),
            (245, 210, 50),
            (60, 195, 110),
            (50, 150, 240),
            (165, 80, 225),
        ]
        return colors[index % len(colors)]

    def _get_sky_colors(self):
        # Color milestones: (height_threshold, top_rgb, bottom_rgb)
        milestones = [
            (0, (100, 180, 240), (210, 235, 255)),   # Daylight
            (10, (220, 90, 50), (250, 180, 80)),     # Sunset
            (25, (60, 30, 90), (170, 70, 120)),      # Twilight
            (45, (10, 12, 30), (30, 40, 75)),        # Deep Space
        ]

        score = self.score

        if score <= milestones[0][0]:
            return milestones[0][1], milestones[0][2]
        if score >= milestones[-1][0]:
            return milestones[-1][1], milestones[-1][2]

        # Find interpolation interval
        for i in range(len(milestones) - 1):
            h_low, top_low, bot_low = milestones[i]
            h_high, top_high, bot_high = milestones[i + 1]

            if h_low <= score <= h_high:
                t = (score - h_low) / float(h_high - h_low)

                top_color = tuple(
                    int(round(top_low[c] + t * (top_high[c] - top_low[c])))
                    for c in range(3)
                )
                bot_color = tuple(
                    int(round(bot_low[c] + t * (bot_high[c] - bot_low[c])))
                    for c in range(3)
                )

                return top_color, bot_color

        return milestones[0][1], milestones[0][2]

    def reset(self):
        self.score = 0
        self.points = 0
        self.perfect_streak = 0
        self.feedback_text = ""
        self.feedback_timer = 0
        self.debris = []
        self.game_over = False

        base_x = (self.width - self.base_width) // 2
        base_y = self.height - 60
        base_block = Block(
            base_x,
            base_y,
            self.base_width,
            self.block_height,
            self.get_color(0),
            speed=0,
        )
        self.stack = [base_block]
        self.spawn_active_block()

    def spawn_active_block(self):
        top_block = self.stack[-1]
        next_y = top_block.y - self.block_height - 4
        speed = min(10.0, 4.5 + len(self.stack) * 0.35)
        color = self.get_color(len(self.stack))
        active_width = top_block.width

        # Randomly choose starting position (left or right)
        start_left = 25
        start_right = self.width - 25 - active_width
        start_x = random.choice([start_left, start_right])

        self.active_block = Block(
            start_x, next_y, active_width, self.block_height, color, speed=speed
        )

    def drop_block(self):
        if self.game_over:
            return

        act = self.active_block
        top_block = self.stack[-1]

        left = max(act.x, top_block.x)
        right = min(act.x + act.width, top_block.x + top_block.width)
        overlap = right - left

        # Reject non-positive overlap (zero or negative)
        if overlap <= 0:
            self.game_over = True
            return

        # Positive overlap -> evaluate perfect alignment
        is_perfect = abs(act.x - top_block.x) <= self.alignment_tolerance

        if is_perfect:
            self.score += 1
            self.points += 6
            self.perfect_streak += 1

            if self.perfect_streak % 3 == 0 and act.width < self.base_width:
                new_width = min(self.base_width, act.width + 10.0)
                self.feedback_text = (
                    f"PERFECT! +5 (Streak {self.perfect_streak} - Width Restored!)"
                )
            else:
                new_width = act.width
                self.feedback_text = "PERFECT! +5"

            self.feedback_timer = 60

            # Center perfect block over the top block
            new_x = top_block.x + (top_block.width - new_width) / 2.0
            new_x = max(20.0, min(self.width - 20.0 - new_width, new_x))

            new_block = Block(
                new_x,
                act.y,
                new_width,
                self.block_height,
                act.color,
                speed=0,
            )
        else:
            self.score += 1
            self.points += 1
            self.perfect_streak = 0

            # Generate trimming debris before creating trimmed block
            # Left off-cut
            if act.x < top_block.x:
                offcut_w = top_block.x - act.x
                if offcut_w > 0:
                    self.debris.append(
                        Debris(
                            act.x,
                            act.y,
                            offcut_w,
                            self.block_height,
                            act.color,
                            vx=-2.0,
                        )
                    )

            # Right off-cut
            if act.x + act.width > top_block.x + top_block.width:
                offcut_w = (act.x + act.width) - (top_block.x + top_block.width)
                if offcut_w > 0:
                    self.debris.append(
                        Debris(
                            top_block.x + top_block.width,
                            act.y,
                            offcut_w,
                            self.block_height,
                            act.color,
                            vx=2.0,
                        )
                    )

            # Trimmed block placement
            new_block = Block(
                left,
                act.y,
                overlap,
                self.block_height,
                act.color,
                speed=0,
            )

        self.stack.append(new_block)

        # Camera scrolling check: shift stack and debris positions down
        if new_block.y < 180:
            shift_amount = self.block_height + 4
            for block in self.stack:
                block.y += shift_amount
            for deb in self.debris:
                deb.y += shift_amount

        self.spawn_active_block()

    def handle_event(self, event):
        if self.game_over:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_r):
                    self.reset()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.reset()
        else:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.drop_block()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.drop_block()

    def update(self):
        if not self.game_over and hasattr(self, "active_block"):
            self.active_block.update(self.width)

        if self.feedback_timer > 0:
            self.feedback_timer -= 1

        # Update falling debris and remove off-screen instances (runs during Game Over)
        for deb in self.debris:
            deb.update()
        self.debris = [deb for deb in self.debris if not deb.is_offscreen(self.height)]

    def render(self, screen):
        # Calculate current sky colors and render vertical gradient
        top_color, bot_color = self._get_sky_colors()
        for y in range(self.height):
            t = y / float(self.height - 1)
            r = int(round(top_color[0] + t * (bot_color[0] - top_color[0])))
            g = int(round(top_color[1] + t * (bot_color[1] - top_color[1])))
            b = int(round(top_color[2] + t * (bot_color[2] - top_color[2])))
            self.bg_surface.set_at((0, y), (r, g, b))

        scaled_bg = pygame.transform.scale(self.bg_surface, (self.width, self.height))
        screen.blit(scaled_bg, (0, 0))

        # Render Title
        title_surf = self.font_title.render("Skyscraper Stack", True, (245, 245, 245))
        title_rect = title_surf.get_rect(center=(self.width // 2, 16))
        screen.blit(title_surf, title_rect)

        # Render Score and Points HUD
        hud_surf = self.font_hud.render(
            f"Height: {self.score} | Points: {self.points}", True, (255, 220, 80)
        )
        hud_rect = hud_surf.get_rect(center=(self.width // 2, 54))
        screen.blit(hud_surf, hud_rect)

        # Render Non-blocking Feedback Banner
        if self.feedback_timer > 0 and self.feedback_text:
            fb_surf = self.font_hud.render(
                self.feedback_text, True, (80, 240, 120)
            )
            fb_rect = fb_surf.get_rect(center=(self.width // 2, 84))
            screen.blit(fb_surf, fb_rect)

        # Render Stack
        for block in self.stack:
            block.render(screen)

        # Render Debris
        for deb in self.debris:
            deb.render(screen)

        # Render Active Block during play
        if not self.game_over and hasattr(self, "active_block"):
            self.active_block.render(screen)

        # Render Game Over Overlay
        if self.game_over:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 195))
            screen.blit(overlay, (0, 0))

            gover_surf = self.font_big.render(
                "TOWER COLLAPSED!", True, (240, 75, 75)
            )
            gover_rect = gover_surf.get_rect(
                center=(self.width // 2, self.height // 2 - 60)
            )
            screen.blit(gover_surf, gover_rect)

            final_surf = self.font_hud.render(
                f"Final Height: {self.score} | Points: {self.points}",
                True,
                (255, 255, 255),
            )
            final_rect = final_surf.get_rect(
                center=(self.width // 2, self.height // 2 - 10)
            )
            screen.blit(final_surf, final_rect)

            restart_surf = self.font_hud.render(
                "Press [Space] or [R] to Play Again", True, (200, 200, 200)
            )
            restart_rect = restart_surf.get_rect(
                center=(self.width // 2, self.height // 2 + 30)
            )
            screen.blit(restart_surf, restart_rect)