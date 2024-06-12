"""
*************************************************************************
**                      RSGP Mobility Estimation                       **
**                                                                     **
** This program demonstrates the function of the Recursive Sparse      **
** Gaussian Process mobility estimation algorithm featured in          **
** Dr. Sarai Sherfield's thesis paper titled "Real-time Mobility       **
** Estimation for Autonomous Rotorcraft to Support Long-term Autonomy" **
**                                                                     **
** Created by: Dr. Sarai Sherifeld                                     **
** Last modified on: 6/3/2024 by Sarai Sherfield                       **
*************************************************************************
"""

# IMPORT LIBRARIES
####################################################################################################
from util.StructureActualData import StructureActualData
from util.GeneratePowerObservations import GeneratePowerObservations
from util.GenerateSGPPowerPrediction import GenerateSGPPowerPrediction
from util.GenerateMobilityMetrics import GenerateMobilityMetrics
from util.SaveMissionMetrics import save_mission_metrics
from util.GeneratePowerObsFromScenario import GeneratePowerObsFromScenario
from util.GenerateRSGPPowerPrediction import GenerateRSGPPowerPrediction
from util.PlotData import PlotData
import pandas as pd
import numpy as np
import copy
import os

####################################################################################################
####################################################################################################
# End {IMPORT LIBRARIES}

# CONSTANTS
####################################################################################################
mission_property_names = ["Normal Mission Property", "Model Error Mission Property", "Payload Change Property",
                          "Engine Failure Mission Property"]
####################################################################################################
####################################################################################################
# End {CONSTANTS}

# MISSION VARIABLES
####################################################################################################
# Measurement Rate {LU, SU, HU}
mission_set = '_SU'  # Only SU available at the moment

# Mission Data File Name
mission_filename_init = 'Full_Speed_Mission'
mission_filename = mission_filename_init + mission_set + '.xlsx'
####################################################################################################
####################################################################################################
# End {MISSION VARIABLES}

# SET ROTORCRAFT VARIABLES
####################################################################################################

# Select Flight Scenario
scenario_filename_init = 'scenarioA'  # Filename Options: {scenarioA, scenarioB, scenarioC}

# Select Mission Property
mission_property = 0  # NMP=0, MEMP=1, PCMP=2, or EFMP=3

# Select Rotorcraft Weight
weight_set = 'Mid'  # Mid or Max

# Select Rotorcraft Engine State (Only one engine can be damaged)
damage_eng_set = False

####################################################################################################
####################################################################################################
# End {SET ROTORCRAFT VARIABLES}

# SET RECURSIVE SPARSE GAUSSIAN PROCESS VARIABLES
####################################################################################################

# Number of Inducing Points
num_ind_points = 14  # I DO NOT RECOMMEND CHANGING FROM 14

# Number of Observation Points for inital Sparse Gaussian Process
num_obs = 1000  # Between 600 and 1000 is a good range for this project

# Measurement/Observation and GP Variance
var_set = 3  # Could vary but set to same value to reduce complexity

# Run the recursive or just the sparse
recursion = True


####################################################################################################
####################################################################################################
# End {SET RECURSIVE SPARSE GAUSSIAN PROCESS VARIABLES}

# LOCAL FUNCTIONS
####################################################################################################
# Functions
def evaluate_mission_property(mission_property_func, actual_power_multi_func, weight_set_func):
    mission_rotor_data_func = []
    # NM = 0, MEM = 1, PCM = 2, EFM = 3
    if mission_property_func == 0:
        if weight_set_func == 'Mid':
            mission_rotor_data_func.append(actual_power_multi_func['Mid_AEO']['ACT'])
            mission_rotor_data_func.append(actual_power_multi_func['Mid_AEO']['RI'])
            mission_rotor_data_func.append(actual_power_multi_func['Mid_AEO']['RD'])
        else:
            mission_rotor_data_func.append(actual_power_multi_func['Max_AEO']['ACT'])
            mission_rotor_data_func.append(actual_power_multi_func['Max_AEO']['RI'])
            mission_rotor_data_func.append(actual_power_multi_func['Max_AEO']['RD'])

    elif mission_property_func == 1:
        if weight_set_func == 'Mid':
            # Change HP by 10%
            temp_hpr = [ele + ele * 0.1 for ele in actual_power_multi_func['Mid_AEO']['ACT']['HP Required']]
            temp_hpa = [ele + ele * 0.1 for ele in mission_power_multi['Mid_AEO']['ACT']['HP Available']]
            actual_power_multi_func['Mid_AEO']['ACT']['HP Required'] = temp_hpr
            actual_power_multi_func['Mid_AEO']['ACT']['HP Available'] = temp_hpa
            mission_rotor_data_func.append(actual_power_multi_func['Mid_AEO']['ACT'])
            mission_rotor_data_func.append(actual_power_multi_func['Mid_AEO']['RI'])
            mission_rotor_data_func.append(actual_power_multi_func['Mid_AEO']['RD'])
        else:
            # Change HP by 10%
            temp_hpr = [ele + ele * 0.3 for ele in actual_power_multi_func['Max_AEO']['ACT']['HP Required']]
            temp_hpa = [ele + ele * 0.3 for ele in actual_power_multi_func['Max_AEO']['ACT']['HP Available']]
            actual_power_multi_func['Max_AEO']['ACT']['HP Required'] = temp_hpr
            actual_power_multi_func['Max_AEO']['ACT']['HP Available'] = temp_hpa
            mission_rotor_data_func.append(actual_power_multi_func['Max_AEO']['ACT'])
            mission_rotor_data_func.append(actual_power_multi_func['Max_AEO']['RI'])
            mission_rotor_data_func.append(actual_power_multi_func['Max_AEO']['RD'])

    elif mission_property_func == 2:
        if weight_set_func == 'Mid':
            mission_rotor_data_func.append(actual_power_multi_func['Max_AEO']['ACT'])
            mission_rotor_data_func.append(actual_power_multi_func['Max_AEO']['RI'])
            mission_rotor_data_func.append(actual_power_multi_func['Max_AEO']['RD'])
        else:
            mission_rotor_data_func.append(actual_power_multi_func['Mid_AEO']['ACT'])
            mission_rotor_data_func.append(actual_power_multi_func['Mid_AEO']['RI'])
            mission_rotor_data_func.append(actual_power_multi_func['Mid_AEO']['RD'])

    elif mission_property_func == 3:
        if weight_set_func == 'Mid':
            mission_rotor_data_func.append(actual_power_multi_func['Mid_OEI']['ACT'])
            mission_rotor_data_func.append(actual_power_multi_func['Mid_OEI']['RI'])
            mission_rotor_data_func.append(actual_power_multi_func['Mid_OEI']['RD'])
        else:
            mission_rotor_data_func.append(actual_power_multi_func['Max_OEI']['ACT'])
            mission_rotor_data_func.append(actual_power_multi_func['Max_OEI']['RI'])
            mission_rotor_data_func.append(actual_power_multi_func['Max_OEI']['RD'])
    else:
        # TODO: Produce Error Message
        print('Please insert a valid Mission Property')

    return mission_rotor_data_func


####################################################################################################
####################################################################################################
# End {LOCAL FUNCTIONS}

# MAIN
####################################################################################################

# Interpolates and Constructs Data
# Returns Actual Data in a Structured Format
actual_rotor_plot_data, rotor_info, rotor_data, actual_power_multi, actual_power_plot \
    = StructureActualData(weight_set,
                          damage_eng_set).get_all_rotorcraft_data()

# Print out scenario parameters
print("\n")
print("ROTORCRAFT VARIABLES")
print("Weight Setting:", weight_set)
print("Damaged Engine Setting:", damage_eng_set)
print("\n")
print("MISSION VARIABLES")
print("Flight Scenario:", scenario_filename_init)
print("mission_property:", mission_property_names[mission_property])
print("\n")
print("RECURSIVE SPARSE GAUSSIAN PROCESS VARIABLES")
print("Number of Inducing Points:", num_ind_points)

# Generate Initial Rotorcraft Observations
rotor_obs_data = GeneratePowerObservations(actual_rotor_plot_data, rotor_info,
                                           rotor_data,
                                           num_obs, var_set).get_observation_data()

# RUN SPARSE GAUSSIAN PROCESS
sgp_pred_rotor_data = GenerateSGPPowerPrediction(rotor_info, rotor_data, actual_rotor_plot_data,
                                                 rotor_obs_data,
                                                 num_ind_points,
                                                 var_set).get_prediction_data()
new_pred_rotor_data = sgp_pred_rotor_data

# Generate Mobility Metrics

# Change scope to speed range for mobility metric calculations (Could be updated, works for these purposes)
indices = np.where(np.logical_and(new_pred_rotor_data['Testing Points X'] >= 0,
                                  new_pred_rotor_data['Testing Points X'] <= 110))
alt_sgp_pred_rotor_data = {'HPR Prediction': new_pred_rotor_data['HPR Prediction'][indices[0]],
                           'HPR Lower Bound': new_pred_rotor_data['HPR Lower Bound'][indices[0]],
                           'HPR Upper Bound': new_pred_rotor_data['HPR Upper Bound'][indices[0]],
                           'HPR Alpha': new_pred_rotor_data['HPR Alpha'],
                           'HPR Inducing Points': new_pred_rotor_data['HPR Inducing Points'],
                           'HPA Prediction': new_pred_rotor_data['HPA Prediction'][indices[0]],
                           'HPA Lower Bound': new_pred_rotor_data['HPA Lower Bound'][indices[0]],
                           'HPA Upper Bound': new_pred_rotor_data['HPA Upper Bound'][indices[0]],
                           'HPR Prediction Multi': new_pred_rotor_data['HPR Prediction Multi'],
                           'HPA Prediction Multi': new_pred_rotor_data['HPA Prediction Multi'],
                           'HPA Alpha': new_pred_rotor_data['HPA Alpha'],
                           'HPA Inducing Points': new_pred_rotor_data['HPA Inducing Points'],
                           'HPR Qm_inv': new_pred_rotor_data['HPR Qm_inv'],
                           'HPA Qm_inv': new_pred_rotor_data['HPA Qm_inv'],
                           'Inducing Points X': new_pred_rotor_data['Inducing Points X'],
                           'Testing Points X': new_pred_rotor_data['Testing Points X'][indices[0]]
                           }

# Generate Mobility Characteristics and Return Metrics
mobility_metric_object = GenerateMobilityMetrics(actual_rotor_plot_data, rotor_obs_data, alt_sgp_pred_rotor_data,
                                                 rotor_info)
mobility_metric_data = mobility_metric_object.get_mobility_data()

# Generate Mobility Characteristics and Return Error
mobility_metric_error = mobility_metric_object.get_mobility_perr()

#######################################################################################################################
# Start Recursive Method

new_data = []
mission_obs_data = []

mission_power_multi = copy.deepcopy(actual_power_multi)
rsgp_data = {'New Speed': None,
             'New HPR': None,
             'New HPA': None}
mission_rotor_data = None
metric_comparison_data = None

# Create File Structure
mission_metrics_data = {'Time': [],
                        'Bucket HPR': [],
                        'Bucket Speed': [],
                        'Max HPR': [],
                        'Max Speed': [],
                        'Max Range HPR': [],
                        'Max Range Speed': [],
                        'Max Range': [],
                        'Max Endurance': [],
                        'Max Climb HOV': [],
                        'Max Climb FF': []}

if recursion:
    collecting_data = True
    i = 0
    # Generate mission observations
    # new_data = ImportMeasurementData.get_rotorcraft_data()

    # Pulls observations from "actual data" that reflects NMP, MEMP, PCMP, or EFMP
    mission_rotor_data = evaluate_mission_property(mission_property, mission_power_multi, weight_set)

    # Save Actual Mission Metrics and Expected Metrics
    metric_comparison_data = save_mission_metrics(mission_rotor_data[0], mission_rotor_data[1], mobility_metric_data)

    # Scenario Observations
    mission_obs_data, time_factor = GeneratePowerObsFromScenario(mission_rotor_data[0],
                                                    False, mission_rotor_data[1],
                                                    mission_rotor_data[2],
                                                    mission_filename, var_set,
                                                    var_set, True).get_observation_data()

    # READ IN SCENARIO DATA
    sheet_name = 'Sheet1'
    data = pd.read_excel(os.getcwd() + "/Data/" + mission_filename, sheet_name=sheet_name)
    mission_metrics_data['Time'] = data['Time'].tolist()  # Set Time divisions

    # TODO: Calculate in code
    temp_end = len(mission_metrics_data['Time']) + time_factor  # Captures real observation range (Set during a time crunch.)

    new_data_x = mission_obs_data['Speed'][0:temp_end]

    new_data_hpr_y = mission_obs_data['HP Required'][0:temp_end]
    new_data_hpa_y = mission_obs_data['HP Available'][0:temp_end]
    # print(new_data_hpa_y)

    rsgp_pred_rotor_data = sgp_pred_rotor_data

    # # Open file for Mobility Metrics overtime file
    # mission_metrics = open('Data/Mission_Metrics.txt', 'w', encoding='UTF8', newline='')

    old_hpr = sgp_pred_rotor_data['HPR Prediction']
    old_hpa = sgp_pred_rotor_data['HPA Prediction']

    while collecting_data:
        j = i + 1
        # Run Recursive Method (mission_rotor_data[1]= rotor_info)
        rsgp_pred_rotor_data = GenerateRSGPPowerPrediction(mission_rotor_data[1], rsgp_pred_rotor_data, var_set,
                                                           var_set,
                                                           new_data_x[i],
                                                           new_data_hpr_y[i],
                                                           new_data_hpa_y[i], old_hpr, old_hpa).get_prediction_data()

        # Change scope to speed range for mobility metric calculations
        indices = np.where(np.logical_and(rsgp_pred_rotor_data['Testing Points X'] >= 0,
                                          rsgp_pred_rotor_data['Testing Points X'] <= 110))
        # print(len(indices[0]))

        alt_rsgp_pred_rotor_data = {'HPR Prediction': rsgp_pred_rotor_data['HPR Prediction'][indices[0]],
                                    'HPR Lower Bound': rsgp_pred_rotor_data['HPR Lower Bound'][indices[0]],
                                    'HPR Upper Bound': rsgp_pred_rotor_data['HPR Upper Bound'][indices[0]],
                                    'HPR Alpha': rsgp_pred_rotor_data['HPR Alpha'],
                                    'HPR Inducing Points': rsgp_pred_rotor_data['HPR Inducing Points'],
                                    'HPA Prediction': rsgp_pred_rotor_data['HPA Prediction'][indices[0]],
                                    'HPA Lower Bound': rsgp_pred_rotor_data['HPA Lower Bound'][indices[0]],
                                    'HPA Upper Bound': rsgp_pred_rotor_data['HPA Upper Bound'][indices[0]],
                                    'HPR Prediction Multi': rsgp_pred_rotor_data['HPR Prediction Multi'],
                                    'HPA Prediction Multi': rsgp_pred_rotor_data['HPA Prediction Multi'],
                                    'HPA Alpha': rsgp_pred_rotor_data['HPA Alpha'],
                                    'HPA Inducing Points': rsgp_pred_rotor_data['HPA Inducing Points'],
                                    'HPR Qm_inv': rsgp_pred_rotor_data['HPR Qm_inv'],
                                    'HPA Qm_inv': rsgp_pred_rotor_data['HPA Qm_inv'],
                                    'Inducing Points X': rsgp_pred_rotor_data['Inducing Points X'],
                                    'Testing Points X': rsgp_pred_rotor_data['Testing Points X'][indices[0]]
                                    }
        # TODO: Update Mobility Metrics versus time data
        # Only need the prediction values and ignoring all other calculations
        mobility_metric_rsgp_data = GenerateMobilityMetrics(actual_rotor_plot_data, mission_obs_data,
                                                            alt_rsgp_pred_rotor_data,
                                                            mission_rotor_data[1]).get_mobility_estimate()

        # Note: Get time from mission_file time vector
        # print(mobility_metric_rsgp_data['Max Speed Pred'])
        # Mission Metrics File
        # Time | 0, 1, 2, 3...
        # Metric1 | v1, v2, v3...
        # Metric2 | v1, v2, v3...
        mission_metrics_data['Bucket HPR'].append(mobility_metric_rsgp_data['Bucket HPR Pred'])
        mission_metrics_data['Bucket Speed'].append(mobility_metric_rsgp_data['Bucket Speed Pred'])
        mission_metrics_data['Max HPR'].append(mobility_metric_rsgp_data['Max HPR Pred'])
        mission_metrics_data['Max Speed'].append(mobility_metric_rsgp_data['Max Speed Pred'])
        mission_metrics_data['Max Range HPR'].append(mobility_metric_rsgp_data['Max HPR Range Pred'])
        mission_metrics_data['Max Range Speed'].append(mobility_metric_rsgp_data['Max Range Speed Pred'])
        mission_metrics_data['Max Range'].append(mobility_metric_rsgp_data['Max Range Pred'])
        mission_metrics_data['Max Endurance'].append(mobility_metric_rsgp_data['Max Endurance Pred'])
        mission_metrics_data['Max Climb HOV'].append(mobility_metric_rsgp_data['Max Climb HOV Pred'])
        mission_metrics_data['Max Climb FF'].append(mobility_metric_rsgp_data['Max Climb FF Pred'])

        i += 1
        # Condition for stopping data collection
        if i == len(new_data_x):
            break

    new_pred_rotor_data = rsgp_pred_rotor_data
    rsgp_data = {'New Speed': new_data_x,
                 'New HPR': new_data_hpr_y,
                 'New HPA': new_data_hpa_y}


# Plot Power Curves
run_plots = PlotData(rotor_data, actual_rotor_plot_data, actual_power_plot, rotor_obs_data, new_pred_rotor_data,
                     mission_obs_data, recursion, rsgp_data, mission_rotor_data, mission_metrics_data,
                     metric_comparison_data, mission_property, time_factor)

####################################################################################################
####################################################################################################
# End Main

