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

# set some variables
export MACHINE=docker

if [ $MACHINE == 'ees' ]; then
  export INPUTDATA=/project/neon_e3sm/inputdata
  export SRCMODS=/home/rfiorella/OLMT/srcmods_gswp3dm4
  export MOD_CTRL=/lclscratch/rfiorella/NGEE-Arctic-E3SM-master
  export MOD_TEST=/lclscratch/rfiorella/E3SM-IM1-patch
elif [ $MACHINE == 'docker' ]; then
  export INPUTDATA=/home/e3smuser/inputdata
  export SRCMODS=/home/e3smuser/OLMT
  export MOD_CTRL=/home/e3smuser/E3SM
  export MOD_TEST=/home/e3smuser/E3SM
else
  stop
fi

# set a common args sting
export COMMON_ARGS='--compiler gnu --mpilib openmpi --site AK-ICP --sitegroup NGEEArctic --nofire --nobudgets \
                    --nopointdata --cpl_bypass --gswp3 --daymet4 --dailyrunoff '

#-----------------------------------------------------------

case=3

if [ $case == 1 ]; then
  python3 ./site_fullrun.py --machine ${MACHINE} ${COMMON_ARGS} \
        --caseidprefix ICP-oldinit --ccsm_input ${INPUTDATA} \
         --domainfile ${INPUTDATA}/share/domains/domain.clm/ngee-arctic-development/IcyCape_domain.nc \
         --surffile ${INPUTDATA}/lnd/clm2/surfdata_map/ngee-arctic-development/IM1/IcyCape/IcyCape_surfdata.nc \
         --landusefile ${INPUTDATA}/lnd/clm2/surfdata_map/ngee-arctic-development/IM1/IcyCape/IcyCape_surfdata.pftdyn.nc \
         --model_root ${MOD_CTRL} --srcmods_loc ${SRCMODS} \
         --metdir ${INPUTDATA}/atm/datm7/IcyCape_1850-2109_fixed
	       
elif [ $case == 2 ]; then
  python3 ./site_fullrun.py --machine ${MACHINE} ${COMMON_ARGS} \
         --caseidprefix ICP-nopolygon --ccsm_input ${INPUTDATA} \
         --domainfile ${INPUTDATA}/share/domains/domain.clm/ngee-arctic-development/IcyCape_domain.nc \
         --surffile ${INPUTDATA}/lnd/clm2/surfdata_map/ngee-arctic-development/IM1/IcyCape/IcyCape_surfdata.nc \
         --landusefile ${INPUTDATA}/lnd/clm2/surfdata_map/ngee-arctic-development/IM1/IcyCape/IcyCape_surfdata.pftdyn.nc \
         --model_root ${MOD_TEST} --srcmods_loc ${SRCMODS} \
         --metdir ${INPUTDATA}/atm/datm7/IcyCape_1850-2109_fixed
elif [ $case == 3 ]; then
  python3 ./site_fullrun.py --machine ${MACHINE} ${COMMON_ARGS} \
         --caseidprefix ICP-HCP-test --ccsm_input ${INPUTDATA} \
         --domainfile ${INPUTDATA}/share/domains/domain.clm/ngee-arctic-development/IcyCape_domain.nc \
         --surffile ${INPUTDATA}/lnd/clm2/surfdata_map/ngee-arctic-development/IM1/IcyCape/IcyCape_surfdata_HCP.nc \
         --landusefile ${INPUTDATA}/lnd/clm2/surfdata_map/ngee-arctic-development/IM1/IcyCape/IcyCape_surfdata.pftdyn.nc \
         --metdir ${INPUTDATA}/atm/datm7/IcyCape_1850-2109_fixed \
         --model_root ${MOD_TEST} --srcmods_loc ${SRCMODS} \
         --use_arctic_init --use_polygonal_tundra \
         --nyears_ad_spinup 20 --nyears_final_spinup 20 --nyears_trans 251
elif [ $case == 4 ]; then
  python3 ./site_fullrun.py --machine ${MACHINE} ${COMMON_ARGS} \
         --caseidprefix ICP-FCP-test --ccsm_input ${INPUTDATA} \
         --domainfile ${INPUTDATA}/share/domains/domain.clm/ngee-arctic-development/IcyCape_domain.nc \
         --surffile ${INPUTDATA}/lnd/clm2/surfdata_map/ngee-arctic-development/IM1/IcyCape/IcyCape_surfdata_FCP.nc \
         --landusefile ${INPUTDATA}/lnd/clm2/surfdata_map/ngee-arctic-development/IM1/IcyCape/IcyCape_surfdata.pftdyn.nc \
         --metdir ${INPUTDATA}/atm/datm7/IcyCape_1850-2109_fixed \
         --model_root ${MOD_TEST} --srcmods_loc ${SRCMODS} \
         --use_polygonal_tundra --use_arctic_init \
         --nyears_ad_spinup 20 --nyears_final_spinup 20 --nyears_trans 251
elif [ $case == 5 ]; then
  python3 ./site_fullrun.py --machine ${MACHINE} ${COMMON_ARGS} \
         --caseidprefix ICP-LCP-test --ccsm_input ${INPUTDATA} \
         --domainfile ${INPUTDATA}/share/domains/domain.clm/ngee-arctic-development/IcyCape_domain.nc \
         --surffile ${INPUTDATA}/lnd/clm2/surfdata_map/ngee-arctic-development/IM1/IcyCape/IcyCape_surfdata_LCP.nc \
         --landusefile ${INPUTDATA}/lnd/clm2/surfdata_map/ngee-arctic-development/IM1/IcyCape/IcyCape_surfdata.pftdyn.nc \
         --metdir ${INPUTDATA}/atm/datm7/IcyCape_1850-2109_fixed \
         --model_root ${MOD_TEST} --srcmods_loc ${SRCMODS} \
         --use_arctic_init --use_polygonal_tundra \
         --nyears_ad_spinup 20 --nyears_final_spinup 20 --nyears_trans 251
fi
