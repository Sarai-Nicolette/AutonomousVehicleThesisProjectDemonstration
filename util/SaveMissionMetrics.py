from util.GenerateMissionMobilityMetrics import GenerateMissionMobilityMetrics


def save_mission_metrics(mission_rotor_data, rotor_info, exp_mobility_metric_data):
    # Generate Mission Mobility Metrics
    mission_metrics = GenerateMissionMobilityMetrics(mission_rotor_data, rotor_info).generate_mmm()

    # Save Expected Mobility Metrics and Actual Mobility Metrics
    # Mobility Metric Titles M0 |M1 | M2 | ...
    # Expected Value
    # Actual Value

    metric_comparison_data = {
        'Bucket HPR': {'Expected': round(exp_mobility_metric_data['Bucket Speed']['Bucket HPR Actual'], 2),
                       'Prediction': round(exp_mobility_metric_data['Bucket Speed']['Bucket HPR Pred'], 2),
                       'Actual': round(mission_metrics['Bucket HPR Actual'], 2)},
        'Bucket Speed': {'Expected': round(exp_mobility_metric_data['Bucket Speed']['Bucket Speed Actual'], 2),
                         'Prediction': round(exp_mobility_metric_data['Bucket Speed']['Bucket Speed Pred'], 2),
                         'Actual': round(mission_metrics['Bucket Speed Actual'], 2)},
        'Max HPR': {'Expected': round(exp_mobility_metric_data['Max Speed']['Max HPR Actual'], 2),
                    'Prediction': round(exp_mobility_metric_data['Max Speed']['Max HPR Pred'], 2),
                    'Actual': round(mission_metrics['Max HPR Actual'], 2)},
        'Max Speed': {'Expected': round(exp_mobility_metric_data['Max Speed']['Max Speed Actual'], 2),
                      'Prediction': round(exp_mobility_metric_data['Max Speed']['Max Speed Pred'], 2),
                      'Actual': round(mission_metrics['Max Speed Actual'], 2)},
        'Max Range HPR': {'Expected': round(exp_mobility_metric_data['Max Range']['Max Range HPR Actual'], 2),
                          'Prediction': round(exp_mobility_metric_data['Max Range']['Max Range HPR Pred'], 2),
                          'Actual': round(mission_metrics['Max Range HPR Actual'], 2)},
        'Max Range Speed': {'Expected': round(exp_mobility_metric_data['Max Range']['Max Range Speed Actual'], 2),
                            'Prediction': round(exp_mobility_metric_data['Max Range']['Max Range Speed Pred'], 2),
                            'Actual': round(mission_metrics['Max Range Speed Actual'], 2)},
        'Max Range': {'Expected': round(exp_mobility_metric_data['Max Range']['Max Range Actual'], 2),
                      'Prediction': round(exp_mobility_metric_data['Max Range']['Max Range Pred'], 2),
                      'Actual': round(mission_metrics['Max Range Actual'], 2)},
        'Max Endurance': {'Expected': round(exp_mobility_metric_data['Max Endurance']['HPR Endurance Actual'], 2),
                          'Prediction': round(exp_mobility_metric_data['Max Endurance']['HPR Endurance Pred'], 2),
                          'Actual': round(mission_metrics['Max Endurance Actual'], 2)},
        'Max Climb HOV': {'Expected': round(exp_mobility_metric_data['Max Climb']['HOV VROC Actual'], 2),
                          'Prediction': round(exp_mobility_metric_data['Max Climb']['HOV VROC Pred'], 2),
                          'Actual': round(mission_metrics['Max Climb HOV Actual'], 2)},
        'Max Climb FF': {'Expected': round(exp_mobility_metric_data['Max Climb']['FF VROC Actual'], 2),
                         'Prediction': round(exp_mobility_metric_data['Max Climb']['FF VROC Pred'], 2),
                         'Actual': round(mission_metrics['Max Climb FF Actual'], 2)},
    }

    # Return mission_metrics
    return metric_comparison_data


class SaveMissionMetrics:

    def __init__(self):
        pass
