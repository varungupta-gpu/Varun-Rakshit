# Batting Phase Style Analysis

## Overview

The batting biomechanics analysis pipeline is designed to characterize a batter's movement by dividing the complete batting action into four distinct movement phases. Each phase represents a specific objective during the execution of a cricket stroke and contains unique biomechanical characteristics that can be quantified using pose-derived features.

Instead of evaluating the batting action as a single continuous movement, the pipeline analyzes each phase independently. This enables detailed assessment of body organization, lower-body movement, upper-body coordination, balance, posture, and movement progression throughout the shot.

For every phase, multiple biomechanical features are computed from the detected pose keypoints. Statistical measures are then calculated over these features to summarize the batter's movement pattern. These statistics are subsequently used to classify various batting styles such as stance type, preparation style, downswing characteristics, follow-through organization, and overall movement tendencies.

The resulting phase-wise interpretations are later provided to a Large Language Model (LLM), which combines the computed biomechanical evidence to generate detailed technical feedback and coaching insights.

## Batting Phases

The complete batting action is divided into four sequential phases.

### 1. Stance

The stance is the initial position adopted by the batter before any significant movement toward the stroke begins. It serves as the reference position for the remainder of the batting action and establishes the batter's initial body alignment, balance, and posture.

During this phase, the batter is expected to remain relatively stable while preparing for the incoming delivery. Most movement-based features computed in later phases are measured relative to this initial posture.

The stance phase primarily represents:

- Initial body alignment
- Lower-body positioning
- Upper-body organization
- Weight distribution
- Overall balance
- Readiness before movement initiation

### 2. Preparation

The preparation phase begins immediately after the stance and continues until the start of the downswing.

This phase represents the loading stage of the batting action, during which the batter prepares the body to generate an efficient stroke. During preparation, coordinated movements occur across the feet, hips, trunk, shoulders, arms, and head while maintaining overall balance.

The preparation phase captures how efficiently the batter organizes the body before accelerating the bat toward the ball.

The preparation phase primarily represents:

- Initial weight transfer
- Foot progression
- Body loading
- Hip and shoulder organization
- Early trunk movement
- Development of rotational energy

### 3. Downswing

The downswing begins once the bat starts accelerating toward the ball and continues until ball impact (or the end of the downswing segment identified by the phase detector).

This is the primary power-generation phase of the batting action. During this stage, the lower body, trunk, shoulders, arms, and wrists work together to transfer momentum into the bat while maintaining balance and body organization.

Most dynamic biomechanical features reach their peak values during this phase.

The downswing phase primarily represents:

- Power generation
- Sequential body coordination
- Lower-body drive
- Upper-body rotation
- Bat acceleration
- Controlled transfer of momentum

### 4. Follow-Through

The follow-through begins immediately after completion of the downswing and continues until the batter reaches a stable finishing position.

Although the ball has already been played, the follow-through provides valuable information regarding movement efficiency, balance, body control, and stroke completion. Efficient follow-through mechanics often indicate that the preceding phases were well coordinated.

The follow-through phase primarily represents:

- Stroke completion
- Recovery of balance
- Upper-body extension
- Lower-body stability
- Postural control
- Final body organization

## Phase-wise Analysis Strategy

Each batting phase is analyzed independently because every phase serves a different biomechanical purpose.

Rather than relying on a single frame, the pipeline evaluates all frames belonging to a phase and computes descriptive statistics over every biomechanical feature. These statistical summaries provide a more robust representation of the batter's movement by reducing the influence of pose-estimation noise and individual frame outliers.

For every biomechanical feature, the following statistics may be computed depending on the feature type:

- Mean
- Signed Mean
- Median
- Standard Deviation
- Variance
- Minimum
- Maximum
- Range
- 5th Percentile
- 95th Percentile
- Total Change (Last Frame − First Frame)
- Coefficient of Variation (where applicable)

These statistical descriptors are then used to determine biomechanical styles such as front-foot or back-foot movement patterns, stance type, preparation style, downswing characteristics, follow-through organization, and head behavior.

---

# Global Batting Style Analysis

## Overview

Before analyzing the individual batting phases, the pipeline first determines the batter's overall movement strategy. Unlike phase-specific characteristics, these styles describe how the batter generally organizes the lower body during stroke execution.

The primary objective of this stage is to determine whether the batter predominantly transfers weight onto the front foot or remains supported on the back foot while playing the stroke. This distinction is fundamental because it influences the interpretation of almost every subsequent biomechanical measurement.

The global batting style is estimated using biomechanical measurements obtained from both the Preparation and Downswing phases, as these phases contain the largest lower-body movements associated with stroke execution.

## Front-Foot vs Back-Foot Shot

### Definition

A **front-foot shot** is characterized by a clear forward progression of the front foot accompanied by coordinated forward weight transfer and lower-body support.

A **back-foot shot** is characterized by the batter remaining supported primarily on the back leg while the stroke is organized around the rear lower body with limited forward progression.

Since these movement patterns develop gradually during stroke execution, the classification is performed using both the Preparation and Downswing phases rather than a single frame.

### Features Used

The following biomechanical features are used to determine whether the stroke is front-foot or back-foot dominated.

#### Primary Features

##### Front Foot Progression

Measures the displacement of the front foot relative to its initial stance position.

A larger positive progression indicates greater forward movement of the lead foot during stroke preparation and execution.

**Importance:**

- Primary indicator of front-foot movement.
- Quantifies forward stride length.
- Indicates initiation of forward weight transfer.

##### Back Foot Progression

Measures the displacement of the back foot relative to its stance position.

This feature captures rear-foot adjustments, back-and-across movement, and rear-leg support during stroke execution.

**Importance:**

- Primary indicator of back-foot movement.
- Identifies back-foot dominated strokes.
- Measures rear-foot contribution during loading.

#### Supporting Features

##### Weighted Center of Mass (COM)

Measures the displacement of the body's estimated center of mass relative to the stance phase.

**Importance:**

- Indicates overall body weight transfer.
- Confirms whether body mass follows front-foot or back-foot movement.
- Improves confidence of the classification.

##### Front Knee Angle

Represents the degree of flexion of the front knee throughout the movement.

**Importance:**

- Indicates loading of the front leg.
- Supports identification of front-foot driven strokes.
- Helps distinguish between a simple stride and actual weight transfer.

##### Back Knee Angle

Represents the flexion of the rear knee.

**Importance:**

- Indicates loading on the back leg.
- Helps identify strokes supported primarily by the rear lower body.
- Complements back-foot progression measurements.

### Statistical Measures

For each feature, descriptive statistics are computed across all frames belonging to the Preparation and Downswing phases.

The following statistical measures are calculated.

**Mean** — Represents the average value of the feature throughout the phase. Used to estimate the overall magnitude of movement.

**Signed Mean** — Preserves the direction of movement while averaging the feature. Unlike the absolute mean, the signed mean differentiates between positive and negative movement, making it particularly useful for progression and rotational features.

**Median** — Represents the central tendency while reducing the influence of noisy pose estimates and occasional outlier frames.

**Standard Deviation** — Measures the variability of the feature across the phase. Lower values indicate stable movement. Higher values indicate inconsistent movement.

**Variance** — Measures the spread of the movement around its mean value. Useful for distinguishing compact movement patterns from highly dynamic ones.

**Minimum and Maximum** — Represent the smallest and largest observed values during the phase. These measurements capture the movement limits achieved by the batter.

**Range** — Computed as:

```
Range = Maximum − Minimum
```

Represents the total movement excursion during the phase.

**5th and 95th Percentiles** — These percentiles summarize the effective movement range while reducing the influence of extreme outliers. Compared with minimum and maximum values, percentile statistics are generally more robust for noisy pose estimation data.

**Total Change (Delta)** — Computed as:

```
Delta = Last Frame − First Frame
```

Measures the net movement occurring during the phase. This statistic is particularly important for progression-based features because it captures the total displacement rather than the average displacement.

### Decision Strategy

The classification is not based on a single feature. Instead, multiple lower-body measurements are evaluated together.

The decision process follows the following principles:

- Greater front-foot progression indicates increasing likelihood of a front-foot shot.
- Greater back-foot progression indicates increasing likelihood of a back-foot shot.
- Forward movement of the center of mass increases confidence in a front-foot classification.
- Sustained loading of the front knee supports front-foot movement.
- Sustained loading of the back knee supports back-foot movement.
- Agreement among multiple features produces a higher-confidence classification.

Rather than relying on fixed thresholds for individual measurements, the pipeline combines evidence from all relevant biomechanical features to determine the dominant lower-body movement strategy.

---

# Stance Analysis

## Overview

The stance represents the batter's initial body organization before any significant movement toward the ball begins. It establishes the foundation upon which the remainder of the batting action is executed.

An efficient stance allows the batter to maintain balance, react to different deliveries, transfer weight efficiently, and generate controlled movement during the subsequent preparation and downswing phases.

Unlike later phases, the stance is characterized by minimal body movement. Therefore, the analysis primarily focuses on the batter's static body alignment, lower-body organization, and overall posture rather than dynamic movement.

The objective of stance analysis is to determine how the batter initially positions the hips, shoulders, feet, and body before initiating the stroke.

## Stance Styles

The pipeline classifies the batter's stance into one of three categories.

### Open Stance

An Open Stance is a batting setup in which the batter's lower and upper body appear oriented more openly toward the bowler. The hips, shoulders, and feet collectively exhibit a relatively open alignment while maintaining overall balance.

Characteristics typically include:

- Open hip orientation
- Open shoulder alignment
- Open stride orientation
- Stable body posture
- Balanced lower-body support

An open stance often allows easier access to off-side strokes while providing greater visual alignment toward the bowler.

### Neutral (Square) Stance

A Neutral Stance represents a balanced starting position where the hips, shoulders, and feet remain approximately aligned with the batting crease.

The body exhibits minimal rotational bias in either direction, allowing efficient movement toward both the front foot and back foot depending on the incoming delivery.

Characteristics typically include:

- Symmetrical body alignment
- Balanced shoulder orientation
- Balanced hip orientation
- Even weight distribution
- Stable lower-body organization

The neutral stance is generally considered the reference posture from which efficient movement can occur in either direction.

### Closed Stance

A Closed Stance is characterized by the batter's body being oriented more across the batting crease.

The hips, shoulders, and feet collectively demonstrate a relatively closed alignment before movement begins.

Characteristics typically include:

- Closed hip orientation
- Closed shoulder orientation
- Closed stride alignment
- Reduced openness toward the bowler
- Compact body organization

A closed stance may assist certain leg-side strokes but can also reduce freedom of movement toward the off side if excessive.

## Features Used

The stance classification is performed using the following biomechanical features.

### Hip Direction

**Importance: ★★★★★**

Hip Direction measures the orientation of the hip line relative to the vertical axis.

It provides the primary indication of whether the pelvis is initially open, neutral, or closed.

Since the hips form the mechanical base of the batting action, this feature contributes significantly to overall stance classification.

**Computed Statistics:** Mean, Signed Mean, Standard Deviation, Variance, 5th Percentile, 95th Percentile

### Shoulder Line Progression Angle

**Importance: ★★★★★**

The Shoulder Line Progression Angle measures the orientation of the shoulder line relative to the vertical axis.

This feature describes the orientation of the upper body and indicates whether the shoulders begin in an open, neutral, or closed configuration.

When interpreted together with Hip Direction, it provides a robust estimate of overall body alignment.

**Computed Statistics:** Mean, Signed Mean, Standard Deviation, Variance, 5th Percentile, 95th Percentile

### Stride Line Progression Angle

**Importance: ★★★★☆**

The Stride Line Progression Angle measures the orientation of the line joining both feet.

It describes the lower-body alignment and helps determine whether the batter's base is open, neutral, or closed.

**Computed Statistics:** Mean, Signed Mean, Standard Deviation, Variance

### Hip–Shoulder Alignment

**Importance: ★★★★☆**

Hip–Shoulder Alignment measures the angular relationship between the hips and shoulders.

Rather than determining openness directly, this feature measures the degree of rotational separation between the upper and lower body.

Small values indicate a compact body organization. Larger values indicate greater torso separation.

**Computed Statistics:** Mean, Standard Deviation, Variance

### Front Foot Ankle–Knee Line

**Importance: ★★★★☆**

Represents the orientation of the front lower leg.

This feature contributes additional information regarding the orientation of the lead side of the stance.

**Computed Statistics:** Mean, Signed Mean, Standard Deviation

### Back Foot Ankle–Knee Line

**Importance: ★★★★☆**

Represents the orientation of the rear lower leg.

Together with the front leg orientation, it provides a more complete description of lower-body organization.

**Computed Statistics:** Mean, Signed Mean, Standard Deviation

### Stride Width

**Importance: ★★☆☆☆**

Stride Width measures the distance between the feet during the stance.

Although it does not directly determine whether a stance is open or closed, it provides useful information regarding the stability and base of support.

**Computed Statistics:** Mean, Standard Deviation, Range

## Decision Strategy

The stance classification is determined using evidence from all primary alignment features rather than relying on any single measurement.

The classification process follows these principles:

- Hip Direction provides the primary estimate of pelvic openness.
- Shoulder Line Progression Angle estimates upper-body openness.
- Stride Line Progression Angle describes lower-body orientation.
- Hip–Shoulder Alignment evaluates whether the upper and lower body remain coordinated.
- Foot alignment measurements validate the overall lower-body organization.
- Stride Width contributes to the assessment of balance and stance stability.

The individual feature measurements are combined to determine the overall body orientation.

- Predominantly open alignment across the hips, shoulders, and stride results in an **Open Stance**.
- Balanced alignment with minimal rotational bias results in a **Neutral Stance**.
- Predominantly closed alignment across the hips, shoulders, and stride results in a **Closed Stance**.

Rather than using a single threshold, the final stance classification is obtained by combining evidence from all biomechanical features, allowing the pipeline to produce a more robust and reliable estimate of the batter's initial body organization.

---

# Preparation Analysis

## Overview

The Preparation phase begins immediately after the batter transitions from the initial stance and continues until the initiation of the downswing. During this phase, the batter organizes the entire body in anticipation of the stroke by initiating lower-body movement, transferring body weight, loading the hips and shoulders, positioning the trunk, and preparing the bat for efficient acceleration.

Unlike the Stance phase, which primarily evaluates static body organization, the Preparation phase focuses on coordinated movement. The quality of movement during this phase directly influences balance, timing, power generation, and stroke execution during the downswing.

The objective of the Preparation analysis is to determine how efficiently the batter organizes and loads the body before initiating the stroke.

## Preparation Styles

The pipeline classifies the batter's preparation into one of five categories.

### Compact Preparation

A Compact Preparation is characterized by minimal unnecessary body movement while maintaining coordinated alignment of the upper and lower body. The batter prepares for the stroke using controlled movement, stable posture, and efficient body organization without excessive displacement or early rotation.

Characteristics typically include:

- Controlled center of mass movement
- Limited trunk movement
- Coordinated upper- and lower-body rotation
- Stable body posture
- Efficient loading sequence
- Minimal unnecessary movement

Compact preparations generally improve timing, consistency, and movement efficiency.

### Open Preparation

An Open Preparation is characterized by the batter progressively opening the body while loading for the stroke. The hips, shoulders, and stride orientation gradually rotate into a more open alignment before the downswing begins.

Characteristics typically include:

- Progressive hip opening
- Progressive shoulder opening
- Open lower-body alignment
- Coordinated rotational loading
- Controlled upper-body organization

Open preparations generally create greater rotational freedom and allow smoother transition into the downswing.

### Closed Preparation

A Closed Preparation is characterized by the batter maintaining or increasing a relatively closed body alignment while loading for the stroke. The batter delays upper-body opening and retains a compact rotational posture before initiating the downswing.

Characteristics typically include:

- Closed hip orientation
- Closed shoulder orientation
- Closed stride alignment
- Compact rotational loading
- Stable body organization

Closed preparations often emphasize stability and delayed body opening before stroke execution.

### Forward-Press Preparation

A Forward-Press Preparation is characterized by coordinated forward progression of the front foot accompanied by forward body weight transfer before the downswing.

Characteristics typically include:

- Forward front-foot movement
- Progressive front-leg loading
- Forward center of mass displacement
- Coordinated upper-body preparation
- Stable lower-body organization

Forward-press preparations generally allow efficient weight transfer into front-foot strokes.

### Back-and-Across Preparation

A Back-and-Across Preparation is characterized by the batter initiating movement through the back foot while maintaining support on the rear lower body before beginning the downswing.

Characteristics typically include:

- Back-foot progression
- Rear-leg loading
- Stable rear-body support
- Controlled body organization
- Coordinated lower-body movement

Back-and-across preparations generally provide stability and create space for back-foot based stroke execution.

## Features Used

The preparation classification is performed using the following biomechanical features.

### Front Foot Progression

**Importance: ★★★★★**

Front Foot Progression measures the displacement of the front foot relative to its initial stance position.

It is the primary indicator of forward movement during preparation and is essential for identifying Forward-Press preparations and front-foot loading strategies.

**Computed Statistics:** Mean, Signed Mean, Standard Deviation, Variance, Maximum, Minimum, 5th Percentile, 95th Percentile, Delta

### Back Foot Progression

**Importance: ★★★★★**

Back Foot Progression measures the displacement of the back foot relative to its stance position.

It represents rear-foot movement during preparation and is the primary feature for identifying Back-and-Across preparations.

**Computed Statistics:** Mean, Signed Mean, Standard Deviation, Variance, Maximum, Minimum, 5th Percentile, 95th Percentile, Delta

### Weighted Center of Mass (COM)

**Importance: ★★★★★**

Weighted Center of Mass measures the displacement of the body's estimated center of mass relative to the stance.

It evaluates overall body weight transfer and confirms whether lower-body progression is accompanied by coordinated movement of the entire body.

**Computed Statistics:** Mean, Standard Deviation, Variance, Range, Delta, 95th Percentile

### Hip Direction

**Importance: ★★★★★**

Hip Direction measures the orientation of the hip line relative to the vertical axis.

It evaluates whether the pelvis progressively opens or remains closed during body loading and serves as one of the primary indicators of rotational preparation.

**Computed Statistics:** Mean, Signed Mean, Standard Deviation, Variance, Delta

### Shoulder Line Progression Angle

**Importance: ★★★★★**

Shoulder Line Progression Angle measures the orientation of the shoulder line relative to the vertical axis.

It evaluates upper-body opening during preparation and provides important information regarding rotational organization before the downswing.

**Computed Statistics:** Mean, Signed Mean, Standard Deviation, Variance, Delta

### Trunk Lateral Flexion

**Importance: ★★★★☆**

Trunk Lateral Flexion measures lateral movement of the trunk relative to the stance posture.

It evaluates body posture throughout preparation and helps distinguish compact loading from excessive leaning.

**Computed Statistics:** Mean, Signed Mean, Standard Deviation, Variance, Delta

### Upper Body Rotation

**Importance: ★★★★☆**

Upper Body Rotation measures rotational loading generated by the shoulders and upper torso.

It represents how efficiently the batter stores rotational energy before initiating the downswing.

**Computed Statistics:** Mean, Standard Deviation, Variance, Delta, Maximum

### Lower Body Rotation

**Importance: ★★★★☆**

Lower Body Rotation measures rotational loading generated by the hips and lower body.

Together with upper-body rotation, it evaluates coordination of the kinetic chain during preparation.

**Computed Statistics:** Mean, Standard Deviation, Variance, Delta, Maximum

### Hip–Shoulder Alignment

**Importance: ★★★★☆**

Hip–Shoulder Alignment measures the angular relationship between the hips and shoulders.

Rather than determining body opening directly, it evaluates rotational separation and body organization throughout preparation.

**Computed Statistics:** Mean, Standard Deviation, Variance

### Front Knee Angle

**Importance: ★★★☆☆**

Front Knee Angle measures loading of the lead leg during preparation.

It supports identification of Forward-Press loading and evaluates lower-body stability.

**Computed Statistics:** Mean, Minimum, Standard Deviation, Delta

### Back Knee Angle

**Importance: ★★★☆☆**

Back Knee Angle measures loading of the rear leg throughout preparation.

It supports identification of Back-and-Across loading strategies and rear-leg support.

**Computed Statistics:** Mean, Minimum, Standard Deviation, Delta

### Stride Line Progression Angle

**Importance: ★★★☆☆**

Stride Line Progression Angle measures the orientation of the line joining both feet relative to the vertical axis.

It provides additional information regarding lower-body organization during preparation.

**Computed Statistics:** Mean, Signed Mean, Standard Deviation, Variance, Delta

## Decision Strategy

The preparation classification is determined using evidence from multiple movement and alignment features rather than relying on any single biomechanical measurement.

The classification process follows these principles:

- Front Foot Progression and Back Foot Progression determine the dominant lower-body loading strategy.
- Weighted Center of Mass evaluates whether body weight transfer accompanies foot progression.
- Hip Direction and Shoulder Line Progression Angle determine whether the body progressively opens or remains closed during preparation.
- Upper Body Rotation and Lower Body Rotation evaluate rotational loading before the downswing.
- Trunk Lateral Flexion assesses body posture and movement efficiency.
- Hip–Shoulder Alignment measures coordination between the upper and lower body.
- Knee angles validate lower-body loading and support.
- Stride Line Progression Angle provides additional information regarding lower-body organization throughout preparation.

The individual feature measurements are combined to determine the overall preparation style.

- Controlled movement with limited displacement results in a **Compact Preparation**.
- Progressive body opening results in an **Open Preparation**.
- Maintenance of a relatively closed body alignment results in a **Closed Preparation**.
- Dominant forward lower-body progression results in a **Forward-Press Preparation**.
- Dominant rear-foot loading and progression results in a **Back-and-Across Preparation**.

Rather than using independent thresholds for individual features, the final preparation classification is obtained by combining evidence from all relevant biomechanical measurements, allowing the pipeline to produce a robust and comprehensive estimate of the batter's loading strategy before the downswing.

---

# Downswing Analysis

## Overview

The Downswing phase begins once the batter initiates the downward acceleration of the bat toward the ball and continues until ball impact (or the end of the downswing segment identified by the phase detector).

This phase represents the primary power-generation stage of the batting action. During the downswing, the energy generated during the Preparation phase is transferred through the lower body, trunk, shoulders, arms, and wrists to accelerate the bat toward the ball.

Unlike the Preparation phase, which primarily evaluates body organization and loading, the Downswing phase focuses on movement execution. It analyzes how efficiently the batter converts stored energy into coordinated motion while maintaining posture, stability, and balance.

The objective of the Downswing analysis is to determine how the batter generates power, coordinates body segments, and executes the stroke.

## Downswing Styles

The pipeline classifies the batter's downswing into one of six categories.

### Compact Downswing

A Compact Downswing is characterized by efficient transfer of energy using coordinated body movement while minimizing unnecessary motion. The batter maintains controlled trunk movement, efficient rotational sequencing, and stable lower-body support throughout the stroke.

Characteristics typically include:

- Controlled body rotation
- Stable trunk posture
- Efficient kinetic chain
- Minimal unnecessary movement
- Balanced lower-body support
- Coordinated arm movement

Compact downswings generally improve bat control, timing, and shot consistency.

### Expansive Downswing

An Expansive Downswing is characterized by larger coordinated body movements throughout stroke execution. The batter generates power through greater rotational movement, increased trunk involvement, and broader arm motion while maintaining overall body organization.

Characteristics typically include:

- Large rotational movement
- Greater trunk involvement
- Increased arm extension
- Dynamic body organization
- Larger movement amplitude

Expansive downswings generally emphasize maximum power generation.

### Front-Foot Driven Downswing

A Front-Foot Driven Downswing is characterized by power generation primarily through the lead leg. The batter transfers body weight onto the front foot while using the front leg as the primary support throughout the stroke.

Characteristics typically include:

- Dominant front-foot progression
- Forward weight transfer
- Progressive front-leg loading
- Stable lower-body support
- Coordinated upper-body acceleration

Front-foot driven downswings are commonly associated with attacking front-foot strokes.

### Back-Foot Driven Downswing

A Back-Foot Driven Downswing is characterized by power generation while maintaining support through the rear leg. The batter executes the stroke around the back lower body with limited forward displacement.

Characteristics typically include:

- Dominant back-foot support
- Rear-leg loading
- Controlled center of mass
- Stable lower-body organization
- Coordinated rear-body movement

Back-foot driven downswings generally occur while playing shorter deliveries and back-foot strokes.

### Upright Downswing

An Upright Downswing is characterized by maintaining a tall upper-body posture with limited lateral trunk movement while executing the stroke.

Characteristics typically include:

- Upright trunk posture
- Limited lateral flexion
- Stable head position
- Controlled body alignment
- Balanced movement

Maintaining an upright posture generally improves balance and consistency throughout the stroke.

### Low Downswing

A Low Downswing is characterized by executing the stroke from a lower body position using greater knee flexion while maintaining coordinated movement.

Characteristics typically include:

- Increased knee flexion
- Lower body posture
- Reduced center of mass height
- Stable lower-body support
- Coordinated upper-body movement

Lower batting positions generally improve stability while playing lower deliveries.

## Features Used

The downswing classification is performed using the following biomechanical features.

### Upper Body Rotation

**Importance: ★★★★★**

Upper Body Rotation measures rotational movement of the shoulders and upper torso during the downswing.

It is one of the primary indicators of rotational power generation and evaluates how efficiently the batter transfers energy through the upper body.

**Computed Statistics:** Mean, Standard Deviation, Variance, Maximum, 95th Percentile, Delta

### Lower Body Rotation

**Importance: ★★★★★**

Lower Body Rotation measures rotational movement generated by the hips and lower body.

Together with Upper Body Rotation, it evaluates the efficiency of the kinetic chain throughout the downswing.

**Computed Statistics:** Mean, Standard Deviation, Variance, Maximum, 95th Percentile, Delta

### Weighted Center of Mass (COM)

**Importance: ★★★★★**

Weighted Center of Mass measures displacement of the body's center of mass relative to the stance.

It evaluates body balance, weight transfer, and lower-body support during stroke execution.

**Computed Statistics:** Mean, Standard Deviation, Variance, Range, Delta, 95th Percentile

### Front Foot Progression

**Importance: ★★★★★**

Front Foot Progression measures the forward displacement of the front foot during the downswing.

It is the primary indicator of front-foot-driven stroke execution.

**Computed Statistics:** Mean, Signed Mean, Standard Deviation, Maximum, Minimum, Delta, 95th Percentile

### Back Foot Progression

**Importance: ★★★★★**

Back Foot Progression measures displacement of the rear foot during the downswing.

It is the primary indicator of back-foot-supported stroke execution.

**Computed Statistics:** Mean, Signed Mean, Standard Deviation, Maximum, Minimum, Delta, 95th Percentile

### Trunk Lateral Flexion

**Importance: ★★★★★**

Trunk Lateral Flexion measures movement of the trunk relative to the stance posture.

It evaluates whether the batter maintains an upright posture or generates power through increased body lean.

**Computed Statistics:** Mean, Signed Mean, Standard Deviation, Variance, Delta

### Front Knee Angle

**Importance: ★★★★☆**

Front Knee Angle measures loading and flexion of the lead leg during stroke execution.

It provides important information regarding front-leg support and body height.

**Computed Statistics:** Mean, Minimum, Standard Deviation, Delta

### Back Knee Angle

**Importance: ★★★★☆**

Back Knee Angle measures loading of the rear leg throughout the downswing.

It evaluates rear-leg stability and lower-body support.

**Computed Statistics:** Mean, Minimum, Standard Deviation, Delta

### Dominant Shoulder–Elbow Angle

**Importance: ★★★★☆**

Measures extension of the batting arm throughout the downswing.

It evaluates how efficiently the batter transfers body movement into bat acceleration.

**Computed Statistics:** Mean, Maximum, Standard Deviation, Delta

### Non-Dominant Shoulder–Elbow Angle

**Importance: ★★★☆☆**

Measures coordination of the supporting arm during stroke execution.

Proper supporting-arm mechanics contribute to maintaining bat control and overall movement organization.

**Computed Statistics:** Mean, Maximum, Standard Deviation, Delta

### Hip Direction

**Importance: ★★★☆☆**

Measures the orientation of the pelvis relative to the vertical axis.

It provides supporting evidence regarding lower-body rotational organization during the downswing.

**Computed Statistics:** Mean, Signed Mean, Standard Deviation, Delta

### Shoulder Line Progression Angle

**Importance: ★★★☆☆**

Measures the orientation of the shoulder line relative to the vertical axis throughout the downswing.

It supports evaluation of upper-body organization and rotational movement.

**Computed Statistics:** Mean, Signed Mean, Standard Deviation, Delta

## Decision Strategy

The downswing classification is determined using evidence from multiple movement and coordination features rather than relying on any single biomechanical measurement.

The classification process follows these principles:

- Upper Body Rotation and Lower Body Rotation determine the efficiency of rotational power generation.
- Front Foot Progression and Back Foot Progression determine the dominant lower-body support strategy.
- Weighted Center of Mass evaluates body balance and weight transfer during stroke execution.
- Trunk Lateral Flexion determines whether the batter maintains an upright or lowered posture.
- Front and Back Knee Angles evaluate lower-body loading and body height.
- Dominant and Non-Dominant Shoulder–Elbow Angles assess coordination of the upper limbs during bat acceleration.
- Hip Direction and Shoulder Line Progression Angle provide supporting evidence regarding rotational body organization.

The individual feature measurements are combined to determine the overall downswing style.

- Controlled rotational movement with minimal unnecessary displacement results in a **Compact Downswing**.
- Large coordinated body movement with greater rotational amplitude results in an **Expansive Downswing**.
- Dominant front-leg loading and forward progression result in a **Front-Foot Driven Downswing**.
- Dominant rear-leg loading and back-foot support result in a **Back-Foot Driven Downswing**.
- Limited trunk movement with stable posture results in an **Upright Downswing**.
- Increased knee flexion accompanied by a lower body position results in a **Low Downswing**.

Rather than using independent thresholds for individual biomechanical measurements, the final downswing classification is obtained by combining evidence from all relevant movement features, allowing the pipeline to generate a comprehensive description of the batter's stroke execution and power-generation strategy.

---

# Follow-Through Analysis

## Overview

The Follow-Through phase begins immediately after completion of the downswing and continues until the batter reaches a stable finishing position.

Although the ball has already been struck, the Follow-Through provides valuable information regarding movement efficiency, balance, body control, and stroke completion. An efficient follow-through is generally an indicator that the preceding preparation and downswing phases were well coordinated.

Unlike the Downswing phase, which focuses on power generation, the Follow-Through phase evaluates how effectively the batter dissipates momentum while maintaining posture, stability, and coordinated body organization.

The objective of the Follow-Through analysis is to determine how efficiently the batter completes the stroke while maintaining balance and movement control.

## Follow-Through Styles

The pipeline classifies the batter's follow-through into one of four categories.

### Balanced Follow-Through

A Balanced Follow-Through is characterized by stable body control after stroke execution. The batter maintains head stability, coordinated trunk posture, balanced lower-body support, and controlled arm extension while allowing the body to naturally decelerate.

Characteristics typically include:

- Stable head position
- Controlled trunk posture
- Balanced lower-body support
- Coordinated arm extension
- Controlled body deceleration
- Stable finishing position

Balanced follow-throughs generally indicate efficient movement sequencing throughout the entire batting action.

### Upright Follow-Through

An Upright Follow-Through is characterized by maintaining a relatively tall upper-body posture after ball contact with limited trunk movement and controlled body alignment.

Characteristics typically include:

- Upright trunk posture
- Limited lateral flexion
- Stable head position
- Controlled body alignment
- Balanced finishing posture

An upright follow-through generally reflects good postural control and efficient body organization.

### Low Follow-Through

A Low Follow-Through is characterized by completing the stroke from a lower body position using increased knee flexion while maintaining coordinated upper-body movement.

Characteristics typically include:

- Increased knee flexion
- Lower body posture
- Reduced body height
- Stable lower-body support
- Coordinated body control

Low follow-throughs are commonly observed when maintaining stability against lower deliveries or after aggressive lower-body movement.

### Expansive Follow-Through

An Expansive Follow-Through is characterized by large coordinated upper-body and arm movements after stroke execution. The batter allows momentum generated during the downswing to continue naturally while maintaining overall movement organization.

Characteristics typically include:

- Large arm extension
- Increased rotational movement
- Dynamic trunk movement
- Natural momentum continuation
- Coordinated body organization

Expansive follow-throughs generally indicate complete transfer of momentum through the stroke.

## Features Used

The follow-through classification is performed using the following biomechanical features.

### Head Stability

**Importance: ★★★★★**

Head Stability measures the displacement of the head relative to the stance position.

It is one of the primary indicators of balance and postural control after stroke execution. Stable head movement generally reflects efficient movement sequencing throughout the batting action.

**Computed Statistics:** Mean, Standard Deviation, Variance, Maximum, 95th Percentile

### Weighted Center of Mass (COM)

**Importance: ★★★★★**

Weighted Center of Mass measures displacement of the body's center of mass relative to the stance.

It evaluates whether the batter maintains balance while decelerating after the stroke.

**Computed Statistics:** Mean, Standard Deviation, Variance, Range, Delta, 95th Percentile

### Trunk Lateral Flexion

**Importance: ★★★★★**

Trunk Lateral Flexion measures lateral trunk movement after stroke completion.

It evaluates postural control and distinguishes upright finishes from lower follow-through positions.

**Computed Statistics:** Mean, Signed Mean, Standard Deviation, Variance, Delta

### Upper Body Rotation

**Importance: ★★★★☆**

Upper Body Rotation measures rotational continuation of the shoulders and upper torso after ball contact.

It evaluates how smoothly rotational momentum is dissipated following the downswing.

**Computed Statistics:** Mean, Standard Deviation, Variance, Maximum, Delta

### Lower Body Rotation

**Importance: ★★★★☆**

Lower Body Rotation measures rotational continuation generated by the hips and lower body.

Together with upper-body rotation, it evaluates overall body coordination during stroke completion.

**Computed Statistics:** Mean, Standard Deviation, Variance, Maximum, Delta

### Front Knee Angle

**Importance: ★★★★☆**

Front Knee Angle measures flexion and support provided by the lead leg during stroke completion.

It contributes to evaluating body height, lower-body stability, and finishing posture.

**Computed Statistics:** Mean, Minimum, Standard Deviation, Delta

### Back Knee Angle

**Importance: ★★★★☆**

Back Knee Angle measures support provided by the rear leg throughout the follow-through.

It evaluates lower-body stability and coordinated completion of the stroke.

**Computed Statistics:** Mean, Minimum, Standard Deviation, Delta

### Dominant Shoulder–Elbow Angle

**Importance: ★★★★☆**

Measures extension of the batting arm during stroke completion.

It evaluates how naturally the batter completes arm extension while dissipating momentum.

**Computed Statistics:** Mean, Maximum, Standard Deviation, Delta

### Non-Dominant Shoulder–Elbow Angle

**Importance: ★★★☆☆**

Measures movement of the supporting arm during the follow-through.

It contributes to evaluating overall upper-body coordination after stroke execution.

**Computed Statistics:** Mean, Maximum, Standard Deviation, Delta

### Hip Direction

**Importance: ★★★☆☆**

Measures orientation of the pelvis relative to the vertical axis after completion of the stroke.

It provides supporting information regarding lower-body organization during the finishing position.

**Computed Statistics:** Mean, Signed Mean, Standard Deviation

### Shoulder Line Progression Angle

**Importance: ★★★☆☆**

Measures orientation of the shoulder line relative to the vertical axis throughout the follow-through.

It evaluates the final upper-body posture after stroke completion.

**Computed Statistics:** Mean, Signed Mean, Standard Deviation

### Hip–Shoulder Alignment

**Importance: ★★★☆☆**

Measures rotational coordination between the hips and shoulders during the finishing phase.

It helps evaluate whether the batter completes the stroke with coordinated body organization.

**Computed Statistics:** Mean, Standard Deviation, Variance

## Decision Strategy

The follow-through classification is determined using evidence from multiple postural, rotational, and balance-related biomechanical features rather than relying on a single measurement.

The classification process follows these principles:

- Head Stability evaluates balance and movement control after stroke execution.
- Weighted Center of Mass determines whether body balance is maintained during deceleration.
- Trunk Lateral Flexion distinguishes upright finishes from lower finishing positions.
- Upper Body Rotation and Lower Body Rotation evaluate continuation and dissipation of rotational momentum.
- Front and Back Knee Angles assess lower-body support and finishing posture.
- Shoulder–Elbow Angles evaluate natural completion of arm extension.
- Hip Direction, Shoulder Line Progression Angle, and Hip–Shoulder Alignment provide supporting evidence regarding overall body organization during the finishing position.

The individual feature measurements are combined to determine the overall follow-through style.

- Stable posture and balanced body control result in a **Balanced Follow-Through**.
- Limited trunk movement with a tall body posture results in an **Upright Follow-Through**.
- Increased knee flexion with a lower finishing position results in a **Low Follow-Through**.
- Large coordinated upper-body and arm movements with continued momentum result in an **Expansive Follow-Through**.

Rather than using independent thresholds for individual biomechanical measurements, the final follow-through classification is obtained by combining evidence from all relevant biomechanical features, allowing the pipeline to generate a comprehensive description of how efficiently the batter completes the stroke and maintains body control after execution.

---

# Head Position Analysis

## Overview

Head position is one of the most important indicators of balance, visual stability, and overall batting technique. Throughout the batting action, the head acts as the primary reference point for maintaining body alignment, tracking the ball, and coordinating movement across the kinetic chain.

Unlike the phase-specific analyses, head position is evaluated throughout the complete batting sequence. The objective is to determine whether the batter maintains a stable and centered head position or consistently demonstrates lateral inclination during stroke execution.

An efficient head position allows the batter to maintain visual focus, preserve balance, and coordinate lower- and upper-body movement throughout the stroke.

The objective of the Head Position analysis is to determine the batter's overall head stability and movement characteristics during the complete batting action.

## Head Position Styles

The pipeline classifies the batter's head position into one of three categories.

### Neutral Head

A Neutral Head is characterized by the head remaining centered and stable relative to the trunk throughout the batting action.

Characteristics typically include:

- Stable head position
- Minimal lateral movement
- Balanced upper-body alignment
- Controlled movement throughout all phases
- Consistent visual stability

A neutral head position generally represents efficient batting technique and good postural control.

### Left-Leaning Head

A Left-Leaning Head is characterized by the head consistently inclining toward the outer side of the body (for a right-handed batter) during the batting action.

Characteristics typically include:

- Consistent lateral inclination toward the outer side
- Reduced head stability
- Increased upper-body asymmetry
- Compensatory body movement

Persistent leftward inclination may indicate imbalance or an aggressive movement strategy depending on the stroke being played.

### Right-Leaning Head

A Right-Leaning Head is characterized by the head consistently inclining toward the inner side of the body (for a right-handed batter) throughout the batting action.

Characteristics typically include:

- Consistent lateral inclination toward the inner side
- Reduced head stability
- Asymmetrical upper-body posture
- Modified balance strategy

Persistent rightward inclination may influence body balance and stroke consistency.

## Features Used

The head position classification is performed using the following biomechanical features.

### Head Stability

**Importance: ★★★★★**

Head Stability measures the displacement of the head relative to its reference position established during the stance.

It is the primary indicator of head control and evaluates how consistently the batter maintains head position throughout the batting action.

**Computed Statistics:** Mean, Standard Deviation, Variance, Maximum, Minimum, 5th Percentile, 95th Percentile, Range

### Trunk Lateral Flexion

**Importance: ★★★★☆**

Trunk Lateral Flexion measures lateral movement of the trunk throughout the batting action.

Head movement is often accompanied by trunk movement, making this feature valuable for evaluating overall postural alignment and distinguishing controlled movement from excessive body lean.

**Computed Statistics:** Mean, Signed Mean, Standard Deviation, Variance, Delta

### Weighted Center of Mass (COM)

**Importance: ★★★★☆**

Weighted Center of Mass measures displacement of the body's center of mass relative to the stance.

It provides supporting information regarding body balance and helps determine whether head movement occurs alongside coordinated whole-body movement.

**Computed Statistics:** Mean, Standard Deviation, Variance, Range, Delta

### Hip–Shoulder Alignment

**Importance: ★★★☆☆**

Hip–Shoulder Alignment measures the angular relationship between the hips and shoulders throughout the batting action.

Although not a direct measure of head position, it provides supporting information regarding upper-body organization and overall posture.

**Computed Statistics:** Mean, Standard Deviation, Variance

## Decision Strategy

The head position classification is determined using evidence from head stability, posture, and overall body organization rather than relying on a single measurement.

The classification process follows these principles:

- Head Stability evaluates the consistency of head movement throughout the batting action.
- Trunk Lateral Flexion determines whether the batter maintains an upright posture or exhibits excessive lateral body movement.
- Weighted Center of Mass evaluates whether head movement is accompanied by coordinated body balance.
- Hip–Shoulder Alignment provides supporting evidence regarding overall upper-body organization.

The individual feature measurements are combined to determine the overall head position.

- Stable head movement with balanced posture results in a **Neutral Head**.
- Consistent movement patterns indicating inclination toward the outer side of the body result in a **Left-Leaning Head**.
- Consistent movement patterns indicating inclination toward the inner side of the body result in a **Right-Leaning Head**.

Rather than relying on isolated frames, the final head position classification is obtained by combining evidence from all relevant biomechanical measurements across the complete batting sequence, allowing the pipeline to produce a robust estimate of the batter's overall head stability, postural control, and movement consistency throughout the stroke.

> **Note:** With the current feature set, Head Stability quantifies the magnitude of head movement but does not explicitly encode the direction of head inclination. Therefore, the distinction between Neutral, Left-Leaning, and Right-Leaning head positions will depend on the directional information available from the underlying pose/keypoint data during implementation. The biomechanical framework remains valid, but the implementation should use the pose coordinates to determine the direction of the observed head inclination.

---



---

# JSON 2 – Biomechanical Style Analysis

## Overview

The output generated by the Batting Biomechanics Analysis pipeline is a structured JSON containing the interpreted biomechanical characteristics of the batter.

This JSON represents the high-level biomechanical understanding of the batting action. The pipeline analyzes the statistical summaries computed in stats json file used as input along with the biomechanics json used as an input and identifies the movement styles that best describe the batter's technique.

Each selected style is supported by the underlying biomechanical evidence and accompanied by a confidence score that reflects the reliability of the classification.

This JSON serves as the primary input to the Large Language Model (LLM), enabling it to generate detailed coaching feedback, technical observations, performance insights, and improvement recommendations.

## Information Included

The JSON is divided into three major sections.

1. Global Analysis
2. Phase-wise Style Analysis
3. Overall Biomechanical Summary

## Global Analysis

The Global Analysis section describes the batter's overall movement strategy throughout the stroke.

Unlike the phase-specific analyses, this section summarizes characteristics that are observed across multiple phases of the batting action.

Currently, the following global characteristic is determined.

### Shot Type

The pipeline determines whether the batter predominantly executes a:

- Front-Foot Shot
- Back-Foot Shot

This classification is obtained by jointly analyzing the Preparation and Downswing phases using lower-body progression, center-of-mass movement, and lower-body loading characteristics.

The selected movement strategy is accompanied by:

- Style meaning
- Biomechanical reasoning
- Detailed description
- Confidence score

## Phase-wise Style Analysis

Following the Global Analysis, the pipeline performs independent biomechanical analysis for every batting phase.

Each phase may contain one or more selected movement styles depending on the observed movement characteristics.

For every selected style, the pipeline stores:

- Category
- Selected Style
- Style Meaning
- Biomechanical Reasoning
- Description
- Confidence Score

### Category

Represents the batting phase or biomechanical component being analyzed.

Examples include:

- stance
- preparation
- downswing
- follow_through
- head_position

### Selected Style

Represents the biomechanical style that best matches the observed movement.

Examples include:

**Stance**

- open_stance
- neutral_stance
- closed_stance

**Preparation**

- compact_preparation
- open_preparation
- closed_preparation
- forward_press_preparation
- back_and_across_preparation

**Downswing**

- compact_downswing
- expansive_downswing
- front_foot_driven_downswing
- back_foot_driven_downswing
- upright_downswing
- low_downswing

**Follow Through**

- balanced_follow_through
- upright_follow_through
- low_follow_through
- expansive_follow_through

**Head Position**

- neutral_head
- left_leaning_head
- right_leaning_head

### Style Meaning

Provides a concise biomechanical explanation of what the selected movement style represents.

This field explains the movement pattern independently of the specific batter.

**Example:** The batter generates power primarily through the lead leg while maintaining coordinated lower-body support.

### Why

Describes the biomechanical evidence responsible for selecting the movement style.

This field is generated directly from the statistical analysis performed in JSON 1.

Rather than simply stating the final classification, it explains which biomechanical measurements contributed most strongly to the decision.

**Example:** Front-foot progression consistently exceeded back-foot progression throughout the Preparation and Downswing phases. Forward center-of-mass movement and progressive front-leg loading further supported the classification.

### Description

Provides a batter-specific interpretation of the selected style.

Unlike the Style Meaning, which defines the style in general, the Description explains how the observed batter demonstrates that movement pattern.

**Example:** The batter consistently demonstrates a front-foot driven downswing by transferring body weight efficiently onto the lead leg while maintaining stable lower-body support throughout stroke execution.

### Confidence Score

Represents the confidence associated with the predicted biomechanical style.

The confidence score is computed from the agreement among the contributing biomechanical features.

Higher scores indicate stronger biomechanical evidence supporting the selected style.

## Overall Biomechanical Summary

The final section of the JSON contains a concise overview of the batter's complete movement profile.

Rather than describing individual phases separately, this section combines the findings from every phase into a single biomechanical summary.

The summary may include observations regarding:

- Overall batting style
- Lower-body movement strategy
- Body organization
- Rotational characteristics
- Balance
- Posture
- Stroke execution
- Movement efficiency

This section provides contextual information for the Large Language Model before detailed coaching analysis is generated.

## JSON Structure

```json
{
    "global_analysis": {

    },

    "styles": [

    ],

    "overall_summary": {

    }
}
```

## Example JSON

```json
{
    "global_analysis": {
        "shot_type": {
            "selected_style": "front_foot_shot",
            "style_meaning": "The batter primarily transfers body weight onto the front leg while executing the stroke.",
            "why": "Front-foot progression consistently exceeded back-foot progression throughout the Preparation and Downswing phases, accompanied by forward center-of-mass movement and progressive front-leg loading.",
            "description": "The batter predominantly executes front-foot shots using coordinated lower-body loading and efficient forward weight transfer.",
            "confidence_score": 94
        }
    },

    "styles": [

        {
            "category": "stance",
            "selected_style": "open_stance",
            "style_meaning": "The batter begins with a relatively open body alignment before initiating movement.",
            "why": "Hip direction, shoulder orientation, and stride alignment consistently indicated an open initial body position.",
            "description": "The batter adopts an open stance with coordinated upper- and lower-body alignment while maintaining balance before stroke initiation.",
            "confidence_score": 92
        },

        {
            "category": "preparation",
            "selected_style": "compact_preparation",
            "style_meaning": "The batter prepares for the stroke using controlled and efficient body organization.",
            "why": "Center-of-mass movement remained controlled while trunk movement and rotational variability were consistently low throughout the preparation phase.",
            "description": "The batter demonstrates a compact preparation characterized by efficient loading, stable posture, and minimal unnecessary movement.",
            "confidence_score": 91
        },

        {
            "category": "preparation",
            "selected_style": "forward_press_preparation",
            "style_meaning": "The batter initiates the stroke through coordinated forward movement of the front foot.",
            "why": "Front-foot progression dominated throughout preparation while forward center-of-mass movement and progressive front-leg loading remained consistent.",
            "description": "The batter utilizes a forward-press preparation before initiating the downswing.",
            "confidence_score": 93
        },

        {
            "category": "downswing",
            "selected_style": "front_foot_driven_downswing",
            "style_meaning": "The batter generates power primarily through the lead leg.",
            "why": "Front-foot progression and forward weight transfer remained dominant throughout the downswing while maintaining coordinated lower-body support.",
            "description": "The batter executes a front-foot driven downswing with efficient body coordination and stable lower-body mechanics.",
            "confidence_score": 95
        },

        {
            "category": "downswing",
            "selected_style": "compact_downswing",
            "style_meaning": "The batter executes the downswing with efficient body organization and controlled movement.",
            "why": "Upper-body rotation, lower-body rotation, trunk movement, and center-of-mass variability remained well controlled throughout stroke execution.",
            "description": "The batter consistently demonstrates a compact downswing with efficient kinetic sequencing and minimal unnecessary movement.",
            "confidence_score": 90
        },

        {
            "category": "follow_through",
            "selected_style": "balanced_follow_through",
            "style_meaning": "The batter completes the stroke while maintaining body balance and movement control.",
            "why": "Head stability, trunk posture, and center-of-mass control remained consistent throughout the follow-through.",
            "description": "The batter completes the stroke in a balanced finishing position with efficient momentum dissipation.",
            "confidence_score": 94
        },

        {
            "category": "head_position",
            "selected_style": "neutral_head",
            "style_meaning": "The batter maintains a stable and balanced head position throughout the batting action.",
            "why": "Head stability remained consistently high across all phases with limited unnecessary movement.",
            "description": "The batter demonstrates excellent head stability while maintaining overall postural control during the complete stroke.",
            "confidence_score": 96
        }

    ],

    "overall_summary": {
        "movement_profile": "The batter demonstrates a compact front-foot batting technique characterized by an open initial stance, efficient body loading, coordinated front-foot power generation, balanced stroke completion, and stable overall body organization.",
        "overall_confidence": 93
    }
}
```

## Purpose

This JSON transforms that evidence into human-interpretable biomechanical styles using the jsons used as an input. Together, these outputs create a clear separation between feature computation and biomechanical interpretation, enabling the Large Language Model to generate accurate, explainable, and coaching-oriented feedback without directly reasoning from raw pose-derived measurements.