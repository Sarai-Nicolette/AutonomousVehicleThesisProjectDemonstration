import numpy as np
import pandas as pd

class InterpolateData:

    def __init__(self, rotor_info, rotor_data, oei):
        self.rotor_info = rotor_info
        self.rotor_data = rotor_data
        self.oei = oei
        self.max_speed = int(rotor_info["rotorcraft_init"]["maxAirspeed"])

    def interpolate_and_return(self):
        # Check whether data needs to be interpolated and return interpolation
        if self.rotor_info["rotorcraft_init"]["interpolate"]:
            x = len(self.rotor_data['HPR'])
            x_points_new = np.linspace(0, self.max_speed, num=self.max_speed)
            x_points_old = np.array(self.rotor_data['Speed'])
            hpr = np.interp(x_points_new, x_points_old, self.rotor_data['HPR']).tolist()
            hpa_cont = np.interp(x_points_new, x_points_old, self.rotor_data['HPA_cont']).tolist()
            vtip = np.interp(x_points_new, x_points_old, self.rotor_data['Vtip']).tolist()
            xflat = np.interp(x_points_new, x_points_old, self.rotor_data['Xflat']).tolist()
            hpa_emrax_cont_d = np.interp(x_points_new, x_points_old, self.rotor_data['HPA_EMRAX_cont_d']).tolist()
            hpa_emrax_cont = np.interp(x_points_new, x_points_old, self.rotor_data['HPA_EMRAX_cont']).tolist()
            hpa_eng_cont_d = np.interp(x_points_new, x_points_old, self.rotor_data['HPA_Nacelle_cont_d']).tolist()
            hpa_eng_cont = np.interp(x_points_new, x_points_old, self.rotor_data['HPA_Nacelle_cont']).tolist()
            hpa_emrax_int_d = np.interp(x_points_new, x_points_old, self.rotor_data['HPA_EMRAX_30_d']).tolist()
            hpa_eng_int_d = np.interp(x_points_new, x_points_old, self.rotor_data['HPA_Nacelle_30_d']).tolist()
            hpi = np.interp(x_points_new, x_points_old, self.rotor_data['HPI']).tolist()
            hppr = np.interp(x_points_new, x_points_old, self.rotor_data['HPPr']).tolist()

            # Calculate HPA Value
            if self.rotor_info["rotorcraft_init"]["engine"] == "intermediate":
                # Calculate HPA Intermediate Value
                hpa_eng = [hpr[i] + hpa_eng_int_d[i] for i in range(len(hpr))]
                hpa_emrax = [hpr[i] + hpa_emrax_int_d[i] for i in range(len(hpr))]
            else:
                # Calculate HPA Continuous Value
                hpa_eng = [hpr[i] + hpa_eng_cont_d[i] for i in range(len(hpr))]
                hpa_emrax = [hpr[i] + hpa_emrax_cont_d[i] for i in range(len(hpr))]

            # Find Limiting factor between EMRAX Generator and Engine
            if self.oei:
                # Reduces Full HPA by 25%
                hpa = [min(hpa_eng[i], hpa_emrax[i]) * 0.75 for i in range(len(hpr))]
            else:
                hpa = [min(hpa_eng[i], hpa_emrax[i]) for i in range(len(hpr))]
            # Overwrite rotor_data file
            new_data = {'Speed': x_points_new,
                        'HPR': hpr,
                        'HPA': hpa,
                        'HPA_cont': hpa_cont,
                        'Vtip': vtip,
                        'Xflat': xflat,
                        'HPA_EMRAX_cont_d': hpa_emrax_cont_d,
                        'HPA_EMRAX_cont': hpa_emrax_cont,
                        'HPA_Nacelle_cont_d': hpa_eng_cont_d,
                        'HPA_Nacelle_cont': hpa_eng_cont,
                        'HPA_EMRAX_30_d': hpa_emrax_int_d,
                        'HPA_Nacelle_30_d': hpa_eng_cont_d,
                        'HPA_EMRAX': hpa_emrax,
                        'HPA_ENG': hpa_eng,
                        'HPI': hpi,
                        'HPPr': hppr
                        }

            self.rotor_data = pd.DataFrame(new_data)

            return self.rotor_info, self.rotor_data
