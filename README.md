# **Recursive Sparse Gaussian Process Mobility Estimation Demonstration**

## **The Problem**

Continuous estimation of the performance envelope of an air vehicle is a necessary element for long-term autonomy of air
vehicles to ensure survivability. This GitHub resource acts as a summary of the 'Real-time Mobility Estimation for
Autonomous Rotorcraft to Support Long-term Autonomy' thesis paper authored by Dr. Sarai Sherfield. The paper spans 174
pages and therefore may not be easily accessible to all learning styles.

## **The Solution**

The paper demonstrates how rotorcraft power data can be utilized in the machine learning algorithm to estimate all key
mobility characteristics for an autonomous rotorcraft, which would support safe operation and awareness.

The code walks through the process of setting up the Recursive Sparse Gaussian Process (RSGP) given the output of the
Sparse
Gaussian Process for a given rotorcraft. The RSGP is then shown to exhibit its ability to adapt to multiple realistic
scenarios such as:

* the posterior model and prior model are the same
* the posterior model contains a 10% error when compared to the prior model
* the posterior model contains a higher payload when compared to the prior model
* the posterior model contains a failed engine when compared to the prior model

An example of a Gaussian Process (GP) is shown in the following image. Denote that the GP provides a confidence interval
around the estimate that add important information, which would improve safety boundary awareness during flight.

GP Example
![GP Example](/assets/GP_Example.PNG)

## **Setting Parameters**

### **Flight Scenario**

There are three different flight scenarios to choose from:

- **Scenario A** models a rotorcraft accelerating from Out-of-Ground-Effect (OGE) hover to max speed
- **Scenario B** models a rotorcraft in a take-off procedure in which the vehicle increases in altitude as it flies
  forward at a constant rate and accelerates to max speed after it surpasses the bucket speed
- **Scenario C** models a rotorcraft flying forward from OGE hover at a low altitude, increasing its altitude, and then
  proceeding to accelerate to max speed

### **Mission Property**

There are four mission properties to choose from that only impact the RSGP results:

- **Normal Mission Property (NMP):** The posterior model is the same as the expected model
- **Model Error Mission Property (MEMP):** The posterior model contains a 10% error when compared to the expected model
- **Payload Change Property (PCMP):** The posterior model contains a higher payload when compared to the expected model
- **Engine Failure Mission Property (EFMP):** The posterior model contains an engine failure not present in the expected
  model

In this example, only one mission rate dataset out of three is available as of June 2024. This is the **Standard
Uncertainty** or mission_set = '_SU', which translates to collecting 1 power observation every 1.2 seconds.

### **Rotorcraft Weight**

There are two rotorcraft total weights to choose from:

- **Moderate Weight (Mid):** This is considered to be a reasonable load of 5263 lbs. for this rotorcraft model and a
  standard mission
- **Maximum Weight (Max):** This is considered to be the maximum reasonable load of 6467 lbs. for this rotorcraft model
  and a loaded mission

### **Rotorcraft Engine Damage**

There are two rotorcraft engine damage states to choose from:

- **Damaged Engine (True):** This is considered to be a reasonable load of 5263 lbs. for this rotorcraft model and a
  standard mission
- **No Damaged Engines (Max):** This is considered to be the maximum reasonable load of 6467 lbs. for this rotorcraft
  model and a loaded mission

***Note that this rotorcraft contains four engines and can continue to operate with one engine loss under most
conditions, but cannot sustain operation without at least three engines***
***Note that the intermediate engine setting is fixed in the rotorcraft.json files. They can be changed to continuous,
but the rotorcraft may not operate given several initial settings due to the lower power rating***

### **Gaussian Process Settings**

The **inducing points** for the RSGP can be determined by the using, but it is recommended to not use any number below 8
and nothing above 20. It is set to 14 as default, but different values may work well depending on the number of total
observations. {num_ind_points}

The **number of observations** is set to 1000 and determines how many equally spaced points are used to estimate the
model during the SGP. {num_obs}

The **variance of the observations** and the process are set to the same value for simplification under {var_set}.

The **boolean recursion value** determines whether the recursive portion is run or if you'd like to only run the SGP.
{recursion}

### **Other Notes**

Note that you may need to manually include openpyxl in your interpreter. This can be done in PyCharm by going to File->
Settings-> Project Interpreter, clicking the +, and searching for openpyxl to install.

## **Example Outputs**

Actual Power Charts
![Actual Power Chart](/assets/Actual_Power_Chart.png)

- HPR - Horsepower Required
- HPA - Horsepower Available
- AEO - All Engines Operable
- OEI - One Engine Inoperable

Model Baseline Solution
![Model Baseline Chart](/assets/Model_Baseline_Solution.png)

Model Mismatch Solution
![Model Mismatch Chart](/assets/Model_Mismatch_Solution.png)

Payload Change Solution
![Payload Change Chart](/assets/Payload_Change_Solution.png)

Engine Failure Solution
![Engine Failure Chart](/assets/Engine_Failure_Solution.png)

## **THANK YOU!**

Thank you for checking out my research project! I did my best to parse through my old code so, it can be organized
without breaking anything.
I'm sure there are small things I missed that shouldn't impact the function of the code, but if it does, please message
me! :)