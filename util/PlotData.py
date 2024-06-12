import pandas as pd
from matplotlib import pyplot as plt, font_manager as fm
import numpy as np


class PlotData:
    def __init__(self, source_data, actual_rc_data, actual_power_plot, rotor_obs_data, gp_pred_rotor_data,
                 mission_obs_data, recursion, rsgp_data, mission_rotor_data, mission_metrics_data,
                 metric_comparison_data, mission_property, time_factor):
        self.source_data = source_data
        self.actual_rc_data = actual_rc_data  # Saved info with set parameters
        self.actual_power_plot = actual_power_plot  # Saved all power info
        self.rotor_obs_data = rotor_obs_data
        self.mission_obs_data = mission_obs_data
        self.recursion = recursion
        self.rsgp_data = rsgp_data
        self.mission_rotor_data = mission_rotor_data
        self.mission_metrics_data = mission_metrics_data
        self.metric_comparison_data = metric_comparison_data
        self.mission_property = mission_property
        self.time_factor = time_factor
        self.fontname = "Times New Roman"
        self.axis_font = 16
        self.axis_num_font = 12
        self.x_max = max(actual_rc_data['Speed'])
        self.y_max = 2400  # max(actual_rc_data['HP Available']) + int(actual_rc_data['HP Available'][0] / 2) + 400
        self.gp_pred_rotor_data = gp_pred_rotor_data
        self.print_statement()

        if recursion:
            self.plot_mission_mobility_evolution()

        self.plot_actual_hp_data()
        self.plot_gp_pred_data()

        # self.plot_pred_multi_data()

    # Plot Actual HP Data
    def plot_actual_hp_data(self):

        ################################################################################################################
        hp_mid_aeo = pd.DataFrame(self.actual_power_plot['Mid_AEO'])
        hp_max_aeo = pd.DataFrame(self.actual_power_plot['Max_AEO'])
        hp_mid_oei = pd.DataFrame(self.actual_power_plot['Mid_OEI'])
        hp_max_oei = pd.DataFrame(self.actual_power_plot['Max_OEI'])

        fig1 = hp_mid_aeo.plot(x='Speed', y='HPR', kind='line', color='black', grid='true')
        plt.rcParams["font.family"] = self.fontname
        hp_max_aeo.plot(ax=fig1, x='Speed', y='HPR', kind='line', color='blue', grid='true')

        hp_mid_aeo.plot(ax=fig1, x='Speed', y='HPA', kind='line', color='black', linestyle="dotted")
        hp_max_aeo.plot(ax=fig1, x='Speed', y='HPA', kind='line', color='blue', linestyle="dotted")

        hp_mid_oei.plot(ax=fig1, x='Speed', y='HPA', kind='line', color='black', linestyle="dashed")
        hp_max_oei.plot(ax=fig1, x='Speed', y='HPA', kind='line', color='blue', linestyle="dashed", grid='true')

        fig1.legend(
            ["Lightweight HPR", "Max Weight HPR", "Lightweight HPA AEO", "Max Weight HPA AEO", "Lightweight HPA OEI",
             "Max Weight HPA OEI"])
        # fig1.legend(
        #     ["Lightweight HPR", "Max Weight HPR"])
        ################################################################################################################
        # Constant Plot Settings
        plt.xlabel("Speed (Knots)", fontname=self.fontname)
        plt.ylabel("Power (Hp)", fontname=self.fontname)
        plt.xlim([0, self.x_max - 1])  # 630
        plt.ylim([0, self.y_max])  # 700
        plt.title('Hexacopter Power Curves', fontname=self.fontname)
        plt.xticks(fontname=self.fontname)
        plt.yticks(fontname=self.fontname)

        # fig2 = source.plot(x='Speed', y='Vtip', kind='line', color='black', title='Rotor Tip Velocity', grid='true')
        # plt.xlabel("Speed (Knots)", fontname=self.fontname)
        # plt.ylabel("Tip Velocity (ft/s)", fontname=self.fontname)
        # plt.xticks(fontname=self.fontname)
        # plt.yticks(fontname=self.fontname)
        # plt.xlim([0, self.x_max])  # 630
        #
        # fig3 = source.plot(x='Speed', y='Xflat', kind='line', color='black', title='Flat Plate Area', grid='true')
        # plt.xlabel("Speed (Knots)", fontname=self.fontname)
        # plt.ylabel("Flat Area ($ft^{2}$)", fontname=self.fontname)
        # plt.xticks(fontname=self.fontname)
        # plt.yticks(fontname=self.fontname)
        # plt.xlim([0, self.x_max])  # 630

        plt.show()

    def plot_actual_cp_data(self):

        hp_mid_aeo = pd.DataFrame(self.actual_power_plot['Mid_AEO'])
        hp_max_aeo = pd.DataFrame(self.actual_power_plot['Max_AEO'])
        hp_mid_oei = pd.DataFrame(self.actual_power_plot['Mid_OEI'])
        hp_max_oei = pd.DataFrame(self.actual_power_plot['Max_OEI'])

        fig1 = hp_mid_aeo.plot(x='Mu', y='CPR', kind='line', color='black', grid='true')
        plt.rcParams["font.family"] = self.fontname
        hp_max_aeo.plot(ax=fig1, x='Mu', y='CPR', kind='line', color='blue', grid='true')

        hp_mid_aeo.plot(ax=fig1, x='Mu', y='CPA', kind='line', color='black', linestyle="dotted")
        hp_max_aeo.plot(ax=fig1, x='Mu', y='CPA', kind='line', color='blue', linestyle="dotted")

        hp_mid_oei.plot(ax=fig1, x='Mu', y='CPA', kind='line', color='black', linestyle="dashed")
        hp_max_oei.plot(ax=fig1, x='Mu', y='CPA', kind='line', color='blue', linestyle="dashed", grid='true')

        fig1.legend(
            ["Lightweight CPR", "Max Weight CPR", "Lightweight CPA AEO", "Max Weight CPA AEO", "Lightweight CPA OEI",
             "Max Weight CPA OEI"])

        ################################################################################################################
        # Constant Plot Settings
        plt.xlabel("Speed (Knots)", fontname=self.fontname, fontsize=16)
        plt.ylabel("Power (hp)", fontname=self.fontname, fontsize=16)
        plt.xlim([0, max(self.actual_power_plot['Mid_AEO']['Mu'][0:len(self.actual_power_plot['Mid_AEO']['Mu']) - 1])])
        plt.ylim([0, max(self.actual_power_plot['Mid_AEO']['CPA']) + 0.003])
        plt.title('Hexcopter Non-Dimensional Power Curves', fontname=self.fontname, fontsize=18)
        plt.xticks(fontname=self.fontname)
        plt.yticks(fontname=self.fontname)

        plt.show()

    # Plot GP Prediction
    def plot_gp_pred_data(self):

        # HP Required ##################################################################################################
        x = self.gp_pred_rotor_data['Testing Points X']
        x_act = self.actual_rc_data['Speed']
        X = np.atleast_2d(self.rotor_obs_data['Speed']).T
        y = np.array(self.rotor_obs_data['HP Required'])
        f = np.array(self.actual_rc_data['HP Required'])
        plt.rcParams["font.family"] = self.fontname
        plt.figure(figsize=(10, 6))

        hpr_act, = plt.plot(x_act, f, label="HPR Actual", color='black')  # , marker='+')

        # Check Recursion
        if self.recursion:
            # Plot HPA Recursive Data
            mission_data, = plt.plot(self.rsgp_data['New Speed'], self.rsgp_data['New HPA'], "y*", alpha=0.3)
            # Plot HPA Actual Model
            hpa_rec, = plt.plot(self.mission_rotor_data[0]["Speed"], self.mission_rotor_data[0]["HP Available"],
                                linestyle=':', color='darkolivegreen', linewidth=5.0)  # , color='#ECB820')

        if self.recursion:
            # Plot HPR Recursive Data
            plt.plot(self.rsgp_data['New Speed'], self.rsgp_data['New HPR'], "y*")
            # Plot HPR Actual Model
            hpr_rec, = plt.plot(self.mission_rotor_data[0]["Speed"], self.mission_rotor_data[0]["HP Required"],
                                linestyle=':', color='orangered', linewidth=5.0)  # , color='#11F326')
            title = 'Updated Power Curve Prediction'
            plt.title(label=title, fontsize=self.axis_font + 2)

        # Plot Observations
        # plt.errorbar(X.ravel(), y, self.gp_pred_rotor_data['HPR Alpha'], fmt="r.", markersize=2, label="_Observations",
        #              alpha=0.3)
        hpr, = plt.plot(x, self.gp_pred_rotor_data['HPR Prediction'], "b-", label="HPR Prediction")  # , alpha=0.4)
        # title = 'Power Curve Prediction w/ ' + str(self.rotor_obs_data['Num Obs']) + ' Observations'
        # plt.title(label=title, fontsize=self.axis_font+2)
        plt.grid(visible=True)
        plt.fill(
            np.concatenate([x, x[::-1]]),
            np.concatenate(
                [self.gp_pred_rotor_data['HPR Lower Bound'], self.gp_pred_rotor_data['HPR Upper Bound'][::-1]]),
            alpha=0.2,
            fc="b",
            ec="None",
            label="_95% confidence interval",
        )

        # HP Available #################################################################################################
        x = self.gp_pred_rotor_data['Testing Points X']
        X = np.atleast_2d(self.rotor_obs_data['Speed']).T
        y = np.array(self.rotor_obs_data['HP Available'])
        f = np.array(self.actual_rc_data['HP Available'])
        self.gp_pred_rotor_data['HPA Upper Bound'], self.gp_pred_rotor_data['HPA Lower Bound'] = \
            self.gp_pred_rotor_data['HPA Upper Bound'].reshape(-1, 1), \
            self.gp_pred_rotor_data['HPA Lower Bound'].reshape(-1, 1)
        # Plot Observations
        # hpr_obs = plt.errorbar(X.ravel(), y, self.gp_pred_rotor_data['HPA Alpha'], fmt="r.", markersize=2,
        #                        label="Observations",
        #                        alpha=0.3)
        hpa, = plt.plot(x, self.gp_pred_rotor_data['HPA Prediction'], marker='_', color='teal',
                        label="HPA Prediction")  # , alpha=0.4)

        # hpa_act, = plt.plot(x, f, label=r"$f(x) = hp available$", color='plum', marker='+')
        hpa_act, = plt.plot(x_act, f, label="HPA Actual", color='darkmagenta')  # , marker='+')

        interval, = plt.fill(
            np.concatenate([x, x[::-1]]),
            np.concatenate(
                [self.gp_pred_rotor_data['HPA Lower Bound'], self.gp_pred_rotor_data['HPA Upper Bound'][::-1]]),
            alpha=0.2,
            fc="b",
            ec="None",
            label="95% confidence interval",
        )

        plt.xlabel("$Speed$ $(Knots)$", fontsize=self.axis_font)
        plt.ylabel("$Power$ $(Hp)$", fontsize=self.axis_font)
        plt.xlim([0, self.x_max])
        plt.ylim([0, self.y_max])
        plt.xticks(visible=True, size=self.axis_num_font)
        plt.yticks(visible=True, size=self.axis_num_font)

        # HPR Inducing Points
        X_u = self.gp_pred_rotor_data['Inducing Points X']
        y_u = self.gp_pred_rotor_data['HPR Inducing Points']

        ind_hpr, = plt.plot(X_u, y_u, "go", label="Inducing Points")

        # HPA Inducing Points
        y_u = self.gp_pred_rotor_data['HPA Inducing Points']
        ind_hpa, = plt.plot(X_u, y_u, "go", label="_HPA Inducing Points")

        # plt.legend(loc="upper right", handles=[hpr, hpa, hpr_act, hpa_act])
        plt.legend(loc="upper right", fontsize=self.axis_font)
        if self.recursion:
            # plt.legend([hpr, hpr_act, hpr_rec, hpa, hpa_act, hpa_rec, interval, ind_hpr, hpr_obs, mission_data],
            #            ["HPR Pred.", "HPR Initial", "HPR Actual", "HPA Pred.", "HPA Initial", "HPA Actual",
            #             "95% confidence interval", "Inducing Points", "Observations", "Mission Data"])
            plt.legend([hpr, hpr_act, hpr_rec, hpa, hpa_act, hpa_rec, ind_hpr, mission_data],
                       ["HPR Pred.", "HPR Initial", "HPR Actual", "HPA Pred.", "HPA Initial", "HPA Actual",
                        "Inducing Points", "Mission Data"], loc="upper right", fontsize=18)

        plt.show()
        # CPR ##########################################################################################################
        # x = np.atleast_2d(self.actual_rc_data['Mu']).T
        # X = np.atleast_2d(self.rotor_obs_data['Mu']).T
        # y = np.array(self.rotor_obs_data['CP Required'])
        # f = np.array(self.actual_rc_data['CP Required'])
        # plt.figure()
        # plt.rcParams["font.family"] = self.fontname
        #
        # # Plot Observations
        # plt.errorbar(X.ravel(), y, self.gp_pred_rotor_data['HPR Alpha'], fmt="r.", markersize=2, label="_Observations",
        #              alpha=0.3)
        # cpr, = plt.plot(x, self.gp_pred_rotor_data['CPR Prediction'], marker='+', color='blue', label="CPR Prediction")
        # title = 'Power Curve Prediction w/ ' + str(self.rotor_obs_data['Num Obs']) + ' Observations'
        # plt.title(label=title)
        # plt.grid(visible=True)
        # plt.fill(
        #     np.concatenate([x, x[::-1]]),
        #     np.concatenate(
        #         [self.gp_pred_rotor_data['CPR Lower Bound'], self.gp_pred_rotor_data['CPR Upper Bound'][::-1]]),
        #     alpha=0.2,
        #     fc="b",
        #     ec="None",
        #     label="_95% confidence interval",
        # )
        # cpr_act, = plt.plot(x, f, label="CP Required", color='black')
        #
        # # TODO: Add cp recursion
        # # if self.recursion:
        # #     # Plot HPR Recursive Data
        # #     plt.plot(self.new_data['x'], self.new_data['hpr'], "y*")
        #
        # plt.xlabel("μ (Units)", fontname=self.fontname, fontsize=16)
        # plt.ylabel("cp (Units)", fontname=self.fontname, fontsize=16)
        # plt.xlim([0, self.x_max])
        # plt.ylim([0, 0.004])
        #
        # # CPA #################################################################################################
        # y = np.array(self.rotor_obs_data['CP Available'])
        # f = np.array(self.actual_rc_data['CP Available'])
        # self.gp_pred_rotor_data['CPA Upper Bound'], self.gp_pred_rotor_data['CPA Lower Bound'] = \
        #     self.gp_pred_rotor_data['CPA Upper Bound'].reshape(-1, 1), \
        #     self.gp_pred_rotor_data['CPA Lower Bound'].reshape(-1, 1)
        # # Plot Observations
        # plt.errorbar(X.ravel(), y, self.gp_pred_rotor_data['HPA Alpha'], fmt="r.", markersize=2, label="Observations",
        #              alpha=0.3)
        #
        #
        # cpr, = plt.plot(x, self.actual_rc_data['CP Required'], 'k-', linewidth=8)
        # cpa, plt.plot(x, x='Mu', y='CP Available', kind='line',
        #          title=title_string, grid='true', color='black', linestyle='dashed', fontsize=1, sharex=True)
        # plt.xlabel("μ (Units)", fontname=self.fontname, fontsize=16)
        # plt.ylabel("cp (Units)", fontname=self.fontname, fontsize=16)
        # plt.xlim([0, self.x_max])
        # cp_obs, = plt.plot(x, self.rotor_obs_data['CP'], 'y.', markersize=3)
        # plt.xlabel("Speed (Knots)")
        # plt.ylabel("CP (Units)")
        # plt.xlim([0, self.x_max])
        # plt.ylim([0, max(self.actual_rc_data['CP']) + 0.001])
        # title = 'Power Curve Prediction w/ '
        # plt.title(label=title, fontsize=18)
        ################################################################################################################
        plt.show()

    def plot_pred_multi_data(self):
        plt.figure()
        plt.rcParams["font.family"] = self.fontname
        print(len(self.gp_pred_rotor_data['HPR Prediction Multi']))
        for i in range(len(self.gp_pred_rotor_data['HPR Prediction Multi'])):
            x = np.atleast_2d(self.actual_rc_data['Speed']).T
            hpr, = plt.plot(x, self.gp_pred_rotor_data['HPR Prediction Multi'][i], alpha=0.4)
            hpa, = plt.plot(x, self.gp_pred_rotor_data['HPA Prediction Multi'][i], alpha=0.4)

        plt.xlabel("$Speed$ $(Knots)$")
        plt.ylabel("$Power$ $(Hp)$")
        title = 'Power Curve Predictions Example'
        plt.title(label=title)
        plt.grid(visible=True)
        plt.xlim([0, self.x_max])
        plt.ylim([0, 1800])
        plt.show()

    def plot_mission_mobility_evolution(self):

        x = self.mission_metrics_data['Time']

        start = [-1 for _ in range(0, self.time_factor)]
        x = start + x

        # Bucket Speed
        if self.mission_property == 0:
            ymin, ymax = 10, 15
        elif self.mission_property == 1:
            ymin, ymax = 10, 15  # ss: 15,25
        elif self.mission_property == 2:
            ymin, ymax = 10, 30  # ss: 15,25 | new hyper 10, 30
        else:
            ymin, ymax = 10, 15
        lgd_titles = ['Bucket Speed', 'Bucket Speed Initial Prediction', 'Bucket Speed Expected Model',
                      'Bucket Speed Actual Model']
        self.handle_mission_metric_data(x, self.mission_metrics_data['Bucket Speed'],
                                        self.metric_comparison_data['Bucket Speed']['Expected'],
                                        self.metric_comparison_data['Bucket Speed']['Prediction'],
                                        self.metric_comparison_data['Bucket Speed']['Actual'], 'Bucket Speed',
                                        "$Speed$ $(Knots)$", ymin, ymax,
                                        lgd_titles)

        # same model ymin, ymax = 2, 12,
        # error model ymin, ymax = 2, 12,
        # payload model ymin, ymax = 2, 12, -> ss: 2, 15
        # engine fail model ymin, ymax = 2, 15,

        # 10, 10

        # Max Speed
        if self.mission_property == 0:
            ymin, ymax = 3, 6
        elif self.mission_property == 1:
            ymin, ymax = 5, 10
        elif self.mission_property == 2:
            ymin, ymax = 15, 10
        else:
            ymin, ymax = 15, 10  # new hyper: (15)80, (15)80 # 100, 80
        lgd_titles = ['Max Speed', 'Max Speed Initial Prediction', 'Max Speed Expected Model', 'Max Speed Actual Model']
        self.handle_mission_metric_data(x, self.mission_metrics_data['Max Speed'],
                                        self.metric_comparison_data['Max Speed']['Expected'],
                                        self.metric_comparison_data['Max Speed']['Prediction'],
                                        self.metric_comparison_data['Max Speed']['Actual'], 'Max Speed',
                                        "$Speed$ $(Knots)$", ymin, ymax,
                                        lgd_titles)

        # same model ymin, ymax = 3, 4,
        # error model ymin, ymax = 3, 4,
        # payload model ymin, ymax = 3, 4,
        # engine fail model ymin, ymax = 3, 6,

        # sm, 3, 6
        # efm, 15, 10

        # Max Range
        if self.mission_property == 0:
            ymin, ymax = 15, 20
        elif self.mission_property == 1:
            ymin, ymax = 150, 150
        elif self.mission_property == 2:
            ymin, ymax = 150, 650
        else:
            ymin, ymax = 5, 10  # new hyper: (15)200, (20)150 # 250, 150   15,20
        lgd_titles = ['Max Range', 'Max Range Initial Prediction', 'Max Range Expected Model', 'Max Range Actual Model']
        self.handle_mission_metric_data(x, self.mission_metrics_data['Max Range'],
                                        self.metric_comparison_data['Max Range']['Expected'],
                                        self.metric_comparison_data['Max Range']['Prediction'],
                                        self.metric_comparison_data['Max Range']['Actual'], 'Max Range',
                                        "$Range$ $(NM)$", ymin, ymax,
                                        lgd_titles)
        # same model ymin, ymax = 15, 20,
        # error model ymin, ymax = 15, 20,
        # payload model ymin, ymax = 250, 150,
        # engine fail model ymin, ymax = 15, 20,

        # Max Endurance
        if self.mission_property == 0:
            ymin, ymax = 0.4, 0.5  # 0.4, 0.5
        elif self.mission_property == 1:
            ymin, ymax = 4, 5
        elif self.mission_property == 2:
            ymin, ymax = 5, 15
        else:
            ymin, ymax = 0.2, 0.3  # 0.4, 0.5
        lgd_titles = ['Max Endurance', 'Max Endurance Initial Prediction', 'Max Endurance Expected Model',
                      'Max Endurance Actual Model']
        self.handle_mission_metric_data(x, self.mission_metrics_data['Max Endurance'],
                                        self.metric_comparison_data['Max Endurance']['Expected'],
                                        self.metric_comparison_data['Max Endurance']['Prediction'],
                                        self.metric_comparison_data['Max Endurance']['Actual'], 'Max Endurance',
                                        "$Endurance$ $(Hrs)$", ymin, ymax,
                                        lgd_titles)
        # same model ymin, ymax = 0.4, 0.5,
        # error model ymin, ymax = 0.4, 0.5,
        # payload model ymin, ymax = 6, 3
        # engine fail model ymin, ymax = 0.4, 0.5,

        # Max Climb HOV
        if self.mission_property == 0:
            ymin, ymax = 100, 200
        elif self.mission_property == 1:
            ymin, ymax = 100, 1000
        elif self.mission_property == 2:
            ymin, ymax = 3000, 2000
        else:
            ymin, ymax = 3000, 2000
        lgd_titles = ['Max Climb HOV', 'Max Climb HOV Initial Prediction', 'Max Climb HOV Expected Model',
                      'Max Climb HOV Actual Model']
        self.handle_mission_metric_data(x, self.mission_metrics_data['Max Climb HOV'],
                                        self.metric_comparison_data['Max Climb HOV']['Expected'],
                                        self.metric_comparison_data['Max Climb HOV']['Prediction'],
                                        self.metric_comparison_data['Max Climb HOV']['Actual'], 'Max Climb HOV',
                                        "$Rate$ $of$ $Climb$ $(ft/min)$", ymin, ymax,
                                        lgd_titles)
        # same model ymin, ymax = 50, 100,
        # error model ymin, ymax = 100, 300,
        # payload model ymin, ymax = 100, 1700, -> ss: 1100, 1700
        # engine fail model ymin, ymax = 900, 1700,

        # sm, 100, 200
        # efm, 3000, 1400

        # Max Climb FF
        if self.mission_property == 0:
            ymin, ymax = 100, 200  # new hyperparameters: 500, 800
        elif self.mission_property == 1:
            ymin, ymax = 100, 1000
        elif self.mission_property == 2:
            ymin, ymax = 2000, 1500
        else:
            ymin, ymax = 2000, 1500
        lgd_titles = ['Max Climb FF', 'Max Climb FF Initial Prediction', 'Max Climb FF Expected Model',
                      'Max Climb FF Actual Model']
        self.handle_mission_metric_data(x, self.mission_metrics_data['Max Climb FF'],
                                        self.metric_comparison_data['Max Climb FF']['Expected'],
                                        self.metric_comparison_data['Max Climb FF']['Prediction'],
                                        self.metric_comparison_data['Max Climb FF']['Actual'], 'Max Climb FF',
                                        "$Rate$ $of$ $Climb$ $(ft/min)$", ymin, ymax,
                                        lgd_titles)
        # same model ymin, ymax = 50, 100,
        # error model ymin, ymax = 100, 300,
        # payload model ymin, ymax = 200, 1400
        # engine fail model ymin, ymax = 200, 1200

        # sm, 100, 200
        # efm, 2000, 1200

        plt.show()

    def handle_mission_metric_data(self, x, y, expected, sgp_prediction, actual, title, ylabel, ymin_del, ymax_del,
                                   legend_titles):

        plt.rcParams["font.family"] = self.fontname
        plt.figure(figsize=(7, 6))
        plt.grid(visible=True)
        mission, = plt.plot(x, y, "k-")
        prediction, = plt.plot(x, [sgp_prediction for _ in x], linestyle=':', color='gray', linewidth=3.0)
        expected_plt, = plt.plot(x, [expected for _ in x], linestyle=':', color='red')
        actual_plt, = plt.plot(x, [actual for _ in x], color='green', dashes=[10, 5, 20, 5], linestyle=(0, (1, 10)))

        plt.xlabel("$Time$ $(Minutes)$", fontsize=self.axis_font)
        plt.xlim([0, 31])
        plt.ylim([expected - ymin_del, expected + ymax_del])
        plt.ylabel(ylabel, fontsize=self.axis_font)
        plt.title(title, fontsize=self.axis_font + 2)
        plt.xticks(visible=True, size=self.axis_num_font)
        plt.yticks(visible=True, size=self.axis_num_font)
        plt.rcParams["font.family"] = self.fontname
        plt.legend([mission, prediction, expected_plt, actual_plt], legend_titles, loc="upper right",
                   fontsize=14)

    @staticmethod
    def print_statement():
        print("Plotting Data")
