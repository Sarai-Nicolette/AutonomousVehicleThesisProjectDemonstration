import random
import os
from statistics import mean
import numpy as np
import pandas as pd


class GeneratePowerObservations:

    def __init__(self, actual_rc_data, rotor_info, rotor_data, num_obs, var_set):
        self.actual_rc_data = actual_rc_data
        self.num_obs = num_obs  # Number of observations
        self.var_re = var_set  # Variance of HP Required Data
        self.var_av = var_set  # Variance of HP Available Data
        self.num_obs_added = None  # Set as a result of experimental studies

        if rotor_info["rotorcraft_init"]["model_type"] == "simple":
            self.rotor_info = rotor_info
            self.rotor_data = []
            self.rho = float(self.rotor_info["rotorcraft_init"]["rho"])
            self.radius = float(self.rotor_info["rotorcraft_init"]["radius"])
            self.v_tip = float(self.rotor_info["rotorcraft_init"]["v_tip"])

        else:
            # Complex Model
            self.rotor_info = rotor_info
            self.rotor_data = rotor_data
            self.rho = float(self.rotor_info["rotorcraft_init"]["rho"])
            self.radius = float(self.rotor_info["rotorcraft_init"]["radius"])
            self.v_tip = rotor_data['Vtip'].values.tolist()

        self.speed_obs = []
        self.mu = []
        self.hp_required_obs = []
        self.hp_available_obs = []
        self.cp_required_obs = []
        self.cp_available_obs = []
        self.__generate_observations()

    def __generate_observations(self):
        # Set Random Seed
        random.seed(20)

        # Get index of equal segments of observations (Change back to knots?)
        speed_vec = self.actual_rc_data['Speed']
        # Linearly space observations and find speed index of closest linearly spaced value
        speed_obs = np.linspace(0, max(speed_vec), num=self.num_obs)

        hp_required_vec = self.actual_rc_data['HP Required']
        hp_available_vec = self.actual_rc_data['HP Available']

        # # Get index of equal segments of observations (Change back to knots?)
        # speed_vec = self.actual_rc_data['Speed']
        # # Linearly space observations and find speed index of closest linearly spaced value
        # speed_obs = np.linspace(0, max(speed_vec), num=self.num_obs)
        # obs_index = [np.argmin(np.abs(np.array(speed_vec) - speed_obs[i])) for i in range(0, len(speed_obs))]

        # speed_obs = [speed_vec[i * k] for i in range(1, self.num_obs + 1)]
        # #print(speed_vec[168])
        # obs_index = [i * k for i in range(1, self.num_obs + 1)]
        self.speed_obs = speed_obs

        # Create Random Observations
        # hp_required_vec = self.actual_rc_data['HP Required']
        # hp_available_vec = self.actual_rc_data['HP Available']
        # self.hp_required_obs = [random.gauss(0, self.var_re/2) +
        #                         hp_required_vec[obs_index[i]] for i in range(0, len(obs_index))]
        # self.hp_available_obs = [random.gauss(0, self.var_av/2) +
        #                          hp_available_vec[obs_index[i]] for i in range(0, len(obs_index))]

        # Create Init and End Observations
        ################################################################################################################
        # Add 1% of observation before and after power chart to smooth out prediction by data duplication
        # Edit: Changed to 50 based on mobility metric study
        # num_obs_added = 8   # int(len(obs_index) * 0.05)  # Number added to each side
        # Add speed index at start and end

        # diff = 1
        # temp1 = np.flip([speed_obs[0] - diff * (i + 1) for i in range(0, self.num_obs_added)])

        # save divisions
        div = []
        speed_temp = speed_obs[0]
        for i in range(0, 500):
            div.append(speed_temp)
            speed_temp = speed_temp - 0.08
        temp1 = np.flip(div)

        temp2 = np.concatenate((temp1, speed_obs))
        # temp3 = speed_obs[len(speed_obs) - self.num_obs_added:len(speed_obs)]
        max_value = max(speed_obs)
        added_value = 1
        # temp3 = [max_value + added_value * (i + 1) for i in range(0, self.num_obs_added)]  # Adds speed to right part

        div = []
        speed_temp = max_value
        for i in range(0, 150):
            div.append(speed_temp)
            speed_temp = speed_temp + 0.06
        temp3 = div
        self.num_obs_added = len(temp3)

        # Complete New Speed Observations
        self.speed_obs = np.concatenate((temp2, temp3))
        # print(len(self.speed_obs))
        obs_index = [np.argmin(np.abs(np.array(speed_vec) - self.speed_obs[i])) for i in range(0, len(self.speed_obs))]
        self.num_obs = len(self.speed_obs)

        # Get Vtip that corresponds to each speed
        # Save the index of each speed as int (Limit bounds of speed for VTIP equivalent values)
        speed_int = []
        for s in self.speed_obs:
            if s < 0:
                speed_int.append(0)
            elif s > int(self.rotor_info["rotorcraft_init"]["maxAirspeed"]) - 1:
                speed_int.append(int(self.rotor_info["rotorcraft_init"]["maxAirspeed"]) - 1)
            else:
                speed_int.append(int(s))
        # Create a new list of v_tips
        if self.rotor_info["rotorcraft_init"]["model_type"] != "simple":
            V_TIP = [self.v_tip[s] for s in speed_int]  # Vtip changes in complex and stays the same in the edge case
        else:
            V_TIP = [self.v_tip for s in speed_int]  # Vtip is the same for all values in simple

        # Create Random Observations
        # Use End Values to generate flat noisy data on either end to support estimate #################################
        self.hp_available_obs = [random.gauss(0, self.var_av / 2) +
                                 hp_available_vec[obs_index[i]] for i in range(0, len(obs_index))]

        # Ensure hp required estimate has sloped observations on right side
        # Get the number of observations at the end by dividing the num_obs_added by 2
        num_obs_hpr_end = self.num_obs_added
        # Save a vector of the last 3% of actual speed data obs_index_hpr_end
        # TODO: May want to change to getting values above a certain speed
        temp = int(max(obs_index[0:len(obs_index) - num_obs_hpr_end]) -
                   round(max(obs_index[0:len(obs_index) - num_obs_hpr_end]) * 0.05))  # Get last ~5% of speed/x values
        # temp = int(max(obs_index[0:len(obs_index) - num_obs_hpr_end]) - 7)
        obs_index_hpr_end = []
        for obs in obs_index:
            if obs >= temp:
                obs_index_hpr_end.append(obs)
        # Remove end observations from obs_index and Save old obs_index in obs_index_save
        obs_index_save = obs_index
        obs_index = obs_index[0:len(obs_index) - num_obs_hpr_end]
        # Save a vector of the corresponding hpr data
        hp_required_obs_end = [random.gauss(0, self.var_re / 2) +
                               hp_required_vec[obs_index_hpr_end[i]] for i in range(0, len(obs_index_hpr_end))]
        # Get approximate slope of the observations using linear regression
        obs_index_hpr_end_mean = round(mean(obs_index_hpr_end))

        hp_required_obs_end_mean = mean(hp_required_obs_end)
        a0, a1, a2, a3 = [], [], [], []
        for i in range(0, len(obs_index_hpr_end)):
            a0.append(obs_index_hpr_end[i] - obs_index_hpr_end_mean)
            a1.append(hp_required_obs_end[i] - hp_required_obs_end_mean)
            a3.append((obs_index_hpr_end[i] - obs_index_hpr_end_mean) ** 2)

        a2 = [a0[i] * a1[i] for i in range(0, len(obs_index_hpr_end))]
        m = sum(a2) / sum(a3)
        if np.isnan(m):
            # If Nan use flat estimate based on last speed observation
            # Create noisy hpr observations at obs_index_save
            hp_required_obs = [random.gauss(0, self.var_re / 2) +
                               hp_required_vec[obs_index_save[i]] for i in range(0, len(obs_index_save))]
            self.hp_required_obs = hp_required_obs
            # TODO: ADD HPR PRIOR DATA HERE (AT END)
        else:
            # If Not Nan use Linear Regression Slope
            b = hp_required_obs_end_mean - m * obs_index_hpr_end_mean
            speed_values_end = temp3
            # Create hpr values
            y = [b + m * speed_values_end[i] for i in range(0, len(speed_values_end))]
            # Create noisy hpr observations at obs_index
            hp_required_obs = [random.gauss(0, self.var_re / 2) +
                               hp_required_vec[obs_index[i]] for i in range(0, len(obs_index))]
            # Create noisy hpr observations at obs_index_hpr_end
            hp_required_obs_add = [random.gauss(0, self.var_re / 2) +
                                   y[i] for i in range(0, len(speed_values_end))]
            # print(len(hp_required_obs))
            # Append end observations to the rest of the observations
            hp_required_obs = np.concatenate((hp_required_obs, hp_required_obs_add))
            self.hp_required_obs = hp_required_obs

        hp_convert = 0.0000565
        # TODO: Change HP convert by using slug/ft^3 format in air density
        # Save CP Equivalent
        # self.cp_required_obs = [hp_el / ((self.rho * math.pi * pow(self.radius, 2) * pow(V_TIP[i], 3))
        #                                  / 550.0) for i, hp_el in enumerate(self.hp_required_obs)]
        # self.cp_available_obs = [hpa_el / ((self.rho * math.pi * pow(self.radius, 2) * pow(V_TIP[i], 3)) / 550.0)
        #                          for i, hpa_el in enumerate(self.hp_available_obs)]
        self.mu = [(element * 1.689) / V_TIP[i] for i, element in enumerate(self.speed_obs)]  # Speed must be ft/s
        self.v_tip = V_TIP

    def get_observation_data(self):

        data = {'Speed': self.speed_obs,
                'Mu': self.mu,
                'HP Required': self.hp_required_obs,
                'HP Available': self.hp_available_obs,
                'CP Required': self.cp_required_obs,
                'CP Available': self.cp_available_obs,
                'Num Obs': self.num_obs,
                'V_TIP': self.v_tip
                }

        return data
