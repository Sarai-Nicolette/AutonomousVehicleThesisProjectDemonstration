import random
from statistics import mean
import numpy as np
import pandas as pd
import os


class GeneratePowerObsFromScenario:

    def __init__(self, actual_rc_data, ms_bool, rotor_info,
                 rotor_data, scenario_filename, var_re, var_av, isSgp):
        self.actual_rc_data = actual_rc_data

        # Complex Model
        self.rotor_info = rotor_info
        self.rotor_data = rotor_data
        self.weight = float(self.rotor_info["rotorcraft_init"]["weight"]) * 32.17
        self.rho = float(self.rotor_info["rotorcraft_init"]["rho"])
        self.radius = float(self.rotor_info["rotorcraft_init"]["radius"])
        self.v_tip = rotor_data['Vtip'].values.tolist()
        self.cd0 = float(self.rotor_info["rotorcraft_init"]["cd0"])
        self.isSgp = isSgp

        self.num_obs = 0  # Number of observations
        self.max_speed = self.rotor_info["rotorcraft_init"]["maxAirspeed"]
        self.mms_bool = ms_bool  # depreciated
        self.var_re = var_re  # Variance of HP Required Data
        self.var_av = var_av  # Variance of HP Available Data
        self.filename = scenario_filename
        self.file_path_name = os.getcwd() + "/Data/" + self.filename
        self.time_factor = 0
        self.speed_obs = []
        self.hp_required_obs = []
        self.hp_available_obs = []
        self.cp_required_obs = []
        self.__read_scenario_and_generate_pow()

    def __read_scenario_and_generate_pow(self):
        # Set Random Seed
        random.seed(20)

        # READ IN SCENARIO DATA
        sheet_name = 'Sheet1'
        data = pd.read_excel(self.file_path_name, sheet_name=sheet_name)
        speed_obs = data['Vx'].tolist()

        # speed_obs = speed_obs[0:102]
        self.num_obs = len(speed_obs)

        self.speed_obs = [round(speed) for speed in speed_obs]  # input for observation generation

        # Get index of equal segments of observations
        speed_vec = self.actual_rc_data['Speed']
        obs_index = [np.argmin(np.abs(np.array(speed_vec) - speed_obs[i])) for i in range(0, len(speed_obs))]

        hp_required_vec = self.actual_rc_data['HP Required']
        hp_available_vec = self.actual_rc_data['HP Available']

        ################################################################################################################
        # Create Noisy HPA Observations
        self.hp_available_obs = [random.gauss(0, self.var_av / 2) +
                                 hp_available_vec[self.speed_obs[i]] for i in range(0, len(self.speed_obs))]

        if self.isSgp:
            ############################################################################################################
            # Adds observations before and after power chart to smooth out prediction by data duplication
            # Edit: Changed to 50 based on mobility metric study
            # TODO: Automatically detect the num obs added for full speed
            num_obs_added = 0  # int(len(obs_index) * 0.05)  # Number added to each side
            # Add speed index at start and end

            # save divisions
            self.time_factor = 500
            div = []
            speed_temp = speed_obs[0]
            for i in range(0, self.time_factor):
                div.append(speed_temp)
                speed_temp = speed_temp - 0.06
            temp1 = np.flip(div)

            temp2 = np.concatenate((temp1, self.speed_obs))
            max_value = self.max_speed
            added_value = 1
            temp3 = [max_value + added_value * (i + 1) for i in range(0, num_obs_added)]  # Adds speed to right part

            # Complete New Speed Observations
            self.speed_obs = np.concatenate((temp2, temp3))
            obs_index = [np.argmin(np.abs(np.array(speed_vec) - self.speed_obs[i])) for i in
                         range(0, len(self.speed_obs))]
            self.num_obs = len(self.speed_obs)

            # Save the index of each speed as int (Limit bounds of speed for VTIP equivalent values)
            speed_int = []
            for s in self.speed_obs:
                if s < 0:
                    speed_int.append(0)
                elif s > int(self.rotor_info["rotorcraft_init"]["maxAirspeed"]) - 1:
                    speed_int.append(int(self.rotor_info["rotorcraft_init"]["maxAirspeed"]) - 1)
                else:
                    speed_int.append(int(s))

            # Create Noisy HPA Observations
            # Use End Values to generate flat noisy data on either end to support estimate #############################
            self.hp_available_obs = [random.gauss(0, self.var_av / 2) +
                                     hp_available_vec[obs_index[i]] for i in range(0, len(obs_index))]

            # Ensure hp required estimate has sloped observations on right side ########################################
            # Create Noisy HPR Observations
            # Get the number of observations at the end by dividing the num_obs_added by 2
            num_obs_hpr_end = num_obs_added
            # Save a vector of the last 3% of actual speed data obs_index_hpr_end
            # TODO: May want to change to getting values above a certain speed
            temp = int(max(obs_index[0:len(obs_index) - num_obs_hpr_end]) -
                       round(
                           max(obs_index[0:len(obs_index) - num_obs_hpr_end]) * 0.05))  # Get last ~5% of speed/x values
            # # temp = int(max(obs_index[0:len(obs_index) - num_obs_hpr_end]) - 7)
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

    def get_observation_data(self):

        data = {'Speed': self.speed_obs,
                'HP Required': self.hp_required_obs,
                'HP Available': self.hp_available_obs,
                'CP': self.cp_required_obs,
                'Num Obs': self.num_obs,
                'V_TIP': self.v_tip
                }

        return data, self.time_factor
