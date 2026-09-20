import numpy as np
from gnuradio import gr
import pmt

class amp_imbalance_quadskew_fixer(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block

    def __init__(self, fft_len=8192, samp_rate=32e3, sps=4, start_calibration=0, frames_to_discard=2, amp_imb_dB_thresh=0.05, amp_imb_adaptation_const=0.1, quadskew_deg_thresh=0.5, quad_skew_adaptation_const=0.5, cosdc_step_size=.001, sindc_step_size=0.001, LOfeedthruMinSuppressdB=70):


        gr.sync_block.__init__(
            self,
            name='IQ Amp Imblance and QuadSkew Fixer',   # will show up in GRC
            in_sig=[np.complex64], # Input: Raw samples
            out_sig=None # Output was Corrected signal, now PMT messages are used to achieve feedback.
        )
        self.message_port_register_out(pmt.intern("stream")) # FOR PMT
        self.message_port_register_out(pmt.intern("value_alphaI")) # FOR PMT I-channal gain adjustment
        self.message_port_register_out(pmt.intern("value_alphaQ")) # FOR PMT Q-channel gain adjustment
        self.message_port_register_out(pmt.intern("value_epsI")) # FOR PMT crosstalk factor for I
        self.message_port_register_out(pmt.intern("value_epsQ")) # FOR PMT crosstalk factor for Q
        self.message_port_register_out(pmt.intern("value_cosdc")) # FOR PMT I-DC offset
        self.message_port_register_out(pmt.intern("value_sindc")) # FOR PMT Q-DC offset

        self.fft_len=fft_len
        self.samp_rate = samp_rate
        self.start_calibration = start_calibration
        self.sps = sps
        self.frames_to_discard = frames_to_discard
        self.amp_imb_dB_thresh = np.abs(amp_imb_dB_thresh) # Make sure user doesn't supply a negative value, handle it if the user does.
        self.amp_imb_adaptation_const = amp_imb_adaptation_const
        self.quadskew_deg_thresh = quadskew_deg_thresh
        self.quad_skew_adaptation_const = quad_skew_adaptation_const
        self.orig_quad_skew_adaptation_const = quad_skew_adaptation_const
        self.cosdc_step_size = cosdc_step_size
        self.sindc_step_size = sindc_step_size
        self.LOfeedthruMinSuppressdB = np.abs(LOfeedthruMinSuppressdB) # The amount in dB that the LO feedthrough must be suppressed relative to Fundamental Positive Peak


        ## Calculate the frequency bins for each tone location (fastplus, fast minus, slow plus, slowminus)
        # fastplus = fs/(sps*2)
        self.fastplus = samp_rate / (sps * 2)
        # fastminus = -fs/(sos*2)
        self.fastminus = -samp_rate / (sps * 2)
        # slowplus = fs/(sps*4)
        self.slowplus = samp_rate / (sps * 4)
        # slowminus = -fs/(sps*4)
        self.slowminus = -samp_rate / (sps * 4)

        # Frequency bins
        self.fft_bin_numbers = np.array(range(0,fft_len))-fft_len//2
        self.fft_freq_vector = self.fft_bin_numbers.astype(float) * samp_rate / fft_len

        self.fastplusindex = np.floor(self.fastplus * fft_len/samp_rate).astype(int) + fft_len//2
        self.fastminusindex = np.floor(self.fastminus * fft_len/samp_rate).astype(int) + fft_len//2
        self.slowplusindex = np.floor(self.slowplus * fft_len/samp_rate).astype(int) + fft_len//2
        self.slowminusindex = np.floor(self.slowminus * fft_len/samp_rate).astype(int) + fft_len//2
        self.indexthresh = (self.fastplusindex-self.slowplusindex)//2
      
        self.slowplusindex_search_start = self.slowplusindex - self.indexthresh
        self.slowplusindex_search_end = self.slowplusindex + self.indexthresh

        self.slowminusindex_search_start = self.slowminusindex - self.indexthresh
        self.slowminusindex_search_end = self.slowminusindex + self.indexthresh

        self.fastplusindex_search_start = self.fastplusindex - self.indexthresh
        self.fastplusindex_search_end = self.fastplusindex + self.indexthresh

        self.fastminusindex_search_start = self.fastminusindex - self.indexthresh
        self.fastminusindex_search_end = self.fastminusindex + self.indexthresh
        
        # Amplitude balance
        self.alphaI = 1 # Used if amplitude imbalance is negative dB
        self.alphaQ = 1 # used if amplitude imbalance is positive dB, change to negative
        self.amplitude_imbalancedB = 0
        self.IfastplusdB = 0
        self.IfastminusdB = 0
        self.IslowplusdB  = 0
        self.IslowminusdB = 0
        self.QfastplusdB = 0
        self.QfastminusdB = 0
        self.QslowplusdB = 0
        self.QslowminusdB = 0

        # Quadrature Skew
        self.quadskew_radians = 0
        self.epsI = 0 # We can apply the value of quadskew_radians to either epsI, epsQ, or both
        self.epsQ = 0
        self.last_quadskew_radians = 0
        self.quadskew_radians_direction = 1 # 1 for positive, -1 for negative
        self.last_quadskew_radians_direction = 1
        #self.prev_last_quadskew_radians_direction = 1
        self.last_PositiveFundamentaldB = 1000
        self.last_NegativeUndesiredImagedB = 1000 # Unrealistically high initially so that first measurement will show improvement
        self.PositiveFundamentaldB = 1000
        self.NegativeUndesiredImagedB = 1000 # Unrealistically high initially so that first measurement will show improvement
        self.PositiveFundamental_search_start = self.slowplusindex_search_start
        self.PositiveFundamental_search_end = self.slowplusindex_search_end
        self.NegativeUndesiredImage_search_start = self.slowminusindex_search_start
        self.NegativeUndesiredImage_search_end = self.slowminusindex_search_end

        # LO Feedthrough
        self.LOFeedThrudB = 1000
        self.last_LOFeedThrudB = 1000 # Unrealistically high initially so that first measurement will show improvement
        self.cosdc = 0
        self.sindc = 0
        self.cosdc_direction = 1 # Either +1 or -1
        self.sindc_direction = 1 # Either +1 or -1
        self.dcbin_search_start = fft_len // 2 - self.indexthresh
        self.dcbin_search_end = fft_len // 2 + self.indexthresh

        # State variables
        self.control_state = 0 # 1 means IfastQslow, 2 means IslowQfast, 3 means quadskew/dc offset, 0 means start / done (random data)
        self.calibration_started = 0
        self.iterations = 0
        self.IQQImeasurements = 0
        self.QIIQmeasurements = 0
        self.quadskewmeasurements = 0
        self.LOFeedThruMeasurements = 0
        self.DCtermToChange = 0 # 0 = COSdc term (I-component DC), 1 = SINdc term (Q-component DC)
        self.frameflag = 0 # This flag allows us to avoid making changes until fft_len*m_of_n samples AFTER a source change.
                           # This flag increments until it reaches "frames_to_discard" value, which tells system to take measurement and reset this to zero.



    def work(self, input_items, output_items):
        #in_data = np.real(input_items[0])*self.alphaI + 1j*np.imag(input_items[0])*self.alphaQ
        in_data = input_items[0]
        #out_data = output_items[0]
        n_samples = len(in_data)

        # Do we have enough info for the requisite number of FFTs?  If not, don't consume the samples yet
                # Determine how many full FFT frames we can process in this execution chunk
        num_frames = len(in_data)//self.fft_len
        
        if num_frames==0:
            # Not enough raw time-=domain samples yet to fill an FFT length
            #out_data[:] = in_data[:]
            #out_data = np.real(in_data)*self.alphaI + 1j*np.imag(in_data)*self.alphaQ
            return 0 # Wait for more data

        # If we have enough info for the requisite number of FFT frames, average the power
        # BE SURE TO INCLUDE THE OLD CORRECTION FACTOR. Without the feedback of the old correction factor, the input power won't change
        # Process each complete FFT fram eavilable in the current buffer
        spectrum = np.zeros(self.fft_len)
        for i in range(num_frames):
            frame = in_data[i * self.fft_len:(i+1)*self.fft_len]
            #frame = in_data[i * self.fft_len:(i+1)*self.fft_len]-(self.current_val_real + 1j*self.current_val_imag) # without including the DC removers, input power never changes

            # Replacing Log Power FFT Block Logic ---
            # 1.  Apply a window function (Hann window) to minimize spectral leakage
            #windowed_frame = frame*np.hanning(self.fft_len)
            windowed_frame = frame

            # 2. Compete the FFT and center it using fftshift
            spectrum = spectrum + np.fft.fftshift(np.fft.fft(windowed_frame))

        # 3. Calculate Log Power Spectrum: 10 * log10(|X|^2)=20*log10(|X|)
        # Add a small epsilon (1e-12) to protect against computing log10 of zero:
        spectrum = spectrum / num_frames
        power_spectrum = 20.0*np.log10(np.abs(spectrum)+1e-12)

        self.iterations += 1

        if self.control_state==0:
            if(self.start_calibration == 1):
                if(self.calibration_started == 0):
                    self.control_state = 1
                    self.calibration_started = 1        

        # Extract the peaks.  If this is control_state 1, then we are using Ifast Qslow (IQQI)
        # If this is control state 2, then we are using IslowQfast (QIIQ)
        elif self.control_state==1: # This is state IQQI (Ifast Qslow)
            if self.frameflag >= self.frames_to_discard: # was 1:
                self.IfastplusdB = np.max(power_spectrum[self.fastplusindex_search_start:self.fastplusindex_search_end])
                self.IfastminusdB = np.max(power_spectrum[self.fastminusindex_search_start:self.fastminusindex_search_end])
                self.QslowplusdB = np.max(power_spectrum[self.slowplusindex_search_start:self.slowplusindex_search_end])
                self.QslowminusdB = np.max(power_spectrum[self.slowminusindex_search_start:self.slowminusindex_search_end])
                self.control_state = 2 # Switch to QIIQ (IslowQfast)
                self.IQQImeasurements += 1
                self.frameflag = 0 # for next frame block, wait before using data
            else:
                self.frameflag += 1 # Do not use current info, change flag
        elif self.control_state==2: # This is state QIIQ (Islow Qfast)
            if self.frameflag >= self.frames_to_discard:  # was 1):
                self.IslowplusdB = np.max(power_spectrum[self.slowplusindex_search_start:self.slowplusindex_search_end])
                self.IslowminusdB = np.max(power_spectrum[self.slowminusindex_search_start:self.slowminusindex_search_end])
                self.QfastplusdB = np.max(power_spectrum[self.fastplusindex_search_start:self.fastplusindex_search_end])
                self.QfastminusdB = np.max(power_spectrum[self.fastminusindex_search_start:self.fastminusindex_search_end])
                self.QIIQmeasurements += 1

                # If we just stored values in control state 1, then we are ready to compte Q-I dB
                self.amplitude_imbalancedB = np.mean(np.array([(self.QfastminusdB-self.IfastminusdB), (self.QslowminusdB-self.IslowminusdB), (self.QslowplusdB-self.IslowplusdB), (self.QfastplusdB-self.IfastplusdB)]))
                


                # Apply the change as an UPDATED correction factor for the Q-channel
                temp_alpha = (10**(-self.amplitude_imbalancedB/20*self.amp_imb_adaptation_const))*(self.alphaQ/self.alphaI) # (new correction) * (prev imbalance)
                if(temp_alpha < 1):
                    self.alphaQ = temp_alpha
                    self.alphaI = 1.0
                else:
                    self.alphaI = 1/temp_alpha
                    self.alphaQ = 1.0

                #if (self.iterations >= 100):
                if np.mod(self.QIIQmeasurements,4) == 1:
                    print(f"[DEBUG] fastminus: {self.QfastminusdB} dB - {self.IfastminusdB} dB = {self.QfastminusdB - self.IfastminusdB} dB")
                    print(f"[DEBUG] slowminus: {self.QslowminusdB} dB - {self.IslowminusdB} dB = {self.QslowminusdB - self.IslowminusdB} dB")
                    print(f"[DEBUG] slowplus: {self.QslowplusdB} dB - {self.IslowplusdB} dB = {self.QslowplusdB - self.IslowplusdB} dB")
                    print(f"[DEBUG] fastplus: {self.QfastplusdB} dB - {self.IfastplusdB} dB = {self.QfastplusdB - self.IfastplusdB} dB")
                    print(f"[DEBUG] Cumulative alphaI value is {self.alphaI} = {20*np.log10(self.alphaI+1e-12)} dB")
                    print(f"[DEBUG] Cumulative alphaQ value is {self.alphaQ} = {20*np.log10(self.alphaQ+1e-12)} dB")
                    print(f"[DEBUG] There have been {self.IQQImeasurements} IQQI and {self.QIIQmeasurements} QIIQ measurements.")
                    print(f"[DEBUG] {self.iterations} iterations have taken place.")
                
                # Check if we're done
                if(np.abs(self.amplitude_imbalancedB) < self.amp_imb_dB_thresh):
                    print(f"[DEBUG - SOLUTION FOUND at iteration {self.iterations}")
                    print(f"[DEBUG - SOLUTION FOUND] fastminus: {self.QfastminusdB} dB - {self.IfastminusdB} dB = {self.QfastminusdB - self.IfastminusdB} dB")
                    print(f"[DEBUG - SOLUTION FOUND] slowminus: {self.QslowminusdB} dB - {self.IslowminusdB} dB = {self.QslowminusdB - self.IslowminusdB} dB")
                    print(f"[DEBUG - SOLUTION FOUND] slowplus: {self.QslowplusdB} dB - {self.IslowplusdB} dB = {self.QslowplusdB - self.IslowplusdB} dB")
                    print(f"[DEBUG - SOLUTION FOUND] fastplus: {self.QfastplusdB} dB - {self.IfastplusdB} dB = {self.QfastplusdB - self.IfastplusdB} dB")
                    print(f"[DEBUG - SOLUTION FOUND] Cumulative alphaI value is {self.alphaI} = {20*np.log10(self.alphaI+1e-12)} dB")
                    print(f"[DEBUG - SOLUTION FOUND] Cumulative alphaQ value is {self.alphaQ} = {20*np.log10(self.alphaQ+1e-12)} dB")
                    print(f"[DEBUG - SOLUTION FOUND] There have been {self.IQQImeasurements} IQQI and {self.QIIQmeasurements} QIIQ measurements.")
                    print(f"[DEBUG - SOLUTION FOUND] {self.iterations} iterations have taken place.")
                    self.control_state = 3 # Go to Quad Skew
                else: # Not done yet                    
                    self.control_state = 1

                self.frameflag = 0 # Change this because we are changing the source
            else:
                self.frameflag += 1 # Do not use the current info or update amplitude imbalance info, change flag
        # This is where we would put "elif self.control_state == 3" and check quad skew and LO feedthrough at same time
        elif self.control_state==3:
            if self.frameflag >= self.frames_to_discard:

                self.quadskewmeasurements += 1

                # Measure the positive fundamental frequency
                self.last_PositiveFundamentaldB = self.PositiveFundamentaldB
                self.PositiveFundamentaldB = np.max(power_spectrum[self.PositiveFundamental_search_start:self.PositiveFundamental_search_end])

                # Measure the negative image frequency
                self.last_NegativeUndesiredImagedB = self.NegativeUndesiredImagedB
                self.NegativeUndesiredImagedB = np.max(power_spectrum[self.NegativeUndesiredImage_search_start:self.NegativeUndesiredImage_search_end])

                # Compute the image rejection ratio
                image_rejection_ratio_dB = self.PositiveFundamentaldB - self.NegativeUndesiredImagedB
                image_rejection_ratio = 10.0**(image_rejection_ratio_dB/10.0)

                # Estimate quadrature skew
                quadskew_radians_sq = 4.0/(image_rejection_ratio - 1.0 + 1e-12)
                #alphatemp = 10.0**(self.amplitude_imbalancedB/20.0)
                #numerator_left_part = image_rejection_ratio*(1.0-2.0*alphatemp+alphatemp*alphatemp)
                #numerator_right_part = (1.0+2.0*alphatemp+alphatemp*alphatemp)
                #denominator_part = alphatemp*alphatemp * (1.0 - image_rejection_ratio) + 1e-12
                #quadskew_radians_sq = (numerator_left_part - numerator_right_part)/denominator_part

                # If undesired peak grew from previous measurement, change sign of quadrature skew and DO NOT UPDATE quadskew number
                #self.prev_last_quadskew_radians_direction = self.last_quadskew_radians_direction
                #self.last_quadskew_radians_direction = self.quadskew_radians_direction
                if(self.NegativeUndesiredImagedB > self.last_NegativeUndesiredImagedB):

                    self.quadskew_radians_direction = -1 * self.quadskew_radians_direction
                    self.quad_skew_adaptation_const = self.quad_skew_adaptation_const / 2.0
                    
                    #self.last_NegativeUndesiredImagedB = 1000 # Prevent unstable direction switching on the next measurement
                    print(f"[DEBUG QUAD SKEW REVERSE DIRECTION] Old image was {self.last_NegativeUndesiredImagedB} dB, new image was {self.NegativeUndesiredImagedB} dB")
                    print(f"[DEBUG QUAD SKEW REVERSE DIRECTION] Iteration number is {self.iterations}")

                else:
                    print(f"[DEBUG QUAD SKEW old direction] Old image was {self.last_NegativeUndesiredImagedB} dB, new image was {self.NegativeUndesiredImagedB} dB")
                    print(f"[DEBUG QUAD SKEW old direction] Iteration number is {self.iterations}")
                    self.last_quadskew_radians = self.quadskew_radians
                self.quadskew_radians += np.sqrt(quadskew_radians_sq) * self.quadskew_radians_direction * self.quad_skew_adaptation_const
                #self.epsI = self.quadskew_radians / 2.0
                #self.epsQ = self.quadskew_radians / 2.0
                self.epsQ = self.quadskew_radians # put it all on the Q-channel.  I is still 0

                print(f"--------------------------------------------------------------------------")
                print(f"[DEBUG QUAD SKEW] This is measurement number {self.quadskewmeasurements}.")
                print(f"[DEBUG QUAD SKEW] Positive fundamental is {self.PositiveFundamentaldB} dB.")
                print(f"[DEUBG QUAD SKEW] Negative fundamental is {self.NegativeUndesiredImagedB} dB.")
                print(f"[DEBUG QUAD SKEW] Image Reject Ratio is {image_rejection_ratio_dB} dB.")
                print(f"[DEBUG QUAD SKEW] Residual quad skew is {np.sqrt(quadskew_radians_sq) * self.quadskew_radians_direction} radians = {np.sqrt(quadskew_radians_sq) * self.quadskew_radians_direction * 180.0/np.pi} degrees.")
                print(f"[DEBUG QUAD SKEW] Quad Skew is {self.quadskew_radians * self.quadskew_radians_direction} radians = {self.quadskew_radians*self.quadskew_radians_direction*180.0/np.pi} degrees.")
                print(f"[DEBUG QUAD SKEW] Old Quad Skew was {self.last_quadskew_radians * self.last_quadskew_radians_direction} radians = {self.last_quadskew_radians * self.last_quadskew_radians_direction * 180.0 / np.pi} degrees.")


                # Now let's also meaure the LO feedthrough (DC) tone so we can correct it, too:
                # Measure the LO Feedthrough frequency
                self.LOFeedThruMeasurements += 1
                self.last_LOFeedThrudB = self.LOFeedThrudB # Save old value of LO Feedthru dB
                self.LOFeedThrudB = np.max(power_spectrum[self.dcbin_search_start:self.dcbin_search_end]) # Get new value of LO Feedthru dB
                
                if (self.LOFeedThrudB > self.last_LOFeedThrudB):
                    if self.DCtermToChange == 0:
                        self.cosdc_direction = -1 * self.cosdc_direction
                        self.cosdc_step_size = np.max([self.cosdc_step_size / 1.414, 0.001])
                        print(f"[DEBUG LO FEEDTHRU CHANGE COSDC DIRECTION], cosdc step change is now {self.cosdc_direction * self.cosdc_step_size}")
                    else:
                        self.sindc_direction = -1 * self.sindc_direction
                        self.sindc_step_size = np.max([self.sindc_step_size / 1.414, 0.001])
                        print(f"[DEBUG LO FEEDTHRU CHANGE SINDC DIRECTION], sindc step change is now {self.sindc_direction * self.sindc_step_size}")

                # Update the DC offset based on which one is being controlled.  (We switch to other one every few measurements)  
                print(f"[DEBUG LO FEEDTHRU]  This is measurement number {self.LOFeedThruMeasurements}")
                if self.DCtermToChange == 0:
                    self.cosdc += self.cosdc_step_size * self.cosdc_direction
                    print(f"[DEBUG LO FEEDTHRU COSDC] Suppression was {self.PositiveFundamentaldB - self.LOFeedThrudB} dB, change cosdc to {self.cosdc}")
                else:
                    self.sindc += self.sindc_step_size * self.sindc_direction
                    print(f"[DEBUG LO FEEDTHRU SINDC] Suppression was {self.PositiveFundamentaldB - self.LOFeedThrudB} dB, change sindc to {self.sindc}")




                # If residual quadrature skew is below the threshod AND LO Feedthru is sufficiently suppressed, change control state to 0 (random signal, calibration complete)
                if(((np.sqrt(quadskew_radians_sq) * 180.0 / np.pi) < self.quadskew_deg_thresh) and ((self.PositiveFundamentaldB-self.LOFeedThrudB) > self.LOfeedthruMinSuppressdB)):
                    print(f"[DEBUG - QUAD SKEW SOLUTION FOUND] Quad skew is now {self.quadskew_radians * 180.0 / np.pi} degrees.  Stopping Calibration")
                    print(f"[DEBUG - DC OFFSETS FOUND] COSdc is now {self.cosdc}, SINdc is now {self.sindc}")
                    self.control_state = 0 # May need to change this later
                elif self.quadskewmeasurements >= 20:
                    self.quadskewmeasurements = 0
                    self.quad_skew_adaptation_const = self.orig_quad_skew_adaptation_const # original value instead of self.quad_skew_adaptation_const / 2
                    self.control_state = 1 # Go back to I/Q amp imbalance
                elif self.LOFeedThruMeasurements >= 10:
                    self.LOFeedThruMeasurements = 0
                    if(self.DCtermToChange == 0):
                        self.DCtermToChange = 1
                    else:
                        self.DCtermToChange = 0
                else:
                    self.control_state = 3 # Stay here if residual quad skew is too high but we haven't hit the number of quad skew measurements to try
                self.frameflag = 0 # Change the source to random, indicating that we are done with calibration.
            else:
                self.frameflag += 1


        msg = pmt.cons(pmt.intern("stream"),pmt.from_long(self.control_state))
        self.message_port_pub(pmt.intern("stream"),msg)

        # PMT messages for the ouptuts (alphaI and alphaQ, epsI and epsQ)
        value_alphaI = pmt.from_double(self.alphaI)
        value_alphaQ = pmt.from_double(self.alphaQ)
        value_epsI = pmt.from_double(self.epsI)
        value_epsQ = pmt.from_double(self.epsQ)
        value_cosdc = pmt.from_double(self.cosdc)
        value_sindc = pmt.from_double(self.sindc)

        # Publish the correction factors
        keyshared = pmt.intern("value") # The adjusted parameters use "value" as the key
        msg_alphaI = pmt.cons(keyshared,value_alphaI)
        msg_alphaQ = pmt.cons(keyshared,value_alphaQ)
        msg_epsI = pmt.cons(keyshared,value_epsI)
        msg_epsQ = pmt.cons(keyshared,value_epsQ)
        msg_cosdc = pmt.cons(keyshared,value_cosdc)
        msg_sindc = pmt.cons(keyshared,value_sindc)
        self.message_port_pub(pmt.intern("value_alphaI"),msg_alphaI)
        self.message_port_pub(pmt.intern("value_alphaQ"),msg_alphaQ)
        self.message_port_pub(pmt.intern("value_epsI"),msg_epsI)
        self.message_port_pub(pmt.intern("value_epsQ"),msg_epsQ)
        self.message_port_pub(pmt.intern("value_cosdc"),msg_cosdc)
        self.message_port_pub(pmt.intern("value_sindc"),msg_sindc)

         # Consume the input data
        return n_samples