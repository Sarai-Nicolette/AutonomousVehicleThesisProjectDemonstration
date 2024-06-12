import math
import numpy as np
from scipy import linalg as lsci
from scipy.stats import multivariate_normal
import time


class GenerateSGPPowerPrediction:

    def __init__(self, rotor_info, rotor_data, actual_rc_data, rotor_obs_data, ind_points, var_set):
        self.rotor_info = rotor_info
        self.rotor_data = rotor_data
        self.actual_rc_data = actual_rc_data
        self.rotor_obs_data = rotor_obs_data
        self.var_re = var_set
        self.var_av = var_set
        self.ind_points = ind_points
        if rotor_info["rotorcraft_init"]["model_type"] == "simple":
            self.rotor_info = rotor_info
            self.rotor_data = []
            self.rho = float(self.rotor_info["rotorcraft_init"]["rho"])
            self.radius = float(self.rotor_info["rotorcraft_init"]["radius"])
            self.v_tip = rotor_data['Vtip']

        else:
            # Complex Model
            self.rotor_info = rotor_info
            self.rotor_data = rotor_data
            self.rho = float(self.rotor_info["rotorcraft_init"]["rho"])
            self.radius = float(self.rotor_info["rotorcraft_init"]["radius"])
            self.v_tip = rotor_data['Vtip']

        np.random.seed(528)
        self.ind_points_x = []
        self.hpr_prediction = []
        self.hpr_prediction_multi = []
        self.hpr_prediction_ind = []
        self.hpr_ind_pred = []
        self.hpr_lower_bound = []
        self.hpr_upper_bound = []
        self.hpr_qm_inv = []
        self.hpa_prediction = []
        self.hpa_prediction_multi = []
        self.hpa_prediction_ind = []
        self.hpa_ind_pred = []
        self.hpa_lower_bound = []
        self.hpa_upper_bound = []
        self.hpa_qm_inv = []
        self.cpr_prediction = []
        self.cpr_prediction_multi = []
        self.cpr_lower_bound = []
        self.cpr_upper_bound = []
        self.cpr_ind_pred = []
        self.ind_points_x_cp = []
        self.cpr_qm_inv = []
        self.cpa_prediction = []
        self.cpa_prediction_multi = []
        self.cpa_lower_bound = []
        self.cpa_upper_bound = []
        self.cpa_ind_pred = []
        self.cpa_qm_inv = []
        self.testing_points = [],
        self.num_of_pred = 60
        self.__generate_hpr_prediction()
        self.__generate_hpa_prediction()

    def __generate_hpr_prediction(self):
        # HP
        X_m = np.atleast_2d(self.rotor_obs_data['Speed']).T  # Measurement Points
        Y_m = np.array(self.rotor_obs_data['HP Required'])  # Measurement Points
        # print(np.array2string(Y_m, threshold=np.inf))
        X_T = np.atleast_2d(self.actual_rc_data['Speed']).T  # Test Points
        # X_T = np.linspace(int(min(self.rotor_obs_data['Speed'])), int(max(self.rotor_obs_data['Speed'])),
        #                   len(self.actual_rc_data['Speed'])+45).reshape(-1, 1)  # Inducing Points
        X_T = np.arange(int(min(self.rotor_obs_data['Speed'])), int(max(self.rotor_obs_data['Speed'])), 1).reshape(-1,
                                                                                                                   1)

        X_u = np.linspace(float(min(self.actual_rc_data['Speed'])), float(max(self.actual_rc_data['Speed'])),
                          self.ind_points).reshape(-1, 1)  # Inducing Points
        X_u = np.linspace(float(min(self.rotor_obs_data['Speed'])), float(max(self.rotor_obs_data['Speed'])),
                          self.ind_points).reshape(-1, 1)  # Inducing Points

        X_u_mu = np.linspace(float(min(self.actual_rc_data['Mu'])), float(max(self.actual_rc_data['Mu'])),
                             self.ind_points).reshape(-1, 1)  # Inducing Points

        # Custom SGP HP
        k_type = 'exp_quad_kernel'
        t0_sgp = time.time()
        μ2, Σ2, KTT, KTU, KUT, KUU, Qm, μ2_ind = self.__sgp_noise(X_m, Y_m, X_T, X_u, self.__kernel, k_type,
                                                                  self.var_re)

        # Compute the standard deviation at the test points to be plotted
        σ2 = np.sqrt(np.diag(Σ2))
        lower_bound = μ2 - 1.9600 * σ2
        upper_bound = μ2 + 1.9600 * σ2

        ################################################################################################################

        self.hpr_prediction = μ2
        self.hpr_lower_bound = lower_bound
        self.hpr_upper_bound = upper_bound
        self.hpr_ind_pred = μ2_ind
        self.ind_points_x = X_u
        self.hpr_qm_inv = lsci.inv(Qm)
        self.testing_points = X_T

        # CP
        self.cpr_prediction = [hp_el / ((self.rho * math.pi *
                                         pow(self.radius, 2) *
                                         pow(self.v_tip, 3))
                                        / 550.0) for i, hp_el in enumerate(self.hpr_prediction)]
        self.cpr_lower_bound = [hp_el / ((self.rho * math.pi *
                                          pow(self.radius, 2) *
                                          pow(self.v_tip, 3))
                                         / 550.0) for i, hp_el in enumerate(self.hpr_lower_bound)]
        self.cpr_upper_bound = [hp_el / ((self.rho * math.pi *
                                          pow(self.radius, 2) *
                                          pow(self.v_tip, 3))
                                         / 550.0) for i, hp_el in enumerate(self.hpr_upper_bound)]
        self.cpr_ind_pred = [hp_el / ((self.rho * math.pi *
                                       pow(self.radius, 2) *
                                       pow(self.v_tip, 3))
                                      / 550.0) for i, hp_el in enumerate(self.hpr_ind_pred)]
        self.ind_points_x_cp = X_u_mu

        # Loop Multiple solutions
        for i in range(0, self.num_of_pred):
            self.hpr_prediction_multi.append(multivariate_normal.rvs(mean=μ2, cov=Σ2))

    def __generate_hpa_prediction(self):
        # HP
        X_m = np.atleast_2d(self.rotor_obs_data['Speed']).T  # Measurement Points
        Y_m = np.array(self.rotor_obs_data['HP Available'])  # Measurement Points

        X_T = np.atleast_2d(self.actual_rc_data['Speed']).T  # Test Points
        # X_T = np.linspace(int(min(self.rotor_obs_data['Speed'])), int(max(self.rotor_obs_data['Speed'])),
        #                   len(self.actual_rc_data['Speed'])+45).reshape(-1, 1)  # Inducing Points
        X_T = np.arange(int(min(self.rotor_obs_data['Speed'])), int(max(self.rotor_obs_data['Speed'])), 1).reshape(-1,
                                                                                                                   1)
        X_u = np.linspace(float(min(self.actual_rc_data['Speed'])), float(max(self.actual_rc_data['Speed'])),
                          self.ind_points).reshape(-1, 1)  # Inducing Points
        X_u = np.linspace(float(min(self.rotor_obs_data['Speed'])), float(max(self.rotor_obs_data['Speed'])),
                          self.ind_points).reshape(-1, 1)  # Inducing Points

        k_type = 'const_kernel'

        # Custom SGP
        μ2, Σ2, KTT, KTU, KUT, KUU, Qm, μ2_ind = self.__sgp_noise(X_m, Y_m, X_T, X_u, self.__kernel, k_type,
                                                                  self.var_av)
        # Compute the standard deviation at the test points to be plotted
        σ2 = np.sqrt(np.diag(Σ2))
        lower_bound = μ2 - 1.9600 * σ2
        upper_bound = μ2 + 1.9600 * σ2
        self.hpa_prediction = μ2
        self.hpa_lower_bound = lower_bound
        self.hpa_upper_bound = upper_bound
        self.hpa_ind_pred = μ2_ind
        self.hpa_qm_inv = lsci.inv(Qm)
        self.testing_points = X_T

        ################################################################################################################
        # CP
        self.cpa_prediction = [hp_el / ((self.rho * math.pi *
                                         pow(self.radius, 2) *
                                         pow(self.v_tip, 3))
                                        / 550.0) for i, hp_el in enumerate(self.hpa_prediction)]
        self.cpa_lower_bound = [hp_el / ((self.rho * math.pi *
                                          pow(self.radius, 2) *
                                          pow(self.v_tip, 3))
                                         / 550.0) for i, hp_el in enumerate(self.hpa_lower_bound)]
        self.cpa_upper_bound = [hp_el / ((self.rho * math.pi *
                                          pow(self.radius, 2) *
                                          pow(self.v_tip, 3))
                                         / 550.0) for i, hp_el in enumerate(self.hpa_upper_bound)]
        self.cpa_ind_pred = [hp_el / ((self.rho * math.pi *
                                       pow(self.radius, 2) *
                                       pow(self.v_tip, 3))
                                      / 550.0) for i, hp_el in enumerate(self.hpa_ind_pred)]

        # Loop Multiple solutions
        for i in range(0, self.num_of_pred):
            self.hpa_prediction_multi.append(multivariate_normal.rvs(mean=μ2, cov=Σ2))

    def __sgp_noise(self, x_m, y_m, x_T, x_u, kernel_func, k_type, noise):
        # Kernel of the observations
        KMM = kernel_func(x_m, x_m, k_type)
        # Kernel of test points
        KTT = kernel_func(x_T, x_T, k_type)
        # Kernel of test points and inducing points
        KTU = kernel_func(x_T, x_u, k_type)
        # Kernel of inducing points and test points
        KUT = kernel_func(x_u, x_T, k_type)
        # Kernel of inducing points and observations
        KMU = kernel_func(x_m, x_u, k_type)
        # Kernel of inducing points
        KUU = kernel_func(x_u, x_u, k_type)
        # print(len(KMM))
        lam_M = KMM - KMU @ lsci.inv(KUU) @ KMU.T
        # print(len(y_m))
        lam_M_tilda = np.diag(np.diag(lam_M)) + ((noise ** 2) * np.eye(len(y_m)))
        # Solve for Qm
        Q_m = KUU + KMU.T @ lsci.inv(lam_M_tilda) @ KMU
        # Covariance Σ
        Σ = KTT - KTU @ (lsci.inv(KUU) - lsci.inv(Q_m)) @ KTU.T + ((noise ** 2) * np.eye(len(x_T)))
        # Prediction μ
        μ = KTU @ lsci.inv(Q_m) @ KMU.T @ lsci.inv(lam_M_tilda) @ y_m
        # Calculate inducing points solution
        μ_ind = KUU @ lsci.inv(Q_m) @ KMU.T @ lsci.inv(lam_M_tilda) @ y_m

        return μ, Σ, KTT, KTU, KUT, KUU, Q_m, μ_ind

    def __kernel(self, x, y, k_type):
        k = 0
        # GP Squared Exponential Kernel
        sq_dist = np.sum(x ** 2, 1).reshape(-1, 1) + np.sum(y ** 2, 1) - 2 * np.dot(x, y.T)

        if k_type == 'exp_quad_kernel':
            # Also known as Radial Basis Function Kernel
            l = self.rotor_info['rotorcraft_init']['hpr_length_param']
            # GP Kernel
            amp = self.rotor_info['rotorcraft_init']['hpr_amp_param']
            k = (amp ** 2) * np.exp(-0.5 * (1 / l ** 2) * sq_dist)
        elif k_type == 'const_kernel':
            # Also known as Radial Basis Function Kernel
            l = self.rotor_info['rotorcraft_init']['hpa_length_param']
            # GP Kernel
            amp = self.rotor_info['rotorcraft_init']['hpa_amp_param']
            k = (amp ** 2) * np.exp(-0.5 * (1 / l ** 2) * sq_dist)

            # k_lin
            sig_b = self.rotor_info['rotorcraft_init']['hpa_bias_param']
            sig_v = self.rotor_info['rotorcraft_init']['hpa_slope_param']

            k = (sig_b ** 2) + (sig_v ** 2) * x.reshape(-1, 1) * y.T + k
        else:
            pass

        return k

    def get_prediction_data(self):

        data = {'HPR Prediction': self.hpr_prediction,
                'HPR Prediction Multi': self.hpr_prediction_multi,
                'CPR Prediction': self.cpr_prediction,
                'HPR Lower Bound': self.hpr_lower_bound,
                'HPR Upper Bound': self.hpr_upper_bound,
                'CPR Lower Bound': self.cpr_lower_bound,
                'CPR Upper Bound': self.cpr_upper_bound,
                'HPR Alpha': self.var_re,
                'HPR Inducing Points': self.hpr_ind_pred,
                'CPR Inducing Points': self.cpr_ind_pred,
                'HPA Prediction': self.hpa_prediction,
                'HPA Prediction Multi': self.hpa_prediction_multi,
                'CPA Prediction': self.cpa_prediction,
                'HPA Lower Bound': self.hpa_lower_bound,
                'HPA Upper Bound': self.hpa_upper_bound,
                'CPA Lower Bound': self.cpa_lower_bound,
                'CPA Upper Bound': self.cpa_upper_bound,
                'HPA Alpha': self.var_av,
                'HPA Inducing Points': self.hpa_ind_pred,
                'CPA Inducing Points': self.cpa_ind_pred,
                'Inducing Points X': self.ind_points_x,
                'Inducing Points X CP': self.ind_points_x_cp,
                'HPR Qm_inv': self.hpr_qm_inv,
                'HPA Qm_inv': self.hpa_qm_inv,
                'Testing Points X': self.testing_points,
                'Mu': self.actual_rc_data['Mu']
                }

        return data
