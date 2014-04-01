SS_TX_TEMPLATE = "import sys\n"\
"import os\n"\
"path = os.path.abspath(os.path.join(os.path.dirname(__file__), \"../\"))\n"\
"sys.path.insert(0, path)\n\n"\
"" \
"from gnuradio import blocks, digital\n\n" \
"" \
"# OpERA imports.\n\n"\
"from OpERAFlow import OpERAFlow\n"\
"from device import RadioDevice, UHDSink\n"\
"from gr_blocks.utils import UHDSourceDummy\n" \
"from packet import PacketGMSKTx, PacketOFDMTx\n\n" \
"from device import RadioDevice, UHDSource\n"\
"from sensing import EnergyDecision, WaveformDecision, BayesLearningThreshold\n"\
"from sensing import EnergySSArch, EnergyCalculator\n"\
"from sensing import WaveformSSArch2, FeedbackSSArch2\n"\
"from channels import AWGNChannel\n\n"\
"" \
"" \
"radio = RadioDevice(name=\"radio\")\n\n" \
"radio.set_center_freq(100e6)\n\n"\
"" \
"# TX\n" \
"tx_sink = {tx_sink}\n\n" \
"" \
"tx_source = UHDSourceDummy()\n\n" \
"" \
"# The arch is a {tx_type}\n" \
"tx_arch = {tx_arch}\n\n" \
"" \
"" \
"radio.add_arch(source=tx_source, arch=tx_arch, sink=tx_sink, uhd_device=tx_sink,\n" \
"               name='tx')\n\n" \
"" \
"# SS\n" \
"#  ss_type = {ss_type}\n\n"\
"" \
"ss_source = {ss_source}\n"\
"ss_source.samp_rate = 195512\n\n"\
"" \
"" \
"ss_detector = {ss_detector}\n"\
"radio.add_arch(source=ss_source, arch=ss_detector, sink=blocks.probe_signal_f(), uhd_device=ss_source,\n" \
"               name='ss')\n"\





