
SPECTRUM_SENSING = "spectrum_sensing"
TYPE = "type"
FFT_SIZE = "fft_size"
ED = "ed"
WFD = "wfd"
USRP = "usrp"
IP = "ip"
FFT_LENGTH = "fft_length"
CP_LENGTH = "cp_length"
MODULATION = "modulation"
OCC_TONES = "occupied_tones"
MODULATOR = "modulator"
OFDM = "ofdm"
GMSK = "gmsk"
TX = "tx"
TRANSMISSION = "transmission"


VALIDS = {SPECTRUM_SENSING: {TYPE: {ED: None, WFD: None},
                             FFT_SIZE: (128, 256, 512, 1024, 2048)},

          TX: {TYPE: {GMSK: {MODULATOR: {}},
                                OFDM: {MODULATION: {}, FFT_LENGTH: {}, CP_LENGTH: {}, OCC_TONES: {}}
                                }
                         }
          }

DEFAULTS = {SPECTRUM_SENSING: {TYPE: ED},

            TX: {GMSK: {MODULATOR: "digital.gmsk_mod(samples_per_symbol=2, bt=0.35))"},
                 OFDM: {MODULATION: "qam64", FFT_LENGTH: 512, CP_LENGTH: 128, OCC_TONES: 200}
                 }
            }