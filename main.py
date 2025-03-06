"""
Main program to analyze errors in topology files.
"""

# Import the functions from our error_finding.py file
from error_finding import extract_error_info, get_context_from_topology, identify_atoms_from_context, display_error_and_atoms, save_results, extract_atom_names

# Import the functions from our dummies.py file
from dummies import process_errors_for_dummies, save_dummies

def main():
    """Main function of the program."""
    
    # Define file paths
    error_file = "input/errors.txt"
    topology_file = "input/topol.top"
    output_file = "output/analysis_results.txt"
    dummies_file = "output/dummy_parameters.itp"
    
    # Show a start message
    print("Starting analysis of errors in topology files...")
    
    # Extract error information
    print(f"\nExtracting error information from {error_file}...")
    errors = extract_error_info(error_file)
    
    # Find sections in the topology file
    print(f"\nFinding sections in {topology_file}...")
    sections = get_context_from_topology(topology_file)
    
    # Extract atom information from the topology file
    print(f"\nExtracting atom information from {topology_file}...")
    atom_info = extract_atom_names(topology_file, sections)
    
    # Process all errors
    print(f"\nProcessing {len(errors)} errors...")
    
    # Process the first 10 errors for demonstration (or all if less than 10)
    num_errors_to_display = min(10, len(errors))
    
    for i in range(len(errors)):
        error = errors[i]
        
        # Identify atoms involved in the error
        atoms, atom_names_list, residue_info_list, atom_type_list = identify_atoms_from_context(error, sections, topology_file, atom_info)
        
        # Store the atoms, atom names, residue information, and atom types in the error dictionary
        error['atoms'] = atoms
        error['atom_names'] = atom_names_list
        error['residues'] = residue_info_list
        error['atom_types'] = atom_type_list
        
        # Display the error information (only for the first few)
        if i < num_errors_to_display:
            display_error_and_atoms(error)
    
    # Save the results to a file
    print(f"\nSaving results to {output_file}...")
    save_results(errors, output_file)
    
    # Generate and save dummy parameters
    print(f"\nGenerating dummy parameters...")
    dummies = process_errors_for_dummies(errors)
    
    # Count the number of dummy parameters
    num_angle_dummies = len(dummies['angles'])
    num_dihedral_dummies = len(dummies['dihedrals'])
    
    print(f"Generated {num_angle_dummies} angle dummy parameters and {num_dihedral_dummies} dihedral dummy parameters.")
    
    # Save the dummy parameters to a file
    print(f"\nSaving dummy parameters to {dummies_file}...")
    save_dummies(dummies, dummies_file)
    
    print("\nAnalysis completed!")

# Check if this file is being run directly
if __name__ == "__main__":
    main()
    
    
    