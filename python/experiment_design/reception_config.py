__author__ = 'jtsreinaldo'

from radio_constants import *
from validation_constants import *


class RXConfigRadioGenerator(object):
    """
    A class for the reception configuration of a radio.
    """
    def __init__(self):
        """
        CTOR
        """
        pass

    @staticmethod
    def rx_generator(radio):
        """
        Receives a variable formatted in YAML file style, containing information about some information about radio
        configurations, which will be used to generate an source file.
        @param radio
        """

        # Checks if the receiver is OFDM or GMSK  and creates the correct instance. If it is not either of them,
        # raise an exception.

        if OFDM in radio[RX][TYPE]:
            rx_type = OFDM

        elif GMSK in radio[RX][TYPE]:
            rx_type = GMSK

        else:
            raise Exception("The type of the receiver should be gmsk or ofdm!")

        if rx_type == OFDM:
            # The user may not given all the parameters (all of them have default values), so we have to be
            # precautious and use the try/except statement.

            try:
                the_fft_length = radio[RX][FFT_LENGTH]

            except:
                # from DEFAULTS dict:
                the_fft_length = DEFAULTS[RX][OFDM][FFT_LENGTH]

            try:
                the_cp_length = radio[RX][CP_LENGTH]

            except:
                # from DEFAULTS dict:
                the_cp_length = DEFAULTS[RX][OFDM][FFT_LENGTH]

            try:
                occ_tones = radio[RX][OCC_TONES]

            except:
                # from DEFAULTS dict:
                occ_tones = DEFAULTS[RX][OFDM][OCC_TONES]

            try:
                the_modulation = radio[RX][MODULATION]

            except:
                #from DEFAULTS dict:
                the_modulation = DEFAULTS[RX][OFDM][MODULATION]

            rx_arch = "PacketOFDMRx(modulation={modulation}, cp_length={cp_length}, fft_length={fft_length}, " \
                      "occupied_tones={occupied_tones})"

            # The modulation needs to be a string, so we have to format it.
            str_modulation = "\"{modulation}\""
            str_modulation = str_modulation.format(modulation=the_modulation)

            the_modulation = str_modulation

            rx_arch = rx_arch.format(fft_length=the_fft_length,
                                     cp_length=the_cp_length,
                                     modulation=the_modulation,
                                     occupied_tones=occ_tones)

        elif rx_type == GMSK:


            try:
                samples_per_symbol = radio[RX][SAMPLES_PER_SYMBOL]

            except:
                samples_per_symbol = DEFAULTS[RX][GMSK][SAMPLES_PER_SYMBOL]

            try:
                demodulator = "digital.gmsk_demod(samples_per_symbol={samples_per_symbol})"

                demodulator = demodulator.format(samples_per_symbol=samples_per_symbol)

            except:
                demodulator = DEFAULTS[RX][GMSK][MODULATOR]

            rx_arch = "PacketGMSKRx(demodulator={demodulator})"
            rx_arch = rx_arch.format(demodulator=demodulator)

        ip = radio[USRP][IP]

        # Checks if the user passed the usrp ip address.
        if ip is None:
            uhd_sink = "UHDSink()"

        else:
            uhd_sink = "UHDSink(\"addr={ip}\")"
            uhd_sink = uhd_sink.format(ip=ip)

        return rx_type, rx_arch, uhd_sink

