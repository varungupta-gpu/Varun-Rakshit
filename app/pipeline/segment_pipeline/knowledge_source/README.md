# Biomechanical Features Documentation

This document provides comprehensive information about the biomechanical features computed for cricket batting analysis, including all formulas, phases, and their mathematical implementations.

## Table of Contents
- [Phases](#phases)
- [Feature Categories](#feature-categories)
- [Feature Formulas](#feature-formulas)
- [Phase-Feature Mapping](#phase-feature-mapping)
- [Stance-Dependent Features](#stance-dependent-features)

---

## Phases

The batting action is divided into four main phases:

### 1. Stance
- **Description**: Initial batting position before any movement
- **Purpose**: Establishes baseline measurements for comparison
- **Features**: Basic alignment and stability metrics

### 2. Preparation
- **Description**: Pre-shot movements and setup
- **Purpose**: Measures body positioning before the swing
- **Features**: Full body alignment, rotation, and progression metrics

### 3. Downswing
- **Description**: Active swinging phase
- **Purpose**: Captures dynamic movements during shot execution
- **Features**: Full body alignment, rotation, and progression metrics

### 4. Followthrough
- **Description**: Post-shot completion phase
- **Purpose**: Measures body position after shot completion
- **Features**: Alignment and rotation metrics (no foot progression)

---

## Feature Categories

### Hip & Shoulder Features
- **hip_direction**: Direction of hip line relative to vertical
- **hip_shoulder_alignment**: Angle between hip and shoulder lines
- **shoulder_tilt**: Shoulder line orientation
- **shoulder_tilt_progression**: Frame-to-frame shoulder tilt change

### Head Features
- **head_stability**: Head position stability relative to stance

### Knee Features
- **front_knee_angle**: Front knee joint angle
- **back_knee_angle**: Back knee joint angle

### Stride & Stance Features
- **stride_width**: Distance between ankles
- **stride_line_progression_angle**: Stride line orientation relative to vertical
- **front_foot_progression**: Front foot movement along stride axis
- **back_foot_progression**: Back foot movement along stride axis

### Trunk Features
- **trunk_lateral_flexion**: Trunk lean change from stance baseline

### Arm Features
- **dominant_shoulder_elbow_line**: Dominant arm elbow joint angle
- **nondominant_shoulder_elbow_line**: Non-dominant arm elbow joint angle
- **dominant_elbow_wrist_line**: Dominant arm elbow-wrist line orientation
- **nondominant_elbow_wrist_line**: Non-dominant arm elbow-wrist line orientation

### Foot Features
- **front_foot_ankle_knee_line**: Front foot ankle-knee line orientation
- **back_foot_ankle_knee_line**: Back foot ankle-knee line orientation
- **front_foot_movement_angle**: Front foot movement direction
- **back_foot_movement_angle**: Back foot movement direction

### Center of Mass & Rotation Features
- **weighted_com**: Weighted center of mass shift from stance
- **upper_body_rotation**: Upper body rotation relative to stance
- **lower_body_rotation**: Lower body rotation relative to stance
- **shoulder_line_progression_angle**: Shoulder line orientation relative to vertical
- **stride_line_progression_angle**: Stride line orientation relative to vertical

---

## Feature Formulas

### Hip & Shoulder Features

#### Hip Direction
```
hip_direction = arctan2(dx, -dy) × (180/π)

Where:
dx = right_hip_x - left_hip_x
dy = right_hip_y - left_hip_y
Vertical reference: (0, -1) where -y points upward (video coordinates)

Calculation method:
- Vector from left hip to right hip: (dx, dy)
- atan2 computes angle between this vector and vertical axis
- -dy used because Y increases downward in video, but "up" is negative Y

Sign interpretation:
- Positive angle (+): Hip line rotated clockwise from vertical
  Example: +30° means right hip is to the right of left hip
- Negative angle (-): Hip line rotated counter-clockwise from vertical
  Example: -30° means right hip is to the left of left hip
- 0°: Hip line perfectly vertical (both hips at same X coordinate)

Range: [-90°, 90°]
```

#### Hip-Shoulder Alignment
```
alignment = arccos(cosine) × (180/π)

Where:
hip_vec = (right_hip_x - left_hip_x, right_hip_y - left_hip_y)
shoulder_vec = (right_shoulder_x - left_shoulder_x, right_shoulder_y - left_shoulder_y)
cosine = (hip_vec · shoulder_vec) / (|hip_vec| × |shoulder_vec|)

Calculation method:
- Compute vectors along hip line and shoulder line
- Use dot product to find angle between the two lines
- arccos converts from cosine value to degrees

Sign interpretation (always positive):
- 0°: Hip and shoulder lines are perfectly parallel or aligned
  Example: Indicates no rotation between hips and shoulders
- 90°: Hip and shoulder lines are perpendicular
  Example: Indicates maximum separation/rotation between hips and shoulders
- 180°: Hip and shoulder lines point in opposite directions (rare)

Cricket context:
- Smaller angles (0-30°) indicate compact, aligned position
- Medium angles (30-60°) indicate moderate shoulder rotation
- Large angles (60-90°) indicate significant hip-shoulder separation (coil)
- Range: [0°, 180°] (always positive, measured as absolute angle between lines)
```

#### Shoulder Tilt
```
shoulder_tilt = arctan2(dy, dx) × (180/π)

Where:
dx = right_shoulder_x - left_shoulder_x
dy = right_shoulder_y - left_shoulder_y

Calculation method:
- Vector from left shoulder to right shoulder: (dx, dy)
- atan2 computes angle of this vector from horizontal axis
- Measures absolute shoulder orientation in image

Sign interpretation:
- Positive angle (+): Right shoulder tilted downward (below left shoulder)
  Example: +30° means right shoulder is lower than left shoulder
- Negative angle (-): Right shoulder tilted upward (above left shoulder)
  Example: -30° means right shoulder is higher than left shoulder
- 0°: Shoulders perfectly horizontal (same Y coordinate)

Range: [-180°, 180°]
```

#### Shoulder Tilt Progression
```
progression = shoulder_tilt[frame] - shoulder_tilt[frame-1]
```

### Head Features

#### Head Stability
```
head_stability = √((rel_x - stance_head_x)² + (rel_y - stance_head_y)²)

Where:
head_x = (left_eye_x + right_eye_x) / 2
head_y = (left_eye_y + right_eye_y) / 2
shoulder_x = (left_shoulder_x + right_shoulder_x) / 2
shoulder_y = (left_shoulder_y + right_shoulder_y) / 2
rel_x = head_x - shoulder_x
rel_y = head_y - shoulder_y
stance_head_x, stance_head_y = average rel positions during stance
```

### Knee Features

#### Front Knee Angle
```
knee_angle = arccos(cosine) × (180/π)

Where:
v1 = hip - knee (vector from knee to hip)
v2 = ankle - knee (vector from knee to ankle)
cosine = (v1 · v2) / (|v1| × |v2|)

Calculation method:
- Compute vectors from knee to hip and from knee to ankle
- Use dot product to find angle at the knee joint
- arccos converts from cosine value to degrees

Result:
- 0°: Leg fully bent (impossible, knee joint collapses)
- 90°: Leg at right angle (knee bent at 90°)
- 180°: Leg fully extended (completely straight)

Cricket context:
- 140-180°: Extended leg during stance and followthrough
- 100-140°: Slightly bent during preparation and downswing
- <100°: Significant knee bend (rare in cricket batting, indicates instability)
- Range: [0°, 180°] (always positive, joint angle always measured as absolute)
```

#### Back Knee Angle
```
Same calculation as front knee angle, using right side keypoints:

knee_angle = arccos(cosine) × (180/π)

Where:
v1 = right_hip - right_knee
v2 = right_ankle - right_knee
cosine = (v1 · v2) / (|v1| × |v2|)

Result:
- 0°: Leg fully bent (impossible, knee joint collapses)
- 90°: Leg at right angle (knee bent at 90°)
- 180°: Leg fully extended (completely straight)

Cricket context:
- 150-180°: Extended leg during stance
- 100-150°: Bent knee during downswing (power generation)
- <100°: Significant knee bend during followthrough (weight transfer)
- Range: [0°, 180°] (always positive, joint angle always measured as absolute)
```

### Stride & Stance Features

#### Stride Width
```
stride_width = √((left_ankle_x - right_ankle_x)² + (left_ankle_y - right_ankle_y)²)
```

#### Front Foot Progression
```
progression = (dx × stride_unit_x + dy × stride_unit_y) / stride_width

Where:
stride_vec = (stance_front_x - stance_back_x, stance_front_y - stance_back_y)
stride_width = |stride_vec|
stride_unit = stride_vec / stride_width
dx = current_front_x - stance_front_x
dy = current_front_y - stance_front_y
```

#### Back Foot Progression
```
Same formula as front foot progression, using back foot keypoints
```

### Trunk Features

#### Trunk Lateral Flexion
```
flexion_change = current_trunk_angle - stance_trunk_angle

Where:
trunk_x = shoulder_x - hip_x
trunk_y = shoulder_y - hip_y
current_trunk_angle = arctan2(trunk_x, -trunk_y) × (180/π)
stance_trunk_angle = average trunk angle during stance

Calculation method:
- Compute trunk vector from hip to shoulder
- Measure angle from vertical at each frame
- Compare to average stance angle for change measurement

Sign interpretation:
- Positive change (+): Trunk leaned forward more than stance
  Example: +20° means leaning 20° more forward than initial stance
  Cricket: Aggressive shot, batter moving into the ball
  
- Negative change (-): Trunk leaned backward from stance
  Example: -15° means leaning back, away from the ball
  Cricket: Defensive shot, pulling away from delivery
  
- 0°: Trunk maintains same angle as stance baseline

Range: [-90°, 90°] (relative change from stance)

Cricket context:
- Small positive changes (0-10°): Balanced shot
- Large positive changes (20-40°): Aggressive driving shots
- Negative changes: Defensive, pulling back from the ball
```

### Arm Features

#### Dominant Shoulder-Elbow Line (Elbow Joint Angle)
```
elbow_angle = arccos(cosine) × (180/π)

Where:
ba = shoulder - elbow (vector from elbow to shoulder)
bc = wrist - elbow (vector from elbow to wrist)
cosine = (ba · bc) / (|ba| × |bc|)

Calculation method:
- Compute vectors from elbow to shoulder and from elbow to wrist
- Use dot product to find angle at the elbow joint
- arccos converts from cosine value to degrees

Result:
- 0°: Arm fully bent (impossible, elbow collapses)
- 90°: Arm at right angle (elbow bent at 90°)
- 180°: Arm fully extended (completely straight)

Cricket context:
- 120-180°: Extended arm during followthrough
- 80-120°: Bent arm during preparation and downswing
- <80°: Very bent arm (rare, indicates unusual technique)
- Range: [0°, 180°] (always positive, joint angle always measured as absolute)
```

#### Non-Dominant Shoulder-Elbow Line (Elbow Joint Angle)
```
Same calculation using left side keypoints:

elbow_angle = arccos(cosine) × (180/π)

Where:
ba = left_shoulder - left_elbow
bc = left_wrist - left_elbow
cosine = (ba · bc) / (|ba| × |bc|)

Result:
- 0°: Arm fully bent (impossible)
- 90°: Arm at right angle
- 180°: Arm fully extended

Cricket context:
- 140-180°: Extended supporting arm during followthrough
- 100-140°: Bent arm during swing (assists balance)
- Range: [0°, 180°] (always positive)
```

#### Dominant Elbow-Wrist Line
```
elbow_wrist_angle = arctan2(dy, dx) × (180/π)

Where:
dx = elbow_x - wrist_x
dy = elbow_y - wrist_y

Calculation method:
- Vector from wrist to elbow: (dx, dy)
- atan2 computes angle of forearm from horizontal
- Measures absolute orientation of forearm in image

Sign interpretation:
- Positive angle (+): Forearm angled downward (wrist below elbow)
  Example: +45° means wrist is below and to the left of elbow
  Cricket: Bat coming down toward ball
  
- Negative angle (-): Forearm angled upward (wrist above elbow)
  Example: -45° means wrist is above and to the left of elbow
  Cricket: Bat coming up after hitting ball
  
- 0°: Forearm perfectly horizontal

Range: [-180°, 180°]

Cricket context:
- Tracks bat position and swing direction through shot
```

#### Non-Dominant Elbow-Wrist Line
```
Same calculation using left side keypoints:

elbow_wrist_angle = arctan2(dy, dx) × (180/π)

Where:
dx = left_elbow_x - left_wrist_x
dy = left_elbow_y - left_wrist_y

Sign interpretation:
- Positive angle (+): Forearm angled downward (wrist below elbow)
- Negative angle (-): Forearm angled upward (wrist above elbow)
- 0°: Forearm perfectly horizontal

Cricket context:
- Tracks supporting arm position throughout shot
- Range: [-180°, 180°]
```

### Foot Features

#### Front Foot Ankle-Knee Line
```
ankle_knee_angle = arctan2(dy, dx) × (180/π)

Where:
dx = ankle_x - knee_x
dy = ankle_y - knee_y

Calculation method:
- Vector from knee to ankle: (dx, dy)
- atan2 computes angle of shin from horizontal
- Measures absolute orientation of front leg in image

Sign interpretation:
- Positive angle (+): Shin angled downward (ankle below knee)
  Example: +30° means ankle is below and to the right of knee
  Cricket: Normal standing position
  
- Negative angle (-): Shin angled upward (ankle above knee)
  Example: -30° means ankle is above and to the right of knee
  Cricket: Unusual, indicates leg abnormality or stumble
  
- 0°: Shin perfectly horizontal

Range: [-180°, 180°]

Cricket context:
- Typically positive (+45° to +90°) in normal batting stance
- Tracks front leg orientation during shot execution
```

#### Back Foot Ankle-Knee Line
```
Same calculation using right side keypoints:

ankle_knee_angle = arctan2(dy, dx) × (180/π)

Where:
dx = right_ankle_x - right_knee_x
dy = right_ankle_y - right_knee_y

Sign interpretation:
- Positive angle (+): Shin angled downward (ankle below knee)
  Cricket: Normal standing position
  
- Negative angle (-): Shin angled upward (ankle above knee)
  Cricket: Unusual, leg strain or abnormal position
  
- 0°: Shin perfectly horizontal

Cricket context:
- Tracks back leg orientation during swing
- Typically positive in normal cricket stance
- Can become negative during followthrough if foot pivots up
- Range: [-180°, 180°]
```

### Center of Mass & Rotation Features

#### Weighted Center of Mass
```
com_x = 0.25 × shoulder_x + 0.45 × hip_x + 0.30 × knee_x
com_y = 0.25 × shoulder_y + 0.45 × hip_y + 0.30 × knee_y

weighted_com = √((com_x - stance_com_x)² + (com_y - stance_com_y)²)
```

#### Upper Body Rotation
```
rotation = current_angle - stance_angle

Where:
current_angle = arctan2(elbow_y - shoulder_y, elbow_x - shoulder_x) × (180/π)
stance_angle = average angle during stance
```

#### Lower Body Rotation
```
rotation = current_angle - stance_angle

Where:
current_angle = arctan2(knee_y - hip_y, knee_x - hip_x) × (180/π)
stance_angle = average angle during stance
```

#### Shoulder Line Progression Angle
```
angle = arctan2(shoulder_x, -shoulder_y) × (180/π)

Where:
shoulder_x = right_shoulder_x - left_shoulder_x
shoulder_y = right_shoulder_y - left_shoulder_y
Vertical reference: (0, -1) where -y points upward (video coordinates)

Calculation method:
- Vector from left shoulder to right shoulder: (shoulder_x, shoulder_y)
- atan2 computes angle between this vector and vertical axis
- -shoulder_y used because Y increases downward in video, but "up" is negative Y

Sign interpretation:
- Positive angle (+): Shoulder line rotated clockwise from vertical
  Example: +45° means right shoulder is to the right of left shoulder (opened up)
- Negative angle (-): Shoulder line rotated counter-clockwise from vertical
  Example: -45° means right shoulder is to the left of left shoulder (closed down)
- 0°: Shoulders perfectly vertical alignment (both at same X coordinate)

Cricket context:
- Positive angles indicate shoulder opening during downswing
- Negative angles indicate shoulder closing or over-rotation
- Range: [-90°, 90°]

This measurement is ABSOLUTE from vertical, not relative to stance.
```

#### Stride Line Progression Angle
```
stride_angle = arctan2(stride_vec_x, -stride_vec_y) × (180/π)

Where:
stride_vec_x = right_ankle_x - left_ankle_x
stride_vec_y = right_ankle_y - left_ankle_y
Vertical reference: (0, -1) where -y points upward (video coordinates)

Calculation method:
- Vector from front ankle to back ankle: (stride_vec_x, stride_vec_y)
- atan2 computes angle between this vector and vertical axis
- -stride_vec_y used because Y increases downward in video, but "up" is negative Y

Sign interpretation:
- Positive angle (+): Stride line rotated clockwise from vertical
  Example: +30° means back foot is to the right of front foot
- Negative angle (-): Stride line rotated counter-clockwise from vertical
  Example: -30° means back foot is to the left of front foot
- 0°: Feet perfectly aligned vertically (both at same X coordinate)

Cricket context:
- Positive angles indicate feet opening (back foot pivoting outward)
- Negative angles indicate feet closing or front foot moving outward
- Larger magnitudes indicate more rotation from natural stance
- Range: [-90°, 90°]

This measurement is ABSOLUTE from vertical, not relative to stance.
```

---

## Phase-Feature Mapping

### Stance Phase Features
- hip_direction
- hip_shoulder_alignment
- head_position_stability
- front_knee_angle
- back_knee_angle
- stride_width
- front_foot_ankle_knee_line
- back_foot_ankle_knee_line
- weighted_com

### Preparation Phase Features
- hip_direction
- hip_shoulder_alignment
- head_position_stability
- front_knee_angle
- back_knee_angle
- stride_width
- trunk_lateral_flexion
- shoulder_elbow_arm_line_dominant
- shoulder_elbow_arm_line_non_dominant
- elbow_wrist_arm_line_dominant
- elbow_wrist_arm_line_non_dominant
- front_foot_ankle_knee_line
- back_foot_ankle_knee_line
- front_foot_progression
- back_foot_progression
- stride_line_progression_angle
- shoulder_line_progression_angle
- weighted_com
- upper_body_rotation
- lower_body_rotation

### Downswing Phase Features
- hip_direction
- hip_shoulder_alignment
- head_position_stability
- front_knee_angle
- back_knee_angle
- stride_width
- trunk_lateral_flexion
- shoulder_elbow_arm_line_dominant
- shoulder_elbow_arm_line_non_dominant
- elbow_wrist_arm_line_dominant
- elbow_wrist_arm_line_non_dominant
- front_foot_ankle_knee_line
- back_foot_ankle_knee_line
- front_foot_progression
- back_foot_progression
- stride_line_progression_angle
- shoulder_line_progression_angle
- weighted_com
- upper_body_rotation
- lower_body_rotation

### Followthrough Phase Features
- hip_direction
- hip_shoulder_alignment
- head_position_stability
- front_knee_angle
- back_knee_angle
- stride_width
- trunk_lateral_flexion
- shoulder_elbow_arm_line_dominant
- shoulder_elbow_arm_line_non_dominant
- elbow_wrist_arm_line_dominant
- elbow_wrist_arm_line_non_dominant
- front_foot_ankle_knee_line
- back_foot_ankle_knee_line
- stride_line_progression_angle
- shoulder_line_progression_angle
- weighted_com
- upper_body_rotation
- lower_body_rotation

---

## Stance-Dependent Features

The following features require stance phase frames as a reference baseline:

- **head_position_stability**: Compares head position to stance baseline
- **trunk_lateral_flexion**: Measures trunk lean change from stance
- **front_foot_progression**: Measures foot movement relative to stance position
- **back_foot_progression**: Measures foot movement relative to stance position
- **weighted_com**: Measures COM shift from stance baseline
- **upper_body_rotation**: Measures rotation from stance baseline
- **lower_body_rotation**: Measures rotation from stance baseline

These features use the average of all frames in the stance phase (stance_start_frame to stance_end_frame) as the reference frame for comparison.

**Note**: The following features measure absolute orientation from vertical and do NOT require stance frames:
- **stride_line_progression_angle**: Measures stride line angle relative to vertical at each frame
- **shoulder_line_progression_angle**: Measures shoulder line angle relative to vertical at each frame
- **hip_direction**: Measures hip line angle relative to vertical at each frame

---

## Coordinate System

- **X-axis**: Horizontal position in image coordinates
- **Y-axis**: Vertical position in image coordinates
- **Angles**: Measured in degrees, typically in range [-180, 180]
- **Left side**: Front side (closer to bowler) for right-handed batter
- **Right side**: Back side for right-handed batter

---

## Key Point Mapping

The following COCO keypoints are used:

- **Face**: left_eye (1), right_eye (2)
- **Shoulders**: left_shoulder (5), right_shoulder (6)
- **Elbows**: left_elbow (7), right_elbow (8)
- **Wrists**: left_wrist (9), right_wrist (10)
- **Hips**: left_hip (11), right_hip (12)
- **Knees**: left_knee (13), right_knee (14)
- **Ankles**: left_ankle (15), right_ankle (16)

---

## Usage

The features are computed frame-by-frame using the `compute_all_frame_features()` function in `src/biomechanics/features.py`. For phase-specific analysis, use `src/biomechanics/compute_features.py` which computes features for each inferred batting phase.

### Example Usage
```python
from src.biomechanics import features

# Compute all features for a frame range
features_df = features.compute_all_frame_features(
    df=df,
    start_frame=stance_start,
    end_frame=followthrough_end,
    stance_start_frame=stance_start,
    stance_end_frame=stance_end
)
```

---

## Notes

- All features return arrays with one value per frame in the specified range
- Angles are computed using arctan2 for proper quadrant handling
- Small epsilon (1e-8) is added to denominators to prevent division by zero
- Cosine values are clipped to [-1, 1] before arccos to handle numerical errors
- Progression features measure change from previous frame or stance baseline
