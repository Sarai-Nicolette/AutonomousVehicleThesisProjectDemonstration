import statistics
import numpy as np
import csv


class GenerateMissionMobilityMetrics:

    def __init__(self, mission_rotor_data, rotor_info):

        self.mission_rotor_data = mission_rotor_data
        self.speed = mission_rotor_data['Speed']
        self.rotor_info = rotor_info
        self.generate_mmm()

    def generate_mmm(self):

        # Bucket Speed

        hprmin_actual = min(self.mission_rotor_data['HP Required'])
        ihprmin_actual = self.mission_rotor_data['HP Required'].index(hprmin_actual)
        speedminhpr_actual = self.speed[ihprmin_actual]

        ################################################################################################################
        ################################################################################################################

        # Max Speed

        inter = 26  # Small value that captures discrete intersection 26 # DO NOT CHANGE
        # Actual
        # Find all intersections and only save the one with the largest speed value
        inter_temp = inter
        # mask = np.abs(
        #     np.array(self.actual_rc_data['HP Required']) - np.array(self.actual_rc_data['HP Available'])) < inter
        while True:
            mask = np.abs(
                np.array(self.mission_rotor_data['HP Required']) - np.array(
                    self.mission_rotor_data['HP Available'])) < inter_temp
            # print(np.abs(np.array(self.hpr_prediction_multi[i]) - np.array(self.hpa_prediction_multi[i])))
            # print(mask)
            inter_temp = inter_temp + 1
            # print(inter_temp)
            if mask.any():
                break

        speed_inter = np.array(self.speed)[mask]
        ihprmax_actual = max(speed_inter)
        hprmax_actual = self.mission_rotor_data['HP Required'][ihprmax_actual]
        speedmaxhpr_actual = self.speed[ihprmax_actual]

        ################################################################################################################
        ################################################################################################################

        # Max Range

        weightfuel = float(self.rotor_info['rotorcraft_init']['weightfuel'])
        sfc = float(self.rotor_info['rotorcraft_init']['sfc'])

        # Actual
        temp = []
        for i in range(0, len(self.mission_rotor_data['HP Required'])):
            if self.speed[i] != 0:
                temp.append(self.mission_rotor_data['HP Required'][i] / self.speed[i])
            else:
                temp.append(self.mission_rotor_data['HP Required'][1] / self.speed[1])
        hprmax_range_actual_del = min(temp)
        ihprmax_range_actual = temp.index(hprmax_range_actual_del)
        speedmax_range_actual = self.speed[ihprmax_range_actual]

        # Checks whether Max Range Exceeds Max Speed. Max Speed limits Max Range.
        if speedmaxhpr_actual > speedmax_range_actual:
            hprmax_range_actual = self.mission_rotor_data['HP Required'][ihprmax_range_actual]
        else:
            hprmax_range_actual = hprmax_actual
            speedmax_range_actual = speedmaxhpr_actual

        max_range_actual = ((speedmax_range_actual * 3600.0 * weightfuel) / (sfc * hprmax_range_actual)) / 5280.0
        speedmax_range_actual = speedmax_range_actual

        ################################################################################################################
        ################################################################################################################

        # Max Endurance

        # Actual
        endurance_actual = weightfuel / (sfc * hprmin_actual)

        ################################################################################################################
        ################################################################################################################

        # Max ROC HOV
        weight = float(self.rotor_info['rotorcraft_init']['weight'])
        ff_index = self.speed.index(speedminhpr_actual)

        # Actual
        vrochov_actual = 60 * 550 * 2 * (self.mission_rotor_data['HP Available'][0] -
                                         self.mission_rotor_data['HP Required'][0]) / weight
        vrocff_actual = 60 * 550 * (self.mission_rotor_data['HP Available'][ff_index] - hprmin_actual) / weight

        # Save Data to Dictionary

        mission_metrics = {'Bucket HPR Actual': hprmin_actual,
                           'Bucket Speed Actual': speedminhpr_actual,
                           'Max HPR Actual': hprmax_actual,
                           'Max Speed Actual': speedmaxhpr_actual,
                           'Max Range HPR Actual': hprmax_range_actual,
                           'Max Range Speed Actual': speedmax_range_actual,
                           'Max Range Actual': max_range_actual,
                           'Max Endurance Actual': endurance_actual,
                           'Max Climb HOV Actual': vrochov_actual,
                           'Max Climb FF Actual': vrocff_actual
                           }

        return mission_metrics
