import moderngl
import moderngl_window

from moderngl_window import Timer, weakref


def create_window(size=(800, 800), aspect_ratio=1.0):
    """
    Creates the window and returns the window object.
    The window object is a moderngl_window.Window instance and provides the
    ModernGL context and the GLFW window object.

    Keyword Arguments:
        size: (int, int) - the size of the window in pixels
        aspect_ratio: float - the aspect ratio of the window

    Notes:
        aspect_ratio has priority over size. The size will be adjusted to
        match the aspect ratio if needed. The dimensions of the window will
        always be less than or equal to the size provided.
    """

    config_cls = moderngl_window.WindowConfig

    moderngl_window.setup_basic_logging(config_cls.log_level)
    parser = moderngl_window.create_parser()
    config_cls.add_arguments(parser)
    values = moderngl_window.parse_args(args=None, parser=parser)
    config_cls.argv = values
    window_cls = moderngl_window.get_local_window_cls(values.window)

    # compute size based on aspect ratio
    if aspect_ratio > 1.0:
        size = (size[0], int(size[0] / aspect_ratio))
    else:
        size = (int(size[1] * aspect_ratio), size[1])

    # Resolve cursor
    show_cursor = values.cursor
    if show_cursor is None:
        show_cursor = config_cls.cursor

    window = window_cls(
        title=config_cls.title,
        size=size,
        fullscreen=config_cls.fullscreen or values.fullscreen,
        resizable=(
            values.resizable if values.resizable is not None else config_cls.resizable
        ),
        gl_version=config_cls.gl_version,
        aspect_ratio=aspect_ratio,
        vsync=values.vsync if values.vsync is not None else config_cls.vsync,
        samples=values.samples if values.samples is not None else config_cls.samples,
        cursor=show_cursor if show_cursor is not None else True,
        backend=values.backend,
    )
    window.print_context_info()
    moderngl_window.activate_context(window=window)
    timer = Timer()
    config = config_cls(ctx=window.ctx, wnd=window, timer=timer)
    # Avoid the event assigning in the property setter for now
    # We want the even assigning to happen in WindowConfig.__init__
    # so users are free to assign them in their own __init__.
    window._config = weakref.ref(config)

    # Swap buffers once before staring the main loop.
    # This can trigged additional resize events reporting
    # a more accurate buffer size
    window.swap_buffers()
    window.set_default_viewport()

    # # Print details about the window and context
    # # print("Window Library:", window.type)
    # print("Window Size:", window.size)
    # print("Window Buffer Size:", window.buffer_size)
    # print("Window Fullscreen:", window.fullscreen)
    # print("Window Vsync:", window.vsync)

    # # Context information
    # print("ModernGL Version:", moderngl.__version__)
    # print("Context Version:", window.ctx.version_code)
    # # print("GL Version:", window.ctx.gl_version)
    # # print("GLSL Version:", window.ctx.glsl_version)
    # print("Default Framebuffer:", window.ctx.screen)
    # # print("Is Core Profile:", window.ctx.core)

    # # Additional context properties
    # # print("Max Texture Size:", window.ctx.max_texture_size)
    # # print("Max Viewport Dimensions:", window.ctx.max_viewport_dims)

    # # Framebuffer information (if applicable)
    # if window.ctx.screen:
    #     print("Framebuffer Size:", window.ctx.screen.size)
    #     print("Framebuffer Samples:", window.ctx.screen.samples)

    return (window, timer)
