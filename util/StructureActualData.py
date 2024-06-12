# Import Libraries
from util.ImportRotorcraftData import ImportRotorcraftData as rotorInfo
from util.GeneratePowerCurve import GeneratePowerCurveData
from util.InterpolateData import InterpolateData


class StructureActualData:
    def __init__(self, weight_set, damage_eng_set):
        self.weight_set = weight_set
        self.damage_eng_set = damage_eng_set
        # Temp Storage for actual data
        self.save_actual_rotor_data = []
        # Weight and Damaged Engine Settings to Loop Through
        self.config = ['Mid', 'Max', 'Mid', 'Max']  # Weight Config ['Mid', 'Max', 'Mid', 'Max']
        self.damaged_engine = [False, False, True, True]  # Engine Config [False, False, True, True]

        # Dictionary structure for storing actual rotorcraft data
        self.actual_power_plot = {'Mid_AEO': {'HPR': [], 'HPA': [], 'Speed': [], 'CPR': [], 'CPA': [], 'Mu': []},
                                  'Max_AEO': {'HPR': [], 'HPA': [], 'Speed': [], 'CPR': [], 'CPA': [], 'Mu': []},
                                  'Mid_OEI': {'HPR': [], 'HPA': [], 'Speed': [], 'CPR': [], 'CPA': [], 'Mu': []},
                                  'Max_OEI': {'HPR': [], 'HPA': [], 'Speed': [], 'CPR': [], 'CPA': [], 'Mu': []}
                                  }
        self.actual_power_multi = {'Mid_AEO': {'ACT': {}, 'RI': {}, 'RD': {}},
                                   'Max_AEO': {'ACT': {}, 'RI': {}, 'RD': {}},
                                   'Mid_OEI': {'ACT': {}, 'RI': {}, 'RD': {}},
                                   'Max_OEI': {'ACT': {}, 'RI': {}, 'RD': {}}
                                   }

    def get_all_rotorcraft_data(self):
        for i in range(0, len(self.config)):

            weight_name = self.config[i]  # Mid and Max

            # Rotorcraft Type (UH60) (1P6R12F4_MidWgt) (1P6R12V4C0_MidWgt)
            rotorcraft_design = "1P6R12V4C0_" + weight_name + "Wgt"
            # Engine Loss
            oei = self.damaged_engine[i]

            # JSON_FILE_NAME = rotorcraft_design + "_rotorcraft.json"
            JSON_FILE_NAME = "1P6R12V4C0_" + weight_name + "Wgt_rotorcraft.json"
            DATA_FILE_NAME = rotorcraft_design + "_data.csv"

            # Import Json File with Initial Input Data
            rotor_info, rotor_data = rotorInfo(JSON_FILE_NAME, DATA_FILE_NAME).get_rotorcraft_data()

            # Interpolates Fragmented Data
            rotor_info, rotor_data = InterpolateData(rotor_info, rotor_data, oei).interpolate_and_return()

            # Generate Actual Rotorcraft Power Curve
            actual_rotor_data = GeneratePowerCurveData(rotor_info, rotor_data)
            actual_rotor_plot_data = actual_rotor_data.get_data_output()

            # Save for plotting
            if self.config[i] == 'Mid' and not self.damaged_engine[i]:
                self.actual_power_plot['Mid_AEO']['HPR'] = actual_rotor_plot_data['HP Required']
                self.actual_power_plot['Mid_AEO']['HPA'] = actual_rotor_plot_data['HP Available']
                self.actual_power_plot['Mid_AEO']['Speed'] = actual_rotor_plot_data['Speed']
                self.actual_power_plot['Mid_AEO']['CPR'] = actual_rotor_plot_data['CP Required']
                self.actual_power_plot['Mid_AEO']['CPA'] = actual_rotor_plot_data['CP Available']
                self.actual_power_plot['Mid_AEO']['Mu'] = actual_rotor_plot_data['Mu']
                self.actual_power_multi['Mid_AEO']['ACT'] = actual_rotor_plot_data
                self.actual_power_multi['Mid_AEO']['RI'] = rotor_info
                self.actual_power_multi['Mid_AEO']['RD'] = rotor_data
                # Save actual data
                if self.weight_set == 'Mid' and not self.damage_eng_set:
                    self.save_actual_rotor_data.append(self.actual_power_multi['Mid_AEO']['ACT'])
                    self.save_actual_rotor_data.append(self.actual_power_multi['Mid_AEO']['RI'])
                    self.save_actual_rotor_data.append(self.actual_power_multi['Mid_AEO']['RD'])
            elif self.config[i] == 'Max' and not self.damaged_engine[i]:
                self.actual_power_plot['Max_AEO']['HPR'] = actual_rotor_plot_data['HP Required']
                self.actual_power_plot['Max_AEO']['HPA'] = actual_rotor_plot_data['HP Available']
                self.actual_power_plot['Max_AEO']['Speed'] = actual_rotor_plot_data['Speed']
                self.actual_power_plot['Max_AEO']['CPR'] = actual_rotor_plot_data['CP Required']
                self.actual_power_plot['Max_AEO']['CPA'] = actual_rotor_plot_data['CP Available']
                self.actual_power_plot['Max_AEO']['Mu'] = actual_rotor_plot_data['Mu']
                self.actual_power_multi['Max_AEO']['ACT'] = actual_rotor_plot_data
                self.actual_power_multi['Max_AEO']['RI'] = rotor_info
                self.actual_power_multi['Max_AEO']['RD'] = rotor_data
                # Save actual data
                if self.weight_set == 'Max' and not self.damage_eng_set:
                    self.save_actual_rotor_data.append(self.actual_power_multi['Max_AEO']['ACT'])
                    self.save_actual_rotor_data.append(self.actual_power_multi['Max_AEO']['RI'])
                    self.save_actual_rotor_data.append(self.actual_power_multi['Max_AEO']['RD'])

            elif self.config[i] == 'Mid' and self.damaged_engine[i]:
                self.actual_power_plot['Mid_OEI']['HPR'] = actual_rotor_plot_data['HP Required']
                self.actual_power_plot['Mid_OEI']['HPA'] = actual_rotor_plot_data['HP Available']
                self.actual_power_plot['Mid_OEI']['Speed'] = actual_rotor_plot_data['Speed']
                self.actual_power_plot['Mid_OEI']['CPR'] = actual_rotor_plot_data['CP Required']
                self.actual_power_plot['Mid_OEI']['CPA'] = actual_rotor_plot_data['CP Available']
                self.actual_power_plot['Mid_OEI']['Mu'] = actual_rotor_plot_data['Mu']
                self.actual_power_multi['Mid_OEI']['ACT'] = actual_rotor_plot_data
                self.actual_power_multi['Mid_OEI']['RI'] = rotor_info
                self.actual_power_multi['Mid_OEI']['RD'] = rotor_data
                # Save actual data
                if self.weight_set == 'Mid' and self.damage_eng_set:
                    self.save_actual_rotor_data.append(self.actual_power_multi['Mid_OEI']['ACT'])
                    self.save_actual_rotor_data.append(self.actual_power_multi['Mid_OEI']['RI'])
                    self.save_actual_rotor_data.append(self.actual_power_multi['Mid_OEI']['RD'])
            else:
                self.actual_power_plot['Max_OEI']['HPR'] = actual_rotor_plot_data['HP Required']
                self.actual_power_plot['Max_OEI']['HPA'] = actual_rotor_plot_data['HP Available']
                self.actual_power_plot['Max_OEI']['Speed'] = actual_rotor_plot_data['Speed']
                self.actual_power_plot['Max_OEI']['CPR'] = actual_rotor_plot_data['CP Required']
                self.actual_power_plot['Max_OEI']['CPA'] = actual_rotor_plot_data['CP Available']
                self.actual_power_plot['Max_OEI']['Mu'] = actual_rotor_plot_data['Mu']
                self.actual_power_multi['Max_OEI']['ACT'] = actual_rotor_plot_data
                self.actual_power_multi['Max_OEI']['RI'] = rotor_info
                self.actual_power_multi['Max_OEI']['RD'] = rotor_data
                # Save actual data
                if self.weight_set == 'Max' and self.damage_eng_set:
                    self.save_actual_rotor_data.append(self.actual_power_multi['Max_OEI']['ACT'])
                    self.save_actual_rotor_data.append(self.actual_power_multi['Max_OEI']['RI'])
                    self.save_actual_rotor_data.append(self.actual_power_multi['Max_OEI']['RD'])

        actual_rotor_plot_data = self.save_actual_rotor_data[0]
        rotor_info, rotor_data = self.save_actual_rotor_data[1], self.save_actual_rotor_data[2]
        return actual_rotor_plot_data, rotor_info, rotor_data, self.actual_power_multi, self.actual_power_plot
