# Outputs Speed Array, Horse Power Required Array, Horse Power Available
import math


class GeneratePowerCurveData:
    def __init__(self, rotor_info, rotor_data):

        # Simple Model
        if rotor_info["rotorcraft_init"]["model_type"] == "simple":
            self.rotor_info = rotor_info
            self.rotor_data = []
            self.weight = float(self.rotor_info["rotorcraft_init"]["weight"])
            self.rho = float(self.rotor_info["rotorcraft_init"]["rho"])
            self.radius = float(self.rotor_info["rotorcraft_init"]["radius"])
            self.v_tip = float(self.rotor_info["rotorcraft_init"]["v_tip"])
            self.cd0 = float(self.rotor_info["rotorcraft_init"]["cd0"])

        else:
            # Complex Model
            self.rotor_info = rotor_info
            self.rotor_data = rotor_data
            self.hpa_source = rotor_data['HPA'].values.tolist()
            self.weight = float(self.rotor_info["rotorcraft_init"]["weight"])
            self.rho = float(self.rotor_info["rotorcraft_init"]["rho"])
            self.radius = float(self.rotor_info["rotorcraft_init"]["radius"])
            self.v_tip = rotor_data['Vtip'].values.tolist()
            self.cd0 = float(self.rotor_info["rotorcraft_init"]["cd0"])

        self.speed = []
        self.speed_knots = []
        self.hp_required = []
        self.hp_available = []
        self.cp = []
        self.cpa = []
        self.mu = []
        self.hp_induced = []
        self.hp_profile = []
        self.hp_para = []

        self.hp_required_act = rotor_data['HPR'].values.tolist()
        self.hp_available_act = rotor_data['HPA'].values.tolist()
        self.cp_act = []
        self.cpa_act = []
        self.hp_induced_act = []
        self.hp_profile_act = rotor_data['HPPr'].values.tolist()
        self.hp_para_act = []

        self.theoretical_rotor_data = False
        self.get_speed_array()
        self.__calculate_hp_required()

    def get_speed_array(self):
        max_speed = self.rotor_info["rotorcraft_init"]["maxAirspeed"]

        if self.rotor_info["rotorcraft_init"]["model_type"] == "simple":
            # Divides Speed Data At Each Knot
            speed_array = list(range(0, round(float(max_speed) * 1.689)))
            # print(len(speed_array))
            # print(speed_array)
            # multiple = 2
            # speed_array = [speed/multiple for speed in range(0, len(multiple*speed_array))]
            # print(len(speed_array))
            # print(speed_array)
            self.speed = speed_array
            self.speed_knots = [(speed / 1.689) for speed in speed_array]

            # Change in Test Points
            self.speed_knots = self.speed_knots
            # print(len(self.speed_knots[0::2]))
            self.speed = speed_array
        else:
            ############################################################################################################
            # Complex Model
            self.speed_knots = [i for i in range(int(max_speed))]
            self.speed = [(speed * 1.689) for speed in self.speed_knots]  # to ft/sec

        return self.speed

    def __calculate_inflow_velocity(self):

        # Simple Model
        ################################################################################################################
        if self.rotor_info["rotorcraft_init"]["model_type"] == "simple":
            # Get Advanced Ratio
            mu = [element / self.v_tip for element in self.speed]
            # Get Coefficient of Thrust
            self.ct = self.weight / (self.rho * math.pi * pow(self.radius, 2)
                                     * pow(self.v_tip, 2))  # Coefficient of Thrust

            lambda_i = [element * 0 for element in list(range(0, len(mu)))]
            for i, mu_element in enumerate(mu):
                if i == 0:
                    lambda_i_try = math.sqrt(self.ct / 2)  # Lambda in hover assumed at first step

                else:
                    lambda_i_try = lambda_i[i - 1]  # Use previous Lambda for next calculation

                k = 0
                while k < 30:
                    k += 1
                    f = lambda_i_try - 0.5 * self.ct / math.sqrt(pow(mu_element, 2) + pow(lambda_i_try, 2))
                    f_prime = (1 + 0.5 * self.ct * lambda_i_try) / pow((pow(mu_element, 2) + pow(lambda_i_try, 2)), 1.5)
                    lambda_i_try = lambda_i_try - f / f_prime

                lambda_i[i] = lambda_i_try  # Set the calculated lambda_i
        else:
            ############################################################################################################
            # Complex Model
            # Get Coefficient of Thrust
            # print(self.v_tip)
            # print(self.speed)
            self.ct = [(self.weight / (self.rho * math.pi * pow(self.radius, 2)
                                       * pow(self.v_tip[i], 2))) for i, s in enumerate(self.speed)]
            # Get Advanced Ratio
            mu = [element / self.v_tip[i] for i, element in enumerate(self.speed)]

            lambda_i = [element * 0 for element in list(range(0, len(mu)))]
            for i, mu_element in enumerate(mu):
                if i == 0:
                    lambda_i_try = math.sqrt(self.ct[i] / 2)  # Lambda in hover assumed at first step

                else:
                    lambda_i_try = lambda_i[i - 1]  # Use previous Lambda for next calculation

                k = 0
                while k < 30:
                    k += 1
                    f = lambda_i_try - 0.5 * self.ct[i] / math.sqrt(pow(mu_element, 2) + pow(lambda_i_try, 2))
                    f_prime = (1 + 0.5 * self.ct[i] * lambda_i_try) / pow((pow(mu_element, 2) + pow(lambda_i_try, 2)),
                                                                          1.5)
                    lambda_i_try = lambda_i_try - f / f_prime

                lambda_i[i] = lambda_i_try  # Set the calculated lambda_i

        return [lambda_i, mu]

    def __calculate_hp_required(self):

        # Simple Model
        ################################################################################################################
        if self.rotor_info["rotorcraft_init"]["model_type"] == "simple":
            # Vars
            n_blades = float(self.rotor_info["rotorcraft_init"]["n_blades"])
            chord = float(self.rotor_info["rotorcraft_init"]["chord"])
            flat = float(self.rotor_info["rotorcraft_init"]["flat"])
            hpa = float(self.rotor_info["rotorcraft_init"]["hpa"])

            # Calculate inflow velocity and Advanced Ratio
            [lambda_i, mu] = self.__calculate_inflow_velocity()

            # Calculate Solidity
            sigma = n_blades * chord / (math.pi * self.radius)

            # Calculate non-dimensional power term
            cp = [self.ct * lam + sigma *
                  self.cd0 * (1 + 4.6 * pow(mu[k], 2))
                  / 8 + 0.5 * pow(mu[k], 3) * flat /
                  (math.pi * pow(self.radius, 2))
                  for k, lam in enumerate(lambda_i)]

            hp_convert = 0.0000565
            # Calculate hp_required
            self.hp_required = [(self.rho * math.pi * pow(self.radius, 2) * pow(self.v_tip, 3)) * cp_el / 550.0 for
                                cp_el in
                                cp]

            # Calculate hp_available
            self.hp_available = [hpa for _ in list(range(0, len(self.hp_required)))]

            # Calculate hp_induced
            self.hp_induced = [((self.rho * math.pi * pow(self.radius, 2) * pow(self.v_tip, 3)) * self.ct * lambda_i[i])
                               / 550.0 for i, cp_el in enumerate(cp)]
            # Calculate hp_profile
            self.hp_profile = [((self.rho * math.pi * pow(self.radius, 2) * pow(self.v_tip, 3)) * sigma * self.cd0 *
                                (1 + 4.6 * pow(mu[i], 2)) / 8) / 550.0 for i, cp_el in enumerate(cp)]
            # Calculate hp_parasite
            self.hp_para = [((self.rho * math.pi * pow(self.radius, 2) * pow(self.v_tip, 3)) * (0.5 * pow(mu[i], 3) *
                                                                                                flat) / (
                                     math.pi * pow(self.radius, 2))) / 550.0 for i, cp_el in enumerate(cp)]

            # For completeness
            self.mu = mu
            self.cp = cp
            self.cpa = [hpa_el / ((self.rho * math.pi * pow(self.radius, 2) * pow(self.v_tip, 3)) * hp_convert)
                        for i, hpa_el in enumerate(self.hp_available)]

        else:
            ############################################################################################################
            # Complex Model
            # Vars
            n_blades = float(self.rotor_info["rotorcraft_init"]["n_blades"])
            chord = float(self.rotor_info["rotorcraft_init"]["chord"])
            flat = self.rotor_data['Xflat'].values.tolist()
            # flat = [flat[-1] for f in flat]  # Sets flat to const
            # Calculate inflow velocity and Advanced Ratio
            [lambda_i, mu] = self.__calculate_inflow_velocity()

            # Calculate Solidity
            sigma = n_blades * chord / (math.pi * self.radius)

            # Calculate non-dimensional power term
            cp = [self.ct[k] * lam + sigma *
                  self.cd0 * (1 + 4.6 * pow(mu[k], 2))
                  / 8 + 0.5 * pow(mu[k], 3) * flat[k] /
                  (math.pi * pow(self.radius, 2))
                  for k, lam in enumerate(lambda_i)]

            # hp_convert = 0.0000565
            # Calculate hp_required
            self.hp_required = [((self.rho * math.pi * pow(self.radius, 2) * pow(self.v_tip[i], 3)) * cp_el) / 550.0
                                for i, cp_el in enumerate(cp)]
            self.cp = [
                self.hp_required[i] / (self.rho * math.pi * pow(self.radius, 2) * pow(self.v_tip[i], 3) / 550.0)
                for i, cp_el in enumerate(cp)]
            self.mu = mu

            # Calculate hp_induced
            self.hp_induced = [
                ((self.rho * math.pi * pow(self.radius, 2) * pow(self.v_tip[i], 3)) * self.ct[i] * lambda_i[i])
                / 550.0 for i, cp_el in enumerate(cp)]
            # Calculate hp_profile
            self.hp_profile = [((self.rho * math.pi * pow(self.radius, 2) * pow(self.v_tip[i], 3)) * sigma * self.cd0 *
                                (1 + 4.6 * pow(mu[i], 2)) / 8) / 550.0 for i, cp_el in enumerate(cp)]
            # Calculate hp_parasite
            self.hp_para = [((self.rho * math.pi * pow(self.radius, 2) * pow(self.v_tip[i], 3)) * (0.5 * pow(mu[i], 3) *
                                                                                                   flat[i]) / (
                                     math.pi * pow(self.radius, 2))) / 550.0 for i, cp_el in enumerate(cp)]

            self.hp_available = self.hpa_source
            self.cpa = [hpa_el / ((self.rho * math.pi * pow(self.radius, 2) * pow(self.v_tip[i], 3)) / 550.0)
                        for i, hpa_el in enumerate(self.hp_available)]

            ############################################################################################################
            # if not self.theoretical_rotor_data:
            # Handle Alteration to Actual Values
            self.cp_act = [self.hp_required_act[i] / (self.rho * math.pi * pow(self.radius, 2) * pow(self.v_tip[i], 3) /
                                                      550.0)
                           for i, cp_el in enumerate(cp)]
            self.cpa_act = [hpa_el / ((self.rho * math.pi * pow(self.radius, 2) * pow(self.v_tip[i], 3)) / 550.0)
                            for i, hpa_el in enumerate(self.hp_available_act)]

            self.hp_induced_act = [self.rotor_data['HPI'][i] - self.hp_para[i] for i, cp_el in enumerate(cp)]
            self.hp_para_act = [self.hp_required_act[i] - self.hp_induced_act[i] - self.hp_profile_act[i] for i, cp_el
                                in enumerate(cp)]

        return [self.hp_required, self.hp_induced, self.hp_profile, self.hp_para, self.hp_available]

    # def get_org_data_output(self):
    #     # Outputs data from rotorcraft source instead of recalculated value
    #     data = {'Speed': self.rotor_data['Speed'],
    #             'HP Required': self.rotor_data['HPR'],
    #             'HP Available': self.rotor_data['HPA'],
    #             'HP Induced': self.hp_induced_act,
    #             'HP Profile': None,
    #             'HP Parasite': None,
    #             'CP Required': [
    #             self.rotor_data['HPR'][i] / (self.rho * math.pi * pow(self.radius, 2) * pow(self.v_tip[i], 3) / 550.0)
    #             for i, cp_el in enumerate(self.rotor_data['HPR'])],
    #             'CP Available': [hpa_el / ((self.rho * math.pi * pow(self.radius, 2) * pow(self.v_tip[i], 3)) / 550.0)
    #                              for i, hpa_el in enumerate(self.rotor_data['HPA'])],
    #             'Mu': self.mu
    #             }
    #
    #     return data
    def get_data_output(self):

        if self.theoretical_rotor_data:
            # Uses Regenerated Results Using Momentum Theory
            data = {'Speed': self.speed_knots,
                    'HP Required': self.hp_required,
                    'HP Available': self.hp_available,
                    'HP Induced': self.hp_induced,
                    'HP Profile': self.hp_profile,
                    'HP Parasite': self.hp_para,
                    'CP Required': self.cp,
                    'CP Available': self.cpa,
                    'Mu': self.mu
                    }
        else:
            # Mainly Uses Data From Modular Rotorcraft
            data = {'Speed': self.speed_knots,
                    'HP Required': self.hp_required_act,
                    'HP Available': self.hp_available_act,
                    'HP Induced': self.hp_induced_act,
                    'HP Profile': self.hp_profile_act,
                    'HP Parasite': self.hp_para_act,
                    'CP Required': self.cp_act,
                    'CP Available': self.cpa_act,
                    'Mu': self.mu
                    }

        return data
