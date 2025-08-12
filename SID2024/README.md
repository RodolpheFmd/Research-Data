# Synergising Automation and Human-In-The-Loop in Multimodal Tactical Conflict Resolution Service for Operations in Urban Airspace
*This repository contains materials and resources related to the research and experiments submitted for the 14<sup>th</sup> edition of the SESAR Innovation Days.*

## **Demonstration**  
This [folder](https://github.com/RodolpheFmd/Research-Data/tree/master/Sesar%20Innovation%20Days%202024/Demonstration) contains data related to our synthetic demonstration at Heathrow Airport, combining simulated BVLOS, synthetic autonomous, and real (commercial) operations.
### *TrafficLog* 
Tracks the operations every 5 seconds, providing detailed position logs.
### *ServiceProviderMonitorHistory*
Records the history of the instructions issued by the Tactical Conflict Resolution service during the demonstration.
### *flight_plan_Heathrow*
Includes flight plans for all operations involved in the scenario to ensure replicability of the demonstration.
### Materials for Figures 7 & 8.


## Medias
This [folder](https://github.com/RodolpheFmd/Research-Data/tree/master/Sesar%20Innovation%20Days%202024/Medias) contains images and screenshots of the different interfaces used in the demonstration:
- The operational environment – ATM & UTM Digital Twin.
- Tactical Conflict Resolution service monitor.
- Extension 2: Ground Control Station using Mission Planner.
- Extension 3: Microsoft Flight Simulator (defunct experiment).

We are continuing our research and plan to propose a video in the coming weeks that will demonstrate our service and the mixed-reality environment, including Extension 3.

## Sensitivity Analysis
This [folder](https://github.com/RodolpheFmd/Research-Data/tree/master/Sesar%20Innovation%20Days%202024/Sensitive%20Analysis) contains the data from two sensitivity analyses mentioned in the paper. These analyses were conducted to determine the optimal conflict resolution settings for the synthetic scenario at Heathrow Airport.
The Experiment_tracker helps identify the setup used for the Monte Carlo simulations. Refer to our previous research for detailed information on the training and experimental scenarios.

### Conflict Resolution Methods
The analysis explores three different conflict resolution methods. Multiple combinations were tested across different protocols to determine the safest approach.
### Preventive Conflict Detection Layer
Based on the selected conflict resolution methods, this experiment varies the Traffic Advisory (TA) and Resolution Advisory (RA) detection timings to identify the best settings for the scenario.
