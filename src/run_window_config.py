import moderngl
from asyncio import Event
from moderngl_window import (
    WindowConfig,
    setup_basic_logging,
    get_local_window_cls,
    activate_context,
    create_parser,
    parse_args,
    Timer,
    weakref,
    logger,
)


async def async_run_window_config(
    rate_limit_event: Event, config_cls: WindowConfig, timer=None, args=None
) -> None:
    """
    Run an WindowConfig entering a blocking main loop

    Args:
        config_cls: The WindowConfig class to render
    Keyword Args:
        timer: A custom timer instance
        args: Override sys.args
    """
    setup_basic_logging(config_cls.log_level)
    parser = create_parser()
    config_cls.add_arguments(parser)
    values = parse_args(args=args, parser=parser)
    config_cls.argv = values
    window_cls = get_local_window_cls(values.window)

    # Calculate window size
    size = values.size or config_cls.window_size
    size = int(size[0] * values.size_mult), int(size[1] * values.size_mult)

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
        aspect_ratio=config_cls.aspect_ratio,
        vsync=values.vsync if values.vsync is not None else config_cls.vsync,
        samples=values.samples if values.samples is not None else config_cls.samples,
        cursor=show_cursor if show_cursor is not None else True,
        backend=values.backend,
    )
    window.print_context_info()
    activate_context(window=window)
    timer = timer or Timer()
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

    timer.start()

    print("Running", config_cls.__name__)

    while not window.is_closing:
        current_time, delta = timer.next_frame()

        print("Loop")

        if config.clear_color is not None:
            window.clear(*config.clear_color)

        # Always bind the window framebuffer before calling render
        window.use()

        window.render(current_time, delta)
        if not window.is_closing:
            window.swap_buffers()

        # Wait for the rate limited output event
        await rate_limit_event.wait()
        rate_limit_event.clear()

    _, duration = timer.stop()
    window.destroy()
    if duration > 0:
        logger.info(
            "Duration: {0:.2f}s @ {1:.2f} FPS".format(
                duration, window.frames / duration
            )
        )
