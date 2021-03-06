import console
import colors
from compositecore import Leaf
import settings


class GraphicChar(Leaf):
    """
    Composites holding this has a graphical representation as a char.
    """

    def __init__(self, color_bg, color_fg, icon):
        super(GraphicChar, self).__init__()
        self.component_type = "graphic_char"
        self._color_bg = color_bg
        self._color_fg = color_fg
        self._icon = icon

    @property
    def color_bg(self):
        if self._color_bg:
            return self._color_bg
        elif self.next:
            return self.next.color_bg
        return None


    @color_bg.setter
    def color_bg(self, value):
        self._color_bg = value

    @property
    def color_fg(self):
        if self._color_fg:
            return self._color_fg
        elif self.next:
            return self.next.color_fg
        return None

    @color_fg.setter
    def color_fg(self, value):
        self._color_fg = value

    @property
    def icon(self):
        if self._icon:
            return self._icon
        elif self.next:
            return self.next.icon
        return None

    @icon.setter
    def icon(self, value):
        self._icon = value

    def copy(self):
        """
        Makes a copy of this component.
        """
        return GraphicChar(self.color_bg, self.color_fg, self.icon)


class CharPrinter(Leaf):
    def __init__(self):
        super(CharPrinter, self).__init__()
        self.component_type = "char_printer"
        self._temp_animation_frames = []

    def _tick_animation(self):
        frame = None
        if len(self._temp_animation_frames) > 0:
            frame = self._temp_animation_frames.pop(0)
        return frame

    def clear_animation(self):
        self._temp_animation_frames = []

    def draw(self, position, the_console=0):
        """
        Draws the char on the given position on the console.
        """
        animation_frame = self._tick_animation()
        if animation_frame:
            return draw_graphic_char_to_console(position, animation_frame, the_console)
        draw_graphic_char_to_console(position, self.parent.graphic_char, the_console)

    def draw_unseen(self, screen_position, the_console=0):
        """
        Draws the char as it looks like outside the field of view.
        """
        self._tick_animation()
        console.console.set_colors_and_symbol(screen_position,
                                              colors.UNSEEN_FG,
                                              colors.UNSEEN_BG,
                                              self.parent.graphic_char.icon,
                                              console=the_console)
    def draw_unvisited(self, screen_position, the_console=0):
        """
        Draws the char as it looks like outside the field of view.
        """
        self._tick_animation()
        console.console.set_colors_and_symbol(screen_position,
                                              colors.DARK_PURPLE,
                                              colors.UNSEEN_BG,
                                              self.parent.graphic_char.icon,
                                              console=the_console)

    def append_graphic_char_temporary_frames(self, graphic_char_frames, animation_delay=settings.ANIMATION_DELAY):
        """
        Appends frames to the graphic char animation frame queue.

        These chars will be drawn as an effect,
        the regular chars won't be drawn until the animation frame queue is empty.
        """
        frames = _expand_frames(graphic_char_frames, animation_delay)
        self._temp_animation_frames.extend(frames)

    def append_fg_color_blink_frames(self, frame_colors, animation_delay=settings.ANIMATION_DELAY):
        """
        Appends frames to  the graphic char animation frame queue. With only fg_color changed.

        These chars will be drawn as an effect,
        the regular chars won't be drawn until the animation frame queue is empty.
        """
        color_bg = self.parent.graphic_char.color_bg
        symbol = self.parent.graphic_char.icon
        frames = [GraphicChar(color_bg, color, symbol) for color in frame_colors]
        self.append_graphic_char_temporary_frames(frames, animation_delay)

    def append_default_graphic_frame(self, frames=settings.ANIMATION_DELAY):
        self.append_graphic_char_temporary_frames([self.parent.graphic_char], frames)

    def copy(self):
        """
        Makes a copy of this component.
        """
        copy = CharPrinter()
        copy._temp_animation_frames = self._temp_animation_frames
        return copy


def draw_graphic_char_to_console(position, graphic_char, the_console=0):
    """
    Draws the char on the given position on the console.

    Bypasses all effects.
    """
    if not graphic_char.color_bg is None:
        console.console.set_color_bg(position, graphic_char.color_bg, console=the_console)
    if not graphic_char.color_fg is None:
        console.console.set_color_fg(position, graphic_char.color_fg, console=the_console)
    if not graphic_char.icon is None:
        console.console.set_symbol(position, graphic_char.icon, console=the_console)


def _expand_frames(graphic_char_frames, animation_delay):
    frames = []
    for frame in graphic_char_frames:
        for _ in range(animation_delay):
            frames.append(frame)
    return frames


class GraphicCharTerrainCorners(GraphicChar):
    """
    Composites holding this has a graphical representation as a char.
    """

    def __init__(self, color_bg, color_fg, icon, sticky_terrain_classes):
        super(GraphicCharTerrainCorners, self).__init__(color_bg, color_fg,
                                                        icon)
        self._sticky_terrain_classes = sticky_terrain_classes
        self._wall_symbol_row = icon
        self.has_calculated = False

    @property
    def icon(self):
        if not self.has_calculated:
            self.calculate_wall_symbol()
        return self._icon

    def calculate_wall_symbol(self):
        neighbours_mask = 0
        for index, neighbour in enumerate(self._get_neighbour_terrains()):
            if (any([terrain is neighbour.__class__
                     for terrain in self._sticky_terrain_classes])):
                neighbours_mask |= 2 ** index
        self._icon = self._wall_symbol_row + neighbours_mask

    def _get_neighbour_terrains(self):
        tiles = (self.parent.dungeon_level.value.
                 get_tiles_surrounding_position(self.parent.position.value))
        return [tile.get_terrain() for tile in tiles]

    def copy(self):
        """
        Makes a copy of this component.
        """
        return GraphicChar(self.color_bg, self.color_fg, self.icon)
