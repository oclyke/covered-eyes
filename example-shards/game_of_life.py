import pysicgl
from hidden_shades import timebase
from hidden_shades.timewarp import TimeWarp
from hidden_shades.frequency import FreqCounter
from hidden_shades.variables.responder import VariableResponder
from hidden_shades.variables.types import FloatingVariable


def frames(layer):
    screen = layer.canvas.screen

    timewarp = TimeWarp(lambda: timebase.seconds())

    # the advance counter is used to control the number of animation steps performed during each frame
    # the speed of the animation will be controlled the timewarp
    advance_counter = FreqCounter(1.0)

    # declare variables
    def handle_variable_changes(variable):
        name = variable.name

        if name == "speed":
            timewarp.set_frequency(variable.value)

    responder = VariableResponder(handle_variable_changes)

    layer.variable_manager.declare_variable(
        FloatingVariable(
            "speed",
            1.0,
            default_range=(0, 5),
            allowed_range=(0, 50),
            responders=[responder],
        )
    )
    layer.variable_manager.initialize_variables()

    # make a list of cells
    cells = [False] * screen.pixels
    cells_workspace = [False] * screen.pixels

    def index(x, y):
        return y * screen.width + x

    def position(idx):
        return (idx % screen.width, idx // screen.width)

    def count_live_neighbors(cells, pos):
        count = 0
        _x, _y = pos
        for offset in [
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 1),  # not (0,0)
            (1, -1),
            (1, 0),
            (1, 1),
        ]:
            offset_x, offset_y = offset

            x = _x + offset_x
            y = _y + offset_y

            if x < 0 or x >= screen.width:
                continue
            if y < 0 or y >= screen.height:
                continue

            if cells[index(x, y)]:
                count += 1

        return count

    def advance():
        """
        computes the next state from the given state
        when complete "cells" contains the updated state

        cells: the given state of cells (each is either dead [False] or alive [True])
        cells_workspace: a scratch space in which the new state may be calculated without
            the old state being modified
        """
        for idx, cell in enumerate(cells):
            pos = position(idx)

            # copy the existing state into the workspace
            cells_workspace[idx] = cell

            # compute number of live neighbors this cell has from the previous state
            live_neighbors = count_live_neighbors(cells, pos)

            # check whether any changes are needed for the new state
            if cell:
                # cell is alive
                if live_neighbors in [2, 3]:
                    continue
                else:
                    cells_workspace[idx] = False
            else:
                # cell is dead
                if live_neighbors == 3:
                    cells_workspace[idx] = True

        # stupid hack here:
        # we want to preserve the "cells" state until after the new state is fully computed but...
        # trying to assign to "cells" (i.e. cells = list(cell for cell in cells_workspace)) results
        # in issues with undeclared variables etc
        for idx, cell in enumerate(cells):
            # copy the computed state into the state variable
            cells[idx] = cells_workspace[idx]

    # functions for some cool shapes:
    def make_pulsar_at(pos):
        cx, cy = pos

        # list offsets (first quadrant only)
        offsets = [
            (2, 1),
            (3, 1),
            (4, 1),
            (1, 2),
            (1, 3),
            (1, 4),
            (2, 6),
            (3, 6),
            (4, 6),
            (6, 2),
            (6, 3),
            (6, 4),
        ]

        for offset_x, offset_y in offsets:
            # draw the cell in each of the four quadrants
            cells[index(cx + offset_x, cy + offset_y)] = True
            cells[index(cx + offset_x, cy - offset_y)] = True
            cells[index(cx - offset_x, cy - offset_y)] = True
            cells[index(cx - offset_x, cy + offset_y)] = True

    # seed cells
    make_pulsar_at((screen.width // 2, screen.height // 2))

    # reset the advance counter
    advance_counter.reset(timebase.seconds())

    while True:
        yield 0

        # update the advance counter
        advance_counter.update(timewarp.local())

        for count in range(advance_counter.outstanding()):
            advance()

        # clear interface
        pysicgl.functional.interface_fill(layer.canvas, 0x000000)  # clear screen

        # draw live cells in white
        for idx, cell in enumerate(cells):
            if cell:
                pysicgl.functional.interface_pixel(
                    layer.canvas, layer.palette[0], position(idx)
                )
