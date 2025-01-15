import pygame

import image
from settings import *


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


def button(surface, pos_y, text=None, click_sound=None, pos_x=None):
    rect = pygame.Rect(
        ((pos_x if pos_x else SCREEN_WIDTH) // 2 - BUTTONS_SIZES[0] // 2, pos_y),
        BUTTONS_SIZES,
    )

    on_button = False
    if rect.collidepoint(pygame.mouse.get_pos()):
        color = COLORS["buttons"]["second"]
        on_button = True
    else:
        color = COLORS["buttons"]["default"]

    pygame.draw.rect(
        surface, COLORS["buttons"]["shadow"], (rect.x - 6, rect.y - 6, rect.w, rect.h)
    )  # draw the shadow rectangle
    pygame.draw.rect(surface, color, rect)  # draw the rectangle
    # draw the text
    if text is not None:
        draw_text(
            surface,
            text,
            rect.center,
            COLORS["buttons"]["text"],
            font=FONTS["small"],
            pos_mode="center",
            shadow=True,
            shadow_color=COLORS["buttons"]["shadow"],
        )

    if on_button and pygame.mouse.get_pressed()[0]:  # if the user press on the button
        if click_sound is not None:  # play the sound if needed
            click_sound.play()
        return True


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
            (x, y + index * 35),
            COLORS["title"],
            font=FONTS["small"],
            shadow=True,
            shadow_color=(255, 255, 255),
            pos_mode="center",
        )
