class Settings:

    def __init__(self):
        self.screen_width, self.screen_height = 640, 400
        self.bg_color = (225, 225, 225)

        self.h2size = self.screen_height >> 1

        self.map_width, self.map_height = 24, 24

        # Feature flags
        self.texture_walls_enabled = True
        self.texture_floors_enabled = True
        self.display_hud_map = False


class COLOR:
    black = (0, 0, 0)
    white = (0, 255, 255)
    gray = (180, 180, 180)
    green = (0, 200, 0)
    red = (200, 0, 0)
    blue = (0, 0, 200)
    purple = (200, 200, 0)
    ceil = (0x25, 0x56, 0x7B)
    floor = (0xBF, 0x82, 0x30)


class Player:
    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.dir_x = dx
        self.dir_y = dy
        self.plane_x = 0
        self.plane_y = 1
        self.angle = 0
