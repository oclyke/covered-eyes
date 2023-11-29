class Display:
    def __init__(self, screen):
        self._screen = screen

        self._numx = screen.width
        self._numy = screen.height
        self._dimx = screen.width - 1
        self._dimy = screen.height - 1

        self._extent = (
            self._numx,
            self._numy,
        )

        self._dimensions = (
            self._dimx,
            self._dimy,
        )  # the dimensions of the display assuming unit spacing between pixels
        self._unity = max(self._dimensions)

        self._shape = (
            self._dimx / self._unity,
            self._dimy / self._unity,
        )  # shape of the display normalized so that the maximum element is 1.0

    @property
    def extent(self):
        return self._extent

    @property
    def dimensions(self):
        return self._dimensions

    @property
    def shape(self):
        return self._shape

    @property
    def center(self):
        (extx, exty) = self.shape
        return (extx / 2, exty / 2)

    def pixel_info(self):
        """
        returns a generator object which will yield information for each pixel in the display
        """
        width, height = (self._screen.width, self._screen.height)
        dimu, dimv = self._dimensions

        if dimu == 0:
            dimu = 1
        if dimv == 0:
            dimv = 1

        for idx in range(self._screen.pixels):
            u = idx % width
            v = idx // width

            coords = (u, v)
            pos = (u / dimu, v / dimv)

            yield (idx, coords, pos)
