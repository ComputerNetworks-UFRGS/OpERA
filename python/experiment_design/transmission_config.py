__author__ = 'jtsreinaldo'

from radio_constants import *
from validation_constants import *


class TXConfigRadioGenerator(object):
    """
    A class for the reception configuration of a radio.
    """
    def __init__(self):
        """
        CTOR
        """
        pass


    @staticmethod
    def tx_generator(radio):
        """
        Receives a variable formatted in YAML file style, containing information about some information about radio
        configurations, which will be used to generate an source file.
        @param radio
        """

        # Checks if the transmitter is OFDM or GMSK  and creates the correct instance. If it is not either of them,
        # raise an exception.

        if OFDM in radio[TX][TYPE]:
            tx_type = OFDM

        elif GMSK in radio[TX][TYPE]:
            tx_type = GMSK

        else:
            raise Exception("The type of the transmitter should be gmsk or ofdm!")

        if tx_type == OFDM:
            # The user may not given all the parameters (all of them have default values), so we have to be
            # precautious and use the try/except statement.

            try:
                the_fft_length = radio[TX][FFT_LENGTH]

            except:
                # from DEFAULTS dict:
                the_fft_length = DEFAULTS[TX][OFDM][FFT_LENGTH]

            try:
                the_cp_length = radio[TX][CP_LENGTH]

            except:
                # from DEFAULTS dict:
                the_cp_length = DEFAULTS[TX][OFDM][FFT_LENGTH]

            try:
                occ_tones = radio[TX][OCC_TONES]

            except:
                # from DEFAULTS dict:
                occ_tones = DEFAULTS[TX][OFDM][OCC_TONES]

            try:
                the_modulation = radio[TX][MODULATION]

            except:
                #from DEFAULTS dict:
                the_modulation = DEFAULTS[TX][OFDM][MODULATION]

            tx_arch = "PacketOFDMTx(modulation={modulation}, cp_length={cp_length}, fft_length={fft_length}, " \
                      "occupied_tones={occupied_tones})"

            # The modulation needs to be a string, so we have to format it.
            str_modulation = "\"{modulation}\""
            str_modulation = str_modulation.format(modulation=the_modulation)

            the_modulation = str_modulation

            tx_arch = tx_arch.format(fft_length=the_fft_length,
                                     cp_length=the_cp_length,
                                     modulation=the_modulation,
                                     occupied_tones=occ_tones)

        elif tx_type == GMSK:

            try:
                samples_per_symbol = radio[TX][SAMPLES_PER_SYMBOL]

            except:
                samples_per_symbol = DEFAULTS[TX][GMSK][SAMPLES_PER_SYMBOL]

            try:
                bt = radio[TX][BT]

            except:
                bt = DEFAULTS[TX][GMSK][SAMPLES_PER_SYMBOL]

            try:
                modulator = "digital.gmsk_mod(samples_per_symbol={samples_per_symbol}, bt={bt})"

                modulator = modulator.format(samples_per_symbol=samples_per_symbol, bt=bt)

            except:
                modulator = DEFAULTS[TX][GMSK][MODULATOR]

            tx_arch = "PacketGMSKTx(modulator={modulator})"
            tx_arch = tx_arch.format(modulator=modulator)

        ip = radio[USRP][IP]

        # Checks if the user passed the usrp ip address.
        if ip is None:
            uhd_sink = "UHDSink()"

        else:
            uhd_sink = "UHDSink(\"addr={ip}\")"
            uhd_sink = uhd_sink.format(ip=ip)

        return tx_type, tx_arch, uhd_sink