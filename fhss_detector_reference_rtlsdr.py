#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Burst Detector Reference
# Author: J. Gilbert
# Copyright: NTESS, LLC
# Description: Reference Application
# GNU Radio version: 3.8.5.0

from gnuradio import blocks
from gnuradio import gr
from gnuradio.filter import firdes
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import fhss_utils
import osmosdr
import time
import pdu_utils
import smart_meters


class fhss_detector_reference_rtlsdr(gr.top_block):

    def __init__(self, burst_width=int(100e3), center_freq=915e6, cfo_start_offset=0, cfo_threshold=0.5, cfo_time_to_average=0.0005, decimation=int(256/10), fft_size=int(1024/10), gain=60, hist_time=0.004, lookahead_time=0.0005, max_burst_time=0.5, min_burst_time=0.020, output_attenuation=40, output_cutoff=0.5, output_trans_width=0.05, post_burst_time=0.00008, pre_burst_time=0.00008, samp_rate=int(2.4e6), threshold=6):
        gr.top_block.__init__(self, "Burst Detector Reference")

        ##################################################
        # Parameters
        ##################################################
        self.burst_width = burst_width
        self.center_freq = center_freq
        self.cfo_start_offset = cfo_start_offset
        self.cfo_threshold = cfo_threshold
        self.cfo_time_to_average = cfo_time_to_average
        self.decimation = decimation
        self.fft_size = fft_size
        self.gain = gain
        self.hist_time = hist_time
        self.lookahead_time = lookahead_time
        self.max_burst_time = max_burst_time
        self.min_burst_time = min_burst_time
        self.output_attenuation = output_attenuation
        self.output_cutoff = output_cutoff
        self.output_trans_width = output_trans_width
        self.post_burst_time = post_burst_time
        self.pre_burst_time = pre_burst_time
        self.samp_rate = samp_rate
        self.threshold = threshold

        ##################################################
        # Variables
        ##################################################
        self.variable_low_pass_filter_taps_0 = variable_low_pass_filter_taps_0 = firdes.low_pass(1.0, (samp_rate/decimation), 19200,9600, firdes.WIN_HAMMING, 6.76)
        self.syncwords = syncwords = '10101010101010101010101010101010101010101010101010'
        self.fir_taps = fir_taps = firdes.low_pass_2(1, 1, 0.5*output_cutoff, 0.5*output_trans_width, output_attenuation)
        self.decim_taps = decim_taps = firdes.low_pass_2(1, 1, output_cutoff/decimation, output_trans_width/decimation, output_attenuation)

        ##################################################
        # Blocks
        ##################################################
        self.smart_meters_GridStream_0 = smart_meters.GridStream(True, 0x4E2D, 0xF136D12F, 0x0, 0x0)
        self.pdu_utils_pdu_split_0_0 = pdu_utils.pdu_split(False)
        self.pdu_utils_pdu_quadrature_demod_cf_0 = pdu_utils.pdu_quadrature_demod_cf(1.0)
        self.pdu_utils_pdu_fir_filter_1 = pdu_utils.pdu_fir_filter(2, fir_taps)
        self.pdu_utils_pdu_fir_filter_0 = pdu_utils.pdu_fir_filter(1, variable_low_pass_filter_taps_0)
        self.pdu_utils_pdu_fine_time_measure_0 = pdu_utils.pdu_fine_time_measure(pre_burst_time, post_burst_time, 10, 15)
        self.pdu_utils_pdu_clock_recovery_0_0 = pdu_utils.pdu_clock_recovery(True, False, pdu_utils.TUKEY_WIN)
        self.pdu_utils_pdu_clock_recovery_0 = pdu_utils.pdu_clock_recovery(False, False, pdu_utils.TUKEY_WIN)
        self.pdu_utils_pdu_align_0 = pdu_utils.pdu_align(syncwords, 0, 0)
        self.osmosdr_source_0 = osmosdr.source(
            args="numchan=" + str(1) + " " + ""
        )
        self.osmosdr_source_0.set_time_unknown_pps(osmosdr.time_spec_t())
        self.osmosdr_source_0.set_sample_rate(samp_rate)
        self.osmosdr_source_0.set_center_freq(center_freq, 0)
        self.osmosdr_source_0.set_freq_corr(0, 0)
        self.osmosdr_source_0.set_dc_offset_mode(0, 0)
        self.osmosdr_source_0.set_iq_balance_mode(0, 0)
        self.osmosdr_source_0.set_gain_mode(True, 0)
        self.osmosdr_source_0.set_gain(30, 0)
        self.osmosdr_source_0.set_if_gain(30, 0)
        self.osmosdr_source_0.set_bb_gain(30, 0)
        self.osmosdr_source_0.set_antenna('', 0)
        self.osmosdr_source_0.set_bandwidth(0, 0)
        self.fhss_utils_tagged_burst_to_pdu_0 = fhss_utils.tagged_burst_to_pdu(decimation, decim_taps, min_burst_time, max_burst_time, 0.0, 1.0, 1.0, samp_rate, 3)
        self.fhss_utils_fft_burst_tagger_0 = fhss_utils.fft_burst_tagger(center_freq, fft_size, samp_rate, int(round((float(samp_rate)/fft_size)*pre_burst_time)), int(round((float(samp_rate)/fft_size)*post_burst_time)), burst_width, 0, 0, threshold, int(round((float(samp_rate)/fft_size)*hist_time)), int(round((float(samp_rate)/fft_size)*lookahead_time)), False)
        self.fhss_utils_fft_burst_tagger_0.set_min_output_buffer(2048000)
        self.fhss_utils_cf_estimate_0 = fhss_utils.cf_estimate(0, [])
        self.blocks_socket_pdu_0 = blocks.socket_pdu('TCP_SERVER', '', '5002', 10000, False)
        self.blocks_probe_rate_0 = blocks.probe_rate(gr.sizeof_gr_complex*1, 500.0, 0.15)
        self.blocks_multiply_const_vxx_0_1_0 = blocks.multiply_const_cc(pow(2,-15) * pow(2,(gain/10)))
        self.blocks_multiply_const_vxx_0_1_0.set_min_output_buffer(1024000)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.fhss_utils_cf_estimate_0, 'out'), (self.pdu_utils_pdu_fir_filter_1, 'pdu_in'))
        self.msg_connect((self.fhss_utils_tagged_burst_to_pdu_0, 'cpdus'), (self.fhss_utils_cf_estimate_0, 'in'))
        self.msg_connect((self.pdu_utils_pdu_align_0, 'pdu_out'), (self.smart_meters_GridStream_0, 'pdu_in'))
        self.msg_connect((self.pdu_utils_pdu_clock_recovery_0, 'pdu_out'), (self.pdu_utils_pdu_split_0_0, 'pdu_in'))
        self.msg_connect((self.pdu_utils_pdu_clock_recovery_0_0, 'pdu_out'), (self.pdu_utils_pdu_align_0, 'pdu_in'))
        self.msg_connect((self.pdu_utils_pdu_fine_time_measure_0, 'pdu_out'), (self.pdu_utils_pdu_quadrature_demod_cf_0, 'cpdus'))
        self.msg_connect((self.pdu_utils_pdu_fir_filter_0, 'pdu_out'), (self.pdu_utils_pdu_clock_recovery_0, 'pdu_in'))
        self.msg_connect((self.pdu_utils_pdu_fir_filter_0, 'pdu_out'), (self.pdu_utils_pdu_clock_recovery_0_0, 'pdu_in'))
        self.msg_connect((self.pdu_utils_pdu_fir_filter_1, 'pdu_out'), (self.pdu_utils_pdu_fine_time_measure_0, 'pdu_in'))
        self.msg_connect((self.pdu_utils_pdu_quadrature_demod_cf_0, 'fpdus'), (self.pdu_utils_pdu_fir_filter_0, 'pdu_in'))
        self.msg_connect((self.smart_meters_GridStream_0, 'pdu_out'), (self.blocks_socket_pdu_0, 'pdus'))
        self.connect((self.blocks_multiply_const_vxx_0_1_0, 0), (self.blocks_probe_rate_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_1_0, 0), (self.fhss_utils_fft_burst_tagger_0, 0))
        self.connect((self.fhss_utils_fft_burst_tagger_0, 0), (self.fhss_utils_tagged_burst_to_pdu_0, 0))
        self.connect((self.osmosdr_source_0, 0), (self.blocks_multiply_const_vxx_0_1_0, 0))


    def get_burst_width(self):
        return self.burst_width

    def set_burst_width(self, burst_width):
        self.burst_width = burst_width

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq
        self.osmosdr_source_0.set_center_freq(self.center_freq, 0)

    def get_cfo_start_offset(self):
        return self.cfo_start_offset

    def set_cfo_start_offset(self, cfo_start_offset):
        self.cfo_start_offset = cfo_start_offset

    def get_cfo_threshold(self):
        return self.cfo_threshold

    def set_cfo_threshold(self, cfo_threshold):
        self.cfo_threshold = cfo_threshold

    def get_cfo_time_to_average(self):
        return self.cfo_time_to_average

    def set_cfo_time_to_average(self, cfo_time_to_average):
        self.cfo_time_to_average = cfo_time_to_average

    def get_decimation(self):
        return self.decimation

    def set_decimation(self, decimation):
        self.decimation = decimation
        self.set_decim_taps(firdes.low_pass_2(1, 1, self.output_cutoff/self.decimation, self.output_trans_width/self.decimation, self.output_attenuation))
        self.set_variable_low_pass_filter_taps_0(firdes.low_pass(1.0, (self.samp_rate/self.decimation), 19200, 9600, firdes.WIN_HAMMING, 6.76))

    def get_fft_size(self):
        return self.fft_size

    def set_fft_size(self, fft_size):
        self.fft_size = fft_size

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain
        self.blocks_multiply_const_vxx_0_1_0.set_k(pow(2,-15) * pow(2,(self.gain/10)))

    def get_hist_time(self):
        return self.hist_time

    def set_hist_time(self, hist_time):
        self.hist_time = hist_time

    def get_lookahead_time(self):
        return self.lookahead_time

    def set_lookahead_time(self, lookahead_time):
        self.lookahead_time = lookahead_time

    def get_max_burst_time(self):
        return self.max_burst_time

    def set_max_burst_time(self, max_burst_time):
        self.max_burst_time = max_burst_time

    def get_min_burst_time(self):
        return self.min_burst_time

    def set_min_burst_time(self, min_burst_time):
        self.min_burst_time = min_burst_time

    def get_output_attenuation(self):
        return self.output_attenuation

    def set_output_attenuation(self, output_attenuation):
        self.output_attenuation = output_attenuation
        self.set_decim_taps(firdes.low_pass_2(1, 1, self.output_cutoff/self.decimation, self.output_trans_width/self.decimation, self.output_attenuation))
        self.set_fir_taps(firdes.low_pass_2(1, 1, 0.5*self.output_cutoff, 0.5*self.output_trans_width, self.output_attenuation))

    def get_output_cutoff(self):
        return self.output_cutoff

    def set_output_cutoff(self, output_cutoff):
        self.output_cutoff = output_cutoff
        self.set_decim_taps(firdes.low_pass_2(1, 1, self.output_cutoff/self.decimation, self.output_trans_width/self.decimation, self.output_attenuation))
        self.set_fir_taps(firdes.low_pass_2(1, 1, 0.5*self.output_cutoff, 0.5*self.output_trans_width, self.output_attenuation))

    def get_output_trans_width(self):
        return self.output_trans_width

    def set_output_trans_width(self, output_trans_width):
        self.output_trans_width = output_trans_width
        self.set_decim_taps(firdes.low_pass_2(1, 1, self.output_cutoff/self.decimation, self.output_trans_width/self.decimation, self.output_attenuation))
        self.set_fir_taps(firdes.low_pass_2(1, 1, 0.5*self.output_cutoff, 0.5*self.output_trans_width, self.output_attenuation))

    def get_post_burst_time(self):
        return self.post_burst_time

    def set_post_burst_time(self, post_burst_time):
        self.post_burst_time = post_burst_time

    def get_pre_burst_time(self):
        return self.pre_burst_time

    def set_pre_burst_time(self, pre_burst_time):
        self.pre_burst_time = pre_burst_time

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_variable_low_pass_filter_taps_0(firdes.low_pass(1.0, (self.samp_rate/self.decimation), 19200, 9600, firdes.WIN_HAMMING, 6.76))
        self.osmosdr_source_0.set_sample_rate(self.samp_rate)

    def get_threshold(self):
        return self.threshold

    def set_threshold(self, threshold):
        self.threshold = threshold

    def get_variable_low_pass_filter_taps_0(self):
        return self.variable_low_pass_filter_taps_0

    def set_variable_low_pass_filter_taps_0(self, variable_low_pass_filter_taps_0):
        self.variable_low_pass_filter_taps_0 = variable_low_pass_filter_taps_0
        self.pdu_utils_pdu_fir_filter_0.set_taps(self.variable_low_pass_filter_taps_0)

    def get_syncwords(self):
        return self.syncwords

    def set_syncwords(self, syncwords):
        self.syncwords = syncwords

    def get_fir_taps(self):
        return self.fir_taps

    def set_fir_taps(self, fir_taps):
        self.fir_taps = fir_taps
        self.pdu_utils_pdu_fir_filter_1.set_taps(self.fir_taps)

    def get_decim_taps(self):
        return self.decim_taps

    def set_decim_taps(self, decim_taps):
        self.decim_taps = decim_taps




def argument_parser():
    description = 'Reference Application'
    parser = ArgumentParser(description=description)
    parser.add_argument(
        "--burst-width", dest="burst_width", type=intx, default=int(100e3),
        help="Set Burst Width [Hz] [default=%(default)r]")
    parser.add_argument(
        "-c", "--center-freq", dest="center_freq", type=eng_float, default="915.0M",
        help="Set center_freq [default=%(default)r]")
    parser.add_argument(
        "--cfo-start-offset", dest="cfo_start_offset", type=eng_float, default="0.0",
        help="Set CFO Start Offset [s] [default=%(default)r]")
    parser.add_argument(
        "--cfo-threshold", dest="cfo_threshold", type=eng_float, default="500.0m",
        help="Set CFO threshold [default=%(default)r]")
    parser.add_argument(
        "--cfo-time-to-average", dest="cfo_time_to_average", type=eng_float, default="500.0u",
        help="Set CFO Average Time [s] [default=%(default)r]")
    parser.add_argument(
        "--decimation", dest="decimation", type=intx, default=int(256/10),
        help="Set Decimation [default=%(default)r]")
    parser.add_argument(
        "--fft-size", dest="fft_size", type=intx, default=int(1024/10),
        help="Set FFT Size [default=%(default)r]")
    parser.add_argument(
        "-g", "--gain", dest="gain", type=eng_float, default="60.0",
        help="Set gain [default=%(default)r]")
    parser.add_argument(
        "--hist-time", dest="hist_time", type=eng_float, default="4.0m",
        help="Set History Time [s] [default=%(default)r]")
    parser.add_argument(
        "--lookahead-time", dest="lookahead_time", type=eng_float, default="500.0u",
        help="Set Lookahead Time [s] [default=%(default)r]")
    parser.add_argument(
        "--max-burst-time", dest="max_burst_time", type=eng_float, default="500.0m",
        help="Set Max Burst Time [s] [default=%(default)r]")
    parser.add_argument(
        "--min-burst-time", dest="min_burst_time", type=eng_float, default="20.0m",
        help="Set Min Burst Time [s] [default=%(default)r]")
    parser.add_argument(
        "--output-attenuation", dest="output_attenuation", type=eng_float, default="40.0",
        help="Set Output Attenuation [default=%(default)r]")
    parser.add_argument(
        "--output-cutoff", dest="output_cutoff", type=eng_float, default="500.0m",
        help="Set Output Cutoff [cycles/samp] [default=%(default)r]")
    parser.add_argument(
        "--output-trans-width", dest="output_trans_width", type=eng_float, default="50.0m",
        help="Set Output Trans. Width [cycles/samp] [default=%(default)r]")
    parser.add_argument(
        "--post-burst-time", dest="post_burst_time", type=eng_float, default="80.0u",
        help="Set Post Burst Time [s] [default=%(default)r]")
    parser.add_argument(
        "--pre-burst-time", dest="pre_burst_time", type=eng_float, default="80.0u",
        help="Set Pre Burst Time [s] [default=%(default)r]")
    parser.add_argument(
        "-r", "--samp-rate", dest="samp_rate", type=intx, default=int(2.4e6),
        help="Set Sample Rate [default=%(default)r]")
    parser.add_argument(
        "-t", "--threshold", dest="threshold", type=eng_float, default="6.0",
        help="Set Threshold [default=%(default)r]")
    return parser


def main(top_block_cls=fhss_detector_reference_rtlsdr, options=None):
    if options is None:
        options = argument_parser().parse_args()
    tb = top_block_cls(burst_width=options.burst_width, center_freq=options.center_freq, cfo_start_offset=options.cfo_start_offset, cfo_threshold=options.cfo_threshold, cfo_time_to_average=options.cfo_time_to_average, decimation=options.decimation, fft_size=options.fft_size, gain=options.gain, hist_time=options.hist_time, lookahead_time=options.lookahead_time, max_burst_time=options.max_burst_time, min_burst_time=options.min_burst_time, output_attenuation=options.output_attenuation, output_cutoff=options.output_cutoff, output_trans_width=options.output_trans_width, post_burst_time=options.post_burst_time, pre_burst_time=options.pre_burst_time, samp_rate=options.samp_rate, threshold=options.threshold)


    def sig_handler(sig=None, frame=None):
            tb.stop()
            tb.wait()

            sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()

    try:
        input('Press Enter to quit: ')
    except EOFError:
        pass

    
        tb.stop()
        tb.wait()


if __name__ == '__main__':
    main()
