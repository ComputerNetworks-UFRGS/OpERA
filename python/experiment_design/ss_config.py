__author__ = 'jtsreinaldo'

from radio_constants import *
from validation_constants import *


class SSConfigRadioGenerator(object):
    """
    A class for the reception configuration of a radio.
    """
    def __init__(self):
        """
        CTOR
        """
        pass

    @staticmethod
    def ss_generator(radio):
        """
        Receives a variable formatted in YAML file style, containing information about some information about radio
        configurations, which will be used to generate an source file.
        @param radio
        """

        # Checks if the detector is an ED or a WFD and creates the correct instance. If it is not either of them,
        # raise an exception.

        # If the ss type is given in the yaml file, use it. But first, check if it is a valid value.
        try:
            ss_type = radio[SPECTRUM_SENSING][TYPE]

            if ss_type is not ED and ss_type is not WFD:
                raise Exception("Invalid spectrum sensing type. The type must be ed or wfd.")

        except:
            ss_type = DEFAULTS[SPECTRUM_SENSING][TYPE]

        try:
            the_fft_size = radio[SPECTRUM_SENSING][FFT_SIZE]

        except:
            the_fft_size = DEFAULTS[SPECTRUM_SENSING][FFT_SIZE]

        if ss_type == ED:
            ss_detector = "EnergySSArch(fft_size={fft_size}, mavg_size=5, algorithm=EnergyDecision(th=0))"


        # ss_type is WFD
        else:
            ss_detector = "WaveformSSArch2(fft_size={fft_size})"

        ss_detector = ss_detector.format(fft_size=the_fft_size)

        ip = radio[USRP][IP]

        # Checks if the user passed the usrp ip address.
        if ip is None:
            ss_source = "UHDSource()"

        else:
            ss_source = "UHDSource(\"addr={ip}\")"
            ss_source = ss_source.format(ip=ip)

        return ss_type, ss_detector, ss_source
