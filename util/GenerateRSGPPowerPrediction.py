import numpy as np
from scipy import linalg as lsci
import time


class GenerateRSGPPowerPrediction:

    def __init__(self, rotor_info, rsgp_pred_rotor_data, var_re, var_av, Xn, Yn_hpr, Yn_hpa, old_hpr, old_hpa):
        self.rotor_info = rotor_info
        self.rsgp_pred_rotor_data = rsgp_pred_rotor_data
        self.var_re = var_re
        self.var_av = var_av
        self.ind_points_x = rsgp_pred_rotor_data['Inducing Points X']
        self.hpr_ind_pred = rsgp_pred_rotor_data['HPR Inducing Points']
        self.hpa_ind_pred = rsgp_pred_rotor_data['HPA Inducing Points']
        self.test_points_x = rsgp_pred_rotor_data['Testing Points X']
        self.hpr_prediction = rsgp_pred_rotor_data['HPR Prediction']
        # TODO: Multi is not updated
        self.hpr_prediction_multi = rsgp_pred_rotor_data['HPR Prediction Multi']
        self.hpa_prediction_multi = rsgp_pred_rotor_data['HPA Prediction Multi']
        self.hpr_Xn = Xn
        self.hpr_Yn = Yn_hpr
        self.hpr_lower_bound = []
        self.hpr_upper_bound = []
        self.hpr_qm_inv = rsgp_pred_rotor_data['HPR Qm_inv']
        self.hpa_prediction = rsgp_pred_rotor_data['HPA Prediction']
        self.hpa_Xn = Xn
        self.hpa_Yn = Yn_hpa
        self.hpa_lower_bound = []
        self.hpa_upper_bound = []
        self.hpa_qm_inv = rsgp_pred_rotor_data['HPA Qm_inv']
        self.__generate_hpr_prediction()
        self.__generate_hpa_prediction()

    def __generate_hpr_prediction(self):

        X_T = self.test_points_x  # Test Points
        X_u = self.ind_points_x  # Inducing Points
        X_n = np.array([self.hpr_Xn])  # New X data point
        Y_n = np.array([self.hpr_Yn])  # New Y data point
        Qm_inv = self.hpr_qm_inv
        ui = self.hpr_prediction
        u_ind = self.hpr_ind_pred

        # Custom RSGP
        k_type = 'exp_quad_kernel'
        t0_sgp = time.time()
        μ2, Σ2, Qm_inv, μ_ind = self.__rsgp_noise(ui, u_ind, Qm_inv, X_T, X_u, X_n, Y_n, self.__kernel, k_type,
                                                  self.var_re)

        self.hpr_qm_inv = Qm_inv
        t1_sgp = time.time() - t0_sgp
        # print(t1_sgp, " seconds")
        # Compute the standard deviation at the test points to be plotted
        σ2 = np.sqrt(np.diag(Σ2))
        lower_bound = μ2 - 1.9600 * σ2
        upper_bound = μ2 + 1.9600 * σ2

        self.hpr_prediction = μ2
        self.hpr_ind_pred = μ_ind
        self.hpr_lower_bound = lower_bound
        self.hpr_upper_bound = upper_bound
        self.hpr_qm_inv = Qm_inv

    def __generate_hpa_prediction(self):
        X_T = self.test_points_x  # Test Points
        X_u = self.ind_points_x  # Inducing Points
        X_n = np.array([self.hpa_Xn])  # New X data point
        Y_n = np.array([self.hpa_Yn])  # New Y data point
        Qm_inv = self.hpa_qm_inv
        ui = self.hpa_prediction
        u_ind = self.hpa_ind_pred

        # Custom RSGP
        k_type = 'const_kernel'
        μ2, Σ2, Qm_inv, μ_ind = self.__rsgp_noise(ui, u_ind, Qm_inv, X_T, X_u, X_n, Y_n, self.__kernel, k_type,
                                                  self.var_av)

        # Compute the standard deviation at the test points to be plotted
        σ2 = np.sqrt(np.diag(Σ2))
        lower_bound = μ2 - 1.9600 * σ2
        upper_bound = μ2 + 1.9600 * σ2
        self.hpa_prediction = μ2
        self.hpa_ind_pred = μ_ind
        self.hpa_lower_bound = lower_bound
        self.hpa_upper_bound = upper_bound
        self.hpa_qm_inv = Qm_inv

    def __rsgp_noise(self, ui, u_ind, Qmi_inv, x_T, x_u, x_n, y_n, kernel_func, k_type, noise):
        # Kernel of the observations
        KMMN = kernel_func(x_n, x_n, k_type)
        # Kernel of inducing points and observations
        KMUN = kernel_func(x_n, x_u, k_type)
        # Kernel of inducing points and inducing points
        KUU = kernel_func(x_u, x_u, k_type)
        # Kernel of testing points and testing points
        KTT = kernel_func(x_T, x_T, k_type)
        # Kernel of testing points and inducing points
        KTU = kernel_func(x_T, x_u, k_type)
        # print(np.shape(KMUN))
        lam_M = KMMN - KMUN @ lsci.inv(KUU) @ KMUN.T  # KMUN.T @ lsci.inv(KUU) @ KMUN
        lam_M_tilda = np.diag(np.diag(lam_M) + (noise ** 2))
        # Find delta change in Qmi equation
        delta_i = KMUN.T @ lam_M_tilda @ KMUN  # KMUN.T * lam_M_tilda @ KMUN ## inverse lam?
        # Solve Ki_star
        Ki_star = KUU @ Qmi_inv @ KUU
        # Solve for inverse Qmi
        Qmi_inv_plus = Qmi_inv - ((Qmi_inv @ delta_i @ Qmi_inv) / (1 + np.trace(Qmi_inv @ delta_i)))
        Qmi_inv = Qmi_inv_plus
        # Solve Ki_star_plus
        Ki_star_plus = KUU @ Qmi_inv_plus @ KUU
        # Solve for covariance
        # Ki_plus = KTT - KUT @ (lsci.inv(KUU) - Qmi_inv_plus) @ KTU + ((noise ** 2) * np.eye(len(KTT[0])))
        Σi = KTT - (KTU @ (lsci.inv(KUU) - Qmi_inv_plus) @ KTU.T) + ((noise ** 2) * np.eye(len(KTT)))
        # print('T', len(ui.reshape(-1, 1)))
        # Solve for prediction
        # μ_i = ui.reshape(-1, 1) + (KTU @ Qmi_inv_plus @ KMUN * lsci.inv(lam_M_tilda) * y_n).reshape(-1, 1)

        # print(np.shape(Qmi_inv_plus))
        # print(np.shape(KMUN))

        # Sign consideration
        # print(len(ui))
        x_T_list = x_T.flatten().tolist()

        x_T_temp = [round(i) for i in x_T_list]

        close_index = self.find_closest_index(x_T_temp, x_n[0])

        # print(close_index)

        sign = 1

        # Reconfigures scope of estimates to match list
        # if x_n >= 0 and x_n <= 90:
        #     if ui.tolist()[int(x_n)+20] < y_n:
        #         sign = 1
        #     else:
        #         sign = -1
        # else:
        #     if x_n < 0:
        #         if ui.tolist()[-int(-x_n)-20] < y_n:
        #             sign = 1
        #         else:
        #             sign = -1

        # Works mostly
        # if x_n >= 0 and x_n <= 111:
        #     if ui.tolist()[int(x_n)] < y_n:
        #         sign = 1
        #     else:
        #         sign = -1
        # else:
        #     if x_n < 0:
        #         if ui.tolist()[0] < y_n:
        #             sign = 1
        #         else:
        #             sign = -1
        #     else:
        #         if ui.tolist()[110] < y_n:
        #             sign = 1
        #         else:
        #             sign = -1

        if ui.tolist()[close_index] < y_n:
            sign = 1
        else:
            sign = -1

        # if x_n >= 0 and x_n <= 111 - 24:
        #     if ui.tolist()[int(x_n) + 23] < y_n:
        #         sign = 1
        #     else:
        #         sign = -1
        # else:
        #     if x_n < 0:
        #         if ui.tolist()[int(-x_n)] < y_n:
        #             sign = 1
        #         else:
        #             sign = -1
        #     else:
        #         if ui.tolist()[110] < y_n:
        #             sign = 1
        #         else:
        #             sign = -1

        μ_i = ui.reshape(-1, 1) + (KTU @ (sign * Qmi_inv_plus) @ KMUN.T @ lsci.inv(lam_M_tilda) * y_n)  # OG
        # print(μ_i)
        μ_ind = u_ind.reshape(-1, 1) + (KUU @ (sign * Qmi_inv_plus) @ KMUN.T @ lsci.inv(lam_M_tilda) * y_n)  # OG

        # μ_i = ui.reshape(-1, 1) + (KTU @ Qmi_inv_plus @ KMUN @ lam_M_tilda * y_n).reshape(-1, 1)
        # # print(μ_i)
        # μ_ind = u_ind.reshape(-1, 1) + (KUU @ Qmi_inv_plus @ KMUN @ lam_M_tilda * y_n).reshape(-1, 1)

        return μ_i.flatten(), Σi, Qmi_inv, μ_ind

    def __kernel(self, x, y, k_type):
        k = 0
        # print('y_len', len(y))
        # GP Squared Exponential Kernel
        if len(x) == 1 and len(y) == 1:
            sq_dist = (x ** 2) + (y ** 2) - 2 * (x * y)
            sq_dist = sq_dist.reshape(-1, 1)

        elif len(x) > 1 and len(y) == 1:
            sq_dist = np.sum(x ** 2, 1).reshape(-1, 1) + pow(y, 2) - 2 * (x * y)
            sq_dist = sq_dist.reshape(-1, 1)

        elif len(x) == 1 and len(y) > 1:
            sq_dist = pow(x, 2) + np.sum(y ** 2, 1).reshape(-1, 1) - 2 * (x * y)
            sq_dist = sq_dist.reshape(-1, 1).T

        else:
            sq_dist = np.sum(x ** 2, 1).reshape(-1, 1) + np.sum(y ** 2, 1) - 2 * np.dot(x, y.T)

        if k_type == 'exp_quad_kernel':
            # Also known as Radial Basis Function Kernel
            l = self.rotor_info['rotorcraft_init']['hpr_length_param']
            # l = 25
            l = 25
            # GP Kernel
            amp = self.rotor_info['rotorcraft_init']['hpr_amp_param']
            # amp = 35
            # amp = 30
            amp = 30
            k = (amp ** 2) * np.exp(-0.5 * (1 / l ** 2) * sq_dist)
            # print('HPR k', np.size(k))

        elif k_type == 'const_kernel':
            # Also known as Radial Basis Function Kernel
            l = self.rotor_info['rotorcraft_init']['hpa_length_param']
            l = 20
            # GP Kernel
            amp = self.rotor_info['rotorcraft_init']['hpa_amp_param']
            # amp = 45, 33
            amp = 39
            k = (amp ** 2) * np.exp(-0.5 * (1 / l ** 2) * sq_dist)

            # # k_lin
            # sig_b = self.rotor_info['rotorcraft_init']['hpa_bias_param']
            # sig_v = self.rotor_info['rotorcraft_init']['hpa_slope_param']
            # # sig_b = 8.65
            # # sig_v = 0.009 #0.0001
            # if len(x) == 1 and len(y) > 1:
            #     k = ((sig_b ** 2) + (sig_v ** 2) * y.reshape(-1, 1).T * x.T + k)
            # else:
            #     k = (sig_b ** 2) + (sig_v ** 2) * x.reshape(-1, 1) * y.T + k

        else:
            pass

        return k

    def get_prediction_data(self):

        data = {'HPR Prediction': self.hpr_prediction,
                'HPR Lower Bound': self.hpr_lower_bound,
                'HPR Upper Bound': self.hpr_upper_bound,
                'HPR Alpha': self.var_re,
                'HPR Inducing Points': self.hpr_ind_pred,
                'HPA Prediction': self.hpa_prediction,
                'HPA Lower Bound': self.hpa_lower_bound,
                'HPA Upper Bound': self.hpa_upper_bound,
                'HPR Prediction Multi': self.hpr_prediction_multi,
                'HPA Prediction Multi': self.hpa_prediction_multi,
                'HPA Alpha': self.var_av,
                'HPA Inducing Points': self.hpa_ind_pred,
                'HPR Qm_inv': self.hpr_qm_inv,
                'HPA Qm_inv': self.hpa_qm_inv,
                'Inducing Points X': self.ind_points_x,
                'Testing Points X': self.test_points_x
                }

        return data

    def find_closest_index(self, numbers, target):
        # Check if the list is empty
        if not numbers:
            return None  # Return None if the list is empty

        # Initialize variables to store the closest difference and index
        closest_difference = float('inf')  # Initialize with positive infinity
        closest_index = None

        # Iterate through the list and find the closest number
        for i, number in enumerate(numbers):
            # Calculate the absolute difference between the target and the current number
            difference = abs(number - target)

            # Update the closest index if the current difference is smaller
            if difference < closest_difference:
                closest_difference = difference
                closest_index = i

        return closest_index
