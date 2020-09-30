# this module contains models required to load textures
import pygame


class SpriteSheet:

    def __init__(self, filename):
        """Load the sheet."""
        try:
            self.sheet = pygame.image.load(filename).convert()
        except pygame.error as e:
            print(f"Unable to load spritesheet image: {filename}")
            raise SystemExit(e)

    def image_at(self, rectangle, colorkey=None):
        """Load a specific image from a specific rectangle."""
        # Loads image from x, y, x+offset, y+offset.
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image

    def images_at(self, rects, colorkey=None):
        """Load a whole bunch of images and return them as a list."""
        return [self.image_at(rect, colorkey) for rect in rects]

    def load_strip(self, rect, image_count, colorkey=None):
        """Load a whole strip of images, and return them as a list."""
        tups = [(rect[0] + rect[2] * x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)


class WallTextures:
    """Represents a set of wall textures.
    Each texture is an object of the Wall class.
    """

    def __init__(self):
        """Initialize attributes to represent the overall set of pieces."""

        self.walls = []
        self._load_pieces()
        self.rows = 8
        self.cols = 8

    def _load_pieces(self):
        """Builds the overall set:
        - Loads images from the sprite sheet.
        - Creates a Wall object, and sets appropriate attributes
          for that texture.
        - Adds each texture to the list self.walls.
        """
        import os

        filepath = 'assets/texture.png'
        # dir = os.path.dirname('assets')
        # filepath = os.path.join(dir, 'wall_textures.png')
        # filepath = os.path.join(dir, 'texture.png')
        wall_ss = SpriteSheet(filepath)

        # Create a black king.
        start = [8, 8, 32, 32]
        for row in range(0, 9):
            for col in range(0, 8):
                wall_a_rect = start
                wall_a_image = wall_ss.image_at(wall_a_rect)

                wall_a = Wall()
                wall_a.image = wall_a_image
                wall_a.name = 'king'
                wall_a.color = 'black'
                self.walls.append(wall_a)
                start[0] = start[0] + 32 + 8
            start[0] = 8
            start[1] = start[1] + 32 + 8


class Wall:
    """Represents a wall texture."""

    def __init__(self):
        """Initialize attributes to represent a wall texture."""
        self.image = None
        self.name = ''
        self.color = ''
        # self.x, self.y = 0.0, 0.0

    def get_image(self):
        return self.image

    #
    # def blitme(self):
    #     """Draw the piece at its current location."""
    #     self.rect = self.image.get_rect()
    #     self.rect.topleft = self.x, self.y
    #     self.screen.blit(self.image, self.rect)
