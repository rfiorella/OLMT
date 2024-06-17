#!/bin/tcsh -f

# script to just keep consistent workflows...

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

module purge
module load e3sm-3.0/gcc-8.5.0-openmpi-5.0.3

set case=1

if ($case == 1) then
  python3 ./site_fullrun.py --compiler gnu --mpilib openmpi --machine ees \
         --site AK-ICP --sitegroup NGEEArctic --caseidprefix ICP-HCP-test --cpl_bypass --gswp3 --daymet4 \
         --domainfile /project/neon_e3sm/inputdata/share/domains/domain.clm/ngee-arctic-development/IcyCape_domain.nc \
         --surffile /project/neon_e3sm/inputdata/lnd/clm2/surfdata_map/ngee-arctic-development/IM1/IcyCape/IcyCape_surfdata_HCP.nc \
         --landusefile /project/neon_e3sm/inputdata/lnd/clm2/surfdata_map/ngee-arctic-development/IM1/IcyCape/IcyCape_surfdata.pftdyn.nc \
         --metdir /project/neon_e3sm/inputdata/atm/datm7/cpl_bypass_IM1_IcyCape \
         --model_root /project/ngee3/rfiorella/NGEE-Arctic-E3SM-lanlIM1 \
         --srcmods_loc /home/rfiorella/OLMT/srcmods_gswp3dm4 \
         --nofire --no_budgets --spinup_vars --nopointdata --use_polygonal_tundra
else if ($case == 2) then
  python3 ./site_fullrun.py --compiler gnu --mpilib openmpi --machine ees \
         --site AK-ICP --sitegroup NGEEArctic --caseidprefix ICP-FCP-test --cpl_bypass --gswp3 --daymet4 \
         --domainfile /project/neon_e3sm/inputdata/share/domains/domain.clm/ngee-arctic-development/IcyCape_domain.nc \
         --surffile /project/neon_e3sm/inputdata/lnd/clm2/surfdata_map/ngee-arctic-development/IM1/IcyCape/IcyCape_surfdata_FCP.nc \
         --landusefile /project/neon_e3sm/inputdata/lnd/clm2/surfdata_map/ngee-arctic-development/IM1/IcyCape/IcyCape_surfdata.pftdyn.nc \
         --metdir /project/neon_e3sm/inputdata/atm/datm7/cpl_bypass_IM1_IcyCape \
         --model_root /project/ngee3/rfiorella/NGEE-Arctic-E3SM-lanlIM1 \
         --srcmods_loc /home/rfiorella/OLMT/srcmods_gswp3dm4 \
         --nofire --no_budgets --spinup_vars --nopointdata --use_polygonal_tundra
else if ($case == 3) then
  python3 ./site_fullrun.py --compiler gnu --mpilib openmpi --machine ees \
         --site AK-ICP --sitegroup NGEEArctic --caseidprefix ICP-LCP-test --cpl_bypass --gswp3 --daymet4 \
         --domainfile /project/neon_e3sm/inputdata/share/domains/domain.clm/ngee-arctic-development/IcyCape_domain.nc \
         --surffile /project/neon_e3sm/inputdata/lnd/clm2/surfdata_map/ngee-arctic-development/IM1/IcyCape/IcyCape_surfdata_LCP.nc \
         --landusefile /project/neon_e3sm/inputdata/lnd/clm2/surfdata_map/ngee-arctic-development/IM1/IcyCape/IcyCape_surfdata.pftdyn.nc \
         --metdir /project/neon_e3sm/inputdata/atm/datm7/cpl_bypass_IM1_IcyCape \
         --model_root /project/ngee3/rfiorella/NGEE-Arctic-E3SM-lanlIM1 \
         --srcmods_loc /home/rfiorella/OLMT/srcmods_gswp3dm4 \
         --nofire --no_budgets --spinup_vars --nopointdata --use_polygonal_tundra
else if ($case == 4) then
  python3 ./site_fullrun.py --compiler gnu --mpilib openmpi --machine ees \
         --site AK-ICP --sitegroup NGEEArctic --caseidprefix ICP-nopolygon --cpl_bypass --gswp3 --daymet4 \
         --domainfile /project/neon_e3sm/inputdata/share/domains/domain.clm/ngee-arctic-development/IcyCape_domain.nc \
         --surffile /project/neon_e3sm/inputdata/lnd/clm2/surfdata_map/ngee-arctic-development/IM1/IcyCape/IcyCape_surfdata.nc \
         --landusefile /project/neon_e3sm/inputdata/lnd/clm2/surfdata_map/ngee-arctic-development/IM1/IcyCape/IcyCape_surfdata.pftdyn.nc \
	 --model_root /project/ngee3/rfiorella/NGEE-Arctic-E3SM-master \
         --metdir /project/neon_e3sm/inputdata/atm/datm7/cpl_bypass_IM1_IcyCape/ \
         --srcmods_loc /home/rfiorella/OLMT/srcmods_gswp3dm4 \
         --nofire --no_budgets --spinup_vars --nopointdata --notrans --nofnsp
else if ($case == 5) then
  python3 ./site_fullrun.py --compiler gnu --mpilib openmpi --machine ees \
         --site AK-ICP --sitegroup NGEEArctic --caseidprefix ICP-nopolygon --cpl_bypass --gswp3 --daymet4 \
         --domainfile /project/neon_e3sm/inputdata/share/domains/domain.clm/ngee-arctic-development/IcyCape_domain.nc \
         --surffile /project/neon_e3sm/inputdata/lnd/clm2/surfdata_map/ngee-arctic-development/IM1/IcyCape/IcyCape_surfdata.nc \
         --landusefile /project/neon_e3sm/inputdata/lnd/clm2/surfdata_map/ngee-arctic-development/IM1/IcyCape/IcyCape_surfdata.pftdyn.nc \
	 --model_root /project/ngee3/rfiorella/NGEE-Arctic-E3SM-lanlIM1 \
         --metdir /project/neon_e3sm/inputdata/atm/datm7/cpl_bypass_IM1_IcyCape/ \
         --srcmods_loc /home/rfiorella/OLMT/srcmods_gswp3dm4 \
         --nofire --no_budgets --spinup_vars --nopointdata --notrans --nofnsp
endif
