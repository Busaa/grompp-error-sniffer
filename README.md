# grompp-error-sniffer
Tool designed to help GROMACS users quickly identify and resolve common errors in topol.top

## Use cases
When working with GROMACS for molecular dynamics (MD) simulations, errors in the topology file can, and will, happen. They can be frustrating and time-consuming to debug—especially when building non-standard force fields or modifying .rtp files for ligands. This tool aims to simplify the process by:
  - Identifying problematic atoms and connections in the topol.top file.

  - Naming the missing parameters and highlighting the specific issues.

  - Generating dummy parameters (if desired) to help you move forward with your simulations.
