#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# Author: sal
# GNU Radio version: v3.8.3.1-14-g34ea1a45

from distutils.version import StrictVersion

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print("Warning: failed to XInitThreads()")

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio.filter import firdes
import sip
from gnuradio import analog
from gnuradio import blocks
from gnuradio import gr
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import predistort

from gnuradio import qtgui

class niwc_pac_paper(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Not titled yet")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Not titled yet")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "niwc_pac_paper")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except:
            pass

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 32000
        self.num_of_inputs = num_of_inputs = 3
        self.freq2 = freq2 = 5e3
        self.freq1 = freq1 = 10e3

        ##################################################
        # Blocks
        ##################################################
        self.qtgui_waterfall_sink_x_0 = qtgui.waterfall_sink_c(
            1024, #size
            firdes.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            "", #name
            1 #number of inputs
        )
        self.qtgui_waterfall_sink_x_0.set_update_time(0.10)
        self.qtgui_waterfall_sink_x_0.enable_grid(False)
        self.qtgui_waterfall_sink_x_0.enable_axis_labels(True)



        labels = ['', '', '', '', '',
                  '', '', '', '', '']
        colors = [0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_waterfall_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_waterfall_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_waterfall_sink_x_0.set_color_map(i, colors[i])
            self.qtgui_waterfall_sink_x_0.set_line_alpha(i, alphas[i])

        self.qtgui_waterfall_sink_x_0.set_intensity_range(-140, 10)

        self._qtgui_waterfall_sink_x_0_win = sip.wrapinstance(self.qtgui_waterfall_sink_x_0.pyqwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_waterfall_sink_x_0_win)
        self.qtgui_edit_box_msg_0 = qtgui.edit_box_msg(qtgui.INT, '', 'Labels do not matter', True, False, 'stream')
        self._qtgui_edit_box_msg_0_win = sip.wrapinstance(self.qtgui_edit_box_msg_0.pyqwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_edit_box_msg_0_win)
        self.predistort_async_signal_mux_0 = predistort.async_signal_mux(gr.sizeof_gr_complex, num_of_inputs)
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)
        self.analog_sig_source_x_0_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, freq2, 0.5, 0, 0)
        self.analog_sig_source_x_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, freq1, 1, 0, 0)
        self.analog_noise_source_x_0 = analog.noise_source_c(analog.GR_GAUSSIAN, 1, 0)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.qtgui_edit_box_msg_0, 'msg'), (self.predistort_async_signal_mux_0, 'ctrl_in'))
        self.connect((self.analog_noise_source_x_0, 0), (self.predistort_async_signal_mux_0, 2))
        self.connect((self.analog_sig_source_x_0, 0), (self.predistort_async_signal_mux_0, 0))
        self.connect((self.analog_sig_source_x_0_0, 0), (self.predistort_async_signal_mux_0, 1))
        self.connect((self.blocks_throttle_0, 0), (self.qtgui_waterfall_sink_x_0, 0))
        self.connect((self.predistort_async_signal_mux_0, 0), (self.blocks_throttle_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "niwc_pac_paper")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.analog_sig_source_x_0.set_sampling_freq(self.samp_rate)
        self.analog_sig_source_x_0_0.set_sampling_freq(self.samp_rate)
        self.blocks_throttle_0.set_sample_rate(self.samp_rate)
        self.qtgui_waterfall_sink_x_0.set_frequency_range(0, self.samp_rate)

    def get_num_of_inputs(self):
        return self.num_of_inputs

    def set_num_of_inputs(self, num_of_inputs):
        self.num_of_inputs = num_of_inputs

    def get_freq2(self):
        return self.freq2

    def set_freq2(self, freq2):
        self.freq2 = freq2
        self.analog_sig_source_x_0_0.set_frequency(self.freq2)

    def get_freq1(self):
        return self.freq1

    def set_freq1(self, freq1):
        self.freq1 = freq1
        self.analog_sig_source_x_0.set_frequency(self.freq1)





def main(top_block_cls=niwc_pac_paper, options=None):

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    def quitting():
        tb.stop()
        tb.wait()

    qapp.aboutToQuit.connect(quitting)
    qapp.exec_()

if __name__ == '__main__':
    main()
