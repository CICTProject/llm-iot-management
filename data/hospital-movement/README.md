# Dialysis data

## Context

In prior work, we developed an inexpensive system based on networked sensors to track movement of healthcare personnel (HCPs) in hospital settings [1-3].
In this project, we used this system to capture movement of HCPs at a dialysis unit in the University of Iowa Hospitals and Clinics (UIHC) (files in `HCP_locations/`).
We do not have access to any patient information due to patient privacy restrictions and therefore we do not know the exact start and end times of dialysis sessions.
However, we imputed patient dialysis session times (files in `dialysis_sessions/`) by exploiting domain specific knowledge about dialysis sessions, namely that HCPs will necessarily spend extended period of 
time at a dialysis chair both at the start and at the end of each dialysis session.

In our previous work, this data was used in agent-based simulation for simulating methicillin-resistant Staphylococcus aureus (MRSA) [4].
Recently, we used this data as the basis for COVID-19 simulations in the dialysis unit.
We evaluated a number of non-pharmaceutical interventions (NPIs) individually as well as in combination to reduce the spread of COVID-19 in the dialysis unit: refer to the Github repository [Dialysis_COVID19](https://github.com/HankyuJang/Dialysis_COVID19) for details.

## Content

We gathered 10 days of HCP movement data in Fall 2013.
Among the 10 days, 6 days had 14.5-15 hours of observation (long days, Day 2, Day 6, Day 7, Day 8, Day 9, and Day 10) and the remaining 4 days had 6-7.5 hours of observation (short days).
Data shared in this directory are long days, where the indicies of the long days (2, 6, 7, 8, 9, 10) appear at the end of the file names in `HCP_locations/` and `dialysis_sessions/`.

- `HCP_locations/latent_positions_day_{}.csv` 2, 6, 7, 8, 9, 10
- `date_time.txt`
- `station_0ft.csv`
- `dialysis_sessions/patient_info_day_{}.csv` 2, 6, 7, 8, 9, 10

## Data Descriptions

`HCP_locations/latent_positions_day_{}.csv` 2, 6, 7, 8, 9, 10

- `ID`: ID of the badge given to each HCP. HCPs are given unique badge each day, which means `ID=1` on Day 2 has nothing to do with `ID=1` on Day 6, i.e. IDs are not linked across days.
- `time`: Time unit is in 8 seconds. E.g. `time=1` corresponds to the time when the first badge is turned on, `time=2` corresponds to time after 8 seconds.
- `x`: location in x-axis (min=-1, max=1). To convert distances between coordinates to feet, divide them by 0.042838596.
- `y`: location in y-axis (min=-1, max=1).

`date_time.txt`
Timestamp (date,time) of when the first HCP badge turned on for each day.
Each row corresponds to the timestamp of one day, from Day 1 to Day 10.

`station_0ft.csv`
This file contains the x,y coordinates of 12 stations at the dialysis unit.
Each station is in a rectangular shape with 4 sets of coordinates.
- `x`: location in x axis (min=-1, max=1).
- `y`: location in y axis (min=-1, max=1).
- `station`: 1-9 (dialysis chairs), 10-11 (hand washing station), 12 (nurses station).

`dialysis_sessions/patient_info_day_{}.csv` 2, 6, 7, 8, 9, 10
Each dialysis session has patient `in` time to chair and `out` time from chair. 
`in` time is sampled uniformly at random from a time interval of `t_in_s` and `t_in_e`. 
Similarly, `out` time is sampled uniformly at random from a time interval of `t_out_s` and `t_out_e`. 
- `chair`: id of the dialysis chair.
- `t_in_s`: start time of the interval for patient `in` time to the chair.
- `t_in_e`: end time of the interval for patient `in` time to the chair.
- `t_out_s`: start time of the interval for patient `out` time to the chair.
- `t_out_e`: end time of the interval for patient `out` time to the chair.

## Generate contact networks
From the provided data we can generate contact networks to use for agent-based simulations.
Refer to section "Prepare contact arrays that are used in simulation" in Github repository [Dialysis_COVID19](https://github.com/HankyuJang/Dialysis_COVID19).

## Reference

[1] Herman, T., Pemmaraju, S. V., Segre, A. M., Polgreen, P. M., Curtis, D. E., Fries, J., ... & Severson, M. (2009, May). Wireless applications for hospital epidemiology. In Proceedings of the 1st ACM international workshop on Medical-grade wireless networks (pp. 45-50).\
[2] Polgreen, P. M., Hlady, C. S., Severson, M. A., Segre, A. M., & Herman, T. (2010). Method for automated monitoring of hand hygiene adherence without radio-frequency identification. Infection control and hospital epidemiology: the official journal of the Society of Hospital Epidemiologists of America, 31(12), 1294.\
[3] Monsalve, M. N., Pemmaraju, S. V., Thomas, G. W., Herman, T., Segre, A. M., & Polgreen, P. M. (2014). Do peer effects improve hand hygiene adherence among healthcare workers?. Infection control and hospital epidemiology, 35(10), 1277.\
[4] Jang, H., Justice, S., Polgreen, P. M., Segre, A. M., Sewell, D. K., & Pemmaraju, S. V. (2019, August). Evaluating Architectural Changes to Alter Pathogen Dynamics in a Dialysis Unit. In 2019 IEEE/ACM International Conference on Advances in Social Networks Analysis and Mining (ASONAM) (pp. 961-968). IEEE.
