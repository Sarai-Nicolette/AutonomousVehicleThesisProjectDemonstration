import statistics
import numpy as np


class GenerateMobilityMetrics:

    def __init__(self, actual_rc_data, rotor_obs_data, gp_pred_rotor_data, rotor_info):
        self.old_actual = actual_rc_data
        self.actual_rc_data = actual_rc_data  ###
        self.speed = actual_rc_data['Speed']  ###
        self.speed_act = self.speed

        # # TODO: Multi edits required for speed range detection issue 11/13/23
        # # For test point array, find the closest speed in actual speed
        # for speed in gp_pred_rotor_data['Testing Points X']:
        #     index = self.find_closest_index(actual_rc_data['Speed'], speed)
        #     self.speed_act.append(actual_rc_data['Speed'][index])
        #
        # # print(len([self.actual_rc_data['HP Required'][i] for i in self.speed_act]))
        # self.actual_rc_data = {'Speed': [actual_rc_data['Speed'][i] for i in self.speed_act],
        #             'HP Required': [actual_rc_data['HP Required'][i] for i in self.speed_act],
        #             'HP Available': [actual_rc_data['HP Available'][i] for i in self.speed_act],
        #             'HP Induced': [actual_rc_data['HP Induced'][i] for i in self.speed_act],
        #             'HP Profile': [actual_rc_data['HP Profile'][i] for i in self.speed_act],
        #             'HP Parasite': [actual_rc_data['HP Parasite'][i] for i in self.speed_act],
        #             'CP Required': [actual_rc_data['CP Required'][i] for i in self.speed_act],
        #             'CP Available': [actual_rc_data['CP Available'][i] for i in self.speed_act],
        #             'Mu': [actual_rc_data['Mu'][i] for i in self.speed_act],
        #             }
        #
        # # Save speed as indexes
        # self.speed = [i for i in range(0, len(gp_pred_rotor_data['Testing Points X']))]  # get test point indexes

        self.rotor_obs_data = rotor_obs_data
        self.rotor_info = rotor_info
        self.hpr_lower_bound = gp_pred_rotor_data['HPR Lower Bound'].tolist()
        self.hpr_upper_bound = gp_pred_rotor_data['HPR Upper Bound'].tolist()
        self.hpr_prediction = gp_pred_rotor_data['HPR Prediction'].tolist()
        self.hpa_lower_bound = gp_pred_rotor_data['HPA Lower Bound'].tolist()
        self.hpa_upper_bound = gp_pred_rotor_data['HPA Upper Bound'].tolist()
        self.hpa_prediction = gp_pred_rotor_data['HPA Prediction'].tolist()
        self.hpr_prediction_multi = gp_pred_rotor_data['HPR Prediction Multi']
        self.hpa_prediction_multi = gp_pred_rotor_data['HPA Prediction Multi']
        self.data = None
        self.data_perr = None
        self.data_est = None
        self.data_up_est = None
        self.data_low_est = None
        self.bucket_speed = None
        self.max_speed = None
        self.max_range = None
        self.max_endurance = None
        self.max_climb = None
        self.bucket_speed_multi = None
        self.max_speed_multi = None
        self.max_range_multi = None
        self.max_endurance_multi = None
        self.max_climb_multi = None
        self.__generate_bucket_speed_data()
        self.__generate_max_speed_data()
        self.__generate_max_range_data()
        self.__generate_endurance_data()
        self.__generate_max_climb()

    def __generate_bucket_speed_data(self):

        # s = 1.689
        # Lower Bound
        hprmin_gp_lowbound = min(self.hpr_lower_bound)
        ihprmin_gp_lowbound = self.hpr_lower_bound.index(hprmin_gp_lowbound)
        speedminhpr_gp_lowbound = self.speed_act[ihprmin_gp_lowbound]

        # Upper Bound
        hprmin_gp_upbound = min(self.hpr_upper_bound)
        ihprmin_gp_upbound = self.hpr_upper_bound.index(hprmin_gp_upbound)
        speedminhpr_gp_upbound = self.speed_act[ihprmin_gp_upbound]

        # Actual
        hprmin_actual = min(self.actual_rc_data['HP Required'])
        ihprmin_actual = self.actual_rc_data['HP Required'].index(hprmin_actual)
        speedminhpr_actual = self.speed[ihprmin_actual]
        # print('HP Act len', len(self.actual_rc_data['HP Required']))
        # print('Min HPR Actual', hprmin_actual)
        # print('Actual Bucket Speed', speedminhpr_actual)
        # print('Actual Bucket Index', ihprmin_actual)
        # print(self.actual_rc_data['HP Required'])

        # Prediction
        # get location of minimum
        # i_min = self.hpr_prediction.index(min(self.hpr_prediction))
        hprmin_pred = min(self.hpr_prediction)
        # hprmin_pred = self.hpr_prediction[i_min]
        ihprmin_pred = self.hpr_prediction.index(hprmin_pred)
        speedminhpr_pred = self.speed_act[ihprmin_pred]  #  i_min  #
        # print('HP Pred len', len(self.hpr_prediction))
        # print('Min HPR Pred', hprmin_pred)
        # print('Pred Bucket Speed', speedminhpr_pred)
        # print('Pred Bucket Index', ihprmin_pred)
        # print(self.hpr_prediction)

        # # Error
        # hprmin_error = self.__rmse(hprmin_actual, hprmin_pred)
        # speedminhpr_error = self.__rmse(speedminhpr_actual, speedminhpr_pred)
        #
        # # Percent Error
        # hprmin_perr = self.__perr(hprmin_actual, hprmin_pred)
        # speedminhpr_perr = self.__perr(speedminhpr_actual, speedminhpr_pred)

        # Error
        hprmin_error = self.__rmse(hprmin_actual, hprmin_pred)
        if speedminhpr_pred == 0:
            speedminhpr_error = 99
        else:
            speedminhpr_error = self.__rmse(speedminhpr_actual, speedminhpr_pred)

        # Percent Error
        hprmin_perr = self.__perr(hprmin_actual, hprmin_pred)
        try:
            speedminhpr_perr = self.__perr(speedminhpr_actual, speedminhpr_pred)
        except ZeroDivisionError:
            speedminhpr_perr = 100

        self.bucket_speed = {'Bucket HPR LB': hprmin_gp_lowbound,
                             'Bucket Speed LB': speedminhpr_gp_lowbound,
                             'Bucket HPR UB': hprmin_gp_upbound,
                             'Bucket Speed UB': speedminhpr_gp_upbound,
                             'Bucket HPR Actual': hprmin_actual,
                             'Bucket Speed Actual': speedminhpr_actual,
                             'Bucket HPR Pred': hprmin_pred,
                             'Bucket Speed Pred': speedminhpr_pred,
                             'Bucket HPR Error': hprmin_error,
                             'Bucket Speed Error': speedminhpr_error,
                             'Bucket HPR % Error': hprmin_perr,
                             'Bucket Speed % Error': speedminhpr_perr}

        ################################################################################################################
        # Bucket Speed Multi - Uses multiple outputs instead of bounds for pdf
        # Bounds
        bounds_temp = []
        bounds_speed_temp = []
        # Loop through each HPR and HPA instance
        for i in range(0, len(self.hpr_prediction_multi)):
            bounds_temp.append(min(self.hpr_prediction_multi[i]))
            ihprmin_gp_bound = self.hpr_prediction_multi[i].tolist().index(bounds_temp[i])
            bounds_speed_temp.append(self.speed[ihprmin_gp_bound])

        hprmin_gp_lowbound = min(bounds_temp)
        speedminhpr_gp_lowbound = min(bounds_speed_temp)
        hprmin_gp_upbound = max(bounds_temp)
        speedminhpr_gp_upbound = max(bounds_speed_temp)
        hprmin_pred = statistics.mean(bounds_temp)
        speedminhpr_pred = statistics.mean(bounds_speed_temp)
        self.bucket_speed_multi = {'Bucket HPR LB': hprmin_gp_lowbound,
                                   'Bucket Speed LB': speedminhpr_gp_lowbound,
                                   'Bucket HPR UB': hprmin_gp_upbound,
                                   'Bucket Speed UB': speedminhpr_gp_upbound,
                                   'Bucket HPR Pred': hprmin_pred,
                                   'Bucket Speed Pred': speedminhpr_pred}
        ################################################################################################################

    def __generate_max_speed_data(self):

        # s = 1.689
        inter = 26  # Small value that captures discrete intersection 26 # DO NOT CHANGE
        # Lower Bound (Upper?)
        # Find all intersections and only save the one with the largest speed value
        inter_temp = inter
        # mask = np.abs(np.array(self.hpr_lower_bound) - np.array(self.hpa_upper_bound)) < inter
        while True:
            mask = np.abs(
                np.array(self.hpr_lower_bound) - np.array(self.hpa_upper_bound)) < inter_temp
            # print(np.abs(np.array(self.hpr_prediction_multi[i]) - np.array(self.hpa_prediction_multi[i])))
            # print(mask)
            inter_temp = inter_temp + 1
            # print(inter_temp)
            if mask.any():
                break


        speed_inter = np.array(self.speed_act)[mask]
        ihprmax_gp_lowbound = max(speed_inter)
        # pos_temp = [abs(self.hpr_lower_bound[i] - self.hpa_upper_bound[i])
        #             for i in range(0, len(self.hpr_lower_bound))]
        # hprmax_gp_lowbound_del = min(pos_temp)
        # ihprmax_gp_lowbound = pos_temp.index(hprmax_gp_lowbound_del)

        # Find test point index where speed = ihprmax_gp_lowbound

        hprmax_gp_lowbound = self.hpr_lower_bound[ihprmax_gp_lowbound]
        speedmaxhpr_gp_lowbound = self.speed_act[ihprmax_gp_lowbound]


        # Upper Bound (Lower?)
        # Find all intersections and only save the one with the largest speed value
        inter_temp = inter
        # mask = np.abs(np.array(self.hpr_upper_bound) - np.array(self.hpa_lower_bound)) < inter
        while True:
            mask = np.abs(
                np.array(self.hpr_upper_bound) - np.array(self.hpa_lower_bound)) < inter_temp
            # print(np.abs(np.array(self.hpr_prediction_multi[i]) - np.array(self.hpa_prediction_multi[i])))
            # print(mask)
            inter_temp = inter_temp + 1
            # print(inter_temp)
            if mask.any():
                break

        speed_inter = np.array(self.speed_act)[mask]
        ihprmax_gp_upbound = max(speed_inter)
        # pos_temp = [abs(self.hpr_upper_bound[i] - self.hpa_lower_bound[i])
        #             for i in range(0, len(self.hpr_upper_bound))]
        # hprmax_gp_upbound_del = min(pos_temp)
        # ihprmax_gp_upbound = pos_temp.index(hprmax_gp_upbound_del)
        hprmax_gp_upbound = self.hpr_upper_bound[ihprmax_gp_upbound]
        speedmaxhpr_gp_upbound = self.speed_act[ihprmax_gp_upbound]

        # Actual
        # Find all intersections and only save the one with the largest speed value
        inter_temp = inter
        # mask = np.abs(
        #     np.array(self.actual_rc_data['HP Required']) - np.array(self.actual_rc_data['HP Available'])) < inter
        while True:
            mask = np.abs(
                np.array(self.actual_rc_data['HP Required']) - np.array(self.actual_rc_data['HP Available'])) < inter_temp
            # print(np.abs(np.array(self.hpr_prediction_multi[i]) - np.array(self.hpa_prediction_multi[i])))
            # print(mask)
            inter_temp = inter_temp + 1
            # print(inter_temp)
            if mask.any():
                break

        speed_inter = np.array(self.speed_act)[mask]
        ihprmax_actual = max(speed_inter)



        # pos_temp = [abs(self.actual_rc_data['HP Required'][i] - self.actual_rc_data['HP Available'][i])
        #             for i in range(0, len(self.actual_rc_data['HP Required']))]
        # hprmax_actual_del = min(pos_temp)
        # ihprmax_actual = pos_temp.index(hprmax_actual_del)
        hprmax_actual = self.actual_rc_data['HP Required'][ihprmax_actual]
        speedmaxhpr_actual = self.speed_act[ihprmax_actual]
        # print(speedmaxhpr_actual)

        # Prediction
        # Find all intersections and only save the one with the largest speed value
        inter_temp = inter
        # mask = np.abs(np.array(self.hpr_prediction) - np.array(self.hpa_prediction)) < inter
        while True:
            mask = np.abs(
                np.array(self.hpr_prediction) - np.array(self.hpa_prediction)) < inter_temp
            # print(np.abs(np.array(self.hpr_prediction_multi[i]) - np.array(self.hpa_prediction_multi[i])))
            #print(mask)
            inter_temp = inter_temp + 1
            # print(inter_temp)
            if mask.any():
                break
        speed_inter = np.array(self.speed_act)[mask]
        ihprmax_pred = max(speed_inter)
        # pos_temp = [abs(self.hpr_prediction[i] - self.actual_rc_data['HP Available'][i])
        #             for i in range(0, len(self.actual_rc_data['HP Required']))]
        # hprmax_pred_del = min(pos_temp)
        # ihprmax_pred = pos_temp.index(hprmax_pred_del)
        hprmax_pred = self.hpr_prediction[ihprmax_pred]
        speedmaxhpr_pred = self.speed_act[ihprmax_pred]
        # print(speedmaxhpr_pred)

        # Error
        hprmax_error = self.__rmse(hprmax_actual, hprmax_pred)
        if speedmaxhpr_pred == 0:
            speedmaxhpr_error = 99
        else:
            speedmaxhpr_error = self.__rmse(speedmaxhpr_actual, speedmaxhpr_pred)

        # Percent Error
        hprmax_perr = self.__perr(hprmax_actual, hprmax_pred)
        # speedmaxhpr_perr = self.__perr(speedmaxhpr_actual, speedmaxhpr_pred)
        try:
            speedmaxhpr_perr = self.__perr(speedmaxhpr_actual, speedmaxhpr_pred)
        except ZeroDivisionError:
            speedmaxhpr_perr = 100

        self.max_speed = {'Max HPR LB': hprmax_gp_lowbound,
                          'Max Speed LB': speedmaxhpr_gp_lowbound,
                          'Max HPR UB': hprmax_gp_upbound,
                          'Max Speed UB': speedmaxhpr_gp_upbound,
                          'Max HPR Actual': hprmax_actual,
                          'Max Speed Actual': speedmaxhpr_actual,
                          'Max HPR Pred': hprmax_pred,
                          'Max Speed Pred': speedmaxhpr_pred,
                          'Max HPR Error': hprmax_error,
                          'Max Speed Error': speedmaxhpr_error,
                          'Max HPR % Error': hprmax_perr,
                          'Max Speed % Error': speedmaxhpr_perr}

        # ################################################################################################################
        # # Max Speed Multi - Uses multiple outputs instead of single instance bounds for pdf
        #
        # # Bounds
        # bounds_temp = []
        # bounds_speed_temp = []
        # # TODO: Change multi calc
        # # Loop through each HPR and HPA instance and find lowest and upper intersection
        # inter_temp = inter
        # for i in range(0, len(self.hpr_prediction_multi)):
        #     # Find all intersections and only save the one with the largest speed value
        #     while True:
        #         mask = np.abs(
        #             np.array(self.hpr_prediction_multi[i]) - np.array(self.hpa_prediction_multi[i])) < inter_temp
        #         # print(np.abs(np.array(self.hpr_prediction_multi[i]) - np.array(self.hpa_prediction_multi[i])))
        #         # print(mask)
        #         inter_temp = inter_temp + 1
        #         # print(inter_temp)
        #         if mask.any():
        #             break
        #
        #     speed_inter = np.array(self.old_actual['Speed'])[mask]
        #     ihprmax_gp = max(speed_inter)
        #     bounds_temp.append(self.hpr_prediction_multi[i][ihprmax_gp])
        #     bounds_speed_temp.append(self.old_actual['Speed'][ihprmax_gp])
        #     inter_temp = inter
        #
        # hprmax_gp_lowbound = min(bounds_temp)
        # speedmaxhpr_gp_lowbound = min(bounds_speed_temp)
        # hprmax_gp_upbound = max(bounds_temp)
        # speedmaxhpr_gp_upbound = max(bounds_speed_temp)
        # hprmax_pred = statistics.mean(bounds_temp)
        # speedmaxhpr_pred = statistics.mean(bounds_speed_temp)
        # self.max_speed_multi = {'Max HPR LB': hprmax_gp_lowbound,
        #                         'Max Speed LB': speedmaxhpr_gp_lowbound,
        #                         'Max HPR UB': hprmax_gp_upbound,
        #                         'Max Speed UB': speedmaxhpr_gp_upbound,
        #                         'Max HPR Pred': hprmax_pred,
        #                         'Max Speed Pred': speedmaxhpr_pred}

        ################################################################################################################

    def __generate_max_range_data(self):

        # s = 1.689
        weightfuel = float(self.rotor_info['rotorcraft_init']['weightfuel'])
        sfc = float(self.rotor_info['rotorcraft_init']['sfc'])

        # Lower Bound
        temp = []  # Smallest slope at each speed
        for i in range(0, len(self.hpr_lower_bound)):
            if self.speed_act[i] != 0:
                temp.append(self.hpr_lower_bound[i] / self.speed_act[i])
            else:
                temp.append(self.hpr_lower_bound[1] / self.speed_act[1])
        hprmax_range_gp_lowbound_del = min(temp)
        ihprmax_range_gp_lowbound = temp.index(hprmax_range_gp_lowbound_del)
        speedmax_range_gp_lowbound = self.speed_act[ihprmax_range_gp_lowbound]
        # Checks whether Max Range Exceeds Max Speed. Max Speed limits Max Range.
        if self.max_speed['Max Speed LB'] > speedmax_range_gp_lowbound:
            hprmax_range_gp_lowbound = self.hpr_lower_bound[ihprmax_range_gp_lowbound]
        else:
            hprmax_range_gp_lowbound = self.max_speed['Max HPR LB']
            speedmax_range_gp_lowbound = self.max_speed['Max Speed LB']

        max_range_lowbound = ((speedmax_range_gp_lowbound * 3600.0 * weightfuel) / (
                sfc * hprmax_range_gp_lowbound)) / 5280.0

        # Upper Bound
        temp = []
        for i in range(0, len(self.hpr_upper_bound)):
            if self.speed_act[i] != 0:
                temp.append(self.hpr_upper_bound[i] / self.speed_act[i])
            else:
                temp.append(self.hpr_upper_bound[1] / self.speed_act[1])
        hprmax_range_gp_upbound_del = min(temp)
        ihprmax_range_gp_upbound = temp.index(hprmax_range_gp_upbound_del)
        speedmax_range_gp_upbound = self.speed_act[ihprmax_range_gp_upbound]

        # Checks whether Max Range Exceeds Max Speed. Max Speed limits Max Range.
        if self.max_speed['Max Speed UB'] > speedmax_range_gp_upbound:
            hprmax_range_gp_upbound = self.hpr_upper_bound[ihprmax_range_gp_upbound]
        else:
            hprmax_range_gp_upbound = self.max_speed['Max HPR UB']
            speedmax_range_gp_upbound = self.max_speed['Max Speed UB']

        max_range_upbound = ((speedmax_range_gp_upbound * 3600.0 * weightfuel) / (
                sfc * hprmax_range_gp_upbound)) / 5280.0

        # Actual
        temp = []
        for i in range(0, len(self.actual_rc_data['HP Required'])):
            if self.speed_act[i] != 0:
                temp.append(self.actual_rc_data['HP Required'][i] / self.speed_act[i])
            else:
                temp.append(self.actual_rc_data['HP Required'][1] / self.speed_act[1])
        hprmax_range_actual_del = min(temp)
        ihprmax_range_actual = temp.index(hprmax_range_actual_del)
        speedmax_range_actual = self.speed_act[ihprmax_range_actual]

        # Checks whether Max Range Exceeds Max Speed. Max Speed limits Max Range.
        if self.max_speed['Max Speed Actual'] > speedmax_range_actual:
            hprmax_range_actual = self.actual_rc_data['HP Required'][ihprmax_range_actual]
        else:
            hprmax_range_actual = self.max_speed['Max HPR Actual']
            speedmax_range_actual = self.max_speed['Max Speed Actual']

        max_range_actual = ((speedmax_range_actual * 3600.0 * weightfuel) / (sfc * hprmax_range_actual)) / 5280.0
        speedmax_range_actual = speedmax_range_actual

        # Prediction
        temp = []
        for i in range(0, len(self.hpr_prediction)):
            if self.speed_act[i] != 0:
                temp.append(self.hpr_prediction[i] / self.speed_act[i])
            else:
                temp.append(self.hpr_prediction[1] / self.speed_act[1])
        hprmax_range_pred_del = min(temp)
        ihprmax_range_pred = temp.index(hprmax_range_pred_del)

        speedmax_range_pred = self.speed_act[ihprmax_range_pred]

        # Checks whether Max Range Exceeds Max Speed. Max Speed limits Max Range.
        # print('Max Speed', self.max_speed['Max Speed Pred'])
        # print('Max Range Speed', speedmax_range_pred)
        if self.max_speed['Max Speed Pred'] > speedmax_range_pred:
            hprmax_range_pred = self.hpr_prediction[ihprmax_range_pred]
        else:
            hprmax_range_pred = self.max_speed['Max HPR Pred']
            speedmax_range_pred = self.max_speed['Max Speed Pred']

        max_range_pred = ((speedmax_range_pred * 3600.0 * weightfuel) / (sfc * hprmax_range_pred)) / 5280.0
        speedmax_range_pred = speedmax_range_pred

        # print(speedmax_range_pred)

        # Error
        hprmax_range_error = self.__rmse(hprmax_range_actual, hprmax_range_pred)
        speedmaxhpr_range_error = self.__rmse(speedmax_range_actual, speedmax_range_pred)
        max_range_error = self.__rmse(max_range_actual, max_range_pred)

        # Percent Error
        hprmax_range_perr = self.__perr(hprmax_range_actual, hprmax_range_pred)
        if speedmax_range_pred == 0:
            speedmaxhpr_range_perr = 99
        else:
            speedmaxhpr_range_perr = self.__perr(speedmax_range_actual, speedmax_range_pred)
        if max_range_pred == 0:
            max_range_perr = 99
        else:
            max_range_perr = self.__perr(max_range_actual, max_range_pred)

        self.max_range = {'Max Range HPR LB': hprmax_range_gp_lowbound,
                          'Max Range Speed LB': speedmax_range_gp_lowbound,
                          'Max Range LB': max_range_lowbound,
                          'Max Range HPR UB': hprmax_range_gp_upbound,
                          'Max Range Speed UB': speedmax_range_gp_upbound,
                          'Max Range UB': max_range_upbound,
                          'Max Range HPR Actual': hprmax_range_actual,
                          'Max Range Speed Actual': speedmax_range_actual,
                          'Max Range Actual': max_range_actual,
                          'Max Range HPR Pred': hprmax_range_pred,
                          'Max Range Speed Pred': speedmax_range_pred,
                          'Max Range Pred': max_range_pred,
                          'Max Range HPR Error': hprmax_range_error,
                          'Max Range Speed Error': speedmaxhpr_range_error,
                          'Max Range Error': max_range_error,
                          'Max Range HPR % Error': hprmax_range_perr,
                          'Max Range Speed % Error': speedmaxhpr_range_perr,
                          'Max Range % Error': max_range_perr}

        # ################################################################################################################
        # # Range Multi - Uses multiple outputs instead of bounds for pdf
        # # Bounds
        # bounds_temp = []  # HPR
        # bounds_value_temp = []  # Range
        # bounds_speed_temp = []  # Speed
        # # Loop through each HPR and HPA instance
        # for i in range(0, len(self.hpr_prediction_multi)):
        #     temp = []
        #     for j in range(0, len(self.hpr_prediction_multi[i])):
        #         if self.old_actual['Speed'][j] != 0:
        #             temp.append(self.hpr_prediction_multi[i][j] / self.old_actual['Speed'][j])
        #         else:
        #             temp.append(self.hpr_prediction_multi[i][1] / self.old_actual['Speed'][1])
        #     hprmax_range_pred_del = min(temp)
        #     ihprmax_range_pred = temp.index(hprmax_range_pred_del)
        #     bounds_speed_temp.append(self.old_actual['Speed'][ihprmax_range_pred])
        #     # Checks whether Max Range Exceeds Max Speed. Max Speed limits Max Range.
        #     if self.max_speed_multi['Max Speed Pred'] > speedmax_range_pred:
        #         bounds_temp.append(self.hpr_prediction_multi[i][ihprmax_range_pred])
        #     else:
        #         bounds_temp.append(self.max_speed_multi['Max HPR Pred'])
        #         bounds_speed_temp.append(self.max_speed_multi['Max Speed Pred'])
        #
        #     bounds_value_temp.append(((bounds_speed_temp[i] * 3600.0 * weightfuel) / (sfc * bounds_temp[i])) / 5280.0)
        #
        # hprmax_range_gp_lowbound = min(bounds_temp)
        # speedmax_range_gp_lowbound = min(bounds_speed_temp)
        # max_range_lowbound = min(bounds_value_temp)
        # hprmax_range_gp_upbound = max(bounds_temp)
        # speedmax_range_gp_upbound = max(bounds_speed_temp)
        # max_range_upbound = max(bounds_value_temp)
        # hprmax_range_pred = statistics.mean(bounds_temp)
        # speedmax_range_pred = statistics.mean(bounds_speed_temp)
        # max_range_pred = statistics.mean(bounds_value_temp)
        # self.max_range_multi = {'Max Range HPR LB': hprmax_range_gp_lowbound,
        #                         'Max Range Speed LB': speedmax_range_gp_lowbound,
        #                         'Max Range LB': max_range_lowbound,
        #                         'Max Range HPR UB': hprmax_range_gp_upbound,
        #                         'Max Range Speed UB': speedmax_range_gp_upbound,
        #                         'Max Range UB': max_range_upbound,
        #                         'Max Range HPR Pred': hprmax_range_pred,
        #                         'Max Range Speed Pred': speedmax_range_pred,
        #                         'Max Range Pred': max_range_pred}
        # ################################################################################################################

    def __generate_endurance_data(self):

        weightfuel = float(self.rotor_info['rotorcraft_init']['weightfuel'])
        sfc = float(self.rotor_info['rotorcraft_init']['sfc'])

        # Lower Bound
        endurance_lowbound = weightfuel / (sfc * self.bucket_speed['Bucket HPR LB'])

        # Upper Bound
        endurance_upbound = weightfuel / (sfc * self.bucket_speed['Bucket HPR UB'])

        # Actual
        endurance_actual = weightfuel / (sfc * self.bucket_speed['Bucket HPR Actual'])

        # Prediction
        endurance_pred = weightfuel / (sfc * self.bucket_speed['Bucket HPR Pred'])

        # Error
        endurance_error = self.__rmse(endurance_actual, endurance_pred)

        # Percent Error
        endurance_perr = self.__perr(endurance_actual, endurance_pred)


        self.max_endurance = {'HPR Endurance LB': endurance_lowbound,
                              'HPR Endurance UB': endurance_upbound,
                              'HPR Endurance Actual': endurance_actual,
                              'HPR Endurance Pred': endurance_pred,
                              'HPR Endurance Error': endurance_error,
                              'HPR Endurance % Error': endurance_perr}

        ################################################################################################################
        # Endurance Multi - Uses multiple outputs instead of bounds for pdf
        # Bounds
        bounds_value_temp = []  # Range
        # Loop through each HPR and HPA instance
        for i in range(0, len(self.hpr_prediction_multi)):
            bounds_value_temp.append(weightfuel / (sfc * min(self.hpr_prediction_multi[i])))

        endurance_lowbound = min(bounds_value_temp)
        endurance_upbound = max(bounds_value_temp)
        endurance_pred = statistics.mean(bounds_value_temp)
        self.max_endurance_multi = {'HPR Endurance LB': endurance_lowbound,
                                    'HPR Endurance UB': endurance_upbound,
                                    'HPR Endurance Pred': endurance_pred}
        ################################################################################################################

    def __generate_max_climb(self):

        # s = 1.689
        # weight = float(self.rotor_info['rotorcraft_init']['weight']) * 32.17
        weight = float(self.rotor_info['rotorcraft_init']['weight'])
        ff_index = self.speed_act.index(self.bucket_speed['Bucket Speed LB'])

        # Lower Bound
        # vrochov_lowbound = 60 * 550 * 2 * (self.hpa_lower_bound[0] - self.hpr_upper_bound[0]) / weight
        # vrocff_lowbound = 60 * 550 * (min(self.hpa_lower_bound) - self.bucket_speed['Bucket HPR UB']) / weight
        vrochov_lowbound = 60 * 550 * 2 * (self.hpa_lower_bound[0] - self.hpr_upper_bound[0]) / weight
        vrocff_lowbound = 60 * 550 * (self.hpa_lower_bound[ff_index] - self.bucket_speed['Bucket HPR UB']) / weight

        ff_index = self.speed_act.index(self.bucket_speed['Bucket Speed UB'])
        # Upper Bound
        vrochov_upbound = 60 * 550 * 2 * (self.hpa_upper_bound[0] - self.hpr_lower_bound[0]) / weight
        vrocff_upbound = 60 * 550 * (self.hpa_upper_bound[ff_index] - self.bucket_speed['Bucket HPR LB']) / weight

        ff_index = self.speed_act.index(self.bucket_speed['Bucket Speed Actual'])
        # Actual
        vrochov_actual = 60 * 550 * 2 * (self.actual_rc_data['HP Available'][0] -
                                         self.actual_rc_data['HP Required'][0]) / weight
        vrocff_actual = 60 * 550 * (
                self.actual_rc_data['HP Available'][ff_index] - self.bucket_speed['Bucket HPR Actual']) / weight

        ff_index = self.speed_act.index(self.bucket_speed['Bucket Speed Pred'])
        # Prediction
        vrochov_pred = 60 * 550 * 2 * (self.hpa_prediction[0] - self.hpr_prediction[0]) / weight
        vrocff_pred = 60 * 550 * (self.hpa_prediction[ff_index] - self.bucket_speed['Bucket HPR Pred']) / weight



        ####################################################################################################
        # TEST
        # slope_power_required = (self.hpr_prediction[0] - self.hpr_prediction[
        #     self.speed_act.index(self.bucket_speed['Bucket Speed Pred'])]) / self.hpr_prediction[0]

        # slope_hov = (self.hpa_prediction[0] - self.hpr_prediction[0]) / self.hpr_prediction[0]
        slope_hov = (self.hpa_prediction[0] - (self.hpa_prediction[0] - self.hpr_prediction[0]) / 2) / vrochov_pred
        #########print(slope_hov)
        # print('HPR', self.hpr_prediction)
        # print('AR', self.actual_rc_data['HP Required'])
        # print('HPA', self.hpa_prediction)
        # print('AA', self.actual_rc_data['HP Available'])
        # slope_ff = (self.hpa_prediction[ff_index] - self.hpr_prediction[ff_index]) / self.hpr_prediction[ff_index]
        slope_ff = (self.hpa_prediction[ff_index] - (
                self.hpa_prediction[ff_index] - self.hpr_prediction[ff_index]) / 2) / vrocff_pred
        ###########print(slope_ff)
        # absolute_ceiling = (self.hpa_prediction[
        #     self.speed_act.index(self.bucket_speed['Bucket Speed Pred'])] - self.hpr_prediction[
        #     self.speed_act.index(self.bucket_speed['Bucket Speed Pred'])]) / slope_power_required

        absolute_ceiling_hov = (vrochov_pred * slope_hov)
        service_ceiling_hov = ((vrochov_pred - 100) * slope_hov)

        absolute_ceiling_ff = (vrocff_pred * slope_ff)
        service_ceiling_ff = ((vrocff_pred - 100) * slope_ff)

        # print(f"Approximate Absolute Ceiling Altitude at hover: {absolute_ceiling_hov} feet")
        # print(f"Approximate Service Ceiling Altitude at hover: {service_ceiling_hov} feet")
        #
        # print(f"Approximate Absolute Ceiling Altitude at Forward Flight: {absolute_ceiling_ff} feet")
        # print(f"Approximate Service Ceiling Altitude at Forward Flight: {service_ceiling_ff} feet")

        ####################################################################################################

        # Error
        vrochov_error = self.__rmse(vrochov_actual, vrochov_pred)
        vrocff_error = self.__rmse(vrocff_actual, vrocff_pred)

        # Percent Error
        vrochov_perr = self.__perr(vrochov_actual, vrochov_pred)
        vrocff_perr = self.__perr(vrocff_actual, vrocff_pred)

        self.max_climb = {'HOV VROC LB': vrochov_lowbound,
                          'FF VROC LB': vrocff_lowbound,
                          'HOV VROC UB': vrochov_upbound,
                          'FF VROC UB': vrocff_upbound,
                          'HOV VROC Actual': vrochov_actual,
                          'FF VROC Actual': vrocff_actual,
                          'HOV VROC Pred': vrochov_pred,
                          'FF VROC Pred': vrocff_pred,
                          'HOV VROC Error': vrochov_error,
                          'FF VROC Error': vrocff_error,
                          'HOV VROC % Error': vrochov_perr,
                          'FF VROC % Error': vrocff_perr}

        ################################################################################################################
        # Max Climb Multi - Uses multiple outputs instead of single instance bounds for pdf

        # Bounds
        bounds_hov_temp = []
        bounds_ff_temp = []
        # Loop through each HPR and HPA instance and find lowest and upper intersection
        for i in range(0, len(self.hpr_prediction_multi)):
            bounds_hov_temp.append(
                60 * 550 * 2 * (self.hpa_prediction_multi[i][0] - self.hpr_prediction_multi[i][0]) / weight)
            bucket_hpr_temp = min(self.hpr_prediction_multi[i])
            ihprmin_temp = self.hpr_prediction_multi[i].tolist().index(bucket_hpr_temp)
            bounds_ff_temp.append(
                60 * 550 * (self.hpa_prediction_multi[i][ihprmin_temp] - min(self.hpr_prediction_multi[i])) / weight)

        ################################################################################################################

    @staticmethod
    def __rmse(a, b):

        mse = pow(pow(a - b, 2), 0.5)

        return mse

    @staticmethod
    def __perr(a, b):

        error = abs((a - b) / b) * 100

        return error

    def get_mobility_data(self):

        self.data = {'Bucket Speed': self.bucket_speed,
                     'Max Speed': self.max_speed,
                     'Max Range': self.max_range,
                     'Max Endurance': self.max_endurance,
                     'Max Climb': self.max_climb,
                     'Bucket Speed Multi': self.bucket_speed_multi,
                     'Max Speed Multi': self.max_speed_multi,
                     'Max Range Multi': self.max_range_multi,
                     'Max Endurance Multi': self.max_endurance_multi,
                     'Max Climb Multi': self.max_climb
                     }

        return self.data

    def get_mobility_perr(self):

        self.data_perr = {'Bucket HPR Error': self.bucket_speed['Bucket HPR % Error'],
                          'Bucket Speed Error': self.bucket_speed['Bucket Speed % Error'],
                          'Max HPR Error': self.max_speed['Max HPR % Error'],
                          'Max Speed Error': self.max_speed['Max Speed % Error'],
                          'Max HPR Range Error': self.max_range['Max Range HPR % Error'],
                          'Max Range Speed Error': self.max_range['Max Range Speed % Error'],
                          'Max Range Error': self.max_range['Max Range % Error'],
                          'Max Endurance Error': self.max_endurance['HPR Endurance % Error'],
                          'Max Climb HOV Error': self.max_climb['HOV VROC % Error'],
                          'Max Climb FF Error': self.max_climb['FF VROC % Error']
                          }

        return self.data_perr

    def get_mobility_estimate(self):

        self.data_est = {'Bucket HPR Pred': self.bucket_speed['Bucket HPR Pred'],
                         'Bucket Speed Pred': self.bucket_speed['Bucket Speed Pred'],
                         'Max HPR Pred': self.max_speed['Max HPR Pred'],
                         'Max Speed Pred': self.max_speed['Max Speed Pred'],
                         'Max HPR Range Pred': self.max_range['Max Range HPR Pred'],
                         'Max Range Speed Pred': self.max_range['Max Range Speed Pred'],
                         'Max Range Pred': self.max_range['Max Range Pred'],
                         'Max Endurance Pred': self.max_endurance['HPR Endurance Pred'],
                         'Max Climb HOV Pred': self.max_climb['HOV VROC Pred'],
                         'Max Climb FF Pred': self.max_climb['FF VROC Pred']
                         }

        return self.data_est

    def print_mobility_data(self):

        # print(self.data)
        print(str(self.data['Bucket Speed']['Bucket Speed Actual']) + ' knots\n')
        print(str(round(self.data['Bucket Speed']['Bucket HPR Actual'], 1)) + ' hp\n')
        print(str(round(self.data['Max Endurance']['HPR Endurance Actual'], 1)) + ' hrs\n')
        print(str(self.data['Max Speed']['Max Speed Actual']) + ' knots\n')
        print(str(round(self.data['Max Speed']['Max HPR Actual'], 1)) + ' hp\n')
        print(str(round(self.data['Max Range']['Max Range Actual'], 0)) + ' NM\n')
        print(str(self.data['Max Range']['Max Range Speed Actual']) + ' knots\n')
        print(str(round(self.data['Max Range']['Max Range HPR Actual'], 1)) + ' hp\n')
        print(str(round(self.data['Max Climb']['HOV VROC Actual'], 1)) + ' ft/min\n')
        print(str(round(self.data['Max Climb']['FF VROC Actual'], 1)) + ' ft/min\n')


    # def print_mobility_error_thesis_format(self):
    #     print_file = open('Data/mobility_err_thesis_tables.txt', 'w', encoding='UTF8', newline='')
    #
    #     if self.run == 0:
    #         csv.writer(print_file).writerow(f"Bucket Speed & ${self.bucket_speed['Bucket HPR % Error']}$ & $-$  & $-$")
    #
    #     print_file.close()

    @staticmethod
    def print_statement():
        print("Generating Mobility Metrics")

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
