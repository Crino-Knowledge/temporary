import numpy as np
from asf import ASF
from cdf import CDF

PRE_STEP_ASF = True  
PRE_STEP_CDF = True

class Pulse():
    def __init__(self, framerate, signal_size, batch_size, image_size=256):
        self.framerate = float(framerate)
        self.signal_size = signal_size
        self.batch_size = batch_size
        self.minFreq = 0.9
        self.maxFreq = 3
        self.fft_spec = []
        self.hr_history = []

    def get_pulse(self, mean_rgb):
        seg_t = 1
        l = int(self.framerate * seg_t)
        n = len(mean_rgb)          # 使用实际帧数，而非固定的 signal_size
        H = np.zeros(n)

        B = [int(0.8 // (self.framerate / l)), int(4 // (self.framerate / l))]
                
        for t in range(0, (n - l + 1)):    # 循环也基于实际帧数
            C = mean_rgb[t:t+l,:].T
           
            if PRE_STEP_CDF:
                C = CDF(C, B)
           
            if PRE_STEP_ASF:
                C = ASF(C)
            mean_color = np.mean(C, axis=1)
            diag_mean_color = np.diag(mean_color)
            diag_mean_color_inv = np.linalg.inv(diag_mean_color)
            Cn = np.matmul(diag_mean_color_inv, C)
            projection_matrix = np.array([[0, 1, -1], [-2, 1, 1]])
            S = np.matmul(projection_matrix, Cn)
            std = np.array([1, np.std(S[0,:])/np.std(S[1,:])])
            P = np.matmul(std, S)
            H[t:t+l] = H[t:t+l] + (P - np.mean(P))

        return H


    def get_rfft_hr(self, signal, smooth_window=6):
        signal_size = len(signal)
        signal = signal.flatten()
        fft_data = np.fft.rfft(signal)
        fft_data = np.abs(fft_data)
        freq = np.fft.rfftfreq(signal_size, 1./self.framerate)
        inds = np.where((freq < self.minFreq) | (freq > self.maxFreq))[0]
        fft_data[inds] = 0
        bps_freq = 60.0 * freq
        max_index = np.argmax(fft_data)
        fft_data[max_index] = fft_data[max_index] ** 2
        self.fft_spec.append(fft_data)
        HR = bps_freq[max_index]
        self.hr_history.append(HR)
        if len(self.hr_history) > smooth_window:
            smoothed_hr = np.mean(self.hr_history[-smooth_window:])
        else:
            smoothed_hr = HR
        
        return smoothed_hr
