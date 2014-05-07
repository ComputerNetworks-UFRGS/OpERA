from radio_constants import *


# Constant with the valid parameters for each configuration.
VALIDS = {SPECTRUM_SENSING: {TYPE: {ED: None, WFD: None},
                             FFT_SIZE: (128, 256, 512, 1024, 2048)},

          TX: {TYPE: {GMSK: {SAMPLES_PER_SYMBOL: None,
                             BT: None},
                      #MODULATOR: {}},
                      OFDM: {MODULATION: None, FFT_LENGTH: None, CP_LENGTH: None, OCC_TONES: None}
          }
          },

          RX: {TYPE: {GMSK: {SAMPLES_PER_SYMBOL: None,
                             BT: None},
                      OFDM: {MODULATION: None, FFT_LENGTH: None, CP_LENGTH: None, OCC_TONES: None}
          }
          }
}

# Constant with the valid types for each configuration.
VALID_TYPES = {TX: {  #  gmsk:
                      SAMPLES_PER_SYMBOL: int, BT: float,
                      #  ofdm:
                      MODULATION: str, FFT_LENGTH: int, CP_LENGTH: int, OCC_TONES: int},
               RX: {  #  gmsk:
                      SAMPLES_PER_SYMBOL: int, BT: float,
                      #  ofdm:
                      MODULATION: str, FFT_LENGTH: int, CP_LENGTH: int, OCC_TONES: int}}


# Constant indicating the default values for each configuration.
DEFAULTS = {SPECTRUM_SENSING: {TYPE: ED, FFT_SIZE: 1024},

            TX: {GMSK: {SAMPLES_PER_SYMBOL: 2,
                        BT: 0.35,
                        MODULATOR: "digital.gmsk_mod(samples_per_symbol=2, bt=0.35)"},
                 OFDM: {MODULATION: "qam64", FFT_LENGTH: 512, CP_LENGTH: 128, OCC_TONES: 200}
            },

            RX: {GMSK: {SAMPLES_PER_SYMBOL: 2,
                        DEMODULATOR: "digital.gmsk_demod(samples_per_symbol=2)"},
                 OFDM: {MODULATION: "qam64", FFT_LENGTH: 512, CP_LENGTH: 128, OCC_TONES: 200}
            }
}
