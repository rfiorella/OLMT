Offline Land Model Testbed (OLMT)
Contact:  Dan Ricciuto (ricciutodm@ornl.gov)

OLMT is a set of python scripts designed to automate offline land model (ELM and CLM/CTSM) simulations at single sites, groups of sites, user-defined regions or global scales.
It will automatically create, build and submit the 3 cases needed for a full land model BGC simulation:
ad spinup:     Accelerated decomposition spinup (Thornton and Rosenbloom, 2005)
final spinup:  Final spinup to equilibrate carbon and nutrient pools
transient:     1850-present day simulation with transient CO2, land use, climate, etc.

This utility will automatically create surface and domain files using an existing global file at the specified resolution (default:  hcru_hcru).

Updates for running on LANL systems - contact Rich Fiorella (rfiorella@lanl.gov)

The following set of cases are currently supported:

| Scope     | Met data source       | Surface/domain source   | Coupler bypass? | BGC or SP? | Machine    | Works    |
|-----------|-----------------------|-------------------------|-----------------|------------|------------|----------|
| site      | DATM, user            | Global 0.5° at runtime  | No              | BGC        | lanl-ees   | yes      |
| site      | GSWP3, global         | Global 0.5° at runtime  | Yes             | BGC        | lanl-ees   | yes      |
| site      | GSWP3, user provided  | user provided           | Yes             | BGC        | lanl-ees   | ?        |
| site      | GSWP3, global         | user provided           | Yes             | BGC        | lanl-ees   | ?        |
| regional  | GSWP3, global         | user provided           | Yes             | SP         | lanl-ees   | sort-of  |
| site      | DATM, ERA5            | Global 0.5° at runtime  | No              | SP         | lanl-ees   | No       |
| site      | ERA5 bypass           | Global 0.5° at runtime  | Yes             | SP         | lanl-ees   | No       |
| site      | ERA5 bypass           | user provided           | Yes             | BGC        | lanl-ees   | No       |
| site      | DATM, ERA5            | user provided           | No              | BGC        | lanl-ees   | No       |