#!/bin/tcsh -f

# script to just keep consistent workflows...
#activate_e3sm

set case=3

if ($case == 1) then
  python3 ./site_fullrun.py --compiler gnu --mpilib openmpi --machine ees --site US-UMB --sitegroup AmeriFlux 
else if ($case == 2) then
  python3 ./site_fullrun.py --compiler gnu --mpilib openmpi --machine ees --site AK-TLG --sitegroup NGEEArctic \
         --caseidprefix OLMT --cpl_bypass --gswp3 \
         --metdir /project/neon_e3sm/inputdata/atm/datm7/atm_forcing.datm7.GSWP3.0.5d.v2.c180716_NGEE-Grid/cpl_bypass_teller-Grid \
         --domainfile /project/neon_e3sm/inputdata/share/domains/domain.clm/domain.lnd.1x1pt_teller-GRID_navy.nc \
         --surffile /project/neon_e3sm/inputdata/lnd/clm2/surfdata_map/surfdata_1x1pt_teller-GRID_simyr1850_c360x720_c171002.nc \
         --landusefile /project/neon_e3sm/inputdata/lnd/clm2/surfdata_map/landuse.timeseries_1x1pt_teller-GRID_simyr1850-2015_c180423.nc \
         --nofire --no_budgets --spinup_vars --nopointdata
else if ($case == 4) then
  python3 ./site_fullrun.py --compiler gnu --mpilib openmpi --machine ees \
         --site AK-TLG --sitegroup NGEEArctic --caseidprefix test4 --cpl_bypass --gswp3 \
         --domainfile /project/neon_e3sm/inputdata/share/domains/domain.clm/domain.lnd.1x1pt_teller-GRID_navy.nc \
         --surffile /project/neon_e3sm/inputdata/lnd/clm2/surfdata_map/surfdata_1x1pt_teller-GRID_simyr1850_c360x720_c171002.nc \
         --landusefile /project/neon_e3sm/inputdata/lnd/clm2/surfdata_map/landuse.timeseries_1x1pt_teller-GRID_simyr1850-2015_c180423.nc \
         --nofire --no_budgets --spinup_vars --nopointdata
else if ($case == 5) then
  python3  ./global_fullrun.py --compiler gnu --mpilib openmpi --machine ees --caseidprefix test5 \
        --nopftdyn --nofire --nopointdata --dailyrunoff --SP \
        --ccsm_input /project/neon_e3sm/inputdata/ --caseroot /project/ngee3/rfiorella/output/ \
        --domainfile /project/neon_e3sm/inputdata/share/domains/domain.clm/Yukon-domain_1584x1_sparse_grid_230731.nc \
        --surffile /project/neon_e3sm/inputdata/lnd/clm2/surfdata_map/Yukon-surfdata_1584x1_sparse_grid_230731.nc \
        --gswp3 --cpl_bypass --ccsm_input /project/neon_e3sm/inputdata --np 64 \
        --model_root /home/rfiorella/NGEE-Arctic-E3SM --exeroot /home/rfiorella/OLMT-output/
endif
