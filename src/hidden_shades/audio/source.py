from audio.fft import FftPlan, reshape, FloatBuffer
from ..variables.manager import VariableManager
from ..variables.types import FloatingVariable, IntegerVariable
from ..variables.responder import VariableResponder


class AudioSourceFFT:
    def __init__(self, sample_frequency, input_buffer):
        self._input_buffer = input_buffer
        sample_length = len(self._input_buffer)

        # create an outp
        # ut buffer
        self._output_buffer = FloatBuffer(sample_length // 2)
        self._plan = FftPlan(
            (self._input_buffer, self._output_buffer), sample_frequency
        )

    def compute(self):
        self._plan.window()
        self._plan.execute()

    @property
    def plan(self):
        return self._plan

    @property
    def output(self):
        return self._output_buffer


class AudioSource:
    def __init__(self, name, configuration):
        self._name = name
        sample_frequency, sample_length = configuration
        self._sample_frequency = sample_frequency
        self._sample_length = sample_length

        # create an FloatBuffer that will hold the samples
        # (this is a faster object to use to store floating point values)
        self._buffer = FloatBuffer(sample_length)

        # create an AudioSourceFFT for the source
        self._fft = AudioSourceFFT(sample_frequency, self._buffer)

    async def run(self):
        """
        This is a stub of the coroutine which an AudioSource implements
        to handle audio data.

        Responsibilities of this routine are as follows:
        - fill the buffer with audio samples

        This coroutine may manipulate the data as needed.
        """

    @property
    def name(self):
        return self._name

    @property
    def fft(self):
        return self._fft


class ManagedAudioSource(AudioSource):
    def __init__(self, path, name, configuration):
        super().__init__(name, configuration)

        # create an output meant to hold nonlinear-corrected fft results
        # this buffer will have equal length to the output buffer despite that the number of bins required may be substantially more or substantially fewer depending on the chosen fft reshape factor.
        self._reshaped_fft_bins_available = len(self._fft._output_buffer)
        self._reshaped_fft_output_buffer = FloatBuffer(
            self._reshaped_fft_bins_available
        )
        self._reshaped_fft_output = self._reshaped_fft_output_buffer.reference()

        self._floor = None
        self._factor = None

        # create root path
        self._root_path = f"{path}/{self._name}"

        # variables which may be dynamically registered for external control
        self._variable_manager = VariableManager(f"{self._root_path}/vars")

        # declare private variables
        self._private_variable_responder = VariableResponder(
            lambda variable: self._handle_private_variable_change(variable)
        )
        self._private_variable_manager = VariableManager(
            f"{self._root_path}/private_vars"
        )
        self._private_variable_manager.declare_variable(
            FloatingVariable(
                "volume",
                0.5,
                default_range=(0.0, 1.0),
                responders=[self._private_variable_responder],
            )
        )
        self._private_variable_manager.declare_variable(
            FloatingVariable(
                "fft_reshape_factor",
                1.5,
                default_range=(1.0, 2.0),
                allowed_range=(0.5, 3.0),
                responders=[self._private_variable_responder],
            )
        )
        self._private_variable_manager.declare_variable(
            FloatingVariable(
                "fft_reshape_floor",
                0.1,
                default_range=(0.0, 1.0),
                responders=[self._private_variable_responder],
            )
        )
        self._private_variable_manager.declare_variable(
            IntegerVariable(
                "fft_min_bin",
                0,
                default_range=(0, self._reshaped_fft_bins_available),
                responders=[self._private_variable_responder],
            )
        )
        self._private_variable_manager.declare_variable(
            IntegerVariable(
                "fft_max_bin",
                self._reshaped_fft_bins_available,
                default_range=(0.0, self._reshaped_fft_bins_available),
                responders=[self._private_variable_responder],
            )
        )
        self._private_variable_manager.initialize_variables()

    def _handle_private_variable_change(self, variable):
        if variable.name in ("fft_reshape_factor", "fft_min_bin", "fft_max_bin"):
            """
            handle changes in variables which affect the fft output buffer reference
            """

            # get variable values
            reshape_factor = self.private_variable_manager.variables[
                "fft_reshape_factor"
            ].value
            min_bin = self.private_variable_manager.variables["fft_min_bin"].value
            max_bin = self.private_variable_manager.variables["fft_max_bin"].value

            # determine the number of valid bins from the reshaped output
            # (this value could be lower or higher than the number of bins allocated for the output buffer)
            bins_available = reshape(
                (reshape_factor, 0), self._fft._output_buffer, None
            )
            bins_available = self._reshaped_fft_bins_available
            if bins_available > self._reshaped_fft_bins_available:
                bins_available = self._reshaped_fft_bins_available

            # set up the window limits, and clamp them to the
            window_min = min_bin
            window_max = max_bin
            if window_min > (bins_available - 1):
                window_min = bins_available - 1
            if window_max > bins_available:
                window_max = bins_available

            # create a new reference to the output bins that selects the desired window
            self._reshaped_fft_output = self._reshaped_fft_output_buffer.reference(
                window=(window_min, window_max)
            )

    def apply_volume(self):
        # scale the audio data by the volume
        volume = self.private_variable_manager.variables["volume"].value
        self._buffer.scale(volume)

    def fft_postprocess(self):
        reshape_factor = self.private_variable_manager.variables[
            "fft_reshape_factor"
        ].value
        reshape_floor = self.private_variable_manager.variables[
            "fft_reshape_floor"
        ].value
        reshape_config = (reshape_factor, reshape_floor)
        reshape(
            reshape_config, self._fft._output_buffer, self._reshaped_fft_output_buffer
        )

    @property
    def variable_manager(self):
        return self._variable_manager

    @property
    def private_variable_manager(self):
        return self._private_variable_manager

    @property
    def reshaped_fft_output(self):
        return self._reshaped_fft_output
