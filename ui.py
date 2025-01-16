import pygame

import image
from settings import *

_last_click_time = 0
_button_cooldown = 200  # milliseconds
_last_toggle_time = 0  # Add at the top with other globals
_toggle_cooldown = 200  # milliseconds

def draw_text(
    surface,
    text,
    pos,
    color,
    font=FONTS["medium"],
    pos_mode="top_left",
    shadow=False,
    shadow_color=(0, 0, 0),
    shadow_offset=2,
):
    label = font.render(text, 1, color)
    label_rect = label.get_rect()
    if pos_mode == "top_left":
        label_rect.x, label_rect.y = pos
    elif pos_mode == "center":
        label_rect.center = pos

    if shadow:  # make the shadow
        label_shadow = font.render(text, 1, shadow_color)
        surface.blit(
            label_shadow, (label_rect.x - shadow_offset, label_rect.y + shadow_offset)
        )

    surface.blit(label, label_rect)  # draw the text


def button(surface, pos_y, text=None, click_sound=None, pos_x=None, disabled=False):
    global _last_click_time
    current_time = pygame.time.get_ticks()
    
    rect = pygame.Rect(
        ((pos_x if pos_x else SCREEN_WIDTH) // 2 - BUTTONS_SIZES[0] // 2, pos_y),
        BUTTONS_SIZES,
    )

    on_button = False
    if rect.collidepoint(pygame.mouse.get_pos()) and not disabled:
        color = COLORS["buttons"]["second"]
        on_button = True
    else:
        color = (128, 128, 128) if disabled else COLORS["buttons"]["default"]

    pygame.draw.rect(
        surface, COLORS["buttons"]["shadow"] if not disabled else (100, 100, 100), 
        (rect.x - 6, rect.y - 6, rect.w, rect.h)
    )  # draw the shadow rectangle
    pygame.draw.rect(surface, color, rect)  # draw the rectangle

    # draw the text
    if text is not None:
        text_color = (180, 180, 180) if disabled else COLORS["buttons"]["text"]
        draw_text(
            surface,
            text,
            rect.center,
            text_color,
            font=FONTS["small"],
            pos_mode="center",
            shadow=True,
            shadow_color=COLORS["buttons"]["shadow"],
        )

    # Check for click with proper timing and button release
    if (on_button and 
        pygame.mouse.get_pressed()[0] and 
        not disabled and 
        current_time - _last_click_time > _button_cooldown):
        
        # Update last click time
        _last_click_time = current_time
        
        if click_sound is not None:
            click_sound.play()
        return True
    
    return False


def back_button(surface, pos_x, pos_y):
    arrow_left = image.load("assets/arrow-left.png")
    rect = pygame.Rect((pos_x, pos_y), (50, 50))

    on_button = False
    if rect.collidepoint(pygame.mouse.get_pos()):
        color = COLORS["buttons"]["second"]
        on_button = True
    else:
        color = COLORS["buttons"]["default"]

    pygame.draw.circle(surface, color, (rect.centerx, rect.centery), 25)
    surface.blit(arrow_left, rect.topleft)

    if on_button and pygame.mouse.get_pressed()[0]:
        return True


def draw_title_text(surface, text: str, *, x: int, y: int = None):
    return draw_text(
        surface,
        text,
        (x, y if y else 120),
        COLORS["title"],
        font=FONTS["big"],
        shadow=True,
        shadow_color=(255, 255, 255),
        pos_mode="center",
    )


def draw_small_texts(surface, texts: list[str], *, x: int, starting_y: int = None):
    y = starting_y if starting_y else 200
    for index, text in enumerate(texts):
        draw_text(
            surface,
            text,
            (x, y + index * 40),
            COLORS["title"],
            font=FONTS["small"],
            shadow=True,
            shadow_color=(255, 255, 255),
            pos_mode="center",
        )


def toggle_button(surface, x, y, width, height, is_active, text=None):
    global _last_toggle_time
    current_time = pygame.time.get_ticks()
    
    background_rect = pygame.Rect(x, y, width, height)
    toggle_radius = height - 4
    toggle_pos = x + width - toggle_radius - 2 if is_active else x + 2
    
    pygame.draw.rect(surface, COLORS["toggle"]["background"], background_rect, border_radius=height//2)
    
    toggle_color = COLORS["toggle"]["active"] if is_active else COLORS["toggle"]["inactive"]
    pygame.draw.circle(surface, toggle_color, (toggle_pos + toggle_radius//2, y + height//2), toggle_radius//2)
    
    # Draw label text
    if text:
        text_x, _ = FONTS['small'].size(text)
        draw_text(
            surface,
            text,
            (x - text_x, y),
            COLORS["title"],
            font=FONTS["small"],
        )
    
    # Check for click with proper timing
    mouse_pos = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()[0]
    
    if (background_rect.collidepoint(mouse_pos) and 
        mouse_click and 
        current_time - _last_toggle_time > _toggle_cooldown):
        _last_toggle_time = current_time
        return True
    return False
