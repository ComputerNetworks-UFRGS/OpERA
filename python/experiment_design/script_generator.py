#!/usr/bin/env python
__author__ = 'jtsreinaldo'

"""
Copyright 2013 OpERA

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
"""

import sys
import os
import yaml

from optparse import OptionParser

path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.insert(0, path)

SPECTRUM_SENSING = "spectrum_sensing"
TYPE = "type"
FFT_SIZE = "fft_size"


class RadioGeneratorSS(object):
    """
    Class for generation of OpeERA scripts.
    """


    def __init__(self):
        """
        """
        pass

    def radio_generator_ss(self, radio):
        """
        Receives a YAML file containing information about some radio configurations, which will be used to generate an
        executable file.
        @param yaml_file
        """

        ED = "ed"
        WFD = "wfd"
        OUT_FILE = "output_file"
        PYTHON_EXT = ".py"
        USRP = "usrp"
        IP = "ip"

        # Checks if the detector is an ED or a WFD and creates the correct instance. If it is not either of them,
        # raise an exception.

        if ED in radio[SPECTRUM_SENSING][TYPE]:
            ss_type = ED

        elif WFD in radio[SPECTRUM_SENSING][TYPE]:
            ss_type = WFD

        else:
            raise Exception("The type of the detector should be ed or wfd!")

        ip = radio[USRP][IP]

        # Checks if the user passed the usrp ip address.
        if ip is None:
            ss_source = "UHDSource()"

        else:
            ss_source = "UHDSource(\"addr={ip}\")"
            ss_source = ss_source.format(ip=ip)

        the_fft_size = radio[SPECTRUM_SENSING][FFT_SIZE]

        ss_detector = radio[SPECTRUM_SENSING][TYPE][ss_type]
        ss_detector = ss_detector.format(fft_size=the_fft_size)

        return ss_type, ss_detector, ss_source


    def radio_generator_tx(self, radio):
        """
        Receives a YAML file containing information about some radio configurations, which will be used to generate an
        executable file.
        @param yaml_file
        """

        from packet import PacketGMSKTx, PacketOFDMTx

        path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
        sys.path.insert(0, path)

        #TODO:: eh pra fazer saporra tudp junto . ver exemplo em radio.py

        TX = "tx"
        FFT_LENGTH = "fft_length"
        CP_LENGTH = "cp_length"
        MODULATION = "modulation"
        OCC_TONES = "occupied_tones"
        MODULATOR = "modulator"
        OFDM = "ofdm"
        GMSK = "gmsk"
        USRP = "usrp"
        IP = "ip"


        # Checks if the transmitter is OFDM or GMSK  and creates the correct instance. If it is not either of them,
        # raise an exception.

        if OFDM in radio[TX][TYPE]:
            tx_type = OFDM

        elif GMSK in radio[TX][TYPE]:
            tx_type = GMSK

        else:
            raise Exception("The type of the transmitter should be gmsk or ofdm!")

        tx_arch = radio[TX][TYPE][tx_type]

        if tx_type == OFDM:
            # The user may not given all the parameters (all of them have default values), so we have to be
            # precautious and use the try/except statement.

            ofdm_inst = PacketOFDMTx()

            try:
                the_fft_length = radio[TX][FFT_LENGTH]

            except:
                the_fft_length = ofdm_inst.get_fft_length()

            try:
                the_cp_length = radio[TX][CP_LENGTH]

            except:
                the_cp_length = ofdm_inst.get_cp_length()

            try:
                occ_tones = radio[TX][OCC_TONES]

            except:
                occ_tones = ofdm_inst.get_occ_tones()

            try:
                the_modulation = radio[TX][MODULATION]

            except:
                the_modulation = ofdm_inst.get_modulation()

            # The modulation needs to be a string, so we have to format it.
            str_modulation = "\"{modulation}\""
            str_modulation = str_modulation.format(modulation=the_modulation)

            the_modulation = str_modulation

            tx_arch = tx_arch.format(fft_length=the_fft_length,
                                     cp_length=the_cp_length,
                                     modulation=the_modulation,
                                     occupied_tones=occ_tones)

        elif tx_type == GMSK:

            modulator = radio[TX][MODULATOR]

            tx_arch = tx_arch.format(modulator=modulator)

        ip = radio[USRP][IP]

        # Checks if the user passed the usrp ip address.
        if ip is None:
            uhd_sink = "UHDSink()"

        else:
            uhd_sink = "UHDSink(\"addr={ip}\")"
            uhd_sink = uhd_sink.format(ip=ip)


        return tx_type, tx_arch, uhd_sink


    #TODO:: juntando o ss e o tx em um metodo
    def radio_generator(self, yaml_file):

        PYTHON_EXT = ".py"

        from ss_tx_template import SS_TX_TEMPLATE

        yaml_stream = open(yaml_file, 'r')
        data = yaml.load(yaml_stream)

        radio_names = []

        for radio_name in data:

            radio = data[radio_name]

            ss_type, ss_detector, ss_source = self.radio_generator_ss(radio)
            tx_type, tx_arch, tx_sink = self.radio_generator_tx(radio)

            script = SS_TX_TEMPLATE.format(ss_type=ss_type,
                                           ss_detector=ss_detector,
                                           ss_source=ss_source,
                                           tx_type=tx_type,
                                           tx_arch=tx_arch,
                                           tx_sink=tx_sink)


            output_filename = radio_name  # The output file name is the name given for the 'instance'.

            # If no input is given, the file will be named "out_file.py".
            if output_filename is None:
                output_filename = "out_file"

            # Gets the 3 last characters of the output filename.
            file_ext = output_filename[(len(output_filename)-3):len(output_filename)]

            # Verifies if it DOES NOT have .py extension
            if file_ext != PYTHON_EXT:

                # If it doesn't, adds the python extension to the output filename.
                output_filename += PYTHON_EXT

            out_file = open(output_filename, "w+")
            out_file.write(script)
            out_file.close()

            radio_names.append(output_filename)

        print "\nYour spectrum sensing files have been generated with the following names:"
        for r_name in radio_names:
            print "\n\t\t%s" %(r_name)

        print "\n"


def main():
    """ Main function. """

    parser = OptionParser()
    parser.add_option("-f", "--file", type="string", default="config_file.yaml",
                      help="The YAML file name.", dest="yaml_file")
    (options, args) = parser.parse_args()

    yaml_file = options.yaml_file

    rg = RadioGeneratorSS()

    rg.radio_generator(yaml_file)


if __name__ == "__main__":
    main()
