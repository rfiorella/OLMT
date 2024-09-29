#!/bin/bash -f

# Icy Cape cases
# case 1: baseline case, uses version of E3SM with no IM1 updates
# case 2: negative control case, uses version of E3SM with IM1 updates
#	  but they are turned off (should be identical results to case 1)
# case 3: High centered polygon test case, polygonal tundra IM1 updates have been
#	  turned on and new surface file assumes polygonal ground is 100% HCP
# case 4: Flat centered polygon test case, polygonal tundra IM1 updates have been
#	  turned on and new surface file assumes polygonal ground is 100% FCP
# case 5: Low centered polygon test case, polygonal tundra IM1 updates have been
#	  turned on and new surface file assumes polygonal ground is 100% LCP
#------------------------------------------------------------
# PREREQUISITES:
# NOTE: YOU WILL NEED TO RUN THE COMMANDS IN THIS BLOCK
# SEPARATELY FROM THIS SCRIPT, AS THEY DO NOT WORK
# IN TCSH IN THIS SCRIPT!

#module purge
#module load e3sm-3.0/gcc-8.5.0-openmpi-5.0.3
#conda activate <some environment that contains netCDF4 python package>

# You may need to make your own conda environment to do this!
# I have one called ncview that has netcdf4 and ncview, so
# I typically use `conda activate ncview`

#-----------------------------------------------------------

case=1

if [ $case == 1 ]; then
  python3 ./site_fullrun.py --compiler gnu --mpilib openmpi --machine ees \
         --site AK-ICP --sitegroup NGEEArctic --caseidprefix ICP-oldinit --cpl_bypass --gswp3 --daymet4 \
         --domainfile /project/neon_e3sm/inputdata/share/domains/domain.clm/ngee-arctic-development/IcyCape_domain.nc \
         --surffile /project/neon_e3sm/inputdata/lnd/clm2/surfdata_map/ngee-arctic-development/IM1/IcyCape/IcyCape_surfdata.nc \
         --landusefile /project/neon_e3sm/inputdata/lnd/clm2/surfdata_map/ngee-arctic-development/IM1/IcyCape/IcyCape_surfdata.pftdyn.nc \
         --model_root /lclscratch/rfiorella/NGEE-Arctic-E3SM-master \
         --srcmods_loc /home/rfiorella/OLMT/srcmods_gswp3dm4 \
         --metdir /project/ngee3/xhuang/IM1_ELM_forcings/IcyCape_1850-2109_fixed/ \
	 --ccsm_input /project/neon_e3sm/inputdata \
         --nofire --no_budgets --notrans --nofnsp --nopointdata
elif [ $case == 2 ]; then
  python3 ./site_fullrun.py --compiler gnu --mpilib openmpi --machine ees \
         --site AK-ICP --sitegroup NGEEArctic --caseidprefix ICP-nopolygon --cpl_bypass --gswp3 --daymet4 \
         --domainfile /project/neon_e3sm/inputdata/share/domains/domain.clm/ngee-arctic-development/IcyCape_domain.nc \
         --surffile /project/neon_e3sm/inputdata/lnd/clm2/surfdata_map/ngee-arctic-development/IM1/IcyCape/IcyCape_surfdata.nc \
         --landusefile /project/neon_e3sm/inputdata/lnd/clm2/surfdata_map/ngee-arctic-development/IM1/IcyCape/IcyCape_surfdata.pftdyn.nc \
         --model_root /lclscratch/rfiorella/IM1-patch \
         --srcmods_loc /home/rfiorella/OLMT/srcmods_gswp3dm4 \
         --metdir /project/ngee3/xhuang/IM1_ELM_forcings/IcyCape_1850-2109_fixed/ \
         --nofire --no_budgets --spinup_vars --nopointdata
elif [ $case == 3 ]; then
  python3 ./site_fullrun.py --compiler gnu --mpilib openmpi --machine ees \
         --site AK-ICP --sitegroup NGEEArctic --caseidprefix ICP-HCP-test --cpl_bypass --gswp3 --daymet4 \
         --domainfile /project/neon_e3sm/inputdata/share/domains/domain.clm/ngee-arctic-development/IcyCape_domain.nc \
         --surffile /project/neon_e3sm/inputdata/lnd/clm2/surfdata_map/ngee-arctic-development/IM1/IcyCape/IcyCape_surfdata_HCP.nc \
         --landusefile /project/neon_e3sm/inputdata/lnd/clm2/surfdata_map/ngee-arctic-development/IM1/IcyCape/IcyCape_surfdata.pftdyn.nc \
         --metdir /project/ngee3/xhuang/IM1_ELM_forcings/IcyCape_1850-2109_fixed \
         --model_root /lclscratch/rfiorella/IM1-patch \
         --srcmods_loc /home/rfiorella/OLMT/srcmods_gswp3dm4 \
         --ccsm_input /project/neon_e3sm/inputdata \
         --use_arctic_init --dailyrunoff --nofire --no_budgets --nyears_ad_spinup 20 --nyears_final_spinup 20 --nopointdata --use_polygonal_tundra --nyears_trans 251
elif [ $case == 4 ]; then
  python3 ./site_fullrun.py --compiler gnu --mpilib openmpi --machine ees \
         --site AK-ICP --sitegroup NGEEArctic --caseidprefix ICP-FCP-test --cpl_bypass --gswp3 --daymet4 \
         --domainfile /project/neon_e3sm/inputdata/share/domains/domain.clm/ngee-arctic-development/IcyCape_domain.nc \
         --surffile /project/neon_e3sm/inputdata/lnd/clm2/surfdata_map/ngee-arctic-development/IM1/IcyCape/IcyCape_surfdata_FCP.nc \
         --landusefile /project/neon_e3sm/inputdata/lnd/clm2/surfdata_map/ngee-arctic-development/IM1/IcyCape/IcyCape_surfdata.pftdyn.nc \
         --metdir /project/ngee3/xhuang/IM1_ELM_forcings/IcyCape_1850-2109_fixed \
         --model_root /lclscratch/rfiorella/IM1-patch \
         --srcmods_loc /home/rfiorella/OLMT/srcmods_gswp3dm4 \
         --ccsm_input /project/neon_e3sm/inputdata \
         --nyears_ad_spinup 20 --nyears_final_spinup 20  --dailyrunoff --nofire --no_budgets --nopointdata --use_polygonal_tundra --use_arctic_init --nyears_trans 251
elif [ $case == 5 ]; then
  python3 ./site_fullrun.py --compiler gnu --mpilib openmpi --machine ees \
         --site AK-ICP --sitegroup NGEEArctic --caseidprefix ICP-LCP-test --cpl_bypass --gswp3 --daymet4 \
         --domainfile /project/neon_e3sm/inputdata/share/domains/domain.clm/ngee-arctic-development/IcyCape_domain.nc \
         --surffile /project/neon_e3sm/inputdata/lnd/clm2/surfdata_map/ngee-arctic-development/IM1/IcyCape/IcyCape_surfdata_LCP.nc \
         --landusefile /project/neon_e3sm/inputdata/lnd/clm2/surfdata_map/ngee-arctic-development/IM1/IcyCape/IcyCape_surfdata.pftdyn.nc \
         --metdir /project/ngee3/xhuang/IM1_ELM_forcings/IcyCape_1850-2109_fixed \
         --model_root /lclscratch/rfiorella/IM1-patch \
         --srcmods_loc /home/rfiorella/OLMT/srcmods_gswp3dm4 \
         --ccsm_input /project/neon_e3sm/inputdata \
         --nofire --no_budgets --nyears_ad_spinup 20 --nyears_final_spinup 20 --dailyrunoff --nyears_trans 251 --nopointdata --use_arctic_init --use_polygonal_tundra
fi
