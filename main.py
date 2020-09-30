import pygame as pg
import math
from settings import Settings, Player, COLOR
from map import MapGenerator
from asset_manage import WallTextures


class GameManager:
    def __init__(self):
        self.settings = Settings()
        self.player = Player(12, 12, -1, 0)
        self.color = COLOR()
        self.map_manager = MapGenerator(self.settings.map_width, self.settings.map_height)
        self.map_manager.generate_maps()
        self.map = self.map_manager.get_map(0)

        pg.init()
        pg.display.set_caption('Wolf 3d')
        self.screen = pg.display.set_mode((self.settings.screen_width, self.settings.screen_height))

        self.wt = WallTextures()
        self.wall_textures = {}
        self.floor_texture = None
        self.ceiling_texture = None
        self.assign_textures()

        self.clock = pg.time.Clock()

    def assign_textures(self):
        self.wall_textures['-'] = self.wt.walls[0].get_image()
        self.wall_textures['X'] = self.wt.walls[1].get_image()
        self.wall_textures['1'] = self.wt.walls[2].get_image()
        self.wall_textures['2'] = self.wt.walls[3].get_image()
        self.wall_textures['3'] = self.wt.walls[4].get_image()
        self.wall_textures['4'] = self.wt.walls[5].get_image()
        self.floor_texture = self.wt.walls[-8].get_image()
        self.ceiling_texture = self.wt.walls[-7].get_image()

    def get_tile_from_map(self, x, y):
        return self.map[y * self.settings.map_width + x]

    @staticmethod
    def darken_color(c, divisor):
        return tuple(ci / divisor for ci in c)

    def generate_hud_map(self):
        map_width = self.settings.map_width
        map_height = self.settings.map_height
        _map = pg.Surface((map_width * 10, map_height * 10))
        _map.set_alpha(128)
        _map.fill(COLOR.black)
        for y in range(0, map_width):
            for x in range(0, map_height):
                if self.get_tile_from_map(y, x) != ' ':
                    _map.fill(COLOR.white, ((x - 1) * 10, (y - 1) * 10, 10, 10))
        dot = pg.Surface((10, 10))
        pg.draw.circle(dot, COLOR.red, (5, 5), 2)
        _map.blit(dot, (int(self.player.x * 10), int(self.player.y * 10)))
        angle = math.atan2(self.player.dir_y, self.player.dir_x)
        _map = pg.transform.rotate(_map, math.degrees(angle))
        return _map

    def hud(self):
        _hud = [
            'X pos : %f' % self.player.x,
            'Y pos : %f' % self.player.y,
            'DX pos : %f' % self.player.dir_x,
            'DY pos : %f' % self.player.dir_y,
            'PX pos : %f' % self.player.plane_x,
            'PY pos : %f' % self.player.plane_y,
        ]
        font1 = pg.font.Font(pg.font.get_default_font(), 12)
        pos_y = 5
        for line in _hud:
            text = font1.render(line, True, COLOR.white)
            self.screen.blit(text, dest=(10, pos_y))
            pos_y += 15
        if self.settings.display_hud_map:
            _map = self.generate_hud_map()
            self.screen.blit(_map, dest=(10, 10))

    def texture_floor_and_ceiling(self):
        texture_w = self.floor_texture.get_width()
        texture_h = self.floor_texture.get_height()

        for y in range(self.settings.h2size + 1, self.settings.screen_height):
            ray_dir_x0 = self.player.dir_x - self.player.plane_x
            ray_dir_y0 = self.player.dir_y - self.player.plane_y
            ray_dir_x1 = self.player.dir_x + self.player.plane_x
            ray_dir_y1 = self.player.dir_y + self.player.plane_y

            p = y - self.settings.h2size
            pos_z = 0.5 * self.settings.screen_height
            row_distance = pos_z / p

            floor_step_x = row_distance * (ray_dir_x1 - ray_dir_x0) / self.settings.screen_width
            floor_step_y = row_distance * (ray_dir_y1 - ray_dir_y0) / self.settings.screen_width

            floor_x = self.player.x + (row_distance * ray_dir_x0)
            floor_y = self.player.y + (row_distance * ray_dir_y0)

            for x in range(0, self.settings.screen_width):
                cell_x = int(floor_x)
                cell_y = int(floor_y)

                t_x = int(texture_w * (floor_x - cell_x)) & (texture_w - 1)
                t_y = int(texture_h * (floor_y - cell_y)) & (texture_h - 1)

                floor_x += floor_step_x
                floor_y += floor_step_y

                c = self.floor_texture.get_at((t_x, t_y))
                self.screen.set_at((x, y), c)

                c = self.ceiling_texture.get_at((t_x, t_y))
                self.screen.set_at((x, self.settings.screen_height - y - 1), c)

    def ray_cast(self):
        # Iterate each vertical line. Cast a ray and see what we hit
        sw = self.settings.screen_width
        sh = self.settings.screen_height
        for x in range(0, sw - 1):
            # calculate ray position and direction
            camera_x = 2 * x / sw - 1
            ray_dir_x = self.player.dir_x + (self.player.plane_x * camera_x)
            ray_dir_y = self.player.dir_y + (self.player.plane_y * camera_x)
            # map_* is the tile which we currently reside in
            map_x = int(self.player.x)
            map_y = int(self.player.y)
            # Calculate the direction of our ray
            dist_delta_x = 0 if ray_dir_y == 0 else 1 if ray_dir_x == 0 else abs(1 / ray_dir_x)
            dist_delta_y = 0 if ray_dir_x == 0 else 1 if ray_dir_y == 0 else abs(1 / ray_dir_y)
            # Did we hit a wall?
            hit = 0
            # Which side of the wall did we hit (NE or SW)
            side = 0
            # Which tile did we hit
            tile = ''
            # Calculate step and initial side delta to get to the first edge of the map from our position
            if ray_dir_x < 0:
                step_x = -1
                side_distance_x = (self.player.x - map_x) * dist_delta_x
            else:
                step_x = 1
                side_distance_x = (map_x + 1.0 - self.player.x) * dist_delta_x
            if ray_dir_y < 0:
                step_y = -1
                side_distance_y = (self.player.y - map_y) * dist_delta_y
            else:
                step_y = 1
                side_distance_y = (map_y + 1.0 - self.player.y) * dist_delta_y
            # Cast the ray until we hit something
            while hit == 0:
                # Go to next tile
                if side_distance_x < side_distance_y:
                    side_distance_x += dist_delta_x
                    map_x += step_x
                    side = 0
                else:
                    side_distance_y += dist_delta_y
                    map_y += step_y
                    side = 1
                # Check if there is something on this tile
                tile = self.get_tile_from_map(map_x, map_y)
                if tile != ' ':
                    hit = 1
            if side == 0:
                perp_wall_distance = (map_x - self.player.x + (1 - step_x) / 2) / ray_dir_x
            else:
                perp_wall_distance = (map_y - self.player.y + (1 - step_y) / 2) / ray_dir_y
            # Calculate height of the wall, based on the distance
            if perp_wall_distance == 0:
                line_height = sh
            else:
                line_height = int(sh / perp_wall_distance)
            draw_start = int(0 - line_height / 2 + sh / 2)
            if draw_start < 0:
                draw_start = 0
            draw_end = int(line_height / 2 + sh / 2)
            if draw_end > sh:
                draw_end = sh - 1
            if self.settings.texture_walls_enabled:
                texture = self.wall_textures[tile]
                wall_x = self.player.y + perp_wall_distance * ray_dir_y if side == 0 else \
                    self.player.x + perp_wall_distance * ray_dir_x
                wall_x -= math.floor(wall_x)
                tex_x = int(wall_x * 32)
                if side == 0 and ray_dir_x > 0:
                    tex_x = 32 - tex_x - 1
                if side == 1 and ray_dir_y < 0:
                    tex_x = 32 - tex_x - 1
                step = 1.0 * 32 / line_height
                tex_pos = (draw_start - self.settings.h2size + line_height / 2) * step
                for y in range(draw_start, draw_end):
                    tex_y = int(tex_pos) & 63
                    tex_pos += step
                    c = texture.get_at((tex_x, tex_y))
                    # On NE side, darken the color of the texture. Looks nicer
                    if side == 1:
                        c = self.darken_color(c, 2)
                    self.screen.set_at((x, y), c)
            else:
                # Check which color we need to draw
                c = self.color.white
                if tile == 'X':
                    c = self.color.gray
                if tile == '-':
                    c = self.color.white
                if tile == '1':
                    c = self.color.blue
                if tile == '2':
                    c = self.color.green
                if tile == '3':
                    c = self.color.red
                if tile == '4':
                    c = self.color.purple
                # On the NE facing side, we draw a darker color. Looks nicer
                if side == 1:
                    c = self.darken_color(c, 2)
                # Draw the line (@TODO: texture)
                pg.draw.line(self.screen, c, (x, draw_start), (x, draw_end))

    def tick(self):
        self.screen.fill(COLOR.black)
        # Paint ceiling and floor
        if self.settings.texture_floors_enabled:
            self.texture_floor_and_ceiling()
        else:
            self.screen.fill(
                COLOR.ceil,
                (0, 0, self.settings.screen_width, self.settings.h2size)
            )
            self.screen.fill(
                COLOR.floor,
                (0, self.settings.h2size, self.settings.screen_width, self.settings.screen_height)
            )
        # Raycast walls
        self.ray_cast()
        # HUD info
        self.hud()

    def movement(self, key, speed, rot_speed):
        if key[pg.K_UP]:
            if self.get_tile_from_map(int(self.player.x + self.player.dir_x * speed), int(self.player.y)) == ' ':
                self.player.x += self.player.dir_x * speed
            if self.get_tile_from_map(int(self.player.x), int(self.player.y + self.player.dir_y * speed)) == ' ':
                self.player.y += self.player.dir_y * speed
        if key[pg.K_DOWN]:
            if self.get_tile_from_map(int(self.player.x - self.player.dir_x * speed), int(self.player.y)) == ' ':
                self.player.x -= self.player.dir_x * speed
            if self.get_tile_from_map(int(self.player.x), int(self.player.y - self.player.dir_y * speed)) == ' ':
                self.player.y -= self.player.dir_y * speed
        if key[pg.K_LEFT]:
            old_dir_x = self.player.dir_x
            old_dir_y = self.player.dir_y
            self.player.dir_x = old_dir_x * math.cos(rot_speed) - old_dir_y * math.sin(rot_speed)
            self.player.dir_y = old_dir_x * math.sin(rot_speed) + old_dir_y * math.cos(rot_speed)
            old_plane_x = self.player.plane_x
            old_plane_y = self.player.plane_y
            self.player.plane_x = old_plane_x * math.cos(rot_speed) - old_plane_y * math.sin(rot_speed)
            self.player.plane_y = old_plane_x * math.sin(rot_speed) + old_plane_y * math.cos(rot_speed)
        if key[pg.K_RIGHT]:
            old_dir_x = self.player.dir_x
            old_dir_y = self.player.dir_y
            self.player.dir_x = old_dir_x * math.cos(-rot_speed) - old_dir_y * math.sin(-rot_speed)
            self.player.dir_y = old_dir_x * math.sin(-rot_speed) + old_dir_y * math.cos(-rot_speed)
            old_plane_x = self.player.plane_x
            old_plane_y = self.player.plane_y
            self.player.plane_x = old_plane_x * math.cos(-rot_speed) - old_plane_y * math.sin(-rot_speed)
            self.player.plane_y = old_plane_x * math.sin(-rot_speed) + old_plane_y * math.cos(-rot_speed)

    def run(self):
        while True:
            self.tick()
            key = pg.key.get_pressed()
            self.movement(key=key, rot_speed=0.5, speed=0.5)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return
            pg.display.flip()


def main():
    game_manager = GameManager()
    game_manager.run()


if __name__ == "__main__":
    main()
