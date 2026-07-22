import os
import json
import logging
from copy import deepcopy


logging.basicConfig(level=logging.INFO, format="%(levelname)s : %(message)s")
# ---------------- PATHS ---------------- #
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BIOMECH_OUTPUT_DIR = os.path.join(BASE_DIR, "biomechanics_output")
OUTPUT_DIR = os.path.join(BASE_DIR, "app","middleware","combined_attribute_outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# HEAD POSITION & STABILITY COMBINER :
def combine_head_position_stability(phase_name: str):
    """
    Combines Head Position & Stability metrics
    from all biomechanics json files for a given phase.
    Parameters:
    -----------
    phase_name : str
        Example:
        - "Gather Phase"
        - "Delivery Stride"
    """
    # ---------------- PARAMETERS TO EXTRACT ---------------- #

    required_parameters = ["signed_mean", "abs_mean", "std_dev", "max_abs", "head_stability_std_x"]

    # ---------------- MASTER STORAGE ---------------- #

    combined_data = {}
    for parameter in required_parameters:        
        combined_data[parameter] = []

    # ---------------- FILE LIST ---------------- #

    json_files = [
        file for file in os.listdir(BIOMECH_OUTPUT_DIR)
        if file.endswith(".json")
    ]

    if len(json_files) == 0:
        logging.warning("No JSON files found in biomechanics_output folder.")
        return

    # ---------------- PHASE EXISTENCE CHECK ---------------- #

    phase_exists = False

    for file_name in json_files:
        file_path = os.path.join(BIOMECH_OUTPUT_DIR, file_name)
        try:
            with open(file_path, "r") as f:
                data = json.load(f)

            if (phase_name in data and "Head Position & Stability" in data[phase_name]):
                phase_exists = True
                break

        except Exception as e:
            logging.error(f"Error reading file {file_name} : {e}")

    if not phase_exists:
        logging.warning(
            f"'Head Position & Stability' does not exist "
            f"for phase : '{phase_name}'"
        )
        logging.info("Please enter a correct phase name.")
        return

    # MAIN COMBINATION LOGIC :

    for file_name in json_files:

        try:
            with open(os.path.join(BIOMECH_OUTPUT_DIR, file_name), "r") as f:
                data = json.load(f)

            attribute_data = data[phase_name]["Head Position & Stability"]

            # ---------------- EXTRACT PARAMETERS ---------------- #
            for parameter in required_parameters:
                value = attribute_data[parameter]
                combined_data[parameter].append(value)

        except Exception as e:
            logging.error(f"Error processing file {file_name} : {e}")

    # SORT ALL PARAMETERS

    for parameter in required_parameters:
        combined_data[parameter] = sorted(combined_data[parameter])

    # FINAL OUTPUT JSON

    final_output = {
        "phase": phase_name,
        "attribute": "Head Position & Stability",
        "combined_parameters": combined_data
    }

    # SAVE JSON

    # safe_phase_name = phase_name.replace(" ", "_")

    # output_file_name = (f"{safe_phase_name}_head_position_stability.json")
    # output_file_path = os.path.join(OUTPUT_DIR, output_file_name)

    # with open(output_file_path, "w") as f:
    #     json.dump(final_output, f, indent=4)

    # logging.info(f"Combined JSON saved successfully at :\n{output_file_path}")

    return final_output

# HIP DIRECTION AS THE BOWLER LOADS UP COMBINER :
def combine_hip_direction_as_bowler_loads_up(phase_name: str):
    """
    Combines Hip direction as the bowler loads up metrics
    from all biomechanics json files for a given phase.

    Parameters:
    -----------
    phase_name : str
        Example:
        - "Gather Phase"
        - "Backfoot Phase"
    """

    # ---------------- PARAMETERS TO EXTRACT ---------------- #

    required_parameters = ["signed_mean", "abs_mean", "std_dev", "max_abs"]

    # ---------------- MASTER STORAGE ---------------- #

    combined_data = {}
    for parameter in required_parameters:
        combined_data[parameter] = []

    # ---------------- FILE LIST ---------------- #

    json_files = [
        file for file in os.listdir(BIOMECH_OUTPUT_DIR)
        if file.endswith(".json")
    ]

    if len(json_files) == 0:
        logging.warning("No JSON files found in biomechanics_output folder.")
        return

    # ---------------- PHASE EXISTENCE CHECK ---------------- #

    phase_exists = False
    for file_name in json_files:

        try:
            with open(os.path.join(BIOMECH_OUTPUT_DIR,file_name), "r") as f:
                data = json.load(f)

            if (phase_name in data and "Hip direction as the bowler loads up"in data[phase_name]):
                phase_exists = True
                break

        except Exception as e:
            logging.error(f"Error reading file {file_name} : {e}")

    if not phase_exists:
        logging.warning(f"'Hip direction as the bowler loads up does not exist for phase : '{phase_name}'")
        logging.info("Please enter a correct phase name.")
        return

    # MAIN COMBINATION LOGIC :

    for file_name in json_files:

        try:
            with open(os.path.join(BIOMECH_OUTPUT_DIR,file_name), "r") as f:
                data = json.load(f)

            attribute_data = data[phase_name]["Hip direction as the bowler loads up"]

            # ---------------- EXTRACT PARAMETERS ---------------- #
            for parameter in required_parameters:
                value = attribute_data[parameter]
                combined_data[parameter].append(value)

        except Exception as e:
            logging.error(f"Error processing file {file_name} : {e}")

    # SORT ALL PARAMETERS

    for parameter in required_parameters:
        combined_data[parameter] = sorted(combined_data[parameter])

    # FINAL OUTPUT JSON

    final_output = {
        "phase": phase_name,
        "attribute": "Hip direction as the bowler loads up",
        "combined_parameters": combined_data
    }

    # SAVE JSON

    # safe_phase_name = phase_name.replace(" ", "_")
    # output_file_name = (f"{safe_phase_name}_hip_direction_as_bowler_loads_up.json")
    # output_file_path = os.path.join(OUTPUT_DIR,output_file_name)

    # with open(output_file_path, "w") as f:
    #     json.dump(final_output, f, indent=4)

    # logging.info(f"Combined JSON saved successfully at : {output_file_path}")

    return final_output

# HIP-SHOULDER ALIGNMENT COMBINER :
def combine_hip_shoulder_alignment(phase_name: str):
    """
    Combines Hip-Shoulder Alignment metrics
    from all biomechanics json files for a given phase.

    Parameters:
    -----------
    phase_name : str
        Example:
        - "Gather Phase"
        - "Delivery Stride"
        - "Frontfoot Phase"
    """

    # ---------------- PARAMETERS TO EXTRACT ---------------- #

    required_parameters = ["abs_mean", "std_dev", "max_abs"]

    # ---------------- MASTER STORAGE ---------------- #

    combined_data = {}
    for parameter in required_parameters:
        combined_data[parameter] = []

    # ---------------- FILE LIST ---------------- #

    json_files = [
        file for file in os.listdir(BIOMECH_OUTPUT_DIR)
        if file.endswith(".json")
    ]

    if len(json_files) == 0:
        logging.warning("No JSON files found in biomechanics_output folder.")
        return

    # ---------------- PHASE EXISTENCE CHECK ---------------- #

    phase_exists = False
    for file_name in json_files:

        try:
            with open(os.path.join(BIOMECH_OUTPUT_DIR, file_name), "r") as f:
                data = json.load(f)

            if (phase_name in data and "Hip-Shoulder Alignment" in data[phase_name]):
                phase_exists = True
                break

        except Exception as e:
            logging.error(f"Error reading file {file_name} : {e}")

    if not phase_exists:
        logging.warning(f"Hip-Shoulder Alignment does not exist for phase : '{phase_name}'")
        logging.info("Please enter a correct phase name.")
        return

    # MAIN COMBINATION LOGIC :

    for file_name in json_files:

        try:
            with open( os.path.join( BIOMECH_OUTPUT_DIR, file_name),"r") as f:
                data = json.load(f)

            attribute_data = data[phase_name]["Hip-Shoulder Alignment"]

            # ---------------- EXTRACT PARAMETERS ---------------- #

            for parameter in required_parameters:
                value = attribute_data[parameter]
                combined_data[parameter].append(value)

        except Exception as e:
            logging.error(f"Error processing file {file_name} : {e}")

    # SORT ALL PARAMETERS :

    for parameter in required_parameters:
        combined_data[parameter] = sorted(combined_data[parameter])

    # FINAL OUTPUT JSON :

    final_output = {
        "phase": phase_name,
        "attribute": "Hip-Shoulder Alignment",
        "combined_parameters": combined_data
    }

    # SAVE JSON :

    # safe_phase_name = phase_name.replace(" ", "_")
    # output_file_name = (f"{safe_phase_name}_hip_shoulder_alignment.json")
    # output_file_path = os.path.join(OUTPUT_DIR, output_file_name)
    # with open(output_file_path, "w") as f:
    #     json.dump(final_output, f, indent=4)

    # logging.info(f"Combined JSON saved successfully at : {output_file_path}")

    return final_output

# SHOULDER TILT PROGRESSION COMBINER :
def combine_shoulder_tilt_progression(phase_name: str):
    """
    Combines Shoulder Tilt Progression metrics
    from all biomechanics json files for a given phase.

    Parameters:
    -----------
    phase_name : str
        Example:
        - "Gather Phase"
    """

    # ---------------- PARAMETERS TO EXTRACT ---------------- #

    required_parameters = ["smoothness_score", "std_dev_tilt"]

    # ---------------- MASTER STORAGE ---------------- #

    combined_data = {}
    for parameter in required_parameters:
        combined_data[parameter] = []

    # ---------------- FILE LIST ---------------- #

    json_files = [
        file for file in os.listdir(BIOMECH_OUTPUT_DIR)
        if file.endswith(".json")
    ]

    if len(json_files) == 0:
        logging.warning("No JSON files found in biomechanics_output folder.")
        return

    # ---------------- PHASE EXISTENCE CHECK ---------------- #

    phase_exists = False
    for file_name in json_files:


        try:
            with open(os.path.join(BIOMECH_OUTPUT_DIR, file_name), "r") as f:
                data = json.load(f)

            if (phase_name in data and "Shoulder Tilt Progression" in data[phase_name]):
                phase_exists = True
                break

        except Exception as e:
            logging.error(f"Error reading file {file_name} : {e}")

    if not phase_exists:
        logging.warning(f"Shoulder Tilt Progression does not exist for phase : '{phase_name}'")
        logging.info("Please enter a correct phase name.")
        return

    # MAIN COMBINATION LOGIC :

    for file_name in json_files:

        try:
            with open(os.path.join(BIOMECH_OUTPUT_DIR, file_name ), "r") as f:
                data = json.load(f)

            attribute_data = data[phase_name]["Shoulder Tilt Progression"]

            # ---------------- EXTRACT PARAMETERS ---------------- #
            for parameter in required_parameters:
                value = attribute_data[parameter]
                combined_data[parameter].append(value)

        except Exception as e:
            logging.error(f"Error processing file {file_name} : {e}")

    # SORT ALL PARAMETERS :

    for parameter in required_parameters:
        combined_data[parameter] = sorted(combined_data[parameter])

    # FINAL OUTPUT JSON :

    final_output = {
        "phase": phase_name,
        "attribute": "Shoulder Tilt Progression",
        "combined_parameters": combined_data
    }

    # SAVE JSON :

    # safe_phase_name = phase_name.replace(" ", "_")
    # output_file_name = (f"{safe_phase_name}_shoulder_tilt_progression.json")
    # output_file_path = os.path.join(OUTPUT_DIR, output_file_name)

    # with open(output_file_path, "w") as f:
    #     json.dump(final_output, f, indent=4)
    # logging.info(f"Combined JSON saved successfully at : {output_file_path}")

    return final_output

# KNEE ANGLE COMBINER :
def combine_knee_angle(phase_name: str):
    """
    Combines Knee Angle metrics
    from all biomechanics json files for a given phase.

    Parameters:
    -----------
    phase_name : str
        Example:
        - "Backfoot Phase"
    """

    # ---------------- PARAMETERS TO EXTRACT ---------------- #

    required_parameters = ["back_knee_mean", "back_knee_std", "back_knee_min", "back_knee_max"]

    # ---------------- MASTER STORAGE ---------------- #

    combined_data = {}
    for parameter in required_parameters:
        combined_data[parameter] = []

    # ---------------- FILE LIST ---------------- #

    json_files = [
        file for file in os.listdir(BIOMECH_OUTPUT_DIR)
        if file.endswith(".json")
    ]

    if len(json_files) == 0:
        logging.warning("No JSON files found in biomechanics_output folder.")
        return

    # ---------------- PHASE EXISTENCE CHECK ---------------- #

    phase_exists = False
    for file_name in json_files:

        try:
            with open(os.path.join(BIOMECH_OUTPUT_DIR, file_name), "r") as f:
                data = json.load(f)

            if (phase_name in data and "Knee Angle" in data[phase_name]):
                phase_exists = True
                break

        except Exception as e:
            logging.error(f"Error reading file {file_name} : {e}")

    if not phase_exists:
        logging.warning(f"Knee Angle does not exist for phase : '{phase_name}'")
        logging.info("Please enter a correct phase name.")
        return

    # MAIN COMBINATION LOGIC :

    for file_name in json_files:

        try:
            with open(os.path.join(BIOMECH_OUTPUT_DIR, file_name ), "r") as f:
                data = json.load(f)

            attribute_data = data[phase_name]["Knee Angle"]

            # ---------------- EXTRACT PARAMETERS ---------------- #

            for parameter in required_parameters:
                value = attribute_data[parameter]
                combined_data[parameter].append(value)

        except Exception as e:
            logging.error(f"Error processing file {file_name} : {e}")

    # SORT ALL PARAMETERS :

    for parameter in required_parameters:
        combined_data[parameter] = sorted(combined_data[parameter])

    # FINAL OUTPUT JSON :

    final_output = {
        "phase": phase_name,
        "attribute": "Knee Angle",
        "combined_parameters": combined_data
    }

    # SAVE JSON :

    # safe_phase_name = phase_name.replace(" ", "_")
    # output_file_name = (f"{safe_phase_name}_knee_angle.json")
    # output_file_path = os.path.join(OUTPUT_DIR, output_file_name)

    # with open(output_file_path, "w") as f:
    #     json.dump(final_output, f, indent=4)

    # logging.info(f"Combined JSON saved successfully at : {output_file_path}")

    return final_output

# DELIVERY STRIDE DIRECTION COMBINER :
def combine_delivery_stride_direction(phase_name: str):
    """
    Combines Delivery Stride Direction metrics
    from all biomechanics json files for a given phase.

    Parameters:
    -----------
    phase_name : str
        Example:
        - "Delivery Stride"
    """

    # ---------------- PARAMETERS TO EXTRACT ---------------- #

    required_parameters = ["stride_direction_angle_deg"]

    # ---------------- MASTER STORAGE ---------------- #

    combined_data = {}
    for parameter in required_parameters:
        combined_data[parameter] = []

    # ---------------- FILE LIST ---------------- #

    json_files = [
        file for file in os.listdir(BIOMECH_OUTPUT_DIR)
        if file.endswith(".json")
    ]

    if len(json_files) == 0:
        logging.warning("No JSON files found in biomechanics_output folder.")
        return

    # ---------------- PHASE EXISTENCE CHECK ---------------- #

    phase_exists = False
    for file_name in json_files:

        try:
            with open(os.path.join(BIOMECH_OUTPUT_DIR, file_name), "r") as f:
                data = json.load(f)

            if (phase_name in data and "Delivery Stride Direction" in data[phase_name]):
                phase_exists = True
                break

        except Exception as e:
            logging.error(f"Error reading file {file_name} : {e}")

    if not phase_exists:
        logging.warning(f"Delivery Stride Direction does not exist for phase : '{phase_name}'")
        logging.info("Please enter a correct phase name.")
        return

    # MAIN COMBINATION LOGIC :

    for file_name in json_files:

        try:
            with open(os.path.join(BIOMECH_OUTPUT_DIR, file_name), "r") as f:
                data = json.load(f)

            attribute_data = data[phase_name]["Delivery Stride Direction"]

            # ---------------- EXTRACT PARAMETERS ---------------- #

            for parameter in required_parameters:
                value = attribute_data[parameter]
                combined_data[parameter].append(value)

        except Exception as e:
            logging.error(f"Error processing file {file_name} : {e}")

    # SORT ALL PARAMETERS :

    for parameter in required_parameters:
        combined_data[parameter] = sorted(combined_data[parameter])

    # FINAL OUTPUT JSON :

    final_output = {
        "phase": phase_name,
        "attribute": "Delivery Stride Direction",
        "combined_parameters": combined_data
    }

    # SAVE JSON :

    # safe_phase_name = phase_name.replace(" ", "_")
    # output_file_name = (f"{safe_phase_name}_delivery_stride_direction.json")
    # output_file_path = os.path.join(OUTPUT_DIR, output_file_name)

    # with open(output_file_path, "w") as f:
    #     json.dump(final_output, f, indent=4)

    # logging.info(f"Combined JSON saved successfully at : {output_file_path}")

    return final_output

# TRUNK LATERAL FLEXION COMBINER :
def combine_trunk_lateral_flexion(phase_name: str):
    """
    Combines Trunk Lateral Flexion metrics
    from all biomechanics json files for a given phase.

    Parameters:
    -----------
    phase_name : str
        Example:
        - "Delivery Stride"
        - "Frontfoot phase"
        - "Follow Through"
    """

    # ---------------- PARAMETERS TO EXTRACT ---------------- #

    required_parameters = ["abs_mean", "std_dev"]

    # ---------------- MASTER STORAGE ---------------- #

    combined_data = {}
    for parameter in required_parameters:
        combined_data[parameter] = []

    # ---------------- FILE LIST ---------------- #

    json_files = [
        file for file in os.listdir(BIOMECH_OUTPUT_DIR)
        if file.endswith(".json")
    ]

    if len(json_files) == 0:
        logging.warning("No JSON files found in biomechanics_output folder.")
        return

    # ---------------- PHASE EXISTENCE CHECK ---------------- #

    phase_exists = False
    for file_name in json_files:

        try:
            with open(os.path.join(BIOMECH_OUTPUT_DIR, file_name), "r") as f:
                data = json.load(f)

            if (phase_name in data and "Trunk Lateral Flexion" in data[phase_name]):
                phase_exists = True
                break

        except Exception as e:
            logging.error(f"Error reading file {file_name} : {e}")

    if not phase_exists:
        logging.warning(f"Trunk Lateral Flexion does not exist for phase : '{phase_name}'")
        logging.info("Please enter a correct phase name.")
        return

    # MAIN COMBINATION LOGIC :
    for file_name in json_files:

        try:
            with open(os.path.join(BIOMECH_OUTPUT_DIR, file_name),"r") as f:
                data = json.load(f)

            attribute_data = data[phase_name]["Trunk Lateral Flexion"]

            # ---------------- EXTRACT PARAMETERS ---------------- #

            for parameter in required_parameters:
                value = attribute_data[parameter]
                combined_data[parameter].append(value)

        except Exception as e:
            logging.error(f"Error processing file {file_name} : {e}")

    # SORT ALL PARAMETERS :

    for parameter in required_parameters:
        combined_data[parameter] = sorted(combined_data[parameter])

    # FINAL OUTPUT JSON :

    final_output = {
        "phase": phase_name,
        "attribute": "Trunk Lateral Flexion",
        "combined_parameters": combined_data
    }

    # SAVE JSON :

    # safe_phase_name = phase_name.replace(" ", "_")
    # output_file_name = (f"{safe_phase_name}_trunk_lateral_flexion.json")
    # output_file_path = os.path.join(OUTPUT_DIR, output_file_name)

    # with open(output_file_path, "w") as f:
    #     json.dump(final_output, f, indent=4)

    # logging.info(f"Combined JSON saved successfully at : {output_file_path}")

    return final_output

# GENERATE TERTILE THRESHOLDS :
def generate_tertile_thresholds(combined_distribution_data: dict):
    """
    Generates 1/3 and 2/3 thresholds
    for every phase -> attribute -> parameter.

    Parameters:
    -----------
    combined_distribution_data : dict
        Final combined biomechanics distribution JSON

    Returns:
    --------
    dict
        Threshold distribution data
    """

    # FINAL THRESHOLD STORAGE :

    threshold_distribution = {}

    # PHASE LOOP ;

    for phase_name, phase_data in combined_distribution_data.items():

        threshold_distribution[phase_name] = {}

        # ATTRIBUTE LOOP

        for attribute_name, attribute_data in phase_data.items():

            threshold_distribution[phase_name][attribute_name] = {}

            # PARAMETERS
            combined_parameters = attribute_data["combined_parameters"]

            # PARAMETER LOOP
            for parameter_name, values in combined_parameters.items():

                total_values = len(values)

                # ---------------- TERTILE INDICES ---------------- #
                first_tertile_index = total_values // 3
                second_tertile_index = ((2 * total_values) // 3)

                # ---------------- TERTILE VALUES ---------------- #
                first_tertile_value = values[first_tertile_index]
                second_tertile_value = values[second_tertile_index]

                # STORE OUTPUT
                threshold_distribution[phase_name][attribute_name][parameter_name] = {
                                                                        "classification_ranges": {
                                                                            "low": [values[0], first_tertile_value],
                                                                            "medium": [first_tertile_value, second_tertile_value],
                                                                            "high": [second_tertile_value, values[-1]]
                                                                        }
                }

    # SAVE FINAL THRESHOLD JSON :
    output_file_path = os.path.join(OUTPUT_DIR, "biomechanics_tertile_thresholds.json")
    with open(output_file_path, "w") as f:
        json.dump(threshold_distribution, f, indent=4)

    logging.info(f"Tertile thresholds saved successfully at : {output_file_path}")
    
    return threshold_distribution

# GENERATE QUINTILE THRESHOLDS :
def generate_quintile_thresholds(combined_distribution_data: dict):
    """
    Generates quintile-based thresholds
    for every phase -> attribute -> parameter.

    Divides data into 5 sections:
        0-20%   -> VERY_LOW
        20-40%  -> LOW
        40-60%  -> MODERATE
        60-80%  -> HIGH
        80-100% -> very_high

    Parameters:
    -----------
    combined_distribution_data : dict
        Final combined biomechanics distribution JSON

    Returns:
    --------
    dict
        Quintile threshold distribution data
    """

    # FINAL THRESHOLD STORAGE :
    threshold_distribution = {}

    # PHASE LOOP :
    for phase_name, phase_data in combined_distribution_data.items():

        threshold_distribution[phase_name] = {}

        # ATTRIBUTE LOOP :
        for attribute_name, attribute_data in phase_data.items():

            threshold_distribution[phase_name][attribute_name] = {}

            # PARAMETERS :
            combined_parameters = attribute_data["combined_parameters"]

            # PARAMETER LOOP :
            for parameter_name, values in combined_parameters.items():

                # SAFETY CHECK
                if not values:
                    continue

                total_values = len(values)

                # ---------------- QUINTILE INDICES ---------------- #
                q1_index = total_values // 5
                q2_index = (2 * total_values) // 5
                q3_index = (3 * total_values) // 5
                q4_index = (4 * total_values) // 5

                # ---------------- INDEX SAFETY ---------------- #
                q1_index = min(q1_index, total_values - 1)
                q2_index = min(q2_index, total_values - 1)
                q3_index = min(q3_index, total_values - 1)
                q4_index = min(q4_index, total_values - 1)

                # ---------------- QUINTILE VALUES ---------------- #
                q1_value = values[q1_index]
                q2_value = values[q2_index]
                q3_value = values[q3_index]
                q4_value = values[q4_index]

                # STORE OUTPUT
                threshold_distribution[phase_name][attribute_name][parameter_name] = {
                    "classification_ranges": {

                        # Bottom 20%
                        "very low": [
                            values[0],
                            q1_value
                        ],

                        # 20% - 40%
                        "emerging": [
                            q1_value,
                            q2_value
                        ],

                        # 40% - 60%
                        "medium": [
                            q2_value,
                            q3_value
                        ],

                        # 60% - 80%
                        "high": [
                            q3_value,
                            q4_value
                        ],

                        # Top 20%
                        "very high": [
                            q4_value,
                            values[-1]
                        ]
                    }
                }

    # SAVE FINAL THRESHOLD JSON :
    output_file_path = os.path.join(os.path.join(BASE_DIR, "app","middleware","combined_quintile_attribute_outputs"), "biomechanics_quintile_thresholds.json")

    with open(output_file_path, "w") as f:
        json.dump(threshold_distribution, f, indent=4)

    logging.info(f"Quintile thresholds saved successfully at : {output_file_path}")

    return threshold_distribution

# FINAL MASTER COMBINED DISTRIBUTION GENERATOR :
def generate_combined_biomechanics_distribution():
    """
    Generates one final combined biomechanics
    distribution JSON containing all phases
    and all combined attributes.

    Returns:
    --------
    dict
        Complete combined biomechanics distribution
    """

    # FINAL MASTER OUTPUT :

    final_distribution = {

        # GATHER PHASE ;
        "Gather Phase": {
            "Hip direction as the bowler loads up": combine_hip_direction_as_bowler_loads_up("Gather Phase"),
            "Hip-Shoulder Alignment": combine_hip_shoulder_alignment("Gather Phase"),
            "Head Position & Stability": combine_head_position_stability("Gather Phase"),
            "Shoulder Tilt Progression": combine_shoulder_tilt_progression("Gather Phase")
        },

        # BACKFOOT PHASE :
        "Backfoot Phase": {
            "Hip direction as the bowler loads up": combine_hip_direction_as_bowler_loads_up("Backfoot Phase"),
            "Knee Angle":combine_knee_angle("Backfoot Phase")
        },

        # DELIVERY STRIDE :
        "Delivery Stride": {
            "Delivery Stride Direction": combine_delivery_stride_direction("Delivery Stride"),
            "Hip-Shoulder Alignment": combine_hip_shoulder_alignment("Delivery Stride"),
            "Head Position & Stability": combine_head_position_stability("Delivery Stride"),
            "Trunk Lateral Flexion": combine_trunk_lateral_flexion("Delivery Stride")
        },

        # FRONTFOOT PHASE :
        "Frontfoot Phase": {
            "Hip-Shoulder Alignment": combine_hip_shoulder_alignment("Frontfoot Phase"),
            "Trunk Lateral Flexion":combine_trunk_lateral_flexion("Frontfoot Phase")
        },

        # FOLLOW THROUGH :
        "Follow Through": {"Trunk Lateral Flexion": combine_trunk_lateral_flexion("Follow Through")}
    
    }

    # SAVE FINAL MASTER JSON :
    # output_file_path = os.path.join(OUTPUT_DIR, "combined_biomechanics_distribution.json")
    # with open(output_file_path, "w") as f:
    #     json.dump(final_distribution, f, indent=4)

    # logging.info(f"Final combined biomechanics distribution saved successfully at :\n{output_file_path}")


    generate_quintile_thresholds(final_distribution)
    return generate_tertile_thresholds(final_distribution)

# CLASSIFY BIOMECHANICS REPORT :
def classify_biomechanics_report(biomechanics_report: dict, threshold_distribution: dict, file_name=None):
    """
    Classifies biomechanics report values
    into LOW / MEDIUM / HIGH using
    threshold distribution ranges.

    Parameters:
    -----------
    biomechanics_report : dict
        Actual bowler biomechanics report

    threshold_distribution : dict
        Threshold distribution JSON

    Returns:
    --------
    dict
        Classified biomechanics report
    """
    # FINAL CLASSIFIED OUTPUT :

    classified_report = {}

    classified_report["Bowling Arm"] = biomechanics_report.get("Bowling Arm", "unknown")

    # PHASE LOOP :

    for phase_name, phase_data in threshold_distribution.items():

        classified_report[phase_name] = {}

        # ATTRIBUTE LOOP

        for attribute_name, attribute_thresholds in phase_data.items():

            classified_report[phase_name][attribute_name] = {}
            report_attribute_data = (biomechanics_report[phase_name][attribute_name])

            # PARAMETER LOOP

            for parameter_name, parameter_threshold_data in (attribute_thresholds.items()):

                actual_value = (report_attribute_data[parameter_name])
                classification_ranges = (parameter_threshold_data["classification_ranges"])

                # RANGE VALUES

                low_min, low_max = (classification_ranges["low"])
                medium_min, medium_max = (classification_ranges["medium"])
                high_min, high_max = (classification_ranges["high"])

                # CLASSIFICATION

                classification = "unknown"

                if low_min <= actual_value < low_max:
                    classification = "low"
                elif (medium_min <= actual_value < medium_max):
                    classification = "medium"
                elif (high_min <= actual_value <= high_max):
                    classification = "high"

                # STORE RESULT 

                classified_report[phase_name][attribute_name][parameter_name] = {
                    "value": actual_value,
                    "classification": classification
                }

    # SAVE :

    # NEW SUBFOLDER
    # RESULTANT_CLASSIFIED_DIR = os.path.join(BASE_DIR, "app", "middleware", "resultant_classified")
    # os.makedirs(RESULTANT_CLASSIFIED_DIR, exist_ok=True)

    # if file_name is not None:
    #     base_name = os.path.splitext(file_name)[0]
    #     output_json_name = (f"{base_name}_classified_biomechanics_report.json")

    # else:
    #     output_json_name = ("classified_biomechanics_report.json")

    # output_file_path = os.path.join(RESULTANT_CLASSIFIED_DIR, output_json_name)
    # with open(output_file_path, "w") as f:
    #     json.dump(classified_report, f, indent=4)

    # logging.info(f"Classified biomechanics report saved successfully at : {output_file_path}")

    return classified_report

# CLASSIFY BIOMECHANICS REPORT USING QUINTILE RANGES :
def classify_biomechanics_report_quintiles(biomechanics_report: dict, threshold_distribution: dict, file_name=None):
    """
    Classifies biomechanics report values
    into:
        very_low
        EMERGING
        medium
        high
        very_high

    using quintile threshold distribution.

    Parameters:
    -----------
    biomechanics_report : dict
        Actual bowler biomechanics report

    threshold_distribution : dict
        Quintile threshold distribution JSON

    Returns:
    --------
    dict
        Classified biomechanics report
    """

    # FINAL CLASSIFIED OUTPUT :
    classified_report = {}
    classified_report["Bowling Arm"] = (biomechanics_report.get("Bowling Arm", "unknown"))

    # PHASE LOOP :
    for phase_name, phase_data in threshold_distribution.items():

        classified_report[phase_name] = {}

        # ATTRIBUTE LOOP :
        for attribute_name, attribute_thresholds in phase_data.items():

            classified_report[phase_name][attribute_name] = {}
            report_attribute_data = (biomechanics_report[phase_name][attribute_name])

            # PARAMETER LOOP :
            for parameter_name, parameter_threshold_data in (attribute_thresholds.items()):

                actual_value = (report_attribute_data[parameter_name])
                classification_ranges = (parameter_threshold_data["classification_ranges"])

                # ---------------- RANGE VALUES ---------------- #

                very_low_min, very_low_max = (classification_ranges["very low"])
                emerging_min, emerging_max = (classification_ranges["emerging"])
                medium_min, medium_max = (classification_ranges["medium"])
                high_min, high_max = (classification_ranges["high"])
                very_high_min, very_high_max = (classification_ranges["very high"])

                # ---------------- CLASSIFICATION ---------------- #

                classification = "unknown"

                if very_low_min <= actual_value < very_low_max:
                    classification = "very_low"

                elif emerging_min <= actual_value < emerging_max:
                    classification = "emerging"

                elif medium_min <= actual_value < medium_max:
                    classification = "medium"

                elif high_min <= actual_value < high_max:
                    classification = "high"

                elif very_high_min <= actual_value <= very_high_max:
                    classification = "very_high"

                # ---------------- STORE RESULT ---------------- #

                classified_report[phase_name][attribute_name][parameter_name] = {"value": actual_value, "classification": classification}

    # ---------------- SAVE OUTPUT ---------------- #

    # RESULTANT_CLASSIFIED_DIR = os.path.join(BASE_DIR, "app", "middleware", "combined_quintile_attribute_outputs", "result", "resultant_classified")
    # os.makedirs(RESULTANT_CLASSIFIED_DIR, exist_ok=True)

    # if file_name is not None:
    #     base_name = os.path.splitext(file_name)[0]
    #     output_json_name = (f"{base_name}_quintile_classified_biomechanics_report.json")

    # else:
    #     output_json_name = ("quintile_classified_biomechanics_report.json")

    # output_file_path = os.path.join(RESULTANT_CLASSIFIED_DIR, output_json_name)

    # with open(output_file_path, "w") as f:
    #     json.dump(classified_report, f, indent=4)

    # logging.info(f"Quintile classified biomechanics report saved successfully at : {output_file_path}")

    return classified_report



def is_report_within_thresholds_generic(biomechanics_report, threshold_distribution):

    for phase_name, phase_data in threshold_distribution.items():
        for attribute_name, attribute_thresholds in phase_data.items():

            report_attribute_data = biomechanics_report[phase_name][attribute_name]

            for parameter_name, parameter_threshold_data in attribute_thresholds.items():

                actual_value = report_attribute_data[parameter_name]
                classification_ranges = (parameter_threshold_data["classification_ranges"])

                all_mins = [
                    value[0]
                    for value in classification_ranges.values()
                ]

                all_maxs = [
                    value[1]
                    for value in classification_ranges.values()
                ]

                overall_min = min(all_mins)
                overall_max = max(all_maxs)

                if actual_value < overall_min or actual_value > overall_max:
                    return False

    return True


def merge_all_fields(source, target):
    """
    Recursively adds fields from source into target
    only if they are missing in target.

    Parameters
    ----------
    source : dict
        Raw biomechanics report

    target : dict
        Classified biomechanics report (modified in-place)
    """

    if not isinstance(source, dict) or not isinstance(target, dict):
        return

    for key, source_value in source.items():

        if key not in target:
            target[key] = deepcopy(source_value)
            continue

        target_value = target[key]

        if isinstance(source_value, dict) and isinstance(target_value, dict):
            merge_all_fields(source_value, target_value)

    return target