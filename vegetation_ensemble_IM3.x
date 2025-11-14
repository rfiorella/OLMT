#/bin/bash

#if ($DEBUG == TRUE) then
#  python3 ./site_fullrun.py \
#        --site AK-TLG \
#        --sitegroup NGEEArctic \
#        --caseidprefix IM3debug \
#        --machine docker \
#        --compiler gnu \
#        --mpilib openmpi \
#        --cpl_bypass \
#        --era5 \
#        --model_root /home/e3smuser/E3SM \
#        --caseroot /home/e3smuser/output \
#        --runroot /home/e3smuser/output \
#        --ccsm_input /home/e3smuser/inputdata \
#        --srcmods_loc /home/e3smuser/OLMT/srcmods_era5cb \
#        --spinup_vars \
#        --nofire --no_budgets \
#        --nopointdata \
#        --metdir /home/e3smuser/inputdata/atm/datm7/ngee-arctic-development/era5_noleap/tl \
#        --domainfile /home/e3smuser/inputdata/share/domains/domain.clm/domain.lnd.1x1pt_teller-GRID_navy.nc \
#        --surffile /home/e3smuser/inputdata/lnd/clm2/surfdata_map/surfdata_1x1pt_teller-GRID_simyr1850_c360x720_c171002.nc \
#        --landusefile /home/e3smuser/inputdata/lnd/clm2/surfdata_map/landuse.timeseries_1x1pt_teller-GRID_simyr1850-2015_c180423.nc
#else 
  python3 ./site_fullrun.py \
	--site AK-TLG \
	--sitegroup NGEEArctic \
	--caseidprefix IM3ens \
	--machine docker \
	--compiler gnu \
	--mpilib mpi-serial \
	--cpl_bypass \
	--era5 \
        --srcmods_loc /home/e3smuser/OLMT/srcmods_era5cb \
	--model_root /home/e3smuser/E3SM \
	--caseroot /home/e3smuser/output \
	--runroot /home/e3smuser/output \
	--ccsm_input /home/e3smuser/inputdata \
	--spinup_vars \
        --nofire --no_budgets \
	--nopointdata \
        --parm_list im3_parms \
        --mc_ensemble 200 \
        --ng 20 \
        --mod_parm_file /home/e3smuser/inputdata/lnd/clm2/paramdata/clm_params_c180524_10x-stocking.nc \
        --metdir /home/e3smuser/inputdata/atm/datm7/ngee-arctic-development/era5_noleap/tl \
	--domainfile /home/e3smuser/inputdata/share/domains/domain.clm/domain.lnd.1x1pt_teller-GRID_navy.nc \
	--surffile /home/e3smuser/inputdata/lnd/clm2/surfdata_map/surfdata_1x1pt_teller-GRID_simyr1850_c360x720_c171002.nc \
	--landusefile /home/e3smuser/inputdata/lnd/clm2/surfdata_map/landuse.timeseries_1x1pt_teller-GRID_simyr1850-2015_c180423.nc
#fi
