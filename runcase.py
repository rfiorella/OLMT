#!/usr/bin/env python

import netcdf4_functions as nffun
import socket, os, sys, csv, time, math, numpy
import re, subprocess
from optparse import OptionParser
#from Numeric import *


#runcase.py does the following:
#
#  1. Call routines to create surface and domain data (makepointdata.py)
#  2. Use create_newcase to build the new case with specified options
#  3. Set point and case-epecific namelist options
#  4. configure case
#  5. build (compile) ACME with clean_build first if requested
#  6. apply user-specified PBS and submit information
#  7. submit single run or parameter ensemble job to PBS queue.
#
#-------------------Parse options-----------------------------------------------

parser = OptionParser()

# general OLMT options
parser.add_option("--caseidprefix", dest="mycaseid", default="", \
                  help="Unique identifier to include as a prefix to the case name")
parser.add_option("--caseroot", dest="caseroot", default='', \
                  help = "case root directory (default = '', i.e., under model_root/cime/scripts/)")
parser.add_option("--runroot", dest="runroot", default="", \
                  help="Directory where the run would be created")
parser.add_option("--model_root", dest="csmdir", default='', \
                  help = "base model directory")
parser.add_option("--ccsm_input", dest="ccsm_input", default='', \
                  help = "input data directory for CESM (required)")
parser.add_option('--project', dest='project',default='', \
                 help='Set project')
parser.add_option("--exeroot", dest="exeroot", default="", \
	         help="Location of executable")
parser.add_option("--constraints", dest="constraints", default="", \
                  help="Directory containing model constraints")
parser.add_option("--metdata_dir", dest="metdata_dir", default='', \
                  help = 'Directory containing cpl_bypass met data (site only)')
parser.add_option("--pft", dest="mypft", default=-1, \
                  help = 'Use this PFT for all gridcells')
parser.add_option("--parm_file", dest="parm_file", default='',
                  help = 'file for parameter modifications')
parser.add_option("--parm_vals", dest="parm_vals", default="", \
                  help = 'User specified parameter values')
parser.add_option("--parm_file_P", dest="parm_file_P", default='',
                  help = 'file for P parameter modifications')


# general model build options
parser.add_option("--machine", dest="machine", default = '', \
                  help = "machine to\n")
parser.add_option("--compiler", dest="compiler", default='', \
	          help = "compiler to use (pgi, gnu)")
parser.add_option("--mpilib", dest="mpilib", default="mpi-serial", \
                      help = "mpi library (openmpi, mpich, ibm, mpi-serial)")
parser.add_option("--diags", dest="diags", default=False, \
                 action="store_true", help="Write special outputs for diagnostics")
parser.add_option("--debugq", dest="debug", default=False, \
                 action="store_true", help='Use debug queue')
parser.add_option("--srcmods_loc", dest="srcmods_loc", default='', \
                  help = 'Copy sourcemods from this location')
parser.add_option("--pio_version", dest="pio_version", default='2', \
                      help = "PIO version (1 or 2)")

# CASE options
parser.add_option("--coldstart", dest="coldstart", default=False, \
                  help = "set cold start (mutually exclusive w/finidat)", \
                  action="store_true")
parser.add_option("--compset", dest="compset", default='I1850CNPRDCTCBC', \
                  help = "component set to use (required)\n"
                         "Currently supports ONLY *CLM45(CN) compsets")





parser.add_option("--istrans", dest="istrans", default=False, action="store_true",\
                 help="Force compset to act like transient")
parser.add_option("--lat_bounds", dest="lat_bounds", default='-999,-999', \
                  help = 'latitude range for regional run')
parser.add_option("--lon_bounds", dest="lon_bounds", default='-999,-999', \
                  help = 'longitude range for regional run')

parser.add_option("--humhol", dest="humhol", default=False, \
                  help = 'Use hummock/hollow microtopography', action="store_true")
parser.add_option("--marsh", dest="marsh", default=False, \
                  help = 'Use marsh hydrology/elevation', action="store_true")
parser.add_option("--tide_components_file", dest="tide_components_file", default='', \
                    help = 'NOAA tide components file')
parser.add_option("--mask", dest="mymask", default='', \
                  help = 'Mask file to use (regional only)')

parser.add_option("--model", dest="mymodel", default='', \
                  help = 'Model to use (ELM,CLM5)')

parser.add_option("--namelist_file",  dest="namelist_file", default='', \
                  help="File containing custom namelist options for user_nl_clm")

parser.add_option("--ilambvars", dest="ilambvars", default=False, \
                 action="store_true", help="Write special outputs for diagnostics")
parser.add_option("--dailyvars", dest="dailyvars", default=False, \
                 action="store_true", help="Write daily ouptut variables")

parser.add_option("--res", dest="res", default="CLM_USRDAT", \
                      help='Resoultion for global simulation')
parser.add_option("--point_list", dest="point_list", default='', \
                  help = 'File containing list of points to run')

# model input options
parser.add_option("--point_area_kmxkm", dest="point_area_kmxkm", default=None, \
                  help = 'user-specific area in kmxkm of each point in point list (unstructured')
parser.add_option("--point_area_degxdeg", dest="point_area_degxdeg", default=None, \
                  help = 'user-specific area in degreeXdegree of each point in point list (unstructured')

parser.add_option("--sitegroup", dest="sitegroup", default="AmeriFlux", \
                  help = "site group to use (default AmeriFlux)")
parser.add_option("--site", dest="site", default='', \
                  help = '6-character FLUXNET code to run (required)')
parser.add_option("--site_forcing", dest="site_forcing", default='', \
                  help = '6-character FLUXNET code for forcing data')
parser.add_option("--metdir", dest="metdir", default="none", \
                  help = 'subdirectory for met data forcing')


# metdata
parser.add_option("--cruncep", dest="cruncep", default=False, \
                  help = "use cru-ncep data", action="store_true")
parser.add_option("--cruncepv8", dest="cruncepv8", default=False, \
                  help = "use cru-ncep data", action="store_true")
parser.add_option("--crujra", dest="crujra", default=False, \
                  help = "use crujra data", action="store_true")
parser.add_option("--cplhist", dest="cplhist", default=False, \
                  help= "use CPLHIST forcing", action="store_true")
parser.add_option("--gswp3", dest="gswp3", default=False, \
                  help= "use GSWP3 forcing", action="store_true")
parser.add_option("--gswp3_w5e5", dest="gswp3_w5e5", default=False, action="store_true", \
                  help = 'Use GSWP3 w5e5 meteorology')
parser.add_option("--princeton", dest="princeton", default=False, \
                  help= "use Princecton forcing", action="store_true")
parser.add_option("--livneh", dest="livneh", default=False, \
                  action="store_true", help = "Livneh correction to CRU precip (CONUS only)")
parser.add_option("--daymet", dest="daymet", default=False, \
                  action="store_true", help = "Daymet correction to GSWP3 precip (CONUS only)")
parser.add_option("--monthly_metdata", dest="monthly_metdata", default = '', \
                  help = "File containing met data (cpl_bypass only)")
parser.add_option("--add_temperature", dest="addt", default=0.0, \
                  help = 'Temperature to add to atmospheric forcing')
parser.add_option("--co2_file", dest="co2_file", default="fco2_datm_rcp4.5_1765-2500_c130312.nc", \
                  help = 'CLM timestep (hours)')
parser.add_option("--add_co2", dest="addco2", default=0.0, \
                  help = 'CO2 (ppmv) to add to atmospheric forcing')
parser.add_option("--startdate_add_temperature", dest="sd_addt", default="99991231", \
                  help = 'Date (YYYYMMDD) to begin addding temperature')
parser.add_option("--startdate_add_co2", dest="sd_addco2", default="99991231", \
                  help = 'Date (YYYYMMDD) to begin addding CO2')

# surface data


parser.add_option("--daymet4", dest="daymet4", default=False, \
                  action="store_true", help = "Daymet v4 downscaled GSWP3-v2 forcing with user-provided domain and surface data)")
parser.add_option("--ad_spinup", action="store_true", \
                  dest="ad_spinup", default=False, \
                  help = 'Run accelerated decomposition spinup')
parser.add_option("--exit_spinup", action="store_true", \
                  dest="exit_spinup", default=False, \
                  help = 'Run exit spinup (CLM 4.0 only)')
parser.add_option("--finidat_case", dest="finidat_case", default='', \
                  help = "case containing initial data file to use" \
                  +" (should be in your run directory)")
parser.add_option("--finidat", dest="finidat", default='', \
                  help = "initial data file to use" \
                  +" (should be in your run directory)")
parser.add_option("--finidat_year", dest="finidat_year", default=-1, \
                  help = "model year of initial data file (default is" \
                  +" last available)")
parser.add_option("--run_units", dest="run_units", default='nyears', \
                  help = "run length units (ndays, nyears)")
parser.add_option("--run_n", dest="run_n", default=50, \
                  help = "run length (in run units)")
parser.add_option("--rest_n", dest="rest_n", default=-1, \
                  help = "restart interval (in run units)")
parser.add_option("--run_startyear", dest="run_startyear",default=-1, \
                      help='Starting year for model output')
parser.add_option("--rmold", dest="rmold", default=False, action="store_true", \
                  help = 'Remove old case directory with same name' \
                  +" before proceeding")

# model output options
parser.add_option("--dailyrunoff", dest="dailyrunoff", default=False, \
                 action="store_true", help="Write daily output for hydrology")
parser.add_option("--hist_mfilt", dest="hist_mfilt", default=-1, \
                  help = 'number of output timesteps per file')
parser.add_option("--hist_nhtfrq", dest="hist_nhtfrq", default=-999, \
                  help = 'output file timestep')
parser.add_option("--hist_vars", dest="hist_vars", default='', \
                  help = 'Output only selected variables in h0 file (comma delimited)')

#parser.add_option("--queue", dest="queue", default='essg08q', \
#                  help = 'PBS submission queue')
parser.add_option("--clean_config", dest="clean_config", default=False, \
                  help = 'Run cesm_setup -clean script')
parser.add_option("--clean_build", dest="clean_build", default=False, \
                  help = 'Perform clean build before building', \
                  action="store_true")
parser.add_option("--no_config", dest="no_config", default=False, \
                  help = 'do NOT configure case', action="store_true")
parser.add_option("--no_build", dest="no_build", default=False, \
                  help = 'do NOT build model', action="store_true")
parser.add_option("--no_submit", dest="no_submit", default=False, \
                  help = 'do NOT submit built model to queue, i.e. build only', action="store_true")
parser.add_option("--align_year", dest="align_year", default=-999, \
                  help = 'Alignment year (transient run only)')
parser.add_option("--np", dest="np", default=1, \
                  help = 'number of processors')
parser.add_option("--ninst", dest="ninst", default=1, \
                  help = 'number of land model instances')
parser.add_option("--ng", dest="ng", default=64, \
                  help = 'number of groups to run in ensmble mode')
parser.add_option("--tstep", dest="tstep", default=0.5, \
                  help = 'model timestep (hours)')

parser.add_option("--nyears_ad_spinup", dest="ny_ad", default=250, \
                  help = 'number of years to run ad_spinup')
parser.add_option("--nopointdata", action="store_true", \
                  dest="nopointdata", help="Do NOT make point data (use data already created)", \
                  default=False)
parser.add_option("--makepointdata_only", action="store_true", \
                  dest="makepointdata_only", \
                  help="make point data for later use ONLY, i.e. no model config/build/submit)", \
                  default=False)
#parser.add_option("--cleanlogs",dest="cleanlogs", help=\
#                   "Removes temporary and log files that are created",\
#                   default=False,action="store_true")
parser.add_option("--nofire", action="store_true", dest="nofire", default=False, \
                    help="To turn off wildfires")
parser.add_option("--nopftdyn", action="store_true", dest="nopftdyn", \
                      default = False, help='Do not use dynamic PFT file')
parser.add_option("--harvmod", action="store_true", dest="harvmod", \
                      default=False, help = "Turn on harvest modificaton" \
                      "All harvest is performed in first timestep")
parser.add_option("--no_dynroot", dest="no_dynroot", default=False, \
                  help = 'Turn off dynamic root distribution', action="store_true")
parser.add_option("--vertsoilc", dest="vsoilc", default=False, \
                  help = 'To turn on CN with multiple soil layers, excluding CENTURY C module (CLM4ME on as well)', action="store_true")
parser.add_option("--centbgc", dest="centbgc", default=False, \
                  help = 'To turn on CN with multiple soil layers, CENTURY C module (CLM4ME on as well)', action="store_true")
parser.add_option("--CH4", dest="CH4", default=False, \
                  help = 'To turn on CN with CLM4me', action="store_true")
parser.add_option("--1850_ndep", dest="ndep1850", default=False, \
                  help = 'Use constant 1850 N deposition', action="store_true")
parser.add_option("--ndep_rcp85", dest="ndeprcp85", default=False, \
                  help = 'Use RCP8.5 N deposition', action="store_true")
parser.add_option("--1850_aero", dest="aero1850", default=False, \
                  help = 'Use constant 1850 aerosol deposition', action="store_true")
parser.add_option("--aero_rcp85", dest="aerorcp85", default=False, \
                  help = 'Use RCP8.5 aerosol deposition', action="store_true")
parser.add_option("--1850_co2", dest="co21850", default=False, \
                  help = 'Use constant 1850 CO2 concentration', action="store_true")
parser.add_option("--C13", dest="C13", default=False, \
                  help = 'Switch to turn on C13', action="store_true")
parser.add_option("--C14", dest="C14", default=False, \
                  help = 'Use C14 as C13 (no decay)', action="store_true")
parser.add_option("--branch", dest="branch", default=False, \
		  help = 'Switch for branch run', action="store_true")
parser.add_option("--makemetdata", dest="makemet", default=False, \
		  help = 'Generate meteorology', action="store_true")
parser.add_option("--surfdata_grid", dest="surfdata_grid", default=False, \
                  help = 'Use gridded surface data instead of site data', action="store_true")
parser.add_option("--include_nonveg", dest="include_nonveg", default=False, \
                  help = 'Include non-vegetated columns/Landunits in surface data')
parser.add_option("--trans2", dest="trans2", default=False, action="store_true", \
                  help = 'Transient phase 2 (1901-2010) - CRUNCEP only')
parser.add_option("--transtag", dest="transtag", default="", \
                  help = 'Transient experiment runs, generally any tag to append to a casename')
parser.add_option("--spinup_vars", dest="spinup_vars", default=False, \
                  help = 'Limit output vars in spinup runs', action="store_true")
parser.add_option("--trans_varlist", dest = "trans_varlist", default='', help = "Transient outputs")
parser.add_option("--c_only", dest="c_only", default=False, \
                 help="Carbon only (supplemental P and N)", action="store_true")
parser.add_option("--cn_only", dest="cn_only", default=False, \
                  help = 'Carbon/Nitrogen only (supplemental P)', action="store_true")
parser.add_option("--cp_only", dest="cp_only", default=False, \
                  help = 'Carbon/Phosphorus only (supplemental N)', action = "store_true")
parser.add_option("--ensemble_file", dest="ensemble_file", default='', \
                  help = 'Parameter sample file to generate ensemble')
parser.add_option("--mc_ensemble", dest="mc_ensemble", default=-1, \
                  help = 'Monte Carlo ensemble (argument is # of simulations)')
parser.add_option("--ensemble_nocopy", dest="ensemble_nocopy", default=False, \
                  help = 'Do not copy files to ensemble directories', action="store_true")
parser.add_option("--surffile", dest="surffile", default="", \
                  help = 'Surface file to use')
parser.add_option("--domainfile", dest="domainfile", default="", \
                  help = 'Domain file to use')
parser.add_option("--fates_hydro", dest="fates_hydro", default=False, action="store_true", \
                  help = 'Set fates hydro to true')
parser.add_option("--fates_nutrient", dest="fates_nutrient", default="", \
                  help = 'Which version of fates_nutrient to use (RD or ECA)')
parser.add_option("--fates_paramfile", dest="fates_paramfile", default="", \
                  help = 'Fates parameter file to use')
parser.add_option("--var_soilthickness", dest="var_soilthickness", default=False, \
                  help = 'Use variable soil thickness from surface data', action="store_true")
parser.add_option("--no_budgets", dest="no_budgets", default=False, \
                  help = 'Turn off CNP budget calculations', action='store_true')
parser.add_option("--use_hydrstress", dest="use_hydrstress", default=False, \
                  help = 'Turn on hydraulic stress', action='store_true')
parser.add_option("--spruce_treatments", dest="spruce_treatments", default=False, \
                  help = 'Run SPRUCE treatment simulations (ensemble mode)', action='store_true')

#Changed by Ming for mesabi
parser.add_option("--archiveroot", dest="archiveroot", default='', \
                  help = "archive root directory only for mesabi")
#Added by Kirk to include the modified parameter file
parser.add_option("--mod_parm_file", dest="mod_parm_file", default='', \
                  help = "adding the path to the modified parameter file")
parser.add_option("--mod_parm_file_P", dest="mod_parm_file_P", default='', \
                  help = "adding the path to the modified parameter file")
parser.add_option("--parm_list", dest="parm_list", default='parm_list', \
                  help = 'File containing list of parameters to vary')
parser.add_option("--postproc_file", dest="postproc_file", default="", \
                  help = 'File for ensemble post processing')
parser.add_option("--walltime", dest="walltime", default=6, \
                  help = "desired walltime for each job (hours)")
parser.add_option("--lai", dest="lai", default=-999, \
                  help = 'Set constant LAI (SP mode only)')
parser.add_option("--maxpatch_pft", dest="maxpatch_pft", default=17, \
                  help = "user-defined max. patch PFT number, default is 17")
parser.add_option("--landusefile", dest="pftdynfile", default='', \
                  help='user-defined dynamic PFT file')
parser.add_option("--var_list_pft", dest="var_list_pft", default="",help='Comma-separated list of vars to output at PFT level')
(options, args) = parser.parse_args()

#-------------------------------------------------------------------------------
# If only make point(s) data, reset relevant options.
if (options.makepointdata_only):
    options.no_config   = True
    options.no_build    = True
    options.no_submit   = True
    options.nopointdata = False
    options.domainfile  = ""
    options.surffile = ""
    options.pftdynfile=""
    options.nopftdyn = False
elif(options.domainfile!="" and options.surffile!="" and \
    (options.nopftdyn or options.pftdynfile!="")):
    options.nopointdata = True
    

#Set default model root
if (options.csmdir == ''):
   if (os.path.exists('../E3SM')):
       options.csmdir = os.path.abspath('../E3SM')
       print('Model root not specified.  Defaulting to '+options.csmdir)
   else:
       print('Error:  Model root not specified.  Please set using --model_root')
       sys.exit(1)
elif (not os.path.exists(options.csmdir)):
     print('Error:  Model root '+options.csmdir+' does not exist.')
     sys.exit(1)

#check whether model named clm or elm
if (os.path.exists(options.csmdir+'/components/elm')):
  mylsm='ELM'
  model_name='elm'
  if (options.res == 'CLM_USRDAT'):
    options.res = 'ELM_USRDAT'
else:
  mylsm='CLM'
  model_name='clm2'

#machine info:  cores per node
ppn=1
if ('titan' in options.machine):
    ppn=16
    if (int(options.walltime) > 2 and int(options.ng) < 2048):
        print('Requested walltime too long')
        print('Setting to 2 hours.')
        options.walltime=2
elif ('metis' in options.machine):
    ppn=16
elif ('oic2' in options.machine):
    ppn=8
elif ('oic5' in options.machine or 'cori-haswell' in options.machine or 'eos' in options.machine \
      or 'cades' in options.machine):
    ppn=32
elif ('cori-knl' in options.machine):
    ppn=64
elif ('edison' in options.machine):
    ppn=24
elif ('anvil' in options.machine):
    ppn=36
elif ('compy' in options.machine):
    ppn=40
elif ('chrysalis' in options.machine):
    ppn=64
elif ('pm-cpu' in options.machine):
    ppn=128
elif ('docker' in options.machine):
    ppn=4
if (options.ensemble_file == ''):
  ppn=min(ppn, int(options.np))

PTCLMdir = os.getcwd()

#if (options.hist_vars != ''):
#    hist_vars = os.path.abspath(options.hist_vars)

#set model if not specified
if (options.mymodel == ''):
  if ('clm5' in options.csmdir): 
      options.mymodel = 'CLM5'
  elif ('E3SM' in options.csmdir or 'e3sm' in options.csmdir or 'ACME' in options.csmdir):
      options.mymodel = 'ELM'
  else:
      print('Error:  Model not specified')
      sys.exit(1)

#check for valid csm directory
if (os.path.exists(options.csmdir) == False):
    print('Error:  invalid model root directory.  Please specify with --model_root')
    sys.exit(1)
else:
    csmdir     = options.csmdir
    scriptsdir = csmdir+'/cime/scripts'
#case directory
if (options.caseroot == '' or (os.path.exists(options.caseroot) == False)):
    caseroot = csmdir+'/cime/scripts'
else:
    caseroot = os.path.abspath(options.caseroot)

#case run root directory
runroot = os.path.abspath(options.runroot)

#check for valid input data directory
if (options.ccsm_input == '' or (os.path.exists(options.ccsm_input) \
                                 == False)):
    print('Error:  invalid input data directory')
    sys.exit(1)
else:
    options.ccsm_input = os.path.abspath(options.ccsm_input)

#----------------------------------------------------------------------------------
# check for a specific forcing data, GSWP3-Daymet4, to offline ELM
# This is high-resolution dataset, usually together with user-defined domain and surface data
if (options.daymet4):
    if (not options.gswp3): options.gswp3 = True
    if (options.metdir=='none'):
        print('Error:  must provide user-defined " --metdir " for " --daymet4"')
        sys.exit(1)
    if (options.domainfile==''):
        print('Error:  must provide user-defined " --domainfile " for " --daymet4"')
        sys.exit(1)
    if (options.surffile==''):
        print('Error:  must provide user-defined " --surffile " for " --daymet4"')
        sys.exit(1)
    if (options.istrans  or '20TR' in options.compset):
        if(options.pftdynfile=='' and not options.nopftdyn):
            print('Error:  must provide user-defined " --pftdynfile " for " --daymet4"')
            sys.exit(1)
#----------------------------------------------------------------------------------



compset = options.compset
isglobal = False
if (options.site == ''):
    isglobal = True
    options.site=options.res

if ('CBCN' in compset or 'ICB' in compset or 'CLM45CB' in compset):
    cpl_bypass = True
else:
    cpl_bypass = False

surfdir = 'surfdata_map'
if (options.mymodel == 'ELM'):
    if ('ECA' in compset or 'ECA' in options.fates_nutrient):
        parm_file = 'clm_params.c180713.nc'
    elif('RD' in compset or 'RD' in options.fates_nutrient):
        parm_file = 'clm_params_c180524.nc'
    else:
        parm_file = 'clm_params_c180301.nc'   #FATES/CROP
if (options.mymodel == 'CLM5'):
    parm_file = 'clm5_params.c171117.nc'

#pftphys_stamp = '_c160711' #'c160711_root'
#pftphys_stamp = '_c160711_test170303'
#CNPstamp = 'c131108'
CNPstamp = 'c180529'

#check consistency of options
if (options.istrans or '20TR' in compset):
    #ignore spinup option if transient compset
    if (options.ad_spinup or options.exit_spinup):
      print('Spinup options not available for transient compset.')
      sys.exit(1)
    #finidat is required for transient compset
    if (options.finidat_case == '' and options.finidat == ''):
        print('Error:  must provide initial data file for I20TR compsets')
        sys.exit(1)

#get full path of finidat file
finidat=''
finidat_year=int(options.finidat_year)

if ('CN' in compset or 'ECA' in compset):
  mybgc = 'CN'
elif ('ED' in compset):
  mybgc = 'ED'
else:
  mybgc = 'none'

if (options.exit_spinup):
    if (options.mycaseid != ''):
        finidat = options.mycaseid+'_'+options.site+'_I1850'+mybgc+'_ad_spinup'
    else:
        finidat = options.site+'_I1850'+mybgc+'_ad_spinup'
    finidat_year = int(options.ny_ad)+1

if (options.finidat == ''  and options.finidat_case == ''):  #not user-defined
    if (options.coldstart==False and compset == "I1850CLM45"+mybgc and options.ad_spinup == False):
        if (options.mycaseid != ''):
            options.finidat_case = options.mycaseid+'_'+options.site+ \
                '_I1850CLM45'+mybgc+'_ad_spinup'
        else:
            options.finidat_case = options.site+'_I1850CLM45'+mybgc+'_ad_spinup'

        if (options.finidat_year == -1):
            finidat_year = int(options.ny_ad)+1
    
    if (compset == "I20TRCLM45"+mybgc or compset == "I20TRCRUCLM45"+mybgc):
        if (options.mycaseid != ''):
            options.finidat_case = options.mycaseid+'_'+options.site+ \
                '_I1850CLM45'+mybgc
        else:
            options.finidat_case = options.site + '_I1850CLM45'+mybgc
            
        if (options.finidat_year == -1):
            finidat_year=1850
    if (compset == "I20TR"+mybgc):
        if (options.mycaseid != ''):
            options.finidat_case = options.mycaseid+'_'+options.site+ \
                '_I1850'+mybgc
        else:
            options.finidat_case = options.site + '_I1850'+mybgc
        if (options.finidat_year == -1):
            finidat_year = 1850

        #finidat is required for transient compset
            if (os.path.exists(runroot+'/'+options.finidat_case) == False):
                print('Error:  must provide initial data file for I20TRCLM45CN/BGC compset OR '+ \
                          runroot+'/'+options.finidat_case+' existed as refcase')
                sys.exit(1)

if (options.finidat_case != ''):
    finidat_yst = str(10000+finidat_year)
    if (mylsm == 'ELM'):
      finidat = runroot+'/'+options.finidat_case+'/run/'+ \
              options.finidat_case+'.elm.r.'+finidat_yst[1:]+ \
              '-01-01-00000.nc'
    else:
      finidat = runroot+'/'+options.finidat_case+'/run/'+ \
              options.finidat_case+'.clm2.r.'+finidat_yst[1:]+ \
              '-01-01-00000.nc'

if (options.finidat != ''):
    finidat = options.finidat
    finidat_year = int(finidat[-19:-15])
    finidat_yst = str(10000+finidat_year)    

#construct default casename
casename    = options.site+"_"+compset
if (options.mycaseid != ""):
    casename = options.mycaseid+'_'+casename

if (options.metdir!='none'):# obviously user-provided met forcing is not reanalysis type
    use_reanalysis = False
#CRU-NCEP 2 transient phases
elif ('CRU' in compset or options.cruncep or options.gswp3 or options.gswp3_w5e5 or \
            options.crujra or options.cruncepv8 or options.princeton or options.cplhist):
    use_reanalysis = True
else:
    use_reanalysis = False
if ('20TR' in compset and use_reanalysis and (not cpl_bypass)):
    if options.trans2:
        casename = casename+'_phase2'
    else:
        casename = casename+'_phase1'
if (options.ad_spinup):
    casename = casename+'_ad_spinup'
if (options.exit_spinup):
    casename = casename+'_exit_spinup'
if (options.istrans and not "20TR" in compset):
    casename = casename+'_trans'
if (options.transtag != ""): 
    casename = casename+'_'+options.transtag

PTCLMfiledir = options.ccsm_input+'/lnd/clm2/PTCLM'

#if (caseroot == runroot):
#    casedir=caseroot+"/"+casename+'/case'
#    os.system('mkdir -p '+casedir)
#elif (caseroot != "./"):
if (caseroot != "./"):
    casedir=os.path.abspath(caseroot+"/"+casename)
else:
    casedir=os.path.abspath(casename)

print('Machine is: '+options.machine)
#Check for existing case directory
if (os.path.exists(casedir)):
    
    print('Warning:  Case directory exists')
    if (options.rmold):
        print('--rmold specified.  Removing old case ')
        os.system('rm -rf '+casedir)
    else:
        var = input('proceed (p), remove old (r), or exit (x)? ')
        if var[0] == 'r':
            os.system('rm -rf '+casedir)
        if var[0] == 'x':
            sys.exit(1)    
print("CASE directory is: "+casedir)

#Construct case build and run directory
if (options.exeroot == '' or (os.path.exists(options.exeroot) == False)):
    exeroot = runroot+'/'+casename+'/bld'
    #if ('titan' in options.machine or 'eos' in options.machine):
    #    exeroot = os.path.abspath(os.environ['HOME']+ \
   # 	    '/acme_scratch/pointclm/'+casename+'/bld')
else:
    options.no_build=True
    exeroot=options.exeroot
print("CASE exeroot is: "+exeroot)
rundir=runroot+'/'+casename+'/run'
print("CASE rundir is: "+rundir)
if (options.rmold):
    if (options.no_build == False):
        print('Removing build directory: '+exeroot)
        os.system('rm -rf '+exeroot)
    print('Removing run directory: '+rundir)
    os.system('rm -rf '+rundir)

#------Make domain, surface data and pftdyn files ------------------
mysimyr=1850
#if (('1850' not in compset and '20TR' not in compset) or 'ED' in compset or 'FATES' in compset):
#    #note - spinup with 2000 conditions for FATES
#    mysimyr=2000

if (options.nopointdata == False):
    ptcmd = 'python makepointdata.py --ccsm_input '+options.ccsm_input+ \
        ' --keep_duplicates --lat_bounds '+options.lat_bounds+' --lon_bounds '+ \
        options.lon_bounds+' --mysimyr '+str(mysimyr)+' --model '+options.mymodel
    if (options.metdir != 'none'):
        ptcmd = ptcmd + ' --metdir '+options.metdir
    if (options.makemet):
        ptcmd = ptcmd + ' --makemetdata'
    if (options.surfdata_grid):
        ptcmd = ptcmd + ' --surfdata_grid'
    if (options.include_nonveg):
        ptcmd = ptcmd + ' --include_nonveg'
    if (options.nopftdyn):
        ptcmd = ptcmd + ' --nopftdyn'
    if (options.mymask != ''):
        ptcmd = ptcmd + ' --mask '+options.mymask
    if (float(options.lai) > 0):
        ptcmd = ptcmd + ' --lai '+str(options.lai)
    if (int(options.mypft) >= 0):
        ptcmd = ptcmd + ' --pft '+str(options.mypft)
    if ('CROP' in compset):
        ptcmd = ptcmd + ' --crop'
    if (isglobal):
        ptcmd = ptcmd + ' --res '+options.res
        
        # if using global dataset to extract for running at a list of grid-points
        if (options.point_list != ''):
            ptcmd = ptcmd+' --point_list '+options.point_list
            # changing resolution of extracted grid point area
            if(options.point_area_kmxkm!=None):# area in a square measured by kmxkm
                ptcmd = ptcmd+' --point_area_kmxkm '+options.point_area_kmxkm
            elif(options.point_area_degxdeg!=None):# area in a square measured by degreexdegree
                ptcmd = ptcmd+' --point_area_degxdeg '+options.point_area_degxdeg

    else:
        ptcmd = ptcmd + ' --site '+options.site+' --sitegroup '+options.sitegroup

    #if(options.domainfile != ''):
    #    ptcmd = ptcmd + ' --nodomain '
    #if(options.surffile !=''):
    #    ptcmd = ptcmd + ' --nosurfdata '
    if(options.marsh):
        ptcmd = ptcmd + ' --marsh'
    if(options.humhol):
        ptcmd = ptcmd + ' --humhol'

    if (options.machine == 'eos' or options.machine == 'titan'):
        os.system('rm temp/*.nc')
        print('Note:  NCO operations are slow on eos and titan.')
        print('Submitting PBS script to make surface and domain data on rhea')
        pbs_rhea=open('makepointdata_rhea.pbs','w')
        pbs_rhea.write('#PBS -l walltime=00:30:00\n')
        pbs_rhea.write('#PBS -l nodes=1\n')
        pbs_rhea.write('#PBS -A cli112\n')
        pbs_rhea.write('#PBS -q rhea\n')
        pbs_rhea.write('#PBS -l gres=atlas1%atlas2\n\n')
        pbs_rhea.write(' module load nco\n')
        pbs_rhea.write(' cd '+os.getcwd()+'\n')
        pbs_rhea.write(' rm temp/*.nc\n')
        pbs_rhea.write(' module unload PE-intel\n')
        pbs_rhea.write(' module load PE-gnu\n')
        pbs_rhea.write(' module load python\n')
        pbs_rhea.write(' module load python_numpy\n')
        pbs_rhea.write(' module load python_scipy\n')
        pbs_rhea.write(ptcmd+'\n')
        pbs_rhea.close()
        os.system('qsub makepointdata_rhea.pbs')
        n_nc_files = 3
        if (options.nopftdyn):
            n_nc_files = 2
        n=0
        while (n < n_nc_files):
            #Wait until files have been generated on rhea to proceed
            list_dir = os.listdir('./temp')
            n=0
            for file in list_dir:
                if file.endswith('.nc'):
                    n=n+1
            os.system('sleep 10')
        #Clean up
        os.system('rm makepointdata_rhea*') 
    else:
        print(ptcmd)
        result = os.system(ptcmd)
        if (result > 0):
            print ('PointCLM:  Error creating point data.  Aborting')
            sys.exit(1)

    if(options.makepointdata_only):
        print ('PointCLM:  Successfully creating point data ONLY, i.e. no further config/build/run CLM/ELM')
        print ('PointCLM:  Files are in ./temp/*.nc, which you may save/rename properly for later use')
        sys.exit(0)

if(options.domainfile != ''):
    print('\n -----INFO: using user-provided DOMAIN')
    print('domain file: '+ options.domainfile)
if(options.surffile !=''):
    print('\n -----INFO: using user-provided SURFDATA')
    print('surface data file: '+ options.surffile)
if(options.pftdynfile !='' or options.nopftdyn):
    print('\n -----INFO: using user-provided 20th landuse data file')
    print('20th landuse data file: '+ options.pftdynfile+"'\n")
if(options.metdir != 'none'):
    print('\n -----INFO: using user-provided forcing data')
    print('Under directory: '+ options.metdir)


#get site year information
sitedatadir = os.path.abspath(PTCLMfiledir)
os.chdir(sitedatadir)
if (isglobal == False):
    AFdatareader = csv.reader(open(options.sitegroup+'_sitedata.txt',"r"))
    for row in AFdatareader:
        if row[0] == options.site:
            if (use_reanalysis):
                if ('CN' in compset or 'BGC' in compset):
                    if (options.trans2):
                        startyear = 1921
                        endyear   = int(row[7])
                    else:
                        startyear = 1901
                        endyear   = 1920
                else:
                    startyear = int(row[6]) #1901
                    endyear   = int(row[7])
            else:
                startyear=int(row[6])
                endyear=int(row[7])
            alignyear = int(row[8])
            if (options.diags):
                timezone = int(row[9])
            if (options.humhol or options.marsh):
                numxpts=2
            else:
                numxpts=1
            numypts=1
else:
    if (use_reanalysis):
        startyear=1901
        if ('20TR' in compset or options.istrans):
            endyear = 2010
            if (options.trans2):
                startyear = 1921
        else:
            endyear   = 1920
    else:    #Global default to Qian
        startyear=1948
        if ('20TR' in compset or options.istrans):
            endyear = 2004
            if (options.trans2):
                startyear = 1973
        else:
            endyear   = 1972

ptstr=''
if (isglobal == False):
    ptstr = str(numxpts)+'x'+str(numypts)+'pt'
os.chdir(csmdir+'/cime/scripts')

#parameter (pft-phys) modifications if desired
tmpdir = PTCLMdir+'/temp'

if (options.mycaseid == ''):
  myscriptsdir = 'none'
else:
  myscriptsdir = options.mycaseid

os.system('mkdir -p '+tmpdir)
if (options.mod_parm_file != ''):
    print('nccopy -3 '+options.mod_parm_file+' '+tmpdir+'/clm_params.nc')
    os.system('nccopy -3 '+options.mod_parm_file+' '+tmpdir+'/clm_params.nc')
else:
    print(parm_file)
    print('nccopy -3 '+options.ccsm_input+'/lnd/clm2/paramdata/'+parm_file+' '+tmpdir+'/clm_params.nc')
    os.system('nccopy -3 '+options.ccsm_input+'/lnd/clm2/paramdata/'+parm_file+' ' \
              +tmpdir+'/clm_params.nc')
    myncap = 'ncap'
    if ('cades' in options.machine or 'chrysalis' in options.machine or 'compy' in options.machine or 'ubuntu' in options.machine \
          or 'mymac' in options.machine or 'anvil' in options.machine):
      myncap='ncap2'

    flnr = nffun.getvar(tmpdir+'/clm_params.nc','flnr')
    if (options.humhol or options.marsh):
      print('Adding hummock-hollow parameters (default for SPRUCE site)')
    #   print('humhol_ht = 0.15m')
    #   print('humhol_dist = 1.0m')
      print('setting rsub_top_globalmax = 1.2e-5')
      print('Making br_mr a PFT-specific parameter')
      os.system(myncap+' -O -s "humhol_ht = br_mr*0+0.15" '+tmpdir+'/clm_params.nc '+tmpdir+'/clm_params.nc')
      if options.marsh:
        os.system(myncap+' -O -s "hum_frac = br_mr*0+0.50" '+tmpdir+'/clm_params.nc '+tmpdir+'/clm_params.nc')
        print('hum_frac  = 0.50')
      else:
        os.system(myncap+' -O -s "hum_frac = br_mr*0+0.64" '+tmpdir+'/clm_params.nc '+tmpdir+'/clm_params.nc')
        print('hum_frac  = 0.64')
      os.system(myncap+' -O -s "humhol_dist = br_mr*0+1.0" '+tmpdir+'/clm_params.nc '+tmpdir+'/clm_params.nc')
      if options.marsh:
        print('qflx_h2osfc_surfrate = 0.0')
        os.system(myncap+' -O -s "qflx_h2osfc_surfrate = br_mr*0+0.0" '+tmpdir+'/clm_params.nc '+tmpdir+'/clm_params.nc')
      else:
        print('qflx_h2osfc_surfrate = 1.0e-7')
        os.system(myncap+' -O -s "qflx_h2osfc_surfrate = br_mr*0+1.0e-7" '+tmpdir+'/clm_params.nc '+tmpdir+'/clm_params.nc')
      os.system(myncap+' -O -s "moss_swc_adjust=scalar(0)" '+tmpdir+'/clm_params.nc '+tmpdir+'/clm_params.nc')
      os.system(myncap+' -O -s "rsub_top_globalmax = br_mr*0+1.2e-5" '+tmpdir+'/clm_params.nc '+tmpdir+'/clm_params.nc')
      os.system(myncap+' -O -s "h2osoi_offset = br_mr*0" '+tmpdir+'/clm_params.nc '+tmpdir+'/clm_params.nc')
      flnr = nffun.getvar(tmpdir+'/clm_params.nc','flnr')
      os.system(myncap+' -O -s "br_mr = flnr" '+tmpdir+'/clm_params.nc '+tmpdir+'/clm_params.nc')
      ierr = nffun.putvar(tmpdir+'/clm_params.nc','br_mr', flnr*0.0+2.52e-6)
    #os.system(myncap+' -O -s "vcmaxse = flnr" '+tmpdir+'/clm_params.nc '+tmpdir+'/clm_params.nc')
    #ierr = nffun.putvar(tmpdir+'/clm_params.nc','vcmaxse', flnr*0.0+670)

    if (options.marsh and options.tide_components_file != ''):
        print('Adding tidal cycle components from file %s'%options.tide_components_file)
        print('Assuming file is in NOAA tide component format, degrees and meters units (e.g.: https://tidesandcurrents.noaa.gov/harcon.html?id=8441241&unit=0)')
        print('Tide datum (tide_baseline parameter) needs to be specified separately. Default is 800 mm')
        import pandas
        tidecomps=pandas.read_csv(options.tide_components_file)
        for comp in range(len(tidecomps)):
            os.system(myncap+' -O -s "tide_coeff_amp_%d = humhol_ht*0+%1.4e" '%(comp+1,tidecomps['Amplitude'].iloc[comp]*1000)+tmpdir+'/clm_params.nc '+tmpdir+'/clm_params.nc')
            os.system(myncap+' -O -s "tide_coeff_period_%d = humhol_ht*0+%1.4e" '%(comp+1,360*3600/tidecomps['Speed'].iloc[comp])+tmpdir+'/clm_params.nc '+tmpdir+'/clm_params.nc')
            os.system(myncap+' -O -s "tide_coeff_phase_%d = humhol_ht*0+%1.4e" '%(comp+1,tidecomps['Phase'].iloc[comp]*math.pi/180)+tmpdir+'/clm_params.nc '+tmpdir+'/clm_params.nc')
            os.system(myncap+' -O -s "tide_baseline = humhol_ht*0+800.0" '+tmpdir+'/clm_params.nc '+tmpdir+'/clm_params.nc')
    elif options.marsh:
        print('Tidal cycle coefficients not specified. Model will use GCREW defaults. Can also edit in parm file.')
    #os.system(myncap+' -O -s "crit_gdd1 = flnr" '+tmpdir+'/clm_params.nc '+tmpdir+'/clm_params.nc')
    #os.system(myncap+' -O -s "crit_gdd2 = flnr" '+tmpdir+'/clm_params.nc '+tmpdir+'/clm_params.nc')
    #os.system(myncap+' -O -s "crit_onset_gdd = ndays_on" '+tmpdir+'/clm_params.nc '+tmpdir+'/clm_params.nc')
    #ierr = nffun.putvar(tmpdir+'/clm_params.nc','crit_gdd1', flnr*0.0+4.8)
    #ierr = nffun.putvar(tmpdir+'/clm_params.nc','crit_gdd2', flnr*0.0+0.13)
    #ndays_on = nffun.getvar(tmpdir+'/clm_params.nc','ndays_on')
    #ierr = nffun.putvar(tmpdir+'/clm_params.nc','crit_onset_gdd', ndays_on*0.0+200.0)

    # BSulman: These Nfix constants can break the model if they don't have the right length.
    #os.system(myncap+' -O -s "Nfix_NPP_c1 = br_mr*+1.8" '+tmpdir+'/clm_params.nc '+tmpdir+'/clm_params.nc')
    #os.system(myncap+' -O -s "Nfix_NPP_c2 = br_mr*0.003" '+tmpdir+'/clm_params.nc '+tmpdir+'/clm_params.nc')
    #os.system(myncap+' -O -s "nfix_timeconst = br_mr*10.0" '+tmpdir+'/clm_params.nc '+tmpdir+'/clm_params.nc')

os.system('chmod u+w ' +tmpdir+'/clm_params.nc')
if (options.parm_file != ''):
    pftfile = tmpdir+'/clm_params.nc'
    if ('/' not in options.parm_file):
       #assume in pointclm directory
       input  = open(PTCLMdir+'/'+options.parm_file)
    else:   #assume full path given
       input   = open(os.path.abspath(options.parm_file))
    for s in input:
        if s[0:1] != '#':
            values = s.split()
            try:
                thisvar = nffun.getvar(pftfile, values[0])
                if (len(values) == 2):
                    thisvar[...] = float(values[1])
                elif (len(values) == 3):
                    if (float(values[1]) > 0):
                        thisvar[int(values[1])] = float(values[2])
                    else:
                        thisvar[...] = float(values[2])
                ierr = nffun.putvar(pftfile, values[0], thisvar)
            except ValueError:
                print('Parameter %s not found in clm_params.nc. Adding.'%values[0])
                if (len(values) == 2):
                    print('No PFT specified. Assuming universal parameter')
                    os.system(myncap+' -O -s "%s = q10_mr*0+%1.4e" '%(values[0],values[1])+tmpdir+'/clm_params.nc '+tmpdir+'/clm_params.nc')
                elif (len(values) == 3):
                    if (float(values[1]) > 0):
                        print('PFT specified. Setting value for all PFTs')
                        os.system(myncap+' -O -s "%s = flnr*0+%s" '%(values[0],values[2])+tmpdir+'/clm_params.nc '+tmpdir+'/clm_params.nc')
                    else:
                        print('No PFT specified. Assuming universal parameter')
                        os.system(myncap+' -O -s "%s = q10_mr*0+%s" '%(values[0],values[2])+tmpdir+'/clm_params.nc '+tmpdir+'/clm_params.nc')
               
    input.close()

if (options.parm_vals != ''):
    pftfile = tmpdir+'/clm_params.nc'
    parms = options.parm_vals.split('/')
    nparms = len(parms)
    for n in range(0,nparms):
        parm_data=parms[n].split(',')
        thisvar = nffun.getvar(pftfile, parm_data[0])
        if (len(parm_data) == 2):
            thisvar[...] = float(parm_data[1])
        elif (len(parm_data) == 3): 
           if (float(parm_data[1]) >= 0):
               thisvar[int(parm_data[1])] = float(parm_data[2])
           else: 
               thisvar[...] = float(parm_data[2])
        ierr =  nffun.putvar(pftfile, parm_data[0], thisvar)
           
#parameter (soil order dependent) modifications if desired    ::X.YANG 
if (options.mymodel == 'ELM'):
    if (options.mod_parm_file_P != ''):
        os.system('cp '+options.mod_parm_file_P+' '+tmpdir+'/CNP_parameters.nc')
    else:
        os.system('cp '+options.ccsm_input+'/lnd/clm2/paramdata/CNP_parameters_'+CNPstamp+'.nc ' \
                  +tmpdir+'/CNP_parameters.nc')
    os.system('chmod u+w ' +tmpdir+'/CNP_parameters.nc')

    if (options.parm_file_P != ''):
        soilorderfile = tmpdir+'/CNP_parameters.nc'
        if ('/' not in options.parm_file_P):
            #assume in pointclm directory
            input  = open(PTCLMdir+'/'+options.parm_file_P)
        else:   #assume full path given
            input   = open(os.path.abspath(options.parm_file_P))
            input   = open(os.path.abspath(options.parm_file_P))
        for s in input:
            if s[0:1] != '#':
                values = s.split()
                thisvar = nffun.getvar(soilorderfile, values[0])
                if (len(values) == 2):
                    thisvar[...] = float(values[1])
                elif (len(values) == 3):
                    if (float(values[1]) >= 0):
                        thisvar[int(values[1])] = float(values[2])
                    else:
                        thisvar[...] = float(values[2])
                ierr = nffun.putvar(soilorderfile, values[0], thisvar)
        input.close()

#set number of run years for ad, exit spinup cases
if (options.ny_ad != options.run_n and options.ad_spinup):
    options.run_n = options.ny_ad
elif (options.exit_spinup):
    options.run_n = 1

#create new case
timestr=str(int(float(options.walltime)))+':'+str(int((float(options.walltime)- \
                                     int(float(options.walltime)))*60))+':00'
cmd = './create_newcase --case '+casedir+' --mach '+options.machine+' --compset '+ \
	   options.compset+' --res '+options.res+' --mpilib '+ \
           options.mpilib+' --walltime '+timestr+' --handle-preexisting-dirs u'

if (options.mymodel == 'CLM5'):
   cmd = cmd+' --run-unsupported'
if (options.project != ''):
   cmd = cmd+' --project '+options.project
if (options.compiler != ''):
   cmd = cmd+' --compiler '+options.compiler
cmd = cmd+' > create_newcase.log'
print(cmd)
result = os.system(cmd)

if (os.path.isdir(casedir)):
    print(casename+' created.  See create_newcase.log for details')
    #os.system('mv create_newcase.log '+casename)
    os.system('mv create_newcase.log '+casedir)
else:
    print('Error:  runcase.py Failed to create case.  See create_newcase.log for details')
    sys.exit(1)

os.chdir(casedir)

#env_build
result = os.system('./xmlchange SAVE_TIMING=FALSE')
result = os.system('./xmlchange EXEROOT='+exeroot)
#if ('ED' in compset):
#    result = os.system('./xmlchange PIO_VERSION=1')
#else:
result = os.system('./xmlchange PIO_VERSION=%s'%options.pio_version)
if (options.mymodel == 'ELM'):
    result = os.system('./xmlchange MOSART_MODE=NULL')

if (options.debug):
    result = os.system('./xmlchange DEBUG=TRUE')

#clm 4_5 cn config options
#clmcn_opts = "'-phys clm4_5 -cppdefs -DMODAL_AER'"
#if (options.mymodel == 'ELM'):
#    os.system("./xmlchange CLM_CONFIG_OPTS="+clmcn_opts)

if (options.machine == 'userdefined'):
    os.system("./xmlchange COMPILER="+options.compiler)
    os.system("./xmlchange OS=linux")
    os.system("./xmlchange EXEROOT="+runroot+'/'+casename+"/bld")

#-------------- env_run.xml modifications -------------------------
os.system('./xmlchange RUNDIR='+rundir)
os.system('./xmlchange DOUT_S=TRUE')
os.system('./xmlchange DOUT_S_ROOT='+runroot+'/archive/'+casename)
os.system('./xmlchange DIN_LOC_ROOT='+options.ccsm_input)
os.system('./xmlchange DIN_LOC_ROOT_CLMFORC='+options.ccsm_input+'/atm/datm7/')    

#define mask and resoultion
if (isglobal == False):
    os.system('./xmlchange '+mylsm+'_USRDAT_NAME='+str(numxpts)+'x'+str(numypts)+'pt_'+options.site)
if (options.ad_spinup):
    if (options.mymodel == 'ELM'):
        os.system("./xmlchange --append "+mylsm+"_BLDNML_OPTS='-bgc_spinup on'")
    elif (options.mymodel == 'CLM5'):
        os.system('./xmlchange CLM_ACCELERATED_SPINUP=on')
        os.system('./xmlchange CLM_FORCE_COLDSTART=on')
#if (options.use_hydrstress):
#    os.system("./xmlchange --append "+mylsm+"_BLDNML_OPTS='-hydrstress'")

if (int(options.run_startyear) > -1):
    os.system('./xmlchange RUN_STARTDATE='+str(options.run_startyear)+'-01-01')
    print("Setting run start date to "+str(options.run_startyear)+'-01-01')
if (options.domainfile == ''):
  os.system('./xmlchange ATM_DOMAIN_PATH="\${RUNDIR}"')
  os.system('./xmlchange LND_DOMAIN_PATH="\${RUNDIR}"')
  os.system('./xmlchange ATM_DOMAIN_FILE=domain.nc')
  os.system('./xmlchange LND_DOMAIN_FILE=domain.nc')
else:
  domainpath = '/'.join(options.domainfile.split('/')[:-1])
  domainfile = options.domainfile.split('/')[-1]
  os.system('./xmlchange ATM_DOMAIN_PATH='+domainpath)
  os.system('./xmlchange LND_DOMAIN_PATH='+domainpath)
  os.system('./xmlchange ATM_DOMAIN_FILE='+domainfile)
  os.system('./xmlchange LND_DOMAIN_FILE='+domainfile)

#turn off archiving
os.system('./xmlchange DOUT_S=FALSE') 
#datm options
if (not cpl_bypass):
    if (use_reanalysis):
        os.system('./xmlchange DATM_MODE=CLMCRUNCEP') 
    else:
        if (isglobal == False):
            os.system('./xmlchange DATM_MODE=CLM1PT') 
    os.system('./xmlchange DATM_CLMNCEP_YR_START='+str(startyear))
    os.system('./xmlchange DATM_CLMNCEP_YR_END='+str(endyear))
    if (options.align_year == -999):
        os.system('./xmlchange DATM_CLMNCEP_YR_ALIGN=1')
    else:
        os.system('./xmlchange DATM_CLMNCEP_YR_ALIGN='+str(options.align_year))

#Change simulation timestep
if (options.tstep != 0.5):
    os.system('./xmlchange ATM_NCPL='+str(int(24/float(options.tstep))))

#Branch run options
if (options.branch or options.exit_spinup):
    os.system('./xmlchange RUN_TYPE=branch')
    os.system('./xmlchange RUN_REFDATE='+finidat_yst[1:]+'-01-01')
    os.system('./xmlchange RUN_REFCASE='+options.finidat_case)
else:
    if (('CN' in compset or 'BGC' in compset) and options.ad_spinup \
            == False and options.coldstart==False):
        os.system('./xmlchange RUN_REFDATE='+finidat_yst[1:]+'-01-01')

    #adds capability to run with transient CO2
if ('20TR' in compset or options.istrans):
    os.system('./xmlchange CCSM_BGC=CO2A')
    os.system('./xmlchange '+mylsm+'_CO2_TYPE=diagnostic')
    if (options.run_startyear == -1):
        os.system('./xmlchange RUN_STARTDATE=1850-01-01')
    
#No pnetcdf for small cases on compy
if (('docker' in options.machine or 'compy' in options.machine) and int(options.np) < 80):
  os.system('./xmlchange PIO_TYPENAME=netcdf')

comps = ['ATM','LND','ICE','OCN','CPL','GLC','ROF','WAV','ESP','IAC']
for c in comps:
    print('Setting NTASKS_'+c+' to '+str(options.np))
    os.system('./xmlchange NTASKS_'+c+'='+str(options.np))
    os.system('./xmlchange NTHRDS_'+c+'=1')

if (int(options.np) > 1):
    os.system('./xmlchange MAX_TASKS_PER_NODE='+str(ppn))
    os.system('./xmlchange MAX_MPITASKS_PER_NODE='+str(ppn))

if (int(options.ninst) > 1):
    os.system('./xmlchange NINST_LND='+options.ninst)
    os.system('./xmlchange NTASKS_LND='+options.ninst)

os.system('./xmlchange STOP_OPTION='+options.run_units)
os.system('./xmlchange STOP_N='+str(options.run_n))

if (options.rest_n > 0):
  print('Setting REST_N to '+str(options.rest_n))
  os.system('./xmlchange REST_N='+str(options.rest_n))

# user-defined PFT numbers (default is 17)
if (options.maxpatch_pft != 17):
  print('resetting maxpatch_pft to '+str(options.maxpatch_pft))
  xval = subprocess.check_output('./xmlquery --value CLM_BLDNML_OPTS', cwd=casedir, shell=True)
  xval = '-maxpft '+str(options.maxpatch_pft)+' '+xval
  os.system("./xmlchange --id CLM_BLDNML_OPTS --val '" + xval + "'")

# for spinup and transient runs, PIO_TYPENAME is pnetcdf, which now not works well
if('mac' in options.machine or 'cades' in options.machine): 
    os.system("./xmlchange --id PIO_TYPENAME --val netcdf ")


#--------------------------CESM setup ----------------------------------------

if (options.clean_config):
    result = os.system('./case.setup -clean')
    if (result > 0):
        print('Error:  PointCLM.py failed to setup case.  Aborting')
        sys.exit(1)
    os.system('rm -f Macro')
    os.system('rm -f user-nl-*')

# Add options for FFLAGS to Macros file here 

#clm namelist modifications
for i in range(1,int(options.ninst)+1):
    if (int(options.ninst) == 1):
        output = open("user_nl_"+mylsm.lower(),'w')
    else:
        if (i < 10):
            output = open("user_nl_"+mylsm.lower()+"_000"+str(i),'w')
        elif (i < 100):
            output = open("user_nl_"+mylsm.lower()+"_00"+str(i),'w')
        elif (i < 1000):
            output = open("user_nl_"+mylsm.lower()+"_0"+str(i),'w')
    output.write('&clm_inparm\n')

    if (options.namelist_file != ''):
      #First assume located in OLMT folder:
      if (os.path.isfile(PTCLMdir+'/'+options.namelist_file)):
        namelist_in = open(PTCLMdir+'/'+options.namelist_file,'r')
      elif (os.path.isfile(options.namelist_file)):
        namelist_in = open(options.namelist_file,'r')
      else: 
        print('Error:  namelist_file does not exist.  Aborting')
        sys.exit(1)
      for s in namelist_in:
        output.write(s)
      namelist_in.close()

    #history file options
    #outputs for SPRUCE MiP and Jiafu's diagnostics code:
    var_list_hourly = ['FPSN','FSH','EFLX_LH_TOT','Rnet','FCTR','FGEV','FCEV','SOILLIQ','QOVER','QDRAI','TG','TV','TSA','TSOI', \
                      'FSA','FSDS','FLDS','TBOT','RAIN','SNOW','WIND','PBOT','QBOT','QVEGT','QVEGE','QSOIL', \
                      'QH2OSFC','H2OSOI','ZWT','SNOWDP','TLAI','RH2M','QRUNOFF']
    if ('RD' in compset or 'ECA' in compset):
      var_list_hourly.extend(['GPP', 'NEE', 'NEP', 'NPP', 'LEAFC_ALLOC', 'AGNPP', 'MR', \
            'CPOOL_TO_DEADSTEMC', 'LIVECROOTC_XFER_TO_LIVECROOTC', 'DEADCROOTC_XFER_TO_DEADCROOTC', \
            'CPOOL_TO_LIVECROOTC', 'CPOOL_TO_DEADCROOTC', 'FROOTC_ALLOC', 'AR', 'LEAF_MR', 'CPOOL_LEAF_GR',
            'TRANSFER_LEAF_GR', 'CPOOL_LEAF_STORAGE_GR', 'LIVESTEM_MR', 'CPOOL_LIVESTEM_GR', \
            'TRANSFER_LIVESTEM_GR', 'CPOOL_LIVESTEM_STORAGE_GR', 'CPOOL_DEADSTEM_GR', \
            'TRANSFER_DEADSTEM_GR', 'CPOOL_DEADSTEM_STORAGE_GR', 'LIVECROOT_MR', 'CPOOL_LIVECROOT_GR', \
            'TRANSFER_LIVECROOT_GR', 'CPOOL_LIVECROOT_STORAGE_GR', 'CPOOL_DEADCROOT_GR', 'TRANSFER_DEADCROOT_GR', 'CPOOL_DEADCROOT_STORAGE_GR', \
            'FROOT_MR', 'CPOOL_FROOT_GR', 'TRANSFER_FROOT_GR', 'CPOOL_FROOT_STORAGE_GR', 'TOTVEGC', 'LEAFC', 'LIVESTEMC', 'DEADSTEMC', \
            'FROOTC', 'LIVECROOTC', 'DEADCROOTC', 'DEADSTEMC_STORAGE', \
            'LIVESTEMC_STORAGE', 'DEADCROOTC_STORAGE', 'LIVECROOTC_STORAGE', 'CPOOL_TO_DEADSTEMC_STORAGE', \
            'CPOOL_TO_LIVESTEMC_STORAGE', 'CPOOL_TO_DEADCROOTC_STORAGE', 'CPOOL_TO_LIVECROOTC_STORAGE', \
            'ER', 'HR', 'FROOTC_STORAGE', 'LEAFC_STORAGE', 'LEAFC_XFER', 'FROOTC_XFER', 'LIVESTEMC_XFER', \
            'DEADSTEMC_XFER', 'LIVECROOTC_XFER', 'DEADCROOTC_XFER', 'SR', 'HR_vr', 'FIRA', 'CPOOL_TO_LIVESTEMC', 'TOTLITC', 'TOTSOMC'])
    #var_list_hourly_bgc 
    var_list_daily = ['TLAI','SNOWDP','H2OSFC','ZWT']
    if ('RD' in compset or 'ECA' in compset):
      var_list_daily.extend(['TOTLITC', 'TOTSOMC', 'CWDC', 'LITR1C_vr', 'LITR2C_vr', 'LITR3C_vr', 'SOIL1C_vr', \
                      'SOIL2C_vr', 'SOIL3C_vr', 'CPOOL','NPOOL','PPOOL','FPI','FPI_P','FPG','FPG_P','FPI_vr','FPI_P_vr'])
    var_list_pft = ['FPSN','TLAI','QVEGE','QVEGT']
    if ('RD' in compset or 'ECA' in compset):
      var_list_pft.extend(['GPP', 'NPP', 'LEAF_MR', 'LEAFC_ALLOC', 'AGNPP', 'CPOOL_TO_DEADSTEMC', \
                    'LIVECROOTC_XFER_TO_LIVECROOTC', 'DEADCROOTC_XFER_TO_DEADCROOTC', \
                    'CPOOL_TO_LIVECROOTC', 'CPOOL_TO_DEADCROOTC', 'FROOTC_ALLOC', 'AR', 'MR', \
                    'CPOOL_LEAF_GR', 'TRANSFER_LEAF_GR', 'CPOOL_LEAF_STORAGE_GR', \
                    'LIVESTEM_MR', 'CPOOL_LIVESTEM_GR', 'TRANSFER_LIVESTEM_GR', \
                    'CPOOL_LIVESTEM_STORAGE_GR', 'CPOOL_DEADSTEM_GR', 'TRANSFER_DEADSTEM_GR', \
                    'CPOOL_DEADSTEM_STORAGE_GR', 'LIVECROOT_MR', 'CPOOL_LIVECROOT_GR', \
                    'TRANSFER_LIVECROOT_GR', 'CPOOL_LIVECROOT_STORAGE_GR', 'CPOOL_DEADCROOT_GR', \
                    'TRANSFER_DEADCROOT_GR', 'CPOOL_DEADCROOT_STORAGE_GR', 'FROOT_MR', \
                    'CPOOL_FROOT_GR', 'TRANSFER_FROOT_GR', 'CPOOL_FROOT_STORAGE_GR', 'FCTR', 'FCEV', \
                    'TOTVEGC', 'LEAFC', 'LIVESTEMC', 'DEADSTEMC', 'FROOTC', 'LIVECROOTC', \
                    'DEADCROOTC', 'DEADSTEMC_STORAGE', 'LIVESTEMC_STORAGE', 'DEADCROOTC_STORAGE', \
                    'LIVECROOTC_STORAGE', 'CPOOL_TO_DEADSTEMC_STORAGE', 'CPOOL_TO_LIVESTEMC_STORAGE', \
                    'CPOOL_TO_DEADCROOTC_STORAGE', 'CPOOL_TO_LIVECROOTC_STORAGE', \
                    'FROOTC_STORAGE', 'LEAFC_STORAGE', 'LEAFC_XFER', 'FROOTC_XFER', 'LIVESTEMC_XFER', \
                    'DEADSTEMC_XFER', 'LIVECROOTC_XFER', 'DEADCROOTC_XFER', 'CPOOL_TO_LIVESTEMC'])
    if options.var_list_pft != '':
        var_list_pft = options.var_list_pft.split(',')
    var_list_spinup = ['PPOOL', 'EFLX_LH_TOT', 'RETRANSN', 'PCO2', 'PBOT', 'NDEP_TO_SMINN', 'OCDEP', \
                       'BCDEP', 'COL_FIRE_CLOSS', 'HDM', 'LNFM', 'NEE', 'GPP', 'FPSN', 'AR', 'HR', \
                       'MR', 'GR', 'ER', 'NPP', 'TLAI', 'SOIL3C', 'TOTSOMC', 'TOTSOMC_1m', 'LEAFC', \
                       'DEADSTEMC', 'DEADCROOTC', 'FROOTC', 'LIVESTEMC', 'LIVECROOTC', 'TOTVEGC', 'N_ALLOMETRY','P_ALLOMETRY',\
                       'TOTCOLC', 'TOTLITC', 'BTRAN', 'SCALARAVG_vr', 'CWDC', 'QVEGE', 'QVEGT', 'QSOIL', 'QDRAI', \
                       'QRUNOFF', 'FPI', 'FPI_vr', 'FPG', 'FPI_P','FPI_P_vr', 'FPG_P', 'CPOOL','NPOOL', 'PPOOL', 'SMINN', 'HR_vr']
    if ('ICBCLM45CB' in compset):
      var_list_spinup = ['FPSN','TLAI','QVEGT','QVEGE','QSOIL','EFLX_LH_TOT','FSH','RH2M','TSA','FSDS','FLDS','PBOT', \
                         'WIND','BTRAN','DAYL','T10','QBOT']

    if (options.C14):
        var_list_spinup.append('C14_TOTSOMC')
        var_list_spinup.append('C14_TOTSOMC_1m')
        var_list_spinup.append('C14_TOTVEGC')
    #ILAMB diagnostic variables
    ilamb_outputs = ['FAREA_BURNED', 'CWDC', 'LEAFC', 'TOTLITC', 'STORVEGC', 'LIVESTEMC', 'DEADSTEMC', \
                     'TOTPRODC', 'FROOTC', 'LIVECROOTC', 'DEADCROOTC', 'SOIL1C', 'SOIL2C', 'SOIL3C', \
                     'TOTSOMC', 'TOTVEGC', 'WOODC', 'QSOIL', 'QVEGE', 'COL_FIRE_CLOSS', \
                     'LITR1C_TO_SOIL1C', 'LITR2C_TO_SOIL2C', 'LITR3C_TO_SOIL3C', 'LAND_USE_FLUX', \
                     'LITFALL', 'GPP', 'FGR', 'TLAI', 'SNOWLIQ', 'SOILICE', 'SOILLIQ', 'QRUNOFF', \
                     'QOVER', 'SOILWATER_10CM', 'NBP', 'LEAFC_ALLOC', 'WOODC_ALLOC', 'QINTR', \
                     'AR', 'GR', 'HR', 'MR', 'FSNO', 'SNOWDP', 'QSNOMELT', 'H2OSNO', 'SNOBCMSL', \
                     'SNODSTMSL', 'SNOOCMSL', 'QVEGT', 'TSOI', 'WIND', 'EFLX_LH_TOT', 'FCTR', \
                     'FCEV', 'FGEV', 'FSH', 'RH2M', 'Q2M', 'RAIN', 'SNOW', 'PBOT', 'FLDS', 'FIRE', \
                     'FSDS', 'FSR', 'TSA', 'QSNOMELT', 'TWS']
    if ('CTC' in compset):
        var_list_daily.append('SOIL4C_vr')
        var_list_spinup.append('SOIL4C')
        ilamb_outputs.append('SOIL4C')

    if ('20TR' not in compset and not options.istrans and int(options.hist_mfilt) == -1):
	#default to annual for spinup runs if not specified
        options.hist_mfilt = 1
        options.hist_nhtfrq = -8760

    if (options.hist_mfilt != -1 and not options.diags):
        if (options.ad_spinup):
            output.write(" hist_mfilt = "+str(options.hist_mfilt)+", "+str(options.hist_mfilt)+"\n")
        else:
            if (options.dailyrunoff):
                #include daily variables related to runoff only
                output.write(" hist_mfilt = "+ str(options.hist_mfilt)+",365\n")
            elif (options.dailyvars):
                #include daily column and PFT level output
                output.write(" hist_dov2xy = .true., .true., .false.\n")
                output.write(" hist_mfilt = "+ str(options.hist_mfilt)+",365,365\n")
            else:
                output.write(" hist_mfilt = "+ str(options.hist_mfilt)+"\n")

    if (options.hist_nhtfrq != -999 and not options.diags):
        if (options.ad_spinup):
            output.write(" hist_nhtfrq = "+ str(options.hist_nhtfrq)+", "+str(options.hist_nhtfrq)+"\n")
        else:
            if (options.dailyvars):
                output.write(" hist_nhtfrq = "+ str(options.hist_nhtfrq)+",-24,-24\n")
                h1varst = "hist_fincl2 = "
                h2varst = "hist_fincl3 = "
                for v in var_list_hourly:
                    h1varst = h1varst+"'"+str(v)+"',"
                for v in var_list_daily:
                    h1varst = h1varst+"'"+str(v)+"',"
                for v in var_list_pft:
                    h2varst = h2varst+"'"+str(v)+"',"
                output.write(h1varst[:-1]+"\n")
                output.write(h2varst[:-1]+"\n")
            elif (options.dailyrunoff):
                output.write(" hist_nhtfrq = "+ str(options.hist_nhtfrq)+",-24\n")
                output.write(" hist_fincl2 = 'TBOT','QBOT','RAIN','SNOW','QBOT','PBOT','WIND','FPSN','QVEGT'," \
                        +"'QVEGE','QSOIL','QRUNOFF','QDRAI','QOVER','H2OSFC','ZWT','SNOWDP','H2OSOI','TSOI','TWS'," \
                        +"'FSDS','FLDS'\n")
            else:
                output.write(" hist_nhtfrq = "+ str(options.hist_nhtfrq)+"\n")

    if (options.hist_vars != ''):
        output.write(" hist_empty_htapes = .true.\n")
        myhistvars = options.hist_vars.split(',')
        output.write(" hist_fincl1 = '"+options.hist_vars+"'\n")
        #read hist_vars file
        #hvars_file = open(hist_vars)
        myline = " hist_fincl1 = "
        #line2 = 0
        #for s2 in hvars_file:
        #    if line2 ==0:
        #        myline = myline+"'"+s2.strip()+"'"
        #    else:
        #        myline = myline+",'"+s2.strip()+"'"
        #    line2=line2+1
        #hvars_file.close()
        for v in myhistvars:
          myline = myline+"'"+v.strip()+"'"
        myline=myline+"\n"
        output.write(myline+"\n")
   
    if (options.spinup_vars and (not '20TR' in compset) and (not options.istrans)):
        output.write(" hist_empty_htapes = .true.\n")
        h0varst = " hist_fincl1 = "
        for v in var_list_spinup:
            h0varst = h0varst+"'"+str(v)+"',"
        h0varst = h0varst[:-1]+"\n"
        output.write(h0varst)

    if (options.diags): #(('20TR' in compset or options.istrans) and options.diags):
        output.write(" hist_dov2xy = .true., .true., .true., .false., .true.\n")
        output.write(" hist_mfilt = 1, 8760, 365, 365, 1\n")
        output.write(" hist_nhtfrq = 0, -1, -24, -24, -8760\n")
        h1varst = " hist_fincl2 = "
        h2varst = " hist_fincl3 = "
        h3varst = " hist_fincl4 = "
        h4varst = " hist_fincl5 = "
        for v in var_list_hourly:
            h1varst = h1varst+"'"+str(v)+"',"
            h2varst = h2varst+"'"+str(v)+"',"
            h4varst = h4varst+"'"+str(v)+"',"
        for v in var_list_daily:
            h2varst = h2varst+"'"+str(v)+"',"
            h4varst = h4varst+"'"+str(v)+"',"
        for v in var_list_pft:
            h3varst = h3varst+"'"+str(v)+"',"
        h1varst = h1varst[:-1]+"\n"
        h2varst = h2varst[:-1]+"\n"
        h3varst = h3varst[:-1]+"\n"
        h4varst = h4varst[:-1]+"\n"
        output.write(h1varst)
        output.write(h2varst)
        output.write(h3varst)
        output.write(h4varst)
    elif (('20TR' in compset or options.istrans) and (options.trans_varlist != '' or options.ilambvars)):
        trans_varlist = options.trans_varlist.split(',')
        if (options.ilambvars):
            trans_varlist = ilamb_outputs
        output.write(" hist_empty_htapes = .true.\n")
        h0varst = " hist_fincl1 = "
        for v in trans_varlist:
            h0varst = h0varst+"'"+str(v)+"',"
        h0varst = h0varst[:-1]+"\n"
        output.write(h0varst)

    if (options.ad_spinup):
        #Write long-term average pool values
        if (not 'ED' in compset and not 'FATES' in compset):
          output.write(" hist_dov2xy = .true., .false.\n")
          h1_advars = ['CWDX_vr', 'SOIL2X_vr', 'SOIL3X_vr', 'DEADSTEMX','DEADCROOTX', 'LITR3X_vr','LEAFC','TOTVEGC','TLAI']
          if ('CTC' in compset):
            h1_advars.append('SOIL4X_vr')
          outst = "hist_fincl2 = "
          for h in h1_advars:
            if 'X' in h:
              outst = outst+"'"+h.replace('X','C')+"',"
              outst = outst+"'"+h.replace('X','N')+"',"
              if (options.mymodel == 'ELM'):
                  outst = outst+"'"+h.replace('X','P')+"',"
            else:
              outst = outst+"'"+h+"',"
          output.write(outst[:-1]+'\n')
        else:
          output.write(" suplphos = 'ALL'\n")
        if (options.mymodel == 'ELM'):
            output.write(" finidat = ''\n")
    elif (options.coldstart == False):
        #user-defined initial data file
        output.write(" finidat = '"+finidat+"'\n")

    #surface data file
    if (options.surffile == ''):
      output.write(" fsurdat = '"+rundir+"/surfdata.nc'\n")
    else:
      output.write(" fsurdat = '"+options.surffile+"'\n")      
    
    if (options.var_soilthickness):
        output.write(" use_var_soil_thick = .TRUE.\n") 
    if (options.no_budgets):
        output.write(" do_budgets = .false.\n")

    #pft dynamics file for transient run
    if ('20TR' in compset or options.istrans):
        if (options.nopftdyn):
            output.write(" flanduse_timeseries = ' '\n") 
        elif(options.pftdynfile !=''):
            output.write(" flanduse_timeseries = '"+options.pftdynfile+"'\n")
        else:
            output.write(" flanduse_timeseries = '"+rundir+"/surfdata.pftdyn.nc'\n")
        if (options.mymodel == 'ELM'):
            output.write(' check_finidat_fsurdat_consistency = .false.\n')
            output.write(' check_finidat_year_consistency = .false.\n')
    #pft-physiology file
    output.write(" paramfile = '"+rundir+"/clm_params.nc'\n")

    if (('ED' in compset or 'FATES' in compset) and options.fates_paramfile != ''):
      output.write(" fates_paramfile = '"+options.fates_paramfile+"'\n")
    if (('ED' in compset or 'FATES' in compset) and options.fates_hydro):
      output.write(" use_fates_planthydro = .true.\n")

    if ('CROP' in compset or 'RD' in compset or 'ECA' in compset or options.fates_nutrient != ''):
        #soil order parameter file
        output.write(" fsoilordercon = '"+rundir+"/CNP_parameters.nc'\n")
        #output.write( " stream_fldfilename_ndep = '"+options.ccsm_input+ \
        #  "/lnd/clm2/ndepdata/fndep_clm_hist_simyr1849-2006_1.9x2.5_" + \
        #              "c100428.nc'\n")
        if (options.ndep1850 == True):
          output.write( " stream_fldfilename_ndep = '"+options.ccsm_input+ \
            "/lnd/clm2/ndepdata/fndep_clm_rcp4.5_simyr1850-1850_1.9x2.5_c100428.nc'\n")
        elif options.ndeprcp85:
          output.write( " stream_fldfilename_ndep = '"+options.ccsm_input+ \
            "/lnd/clm2/ndepdata/fndep_clm_rcp8.5_simyr1849-2106_1.9x2.5_c100428.nc'\n")
        else:
          output.write( " stream_fldfilename_ndep = '"+options.ccsm_input+ \
            "/lnd/clm2/ndepdata/fndep_clm_rcp4.5_simyr1849-2106_1.9x2.5_c100428.nc'\n")
        if (model_name == 'clm2'):  #set for older tags/branches (option was removed, this may not capture all tags 
                                    #between rename to elm and removal of nitrif_dentrif)   
            output.write(" use_nitrif_denitrif = .true.\n")
        if (options.vsoilc):
            output.write(" use_vertsoilc = .true.\n")
        if (options.centbgc or 'ECA' in options.fates_nutrient):
            output.write(" use_century_decomp = .true.\n")
        if (options.no_dynroot):
            output.write(" use_dynroot = .false.\n")
        if ('CROP' in compset):
            output.write(" suplphos = 'ALL'\n")
        if (options.fates_nutrient != ''):
            output.write(" fates_parteh_mode = 2\n")
            if (not options.c_only):
              output.write(" suplnitro = 'NONE'\n")
            else:
              output.write(" suplnitro = 'ALL'\n")
        elif ('ED' in compset or 'FATES' in compset):    #C-only mode (no nutrient enabled)
            options.write(" fates_parteh_mode = 1\n")
#        if (options.CH4 and options.fates_nutrient == ''):
#            output.write(" use_lch4 = .true.\n")
#        elif (options.fates_nutrient != ''):
#            output.write(" use_lch4 = .false.\n")  
        if (options.CH4):
            output.write(" use_lch4 = .true.\n")
        # APW: given RK suggests nitrif/denitrif is not correct w/o ch4 shuld this be for all nutrient enabled runs?
        elif (options.fates_nutrient != ''):
            output.write(" use_lch4 = .true.\n")  
        if (options.nofire):
            output.write(" use_nofire = .true.\n")
        if (options.C13):
            output.write(" use_c13 = .true.\n")
        if (options.C14):
            output.write(" use_c14 = .true.\n")
            output.write(" use_c14_bombspike = .true.\n")
            output.write(" atm_c14_filename = '"+options.ccsm_input+"/atm/datm7/CO2/" + \
                         "atm_delta_C14_data_1850-2007_monthly_25082011.nc'\n")
        if ('ECA' in compset):
            output.write(" nyears_ad_carbon_only = 0\n")
            output.write(" spinup_mortality_factor = 1\n")
        elif (options.c_only):
            output.write(" nyears_ad_carbon_only = 9999\n")
            output.write(" spinup_mortality_factor = 10\n")
        else:
            output.write(" nyears_ad_carbon_only = 25\n")
            output.write(" spinup_mortality_factor = 10\n")
        if ('ECA' in options.fates_nutrient):
            output.write(" nu_com = 'ECA'\n")
        elif ('RD' in options.fates_nutrient):
            output.write(" nu_com = 'RD'\n")
    if (options.use_hydrstress):
      output.write(" use_hydrstress = .true.\n")

    if (cpl_bypass):
        if (use_reanalysis):
            if (options.cruncepv8):
                    output.write(" metdata_type = 'cru-ncep'\n")
                    output.write(" metdata_bypass = '"+options.ccsm_input+"/atm/datm7/" \
                         +"atm_forcing.datm7.cruncep_qianFill.0.5d.v8.c180815" + \
                         "/cpl_bypass_full'\n")
            elif (options.cruncep):
                if (options.livneh):
                    output.write(" metdata_type = 'cru-ncep_livneh'\n")
                    output.write(" metdata_bypass = '"+options.ccsm_input+"/atm/datm7/" \
                         +"atm_forcing.datm7.cruncep_qianFill.0.5d.V5.c140715.CONUS_Livneh" + \
                         "/cpl_bypass_full'\n")
                elif (options.daymet):
                    output.write(" metdata_type = 'cru-ncep_daymet'\n")
                    output.write(" metdata_bypass = '"+options.ccsm_input+"/atm/datm7/" \
                         +"atm_forcing.datm7.cruncep_qianFill.0.5d.V5.c140715.CONUS_Daymet3" + \
                         "/cpl_bypass_full'\n")
                else:
                    output.write(" metdata_type = 'cru-ncep'\n")
                    output.write(" metdata_bypass = '"+options.ccsm_input+"/atm/datm7/" \
                         +"atm_forcing.datm7.cruncep_qianFill.0.5d.V5.c140715/cpl_bypass_full'\n")
            elif (options.crujra):
                    output.write(" metdata_type = 'crujra'\n")
                    output.write(" metdata_bypass = '"+options.ccsm_input+"/atm/datm7/" \
                         +"atm_forcing.datm7.CRUJRA.0.5d.v1.c190604/cpl_bypass_full'\n")
            elif (options.gswp3):
                if (options.livneh):
                    output.write(" metdata_type = 'gswp3_livneh'\n")
                    output.write(" metdata_bypass = '"+options.ccsm_input+"/atm/datm7/" \
                         +"atm_forcing.datm7.GSWP3.0.5d.v1.c170516.CONUS_Livneh/cpl_bypass_full'\n")
                elif (options.daymet):
                    output.write(" metdata_type = 'gswp3_daymet'\n")
                    output.write(" metdata_bypass = '"+options.ccsm_input+"/atm/datm7/" \
                         +"atm_forcing.datm7.GSWP3.0.5d.v1.c170516.CONUS_Daymet3/cpl_bypass_full'\n")
                else:
                    output.write(" metdata_type = 'gswp3'\n")
                    output.write(" metdata_bypass = '"+options.ccsm_input+"/atm/datm7/" \
                          +"/atm_forcing.datm7.GSWP3.0.5d.v2.c180716/cpl_bypass_full'\n")
#                         +"atm_forcing.datm7.GSWP3.0.5d.v1.c170516/cpl_bypass_full'\n")
            elif (options.gswp3_w5e5):
                output.write(" metdata_type = 'gswp3_w5e5'\n")
                output.write(" metdata_bypass = '"+options.ccsm_input+"/atm/datm7/" \
                         +"atm_forcing.GSWP3-w5e5.c211106/cpl_bypass_full'\n")
            elif (options.princeton):
                if (options.livneh):
                    output.write(" metdata_type = 'princeton_livneh'\n")
                    output.write(" metdata_bypass = '"+options.ccsm_input+"/atm/datm7/" \
                         +"atm_forcing.datm7.Princeton.0.5d.v1.c180222.CONUS_Livneh/cpl_bypass_full'\n")
                elif (options.daymet):
                    output.write(" metdata_type = 'princeton_daymet'\n")
                    output.write(" metdata_bypass = '"+options.ccsm_input+"/atm/datm7/" \
                         +"atm_forcing.datm7.Princeton.0.5d.v1.c180222.CONUS_Daymet3/cpl_bypass_full'\n")
                else:
                    output.write(" metdata_type = 'princeton'\n")
                    output.write(" metdata_bypass = '"+options.ccsm_input+"/atm/datm7/" \
                         +"atm_forcing.datm7.Princeton.0.5d.v1.c180222/cpl_bypass_full'\n")
            elif (options.cplhist):
                output.write(" metdata_type = 'cplhist'\n")
                output.write(" metdata_bypass = '"+options.ccsm_input+"/atm/datm7/" \
                          +"atm_forcing.cpl.CBGC1850S.ne30.c181011/cpl_bypass_full'\n")
#                         +"atm_forcing.cpl.WCYCL1850S.ne30.c171204/cpl_bypass_full'\n")
        elif options.metdir != 'none':
            if (options.daymet4 and options.gswp3):
                output.write(" metdata_type = 'gswp3_daymet4'\n")
            #else:
            #    output.write(" metdata_type = 'gswp3v1_daymet'\n") # This needs to be updated for other types
            output.write(" metdata_bypass = '%s'\n"%options.metdir)
            
        # not reanalysis
        else:
            if (options.site_forcing == ''):
              options.site_forcing=options.site
            if (ptstr == ''):
              ptstr='1x1pt'
            output.write("metdata_type = 'site'\n")
            if (options.metdata_dir == ''):
              output.write(" metdata_bypass = '"+options.ccsm_input+"/atm/datm7/" \
                             +"CLM1PT_data/"+ptstr+"_"+options.site_forcing+"/'\n")
            else:
              output.write(" metdata_bypass = '"+options.metdata_dir+"'\n")
        if (options.monthly_metdata != ''):
            output.write(" metdata_biases = '"+options.monthly_metdata+"'\n")

        if (options.co21850):
          output.write(" co2_file = '"+options.ccsm_input+"/atm/datm7/CO2/" \
                         +"fco2_datm_rcp4.5_1850-1850_c130312.nc'\n")
        else:
          output.write(" co2_file = '"+options.ccsm_input+"/atm/datm7/CO2/" \
                         +options.co2_file+"'\n")
        if (options.aero1850):
          output.write(" aero_file = '"+options.ccsm_input+"/atm/cam/chem/" \
                         +"trop_mozart_aero/aero/aerosoldep_rcp4.5_monthly_1850-1850_1.9x2.5_c100402.nc'\n")
        elif (options.aerorcp85):
          output.write(" aero_file = '"+options.ccsm_input+"/atm/cam/chem/" \
                         +"trop_mozart_aero/aero/aerosoldep_rcp8.5_monthly_1849-2104_1.9x2.5_c100201.nc'\n")
        else:
          output.write(" aero_file = '"+options.ccsm_input+"/atm/cam/chem/" \
                         +"trop_mozart_aero/aero/aerosoldep_rcp4.5_monthly_1849-2104_1.9x2.5_c100402.nc'\n")
    
    if (options.addt != 0):
      output.write(" add_temperature = "+str(options.addt)+"\n")
      output.write(" startdate_add_temperature = '"+str(options.sd_addt)+"'\n")

    if (options.addco2 != 0):
      output.write(" add_co2 = "+str(options.addco2)+"\n")
      output.write(" startdate_add_co2 = '"+str(options.sd_addco2)+"'\n")
    output.close()


#configure case
#if (isglobal):
os.system("./xmlchange --id BATCH_SYSTEM --val none")
if (options.no_config == False):
    print('Running case.setup')
    result = os.system('./case.setup > case_setup.log')
    if (result > 0):
        print('Error: runcase.py failed to setup case')
        sys.exit(1)
else:
    print("Warning:  No case configure performed")
    sys.exit(1)

#Land CPPDEF modifications
if (options.humhol):
    print("Turning on HUM_HOL modification\n")
    os.system("./xmlchange --id "+mylsm+"_CONFIG_OPTS --append --val '-cppdefs -DHUM_HOL'")

if (options.marsh):
    print("Turning on MARSH modification\n")
    os.system("./xmlchange --id "+mylsm+"_CONFIG_OPTS --append --val '-cppdefs -DMARSH'")
if (options.harvmod):
    print('Turning on HARVMOD modification\n')
    os.system("./xmlchange --id "+mylsm+"_CONFIG_OPTS --append --val '-cppdefs -DHARVMOD'")

#Global CPPDEF modifications
if (cpl_bypass):
  if (os.path.isfile("./Macros.make")):
    infile  = open("./Macros.make")
    outfile = open("./Macros.make.tmp",'a')

    for s in infile:
      if ('CPPDEFS' in s and cpl_bypass):
         stemp = s[:-1]+' -DCPL_BYPASS\n'
         outfile.write(stemp)
      elif ('llapack' in s):
         outfile.write(s.replace('llapack','llapack -lgfortran'))
      else:
         outfile.write(s.replace('mcmodel=medium','mcmodel=small'))
    infile.close()
    outfile.close()
    os.system('mv Macros.make.tmp Macros.make')

  if (options.mymodel == 'ELM' and os.path.isfile("./Macros.cmake")):
    infile  = open("./Macros.cmake")
    outfile = open("./Macros.cmake.tmp",'a')

    for s in infile:
      if ('CPPDEFS' in s and cpl_bypass):
       stemp = s[:-3]+' -DCPL_BYPASS")\n'
       outfile.write(stemp)
      elif ('llapack' in s):
        outfile.write(s.replace('llapack','llapack -lgfortran'))
      else:
        outfile.write(s.replace('mcmodel=medium','mcmodel=small'))
    infile.close()
    outfile.close()
    os.system('mv Macros.cmake.tmp Macros.cmake')

  if (os.path.isfile("./cmake_macros/universal.cmake")):
    #infile = open("./cmake_macros/universal.cmake")
    os.system("echo 'string(APPEND CPPDEFS \" -DCPL_BYPASS\")' >> cmake_macros/universal.cmake")

#copy sourcemods
os.chdir('..')
if (options.srcmods_loc != ''):
    if (os.path.exists(options.srcmods_loc) == False):
        print('Invalid srcmods directory.  Exiting')
        sys.exit(1)
    options.srcmods_loc = os.path.abspath(options.srcmods_loc)
    os.system('cp -r '+options.srcmods_loc+'/* ./'+casename+ \
                  '/SourceMods')
if (options.caseroot == './' ):
    os.chdir(csmdir+"/cime/scripts/"+casename)
else:
    os.chdir(casedir)       

os.system('mkdir Srcfiles')
#clean build if requested
if (options.clean_build):
    os.system('./case.build --clean')
#compile cesm
if (options.no_build == False):
    print('Running case.build')
    if ('edison' in options.machine or 'titan' in options.machine):
        #send output to screen since build times are very slow
        result = os.system('./case.build') 
    else:
        result = os.system('./case.build > case_build.log')
    if (result > 0):
        print('Error:  Pointclm.py failed to build case.  Aborting')
        print('See '+os.getcwd()+'/case_build.log for details')
        sys.exit(1)
else:
    os.system('./xmlchange BUILD_COMPLETE=TRUE')
    os.system('mkdir -p '+rundir)
    if ('CLM5' in options.mymodel):
        os.system('./preview_namelists')
if (options.caseroot == ''):
    os.chdir(csmdir+"/cime/scripts/"+casename)
else:
    os.chdir(casedir) 

#stream file modifications for site runs
#Datm mods/ transient CO2 patch for transient run (datm buildnml mods)
if (not cpl_bypass):
    myinput  = open('./Buildconf/datmconf/datm_in')
    myoutput = open('user_nl_datm','w')
    for s in myinput:
        if ('streams =' in s):
            myalign_year = 1 #startyear
            if (options.align_year != -999):
                myalign_year = options.align_year
            if (options.istrans or '20TR' in compset):
                mypresaero = '"datm.streams.txt.presaero.trans_1850-2000 1850 1850 2000"'
                myco2      = ', "datm.streams.txt.co2tseries.20tr 1766 1766 2010"'
            elif ('1850' in compset):
                mypresaero = '"datm.streams.txt.presaero.clim_1850 1 1850 1850"'
                myco2=''
            else:
                mypresaero = '"datm.streams.txt.presaero.clim_2000 1 2000 2000"'
                myco2=''
            if (options.cruncep):
                myoutput.write(' streams = "datm.streams.txt.CLMCRUNCEP.Solar '+str(myalign_year)+ \
                                   ' '+str(startyear)+' '+str(endyear)+'  ", '+ \
                                   '"datm.streams.txt.CLMCRUNCEP.Precip '+str(myalign_year)+ \
                                   ' '+str(startyear)+' '+str(endyear)+'  ", '+ \
                                   '"datm.streams.txt.CLMCRUNCEP.TPQW '+str(myalign_year)+ \
                                   ' '+str(startyear)+' '+str(endyear)+'  ", '+mypresaero+myco2+ \
                                   ', "datm.streams.txt.topo.observed 1 1 1"\n')
            else:
                myoutput.write(' streams = "datm.streams.txt.CLM1PT.'+mylsm+'_USRDAT '+str(myalign_year)+ \
                                   ' '+str(startyear)+' '+str(endyear)+'  ", '+mypresaero+myco2+ \
                                   ', "datm.streams.txt.topo.observed 1 1 1"\n')
        elif ('streams' in s):
            continue  #do nothing
        elif ('taxmode' in s):
            if (options.cruncep or options.cruncepv8):
                taxst = "taxmode = 'cycle', 'cycle', 'cycle', 'extend', 'extend'"
            else:
                taxst = "taxmode = 'cycle', 'extend', 'extend'"
            if (options.istrans or '20TR' in compset):
                taxst = taxst+", 'extend'"
            myoutput.write(taxst+'\n')
        else:
            myoutput.write(s)
    myinput.close()
    myoutput.close()

if (not cpl_bypass and not isglobal):
    if ('1850' in compset):
        myinput  = open('./Buildconf/datmconf/datm.streams.txt.presaero.clim_1850')
        myoutput = open('./user_datm.streams.txt.presaero.clim_1850','w')
        for s in myinput:
            if ('aerosoldep_monthly' in s):
                myoutput.write('            aerosoldep_monthly_1849-2006_1.9x2.5_c090803.nc\n')
            else:
                myoutput.write(s)
        myinput.close()
        myoutput.close()

    if (options.co2_file != '' and '20TR' in compset):
        myinput  = open('./Buildconf/datmconf/datm.streams.txt.co2tseries.20tr')
        myoutput = open('./user_datm.streams.txt.co2tseries.20tr','w')
        for s in myinput:
            if ('.nc' in s):
                myoutput.write('      '+options.co2_file+'\n')
            else:
                myoutput.write(s)
        myinput.close()
        myoutput.close()

    #reverse directories for CLM1PT and site
    if (options.cruncep == False):
        myinput  = open('./Buildconf/datmconf/datm.streams.txt.CLM1PT.'+mylsm+'_USRDAT')
        myoutput = open('./user_datm.streams.txt.CLM1PT.'+mylsm+'_USRDAT','w')
        for s in myinput:
            if ('CLM1PT_data' in s):
                temp = s.replace('CLM1PT_data', 'TEMPSTRING')
                s    = temp.replace(str(numxpts)+'x'+str(numypts)+'pt'+'_'+options.site, 'CLM1PT_data')
                temp  =s.replace('TEMPSTRING', str(numxpts)+'x'+str(numypts)+'pt'+'_'+options.site)
                myoutput.write(temp)
            elif (('ED' in compset or 'FATES' in compset) and 'FLDS' in s):
                print('Not including FLDS in atm stream file')
            else:
                myoutput.write(s)
        myinput.close()
        myoutput.close()
    # run preview_namelists to copy user_datm.streams.... to CaseDocs
    os.system(os.path.abspath(options.csmdir)+'/cime/scripts/Tools/preview_namelists')


#copy site data to run directory
os.system('cp '+PTCLMdir+'/temp/*param*.nc '+runroot+'/'+casename+'/run/')
if (options.domainfile == ''):
    os.system('cp '+PTCLMdir+'/temp/domain.nc '+runroot+'/'+casename+'/run/')
if (options.surffile == ''):
    os.system('cp '+PTCLMdir+'/temp/surfdata.nc '+runroot+'/'+casename+'/run/')
if ('20TR' in compset and options.nopftdyn == False and options.pftdynfile ==''):
    os.system('cp '+PTCLMdir+'/temp/surfdata.pftdyn.nc '+runroot+'/'+casename+'/run/')

#submit job if requested
if (options.no_submit == False and int(options.mc_ensemble) < 0 and options.ensemble_file == ''):
# Ming, 01/22/16, use a csh script instead of the perl script to submit the job.
#    os.system("qsub "+casename+".run")
    if ("mesabi" in options.machine):
        os.system("cp /home/reichpb/shared/Scripts/Ming/shell/qsub1.csh ./")
        os.system("cp /home/reichpb/shared/Scripts/Ming/shell/st_archive.sh ./")
        f = open("qsub.csh",'r+')
        filedata = f.read()
        newdata0 = filedata.replace("newdir",casedir)
        newdata = newdata0.replace("archivedir",options.archiveroot)
        f.seek(0)
        f.write(newdata)
        f.truncate()
        f.close()
        os.system("qsub qsub.csh")
    else:
        os.system("./case.submit")



#------------------------- Code to generate and run parameter ensembles --------------------------------------

os.chdir(PTCLMdir)

if ((options.ensemble_file != '' or int(options.mc_ensemble) != -1) and (options.constraints == '' or (
        options.constraints != '' and not '1850' in casename))):
    if (not(os.path.isfile(options.parm_list))):
        print('parm_list file does not exist')
        sys.exit(1)
    elif (isglobal):
        print('Ensemble simulations not supported for regional/global simulations')
        sys.exit(1)
    else:
        param_names=[]
        param_min=[]
        param_max=[]
        input = open(options.parm_list,'r')
        for s in input:
            if (s):
                param_names.append(s.split()[0])
                if (int(options.mc_ensemble) > 0):
                    if (len(s.split()) == 3):
                        param_min.append(float(s.split()[1]))
                        param_max.append(float(s.split()[2]))
                    else:
                        param_min.append(float(s.split()[2]))
                        param_max.append(float(s.split()[3]))
        input.close() 
        n_parameters = len(param_names)
    if (options.ensemble_file != ''):    
        if (not os.path.isfile(options.ensemble_file)):
            print('Error:  ensemble file does not exist')
            sys.exit(1)

        samples=numpy.zeros((n_parameters,100000), dtype=numpy.float) 
        #get parameter samples and information
        myinput=open(options.ensemble_file)
        nsamples = 0
        for s in myinput:
            for j in range(0,n_parameters):
                samples[j][nsamples] = float(s.split()[j]) 
            nsamples=nsamples+1
        myinput.close()
    elif (int(options.mc_ensemble) > 0):
        nsamples = int(options.mc_ensemble)
        samples=numpy.zeros((n_parameters,nsamples), dtype=numpy.float)
        for i in range(0,nsamples):
            for j in range(0,n_parameters):
                samples[j][i] = param_min[j]+(param_max[j]-param_min[j])*numpy.random.rand(1)
        numpy.savetxt('mcsamples_'+casename+'.txt', numpy.transpose(samples))
        options.ensemble_file = 'mcsamples_'+casename+'.txt'

    print('')
    print('')
    print('Parameter ensembles selected:') 
    print(str(n_parameters)+' parameters are being modified') 
    print(str(nsamples)+' parameter samples provided')
  
    #total number of processors required in each pbs script
    np_total = int(options.np)*int(options.ng)
    #number of scripts required
    n_scripts = int(math.ceil(nsamples/float(options.ninst*options.ng)))
 
    num=0
    #Launch ensemble if requested 
    mysubmit_type = 'qsub'
    if ('cades' in options.machine or 'compy' in options.machine or 'ubuntu' in options.machine or 'cori' in options.machine or \
        options.machine == 'anvil' or options.machine == 'edison' or options.machine == 'chrysalis'):
        mysubmit_type = 'sbatch'
    if (options.ensemble_file != ''):
        os.system('mkdir -p '+PTCLMdir+'/scripts/'+myscriptsdir)
        output_run  = open(PTCLMdir+'/scripts/'+myscriptsdir+'/ensemble_run_'+casename+'.pbs','w')
        timestr=str(int(float(options.walltime)))+':'+str(int((float(options.walltime)- \
                                     int(float(options.walltime)))*60))+':00'
        if (options.debug):
           timestr='00:30:00'
           if ('compy' in options.machine):
             timestr='02:00:00'
        output_run.write("#!/bin/csh -f\n")
        if (mysubmit_type == 'qsub'):
            output_run.write('#PBS -l walltime='+timestr+'\n')
            output_run.write('#PBS -N ens_'+casename+'\n')
            if (options.project != ''):
                output_run.write('#PBS -A '+options.project+'\n')
            if (options.machine == 'cades'):
                output_run.write('#PBS -l nodes='+str(int(math.ceil(np_total/(ppn*1.0))))+ \
                                    ':ppn='+str(ppn)+'\n')
                output_run.write('#PBS -W group_list=cades-ccsi\n')
            else:
                output_run.write('#PBS -l nodes='+str(int(math.ceil(np_total/(ppn*1.0))))+ \
                                     '\n')
        else:
            output_run.write('#SBATCH --time='+timestr+'\n')
            output_run.write('#SBATCH -J ens_'+casename+'\n')
            output_run.write('#SBATCH --nodes='+str(int(math.ceil(np_total/(ppn*1.0))))+'\n')
            if ('edison' in options.machine or 'cori' in options.machine):
              if (options.debug):
                output_run.write('#SBATCH --qos=debug\n')
              else:
                output_run.write('#SBATCH --qos=regular\n')
              if ('haswell' in options.machine):
                output_run.write('#SBATCH --constraint=haswell\n')
              if ('knl' in options.machine):
                output_run.write('#SBATCH --constraint=knl\n')
            if ('compy' in options.machine and options.debug):
              output_run.write('#SBATCH --qos=short\n')
            if ('cades' in options.machine):
              output_run.write('#SBATCH -A ccsi\n')
              output_run.write('#SBATCH -p batch\n')
              output_run.write('#SBATCH --mem=64G\n')
              output_run.write('#SBATCH --ntasks-per-node 32\n')
            if ('anvil' in options.machine):
              output_run.write('#SBATCH -A condo\n')
              output_run.write('#SBATCH -p acme-small\n')
        output_run.write("\n")
        if (options.machine == 'eos'):
            output_run.write('source $MODULESHOME/init/csh\n')
            output_run.write('module load nco\n')
            output_run.write('module load cray-netcdf\n')
            output_run.write('module unload python\n')
            output_run.write('module load python/2.7.5\n')
            output_run.write('module unload PrgEnv-intel\n')
            output_run.write('module load PrgEnv-gnu\n')
            output_run.write('module load python_numpy\n')
            output_run.write('module load python_scipy\n')
            output_run.write('module load python_mpi4py/2.0.0\n')
            output_run.write('module unload PrgEnv-gnu\n')
            output_run.write('module load PrgEnv-intel\n')
        if (options.machine == 'titan'):
            output_run.write('source $MODULESHOME/init/csh\n')
            output_run.write('module load nco\n')
            output_run.write('module load cray-netcdf\n')
            output_run.write('module load python/2.7.9\n')
            output_run.write('module load python_numpy/1.9.2\n')
            output_run.write('module load python_scipy/0.15.1\n')
            output_run.write('module load python_mpi4py/2.0.0\n')
        if ('cori' in options.machine or 'edison' in options.machine):
            output_run.write('module unload python\n')
            output_run.write('module unload scipy\n')
            output_run.write('module unload numpy\n')
            output_run.write('module load cray-netcdf\n')
            output_run.write('module load python/2.7-anaconda-5.2\n')
            output_run.write('module load nco\n')
        if ('compy' in options.machine or 'anvil' in options.machine or 'chrysalis' in options.machine):
            #get the software environment
            softenvfile = open(casedir+'/software_environment.txt','r')
            for line in softenvfile:
              if ('LD_LIBRARY_PATH' in line[0:20]):
                output_run.write('setenv '+line.replace('=',' '))
            softenvfile.close()
        output_run.write('cd '+PTCLMdir+'\n')
        cnp = 'True'
        if (options.cn_only or options.c_only):
            cnp= 'False'
        if ('docker' in options.machine or 'oic' in options.machine or 'cades' in options.machine or 'ubuntu' in options.machine):
            mpicmd = 'mpirun'
            if ('cades' in options.machine):
                mpicmd = '/software/dev_tools/swtree/cs400_centos7.2_pe2016-08/openmpi/1.10.3/centos7.2_gnu5.3.0/bin/mpirun'
            cmd = mpicmd+' -np '+str(np_total)+' python manage_ensemble.py ' \
               +'--case '+casename+' --runroot '+runroot+' --n_ensemble '+str(nsamples)+' --ens_file '+ \
               options.ensemble_file+' --exeroot '+exeroot+' --parm_list '+options.parm_list+' --cnp '+cnp + \
               ' --site '+options.site+' --model_name '+model_name
        elif (('titan' in options.machine or 'eos' in options.machine) and int(options.ninst) == 1):
            cmd = 'aprun -n '+str(np_total)+' python manage_ensemble.py ' \
               +'--case '+casename+' --runroot '+runroot+' --n_ensemble '+str(nsamples)+' --ens_file '+ \
               options.ensemble_file+' --exeroot '+exeroot+' --parm_list '+options.parm_list+' --cnp '+cnp + \
               ' --site '+options.site+' --model_name '+model_name
        elif ('compy' in options.machine):
            cmd = 'mpirun -np '+str(np_total)+' python manage_ensemble.py ' \
               +'--case '+casename+' --runroot '+runroot+' --n_ensemble '+str(nsamples)+' --ens_file '+ \
               options.ensemble_file+' --exeroot '+exeroot+' --parm_list '+options.parm_list+' --cnp '+cnp + \
               ' --site '+options.site+' --model_name '+model_name
        elif ('anvil' in options.machine or 'cori' in options.machine or 'chrysalis' in options.machine):
            cmd = 'srun -n '+str(np_total)+' python manage_ensemble.py ' \
               +'--case '+casename+' --runroot '+runroot+' --n_ensemble '+str(nsamples)+' --ens_file '+ \
               options.ensemble_file+' --exeroot '+exeroot+' --parm_list '+options.parm_list+' --cnp '+cnp + \
               ' --site '+options.site+' --model_name '+model_name
        if (options.constraints != ''):
            cmd = cmd + ' --constraints '+options.constraints
        if (options.postproc_file != ''): 
            cmd = cmd + ' --postproc_file '+options.postproc_file
        if (options.spruce_treatments):
            cmd = cmd + ' --spruce_treatments'
        output_run.write(cmd+'\n')
        output_run.close()

        if (options.no_submit == False):
            os.system(mysubmit_type+' '+PTCLMdir+'/scripts/'+myscriptsdir+'/ensemble_run_'+casename+'.pbs')

# END
