#!/bin/tcsh -f

# script to just keep consistent workflows...
#activate_e3sm

# case 1: test site when metdata is provided (as user data in $INPUTDATA),
# but does not use coupler bypass. Makes own site data.
# case 2: case 1, but use gswp coupler bypass data. Make own site data.
# case 3: test site when metdata for site (in coupler bypass format), 
# domain file, surface file, and landuse file are all provided.
# case 4: test site when domain file, surface file, and landuse file
# are provided, but use global coupler bypass file for met data.
# case 5: test regional run with user provided domain and surface file.
# no landuse file. get metdata from global coupler bypass (gswp3).
# case 6: test site run with ERA5 cpl bypass format. user provided domain, surface, and
# landuse files.

set case=9

if ($case == 1) then
  python3 ./site_fullrun.py --compiler gnu --mpilib openmpi --machine lanl-ees \
         --site US-UMB --sitegroup AmeriFlux --caseidprefix test1
else if ($case == 2) then
  python3 ./site_fullrun.py --compiler gnu --mpilib openmpi --machine lanl-ees \
         --site US-UMB --sitegroup AmeriFlux --gswp3 --cpl_bypass --caseidprefix test2 \
         --ccsm_input /project/neon_e3sm/inputdata --model_root /home/rfiorella/NGEE-Arctic-E3SM
else if ($case == 3) then
  python3 ./site_fullrun.py --compiler gnu --mpilib openmpi --machine lanl-ees \
         --site AK-TLG --sitegroup NGEEArctic --caseidprefix test3 --cpl_bypass --gswp3 \
         --metdir /project/neon_e3sm/inputdata/atm/datm7/atm_forcing.datm7.GSWP3.0.5d.v2.c180716_NGEE-Grid/cpl_bypass_teller-Grid \
         --domainfile /project/neon_e3sm/inputdata/share/domains/domain.clm/domain.lnd.1x1pt_teller-GRID_navy.nc \
         --surffile /project/neon_e3sm/inputdata/lnd/clm2/surfdata_map/surfdata_1x1pt_teller-GRID_simyr1850_c360x720_c171002.nc \
         --landusefile /project/neon_e3sm/inputdata/lnd/clm2/surfdata_map/landuse.timeseries_1x1pt_teller-GRID_simyr1850-2015_c180423.nc \
         --nofire --no_budgets --spinup_vars --nopointdata
else if ($case == 4) then
  python3 ./site_fullrun.py --compiler gnu --mpilib openmpi --machine lanl-ees \
         --site AK-TLG --sitegroup NGEEArctic --caseidprefix test4 --cpl_bypass --gswp3 \
         --domainfile /project/neon_e3sm/inputdata/share/domains/domain.clm/domain.lnd.1x1pt_teller-GRID_navy.nc \
         --surffile /project/neon_e3sm/inputdata/lnd/clm2/surfdata_map/surfdata_1x1pt_teller-GRID_simyr1850_c360x720_c171002.nc \
         --landusefile /project/neon_e3sm/inputdata/lnd/clm2/surfdata_map/landuse.timeseries_1x1pt_teller-GRID_simyr1850-2015_c180423.nc \
         --nofire --no_budgets --spinup_vars --nopointdata
else if ($case == 5) then
  python3  ./global_fullrun.py --compiler gnu --mpilib openmpi --machine lanl-ees --caseidprefix test5 \
        --nopftdyn --nofire --nopointdata --dailyrunoff --SP \
        --ccsm_input /project/neon_e3sm/inputdata/ --caseroot /project/ngee3/rfiorella/output/ \
        --domainfile /project/neon_e3sm/inputdata/share/domains/domain.clm/Yukon-domain_1584x1_sparse_grid_230731.nc \
        --surffile /project/neon_e3sm/inputdata/lnd/clm2/surfdata_map/Yukon-surfdata_1584x1_sparse_grid_230731.nc \
        --gswp3 --cpl_bypass --np 32 --model_root /home/rfiorella/NGEE-Arctic-E3SM \
        --srcmods_loc /home/rfiorella/OLMT/srcmods_gswp3v1
else if ($case == 6) then
  python3 ./site_fullrun.py --compiler gnu --mpilib openmpi --machine lanl-ees \
         --site AK-TLG --sitegroup NGEEArctic --caseidprefix test6 --cpl_bypass --era5 \
         --metdir /project/neon_e3sm/inputdata/atm/datm7/atm_forcing.datm7.ERA5Land.c230829_teller \
         --srcmods_loc /home/rfiorella/OLMT/srcmods_era5cb \
         --domainfile /project/neon_e3sm/inputdata/share/domains/domain.clm/domain.lnd.1x1pt_teller-GRID_navy.nc \
         --surffile /project/neon_e3sm/inputdata/lnd/clm2/surfdata_map/surfdata_1x1pt_teller-GRID_simyr1850_c360x720_c171002.nc \
         --landusefile /project/neon_e3sm/inputdata/lnd/clm2/surfdata_map/landuse.timeseries_1x1pt_teller-GRID_simyr1850-2015_c180423.nc \
         --nofire --no_budgets --nopointdata --model_root /home/rfiorella/NGEE-Arctic-E3SM
else if ($case == 7) then
  python3  ./global_fullrun.py --compiler gnu --mpilib openmpi --machine lanl-ees --caseidprefix test7 \
        --nopftdyn --topounits --nofire --nopointdata --dailyrunoff --SP \
        --ccsm_input /project/neon_e3sm/inputdata/ --caseroot /project/ngee3/rfiorella/output/ \
        --domainfile /project/neon_e3sm/inputdata/share/domains/domain.clm/Yukon-domain_1584x1_sparse_grid_230731.nc \
        --surffile /project/neon_e3sm/inputdata/lnd/clm2/surfdata_map/Yukon-surfdata_1584x1_sparse_grid_230731.nc \
        --gswp3 --cpl_bypass --np 32 --model_root /home/rfiorella/NGEE-Arctic-E3SM \
        --srcmods_loc /home/rfiorella/OLMT/srcmods_gswp3v1
else if ($case == 8) then
  python3  ./global_fullrun.py --compiler gnu --mpilib openmpi --machine lanl-ees --caseidprefix test8 \
        --nopftdyn --topounits --topounits_atmdownscale --nofire --nopointdata --dailyrunoff --SP \
        --ccsm_input /project/neon_e3sm/inputdata/ --caseroot /project/ngee3/rfiorella/output/ \
        --domainfile /project/neon_e3sm/inputdata/share/domains/domain.clm/Yukon-domain_1584x1_sparse_grid_230731.nc \
        --surffile /project/neon_e3sm/inputdata/lnd/clm2/surfdata_map/Yukon-surfdata_1584x1_sparse_grid_230731.nc \
        --gswp3 --cpl_bypass --np 32 --model_root /home/rfiorella/NGEE-Arctic-E3SM \
        --srcmods_loc /home/rfiorella/OLMT/srcmods_gswp3v1
else if ($case == 9) then
  python3 ./site_fullrun.py --compiler gnu --mpilib openmpi --machine lanl-ees \
         --site AK-TLG --sitegroup NGEEArctic --caseidprefix test9 --cpl_bypass --era5 \
         --metdir /project/neon_e3sm/inputdata/atm/datm7/atm_forcing.datm7.ERA5Land.c230829_teller \
         --srcmods_loc /home/rfiorella/OLMT/srcmods_era5cb --topounits --topounits_atmdownscale \
         --domainfile /project/neon_e3sm/inputdata/share/domains/domain.clm/domain.lnd.1x1pt_teller-GRID_navy.nc \
         --surffile /project/neon_e3sm/inputdata/lnd/clm2/surfdata_map/surfdata_1x1pt_teller-GRID_simyr1850_c360x720_c171002.nc \
         --landusefile /project/neon_e3sm/inputdata/lnd/clm2/surfdata_map/landuse.timeseries_1x1pt_teller-GRID_simyr1850-2015_c180423.nc \
         --nofire --no_budgets --nopointdata --model_root /home/rfiorella/NGEE-Arctic-E3SM
else if ($case == 10) then
  python3 ./site_fullrun.py --compiler gnu --mpilib openmpi --machine lanl-ees \
         --site AK-TLG --sitegroup NGEEArctic --caseidprefix test10 --cpl_bypass --era5 \
         --metdir /project/neon_e3sm/inputdata/atm/datm7/atm_forcing.datm7.ERA5Land.c230829_teller \
         --srcmods_loc /home/rfiorella/OLMT/srcmods_era5cb --topounits --topounits_atmdownscale \
         --domainfile /project/neon_e3sm/inputdata/share/domains/domain.clm/domain.lnd.1x1pt_teller-GRID_navy.nc \
         --surffile /project/neon_e3sm/inputdata/lnd/clm2/surfdata_map/surfdata_1x1pt_teller-GRID_simyr1850_c360x720_c171002.nc \
         --landusefile /project/neon_e3sm/inputdata/lnd/clm2/surfdata_map/landuse.timeseries_1x1pt_teller-GRID_simyr1850-2015_c180423.nc \
         --nofire --no_budgets --nopointdata --model_root /home/rfiorella/NGEE-Arctic-E3SM
endif
