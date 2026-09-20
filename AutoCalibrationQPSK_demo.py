#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: AutoCalibrationQPSK_demo
# Author: Brendan Hill, Salwan Damman
# Description: Demonstration of QPSK Self-Calibration of USRP using peak minimization
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
from gnuradio import blocks
import numpy
from gnuradio import digital
from gnuradio import gr
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import uhd
import time
from gnuradio.qtgui import Range, RangeWidget
import epy_block_0
import predistort

from gnuradio import qtgui

class AutoCalibrationQPSK_demo(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "AutoCalibrationQPSK_demo")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("AutoCalibrationQPSK_demo")
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

        self.settings = Qt.QSettings("GNU Radio", "AutoCalibrationQPSK_demo")

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
        self.start_calibration = start_calibration = 0
        self.sps = sps = 4
        self.samp_rate = samp_rate = 2e6
        self.QPSK_ideal = QPSK_ideal = digital.constellation_rect([-0.707-0.707j, -0.707+0.707j, 0.707-0.707j, 0.707+0.707j], [0, 1, 2, 3],
        4, 2, 2, 1, 1).base()
        self.QPSK_ampl_imbalance_and_15degQuadskew_try2 = QPSK_ampl_imbalance_and_15degQuadskew_try2 = digital.constellation_rect([-0.482362-1.931852j, -1.517638+1.931852j, 1.517638-1.931852j, 0.482362+1.931852j], [0, 1, 2, 3],
        4, 2, 2, 1, 1).base()
        self.QPSK_ampl_imbalance_and_15degQuadskew = QPSK_ampl_imbalance_and_15degQuadskew = digital.constellation_rect(((-0.5016-0.76635j), (-0.91245+0.76635j), (0.91245-0.76635j), (0.50176+0.76635j)), [0, 1, 2, 3],
        4, 2, 2, 1, 1).base()
        self.QPSK_NoQuadSkew_6dB_amp_imb = QPSK_NoQuadSkew_6dB_amp_imb = digital.constellation_rect([-0.3535-0.707j, -0.3535+0.707j, 0.3535-0.707j, 0.3535+0.707j], [0, 1, 2, 3],
        4, 2, 2, 1, 1).base()
        self.QPSK_20dB_amp_imbalance = QPSK_20dB_amp_imbalance = digital.constellation_rect([-0.707-0.0707j, -0.707+0.0707j, 0.707-0.0707j, 0.707+0.0707j], [0, 1, 2, 3],
        4, 2, 2, 1, 1).base()

        ##################################################
        # Blocks
        ##################################################
        self._start_calibration_range = Range(0, 1, 1, 0, 200)
        self._start_calibration_win = RangeWidget(self._start_calibration_range, self.set_start_calibration, 'start_calibration', "counter_slider", int)
        self.top_layout.addWidget(self._start_calibration_win)
        self.uhd_usrp_source_0 = uhd.usrp_source(
            ",".join(("", "")),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
        )
        self.uhd_usrp_source_0.set_center_freq(900e6, 0)
        self.uhd_usrp_source_0.set_gain(30, 0)
        self.uhd_usrp_source_0.set_antenna('RX2', 0)
        self.uhd_usrp_source_0.set_samp_rate(samp_rate)
        self.uhd_usrp_source_0.set_time_now(uhd.time_spec(time.time()), uhd.ALL_MBOARDS)
        self.uhd_usrp_sink_0 = uhd.usrp_sink(
            ",".join(("", "")),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
            '',
        )
        self.uhd_usrp_sink_0.set_center_freq(900e6, 0)
        self.uhd_usrp_sink_0.set_gain(6, 0)
        self.uhd_usrp_sink_0.set_antenna('TX/RX', 0)
        self.uhd_usrp_sink_0.set_samp_rate(samp_rate)
        self.uhd_usrp_sink_0.set_time_now(uhd.time_spec(time.time()), uhd.ALL_MBOARDS)
        self.qtgui_freq_sink_x_0_0_0 = qtgui.freq_sink_c(
            8192, #size
            firdes.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            "FROM USRP SOURCE", #name
            1
        )
        self.qtgui_freq_sink_x_0_0_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0_0_0.set_y_axis(-140, 10)
        self.qtgui_freq_sink_x_0_0_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0_0_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0_0_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0_0_0.enable_grid(True)
        self.qtgui_freq_sink_x_0_0_0.set_fft_average(1.0)
        self.qtgui_freq_sink_x_0_0_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0_0_0.enable_control_panel(False)



        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0_0_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0_0_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0_0_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0_0_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0_0_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_0_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0_0_0.pyqwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_freq_sink_x_0_0_0_win)
        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_c(
            8192, #size
            firdes.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            "RAW", #name
            1
        )
        self.qtgui_freq_sink_x_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0.set_y_axis(-140, 10)
        self.qtgui_freq_sink_x_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0.enable_grid(True)
        self.qtgui_freq_sink_x_0.set_fft_average(1.0)
        self.qtgui_freq_sink_x_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0.enable_control_panel(False)



        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0.pyqwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_freq_sink_x_0_win)
        self.qtgui_const_sink_x_0_0 = qtgui.const_sink_c(
            1024, #size
            "AFTER SCALING", #name
            1 #number of inputs
        )
        self.qtgui_const_sink_x_0_0.set_update_time(0.10)
        self.qtgui_const_sink_x_0_0.set_y_axis(-2, 2)
        self.qtgui_const_sink_x_0_0.set_x_axis(-2, 2)
        self.qtgui_const_sink_x_0_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, "")
        self.qtgui_const_sink_x_0_0.enable_autoscale(False)
        self.qtgui_const_sink_x_0_0.enable_grid(True)
        self.qtgui_const_sink_x_0_0.enable_axis_labels(True)


        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "red", "red", "red",
            "red", "red", "red", "red", "red"]
        styles = [1, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        markers = [0, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_const_sink_x_0_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_const_sink_x_0_0.set_line_label(i, labels[i])
            self.qtgui_const_sink_x_0_0.set_line_width(i, widths[i])
            self.qtgui_const_sink_x_0_0.set_line_color(i, colors[i])
            self.qtgui_const_sink_x_0_0.set_line_style(i, styles[i])
            self.qtgui_const_sink_x_0_0.set_line_marker(i, markers[i])
            self.qtgui_const_sink_x_0_0.set_line_alpha(i, alphas[i])

        self._qtgui_const_sink_x_0_0_win = sip.wrapinstance(self.qtgui_const_sink_x_0_0.pyqwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_const_sink_x_0_0_win)
        self.qtgui_const_sink_x_0 = qtgui.const_sink_c(
            1024, #size
            "RAW", #name
            1 #number of inputs
        )
        self.qtgui_const_sink_x_0.set_update_time(0.10)
        self.qtgui_const_sink_x_0.set_y_axis(-2, 2)
        self.qtgui_const_sink_x_0.set_x_axis(-2, 2)
        self.qtgui_const_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, "")
        self.qtgui_const_sink_x_0.enable_autoscale(False)
        self.qtgui_const_sink_x_0.enable_grid(True)
        self.qtgui_const_sink_x_0.enable_axis_labels(True)


        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "red", "red", "red",
            "red", "red", "red", "red", "red"]
        styles = [1, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        markers = [0, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_const_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_const_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_const_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_const_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_const_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_const_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_const_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_const_sink_x_0_win = sip.wrapinstance(self.qtgui_const_sink_x_0.pyqwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_const_sink_x_0_win)
        self.predistort_mult_by_msg_3 = predistort.mult_by_msg()
        self.predistort_mult_by_msg_2 = predistort.mult_by_msg()
        self.predistort_mult_by_msg_1 = predistort.mult_by_msg()
        self.predistort_mult_by_msg_0 = predistort.mult_by_msg()
        self.predistort_async_signal_mux_0_0 = predistort.async_signal_mux(gr.sizeof_char, 4)
        self.predistort_add_by_msg_1 = predistort.add_by_msg()
        self.predistort_add_by_msg_0 = predistort.add_by_msg()
        self.epy_block_0 = epy_block_0.amp_imbalance_quadskew_fixer(fft_len=8192, samp_rate=samp_rate, sps=sps, start_calibration=start_calibration, frames_to_discard=1000, amp_imb_dB_thresh=0.01, amp_imb_adaptation_const=0.99, quadskew_deg_thresh=0.1, quad_skew_adaptation_const=0.5, cosdc_step_size=0.1, sindc_step_size=0.1, LOfeedthruMinSuppressdB=50)
        self.digital_constellation_modulator_0 = digital.generic_mod(
            constellation=QPSK_ampl_imbalance_and_15degQuadskew,
            differential=False,
            samples_per_symbol=sps,
            pre_diff_code=True,
            excess_bw=0.5,
            verbose=False,
            log=False)
        self.blocks_vector_source_x_0_0_0 = blocks.vector_source_b((45, 45, 45, 45, 45, 45, 45, 45), True, 1, [])
        self.blocks_vector_source_x_0_0 = blocks.vector_source_b((228, 228, 228, 228, 228, 228, 228, 228), True, 1, [])
        self.blocks_vector_source_x_0 = blocks.vector_source_b((216, 216, 216, 216, 216, 216, 216, 216), True, 1, [])
        self.blocks_float_to_complex_0 = blocks.float_to_complex(1)
        self.blocks_complex_to_float_0 = blocks.complex_to_float(1)
        self.blocks_add_xx_0_0 = blocks.add_vff(1)
        self.blocks_add_xx_0 = blocks.add_vff(1)
        self.analog_random_source_x_0 = blocks.vector_source_b(list(map(int, numpy.random.randint(0, 256, 10000))), True)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.epy_block_0, 'value_cosdc'), (self.predistort_add_by_msg_0, 'ctrl_in'))
        self.msg_connect((self.epy_block_0, 'value_sindc'), (self.predistort_add_by_msg_1, 'ctrl_in'))
        self.msg_connect((self.epy_block_0, 'stream'), (self.predistort_async_signal_mux_0_0, 'ctrl_in'))
        self.msg_connect((self.epy_block_0, 'value_alphaI'), (self.predistort_mult_by_msg_0, 'ctrl_in'))
        self.msg_connect((self.epy_block_0, 'value_alphaQ'), (self.predistort_mult_by_msg_1, 'ctrl_in'))
        self.msg_connect((self.epy_block_0, 'value_epsQ'), (self.predistort_mult_by_msg_2, 'ctrl_in'))
        self.msg_connect((self.epy_block_0, 'value_epsI'), (self.predistort_mult_by_msg_3, 'ctrl_in'))
        self.connect((self.analog_random_source_x_0, 0), (self.predistort_async_signal_mux_0_0, 0))
        self.connect((self.blocks_add_xx_0, 0), (self.predistort_mult_by_msg_0, 0))
        self.connect((self.blocks_add_xx_0_0, 0), (self.predistort_mult_by_msg_1, 0))
        self.connect((self.blocks_complex_to_float_0, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.blocks_complex_to_float_0, 1), (self.blocks_add_xx_0_0, 1))
        self.connect((self.blocks_complex_to_float_0, 1), (self.predistort_mult_by_msg_2, 0))
        self.connect((self.blocks_complex_to_float_0, 0), (self.predistort_mult_by_msg_3, 0))
        self.connect((self.blocks_float_to_complex_0, 0), (self.qtgui_const_sink_x_0_0, 0))
        self.connect((self.blocks_float_to_complex_0, 0), (self.uhd_usrp_sink_0, 0))
        self.connect((self.blocks_vector_source_x_0, 0), (self.predistort_async_signal_mux_0_0, 1))
        self.connect((self.blocks_vector_source_x_0_0, 0), (self.predistort_async_signal_mux_0_0, 2))
        self.connect((self.blocks_vector_source_x_0_0_0, 0), (self.predistort_async_signal_mux_0_0, 3))
        self.connect((self.digital_constellation_modulator_0, 0), (self.blocks_complex_to_float_0, 0))
        self.connect((self.digital_constellation_modulator_0, 0), (self.qtgui_const_sink_x_0, 0))
        self.connect((self.digital_constellation_modulator_0, 0), (self.qtgui_freq_sink_x_0, 0))
        self.connect((self.predistort_add_by_msg_0, 0), (self.blocks_float_to_complex_0, 0))
        self.connect((self.predistort_add_by_msg_1, 0), (self.blocks_float_to_complex_0, 1))
        self.connect((self.predistort_async_signal_mux_0_0, 0), (self.digital_constellation_modulator_0, 0))
        self.connect((self.predistort_mult_by_msg_0, 0), (self.predistort_add_by_msg_0, 0))
        self.connect((self.predistort_mult_by_msg_1, 0), (self.predistort_add_by_msg_1, 0))
        self.connect((self.predistort_mult_by_msg_2, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.predistort_mult_by_msg_3, 0), (self.blocks_add_xx_0_0, 0))
        self.connect((self.uhd_usrp_source_0, 0), (self.epy_block_0, 0))
        self.connect((self.uhd_usrp_source_0, 0), (self.qtgui_freq_sink_x_0_0_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "AutoCalibrationQPSK_demo")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_start_calibration(self):
        return self.start_calibration

    def set_start_calibration(self, start_calibration):
        self.start_calibration = start_calibration
        self.epy_block_0.start_calibration = self.start_calibration

    def get_sps(self):
        return self.sps

    def set_sps(self, sps):
        self.sps = sps
        self.epy_block_0.sps = self.sps

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.epy_block_0.samp_rate = self.samp_rate
        self.qtgui_freq_sink_x_0.set_frequency_range(0, self.samp_rate)
        self.qtgui_freq_sink_x_0_0_0.set_frequency_range(0, self.samp_rate)
        self.uhd_usrp_sink_0.set_samp_rate(self.samp_rate)
        self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)

    def get_QPSK_ideal(self):
        return self.QPSK_ideal

    def set_QPSK_ideal(self, QPSK_ideal):
        self.QPSK_ideal = QPSK_ideal

    def get_QPSK_ampl_imbalance_and_15degQuadskew_try2(self):
        return self.QPSK_ampl_imbalance_and_15degQuadskew_try2

    def set_QPSK_ampl_imbalance_and_15degQuadskew_try2(self, QPSK_ampl_imbalance_and_15degQuadskew_try2):
        self.QPSK_ampl_imbalance_and_15degQuadskew_try2 = QPSK_ampl_imbalance_and_15degQuadskew_try2

    def get_QPSK_ampl_imbalance_and_15degQuadskew(self):
        return self.QPSK_ampl_imbalance_and_15degQuadskew

    def set_QPSK_ampl_imbalance_and_15degQuadskew(self, QPSK_ampl_imbalance_and_15degQuadskew):
        self.QPSK_ampl_imbalance_and_15degQuadskew = QPSK_ampl_imbalance_and_15degQuadskew

    def get_QPSK_NoQuadSkew_6dB_amp_imb(self):
        return self.QPSK_NoQuadSkew_6dB_amp_imb

    def set_QPSK_NoQuadSkew_6dB_amp_imb(self, QPSK_NoQuadSkew_6dB_amp_imb):
        self.QPSK_NoQuadSkew_6dB_amp_imb = QPSK_NoQuadSkew_6dB_amp_imb

    def get_QPSK_20dB_amp_imbalance(self):
        return self.QPSK_20dB_amp_imbalance

    def set_QPSK_20dB_amp_imbalance(self, QPSK_20dB_amp_imbalance):
        self.QPSK_20dB_amp_imbalance = QPSK_20dB_amp_imbalance





def main(top_block_cls=AutoCalibrationQPSK_demo, options=None):

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
