#/bin/bash

export case=1
export INPUT_ROOT=/project/neon_e3sm/inputdata
export MODEL_ROOT=/lclscratch/rfiorella/NGEE-Arctic-E3SM-rfiorellaIM3
export RUN_ROOT=/project/ngee3/rfiorella/
export CASE_ROOT=/project/ngee3/rfiorella/

#case 1 = control
#case 2-4 = stocking density (plants/area), 10x, 4x, and 2x
#case 5-7 = bendresist parameter (case 1 = 1.0), then 0.5, 0.25, and 0.1
#case 8-9 = altered shrub taper value (8 = 2x, 9 = 4x) (note, these are expected to make shrubs taller!)
# so should not improve fit w/ observatons with only taper changes.

if [ $case == 1 ]; then
  python3 ./site_fullrun.py --site AK-TLG --sitegroup NGEEArctic \
        --caseidprefix IM3-control --machine ees --compiler gnu \
        --mpilib openmpi --cpl_bypass --era5 --model_root $MODEL_ROOT \
        --caseroot $CASE_ROOT --runroot $RUN_ROOT --ccsm_input $INPUT_ROOT \
        --srcmods_loc /home/e3smuser/OLMT/srcmods_era5cb --spinup_vars \
        --nofire --no_budgets --nopointdata \
        --metdir $INPUT_ROOT/atm/datm7/ngee-arctic-development/era5_noleap/tl \
        --domainfile $INPUT_ROOT/share/domains/domain.clm/domain.lnd.1x1pt_teller-GRID_navy.nc \
        --surffile $INPUT_ROOT/lnd/clm2/surfdata_map/surfdata_1x1pt_teller-GRID_simyr1850_c360x720_c171002.nc \
        --landusefile $INPUT_ROOT/lnd/clm2/surfdata_map/landuse.timeseries_1x1pt_teller-GRID_simyr1850-2015_c180423.nc
elif [ $case == 2 ]; then
  python3 ./site_fullrun.py --site AK-TLG --sitegroup NGEEArctic \
        --caseidprefix IM3-10x-stocking --machine ees --compiler gnu \
        --mpilib openmpi --cpl_bypass --era5 --model_root $MODEL_ROOT \
        --caseroot $CASE_ROOT --runroot $RUN_ROOT --ccsm_input $INPUT_ROOT \
        --srcmods_loc /home/e3smuser/OLMT/srcmods_era5cb --spinup_vars \
        --nofire --no_budgets --nopointdata \
        --metdir $INPUT_ROOT/atm/datm7/ngee-arctic-development/era5_noleap/tl \
        --domainfile $INPUT_ROOT/share/domains/domain.clm/domain.lnd.1x1pt_teller-GRID_navy.nc \
        --surffile $INPUT_ROOT/lnd/clm2/surfdata_map/surfdata_1x1pt_teller-GRID_simyr1850_c360x720_c171002.nc \
        --landusefile $INPUT_ROOT/lnd/clm2/surfdata_map/landuse.timeseries_1x1pt_teller-GRID_simyr1850-2015_c180423.nc \
        --mod_parm_file $INPUT_ROOT/lnd/clm2/paramdata/clm_params_c180524_10x-stocking.nc
elif [ $case == 3 ]; then
  python3 ./site_fullrun.py --site AK-TLG --sitegroup NGEEArctic \
        --caseidprefix IM3-4x-stocking --machine ees --compiler gnu \
        --mpilib openmpi --cpl_bypass --era5 --model_root $MODEL_ROOT \
        --caseroot $CASE_ROOT --runroot $RUN_ROOT --ccsm_input $INPUT_ROOT \
        --srcmods_loc /home/e3smuser/OLMT/srcmods_era5cb --spinup_vars \
        --nofire --no_budgets --nopointdata \
        --metdir $INPUT_ROOT/atm/datm7/ngee-arctic-development/era5_noleap/tl \
        --domainfile $INPUT_ROOT/share/domains/domain.clm/domain.lnd.1x1pt_teller-GRID_navy.nc \
        --surffile $INPUT_ROOT/lnd/clm2/surfdata_map/surfdata_1x1pt_teller-GRID_simyr1850_c360x720_c171002.nc \
        --landusefile $INPUT_ROOT/lnd/clm2/surfdata_map/landuse.timeseries_1x1pt_teller-GRID_simyr1850-2015_c180423.nc \
        --mod_parm_file $INPUT_ROOT/lnd/clm2/paramdata/clm_params_c180524_4x-stocking.nc
elif [ $case == 4 ]; then  python3 ./site_fullrun.py --site AK-TLG --sitegroup NGEEArctic \
        --caseidprefix IM3-2x-stocking --machine ees --compiler gnu \
        --mpilib openmpi --cpl_bypass --era5 --model_root $MODEL_ROOT \
        --caseroot $CASE_ROOT --runroot $RUN_ROOT --ccsm_input $INPUT_ROOT \
        --srcmods_loc /home/e3smuser/OLMT/srcmods_era5cb --spinup_vars \
        --nofire --no_budgets --nopointdata \
        --metdir $INPUT_ROOT/atm/datm7/ngee-arctic-development/era5_noleap/tl \
        --domainfile $INPUT_ROOT/share/domains/domain.clm/domain.lnd.1x1pt_teller-GRID_navy.nc \
        --surffile $INPUT_ROOT/lnd/clm2/surfdata_map/surfdata_1x1pt_teller-GRID_simyr1850_c360x720_c171002.nc \
        --landusefile $INPUT_ROOT/lnd/clm2/surfdata_map/landuse.timeseries_1x1pt_teller-GRID_simyr1850-2015_c180423.nc \
        --mod_parm_file $INPUT_ROOT/lnd/clm2/paramdata/clm_params_c180524_2x-stocking.nc
elif [ $case == 5 ]; then
  python3 ./site_fullrun.py --site AK-TLG --sitegroup NGEEArctic \
        --caseidprefix IM3-050-bendresist --machine ees --compiler gnu \
        --mpilib openmpi --cpl_bypass --era5 --model_root $MODEL_ROOT \
        --caseroot $CASE_ROOT --runroot $RUN_ROOT --ccsm_input $INPUT_ROOT \
        --srcmods_loc /home/e3smuser/OLMT/srcmods_era5cb --spinup_vars \
        --nofire --no_budgets --nopointdata \
        --metdir $INPUT_ROOT/atm/datm7/ngee-arctic-development/era5_noleap/tl \
        --domainfile $INPUT_ROOT/share/domains/domain.clm/domain.lnd.1x1pt_teller-GRID_navy.nc \
        --surffile $INPUT_ROOT/lnd/clm2/surfdata_map/surfdata_1x1pt_teller-GRID_simyr1850_c360x720_c171002.nc \
        --landusefile $INPUT_ROOT/lnd/clm2/surfdata_map/landuse.timeseries_1x1pt_teller-GRID_simyr1850-2015_c180423.nc \
        --mod_parm_file $INPUT_ROOT/lnd/clm2/paramdata/clm_params_c180524_050x-bendresist.nc
elif [ $case == 6 ]; then
  python3 ./site_fullrun.py --site AK-TLG --sitegroup NGEEArctic \
        --caseidprefix IM3-025-bendresist --machine ees --compiler gnu \
        --mpilib openmpi --cpl_bypass --era5 --model_root $MODEL_ROOT \
        --caseroot $CASE_ROOT --runroot $RUN_ROOT --ccsm_input $INPUT_ROOT \
        --srcmods_loc /home/e3smuser/OLMT/srcmods_era5cb --spinup_vars \
        --nofire --no_budgets --nopointdata \
        --metdir $INPUT_ROOT/atm/datm7/ngee-arctic-development/era5_noleap/tl \
        --domainfile $INPUT_ROOT/share/domains/domain.clm/domain.lnd.1x1pt_teller-GRID_navy.nc \
        --surffile $INPUT_ROOT/lnd/clm2/surfdata_map/surfdata_1x1pt_teller-GRID_simyr1850_c360x720_c171002.nc \
        --landusefile $INPUT_ROOT/lnd/clm2/surfdata_map/landuse.timeseries_1x1pt_teller-GRID_simyr1850-2015_c180423.nc \
        --mod_parm_file $INPUT_ROOT/lnd/clm2/paramdata/clm_params_c180524_025x-bendresist.nc
elif [ $case == 7 ]; then  python3 ./site_fullrun.py --site AK-TLG --sitegroup NGEEArctic \
        --caseidprefix IM3-010-bendresist --machine ees --compiler gnu \
        --mpilib openmpi --cpl_bypass --era5 --model_root $MODEL_ROOT \
        --caseroot $CASE_ROOT --runroot $RUN_ROOT --ccsm_input $INPUT_ROOT \
        --srcmods_loc /home/e3smuser/OLMT/srcmods_era5cb --spinup_vars \
        --nofire --no_budgets --nopointdata \
        --metdir $INPUT_ROOT/atm/datm7/ngee-arctic-development/era5_noleap/tl \
        --domainfile $INPUT_ROOT/share/domains/domain.clm/domain.lnd.1x1pt_teller-GRID_navy.nc \
        --surffile $INPUT_ROOT/lnd/clm2/surfdata_map/surfdata_1x1pt_teller-GRID_simyr1850_c360x720_c171002.nc \
        --landusefile $INPUT_ROOT/lnd/clm2/surfdata_map/landuse.timeseries_1x1pt_teller-GRID_simyr1850-2015_c180423.nc \
        --mod_parm_file $INPUT_ROOT/lnd/clm2/paramdata/clm_params_c180524_010x-bendresist.nc
elif [ $case == 8 ]; then  python3 ./site_fullrun.py --site AK-TLG --sitegroup NGEEArctic \
        --caseidprefix IM3-2x-taper --machine ees --compiler gnu \
        --mpilib openmpi --cpl_bypass --era5 --model_root $MODEL_ROOT \
        --caseroot $CASE_ROOT --runroot $RUN_ROOT --ccsm_input $INPUT_ROOT \
        --srcmods_loc /home/e3smuser/OLMT/srcmods_era5cb --spinup_vars \
        --nofire --no_budgets --nopointdata \
        --metdir $INPUT_ROOT/atm/datm7/ngee-arctic-development/era5_noleap/tl \
        --domainfile $INPUT_ROOT/share/domains/domain.clm/domain.lnd.1x1pt_teller-GRID_navy.nc \
        --surffile $INPUT_ROOT/lnd/clm2/surfdata_map/surfdata_1x1pt_teller-GRID_simyr1850_c360x720_c171002.nc \
        --landusefile $INPUT_ROOT/lnd/clm2/surfdata_map/landuse.timeseries_1x1pt_teller-GRID_simyr1850-2015_c180423.nc \
        --mod_parm_file $INPUT_ROOT/lnd/clm2/paramdata/clm_params_c180524_2x-taper.nc
elif [ $case == 9 ]; then  python3 ./site_fullrun.py --site AK-TLG --sitegroup NGEEArctic \
        --caseidprefix IM3-5x-taper --machine ees --compiler gnu \
        --mpilib openmpi --cpl_bypass --era5 --model_root $MODEL_ROOT \
        --caseroot $CASE_ROOT --runroot $RUN_ROOT --ccsm_input $INPUT_ROOT \
        --srcmods_loc /home/e3smuser/OLMT/srcmods_era5cb --spinup_vars \
        --nofire --no_budgets --nopointdata \
        --metdir $INPUT_ROOT/atm/datm7/ngee-arctic-development/era5_noleap/tl \
        --domainfile $INPUT_ROOT/share/domains/domain.clm/domain.lnd.1x1pt_teller-GRID_navy.nc \
        --surffile $INPUT_ROOT/lnd/clm2/surfdata_map/surfdata_1x1pt_teller-GRID_simyr1850_c360x720_c171002.nc \
        --landusefile $INPUT_ROOT/lnd/clm2/surfdata_map/landuse.timeseries_1x1pt_teller-GRID_simyr1850-2015_c180423.nc \
        --mod_parm_file $INPUT_ROOT/lnd/clm2/paramdata/clm_params_c180524_5x-taper.nc
fi
