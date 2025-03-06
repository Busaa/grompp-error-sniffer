"""
Functions to read and analyze error and topology files.
"""

# Import the re module for regular expressions
import re

def extract_error_info(error_file_path):
    """
    Reads the error file and extracts error information.
    
    Args:
        error_file_path: Path to the error file
        
    Returns:
        A list of dictionaries with error information
    """
    try:
        # Open and read the error file
        with open(error_file_path, 'r') as file:
            error_content = file.read()
        
        # Initialize empty list for errors
        errors = []
        
        # Check if we have content to process
        if not error_content:
            print("No error content to process.")
            return errors
        
        # Use pattern matching to find errors
        # Pattern: "ERROR X [file topol.top, line Y]: Message"
        error_pattern = r'ERROR (\d+) \[file topol\.top, line (\d+)\]:\s+(.*?)(?=\n\n|\Z)'
        
        # Find all matches in the content
        # re.DOTALL allows the dot (.) to match newlines as well
        matches = re.finditer(error_pattern, error_content, re.DOTALL)
        
        # For each match:
        for match in matches:
            # Extract error number, line number, and message
            error_num = int(match.group(1))
            line_num = int(match.group(2))
            error_msg = match.group(3).strip()
            
            # Add to errors list
            errors.append({
                'error_num': error_num,
                'line_number': line_num,
                'error_msg': error_msg
            })
        
        # Print a summary of what we found
        print(f"Found {len(errors)} errors in the file.")
        
        # Return the list of errors
        return errors
        
    except Exception as e:
        # Handle any errors that might occur
        print(f"Error processing error file: {e}. Please check the file path.")
        return []


def get_context_from_topology(topology_file):
    """
    Reads the topology file and finds where specific sections start.
    
    Args:
        topology_file: Path to the topology file
        
    Returns:
        A dictionary with section names as keys and their line numbers as values
    """
    try:
        # Define the sections we're looking for
        sections = ['[ atoms ]', '[ bonds ]', '[ pairs ]', '[ angles ]', '[ dihedrals ]']
        
        # Initialize a dictionary to store the line numbers
        section_lines = {}
        
        # Keep track of how many times we've seen each section
        section_counts = {section: 0 for section in sections}
        
        # Open the topology file
        with open(topology_file, 'r') as file:
            # Use enumerate to count lines (starting from 1)
            for i, line in enumerate(file, 1):
                # Strip whitespace from the line
                line = line.strip()
                
                # Check if the line matches any of our sections
                for section in sections:
                    if line.lower() == section.lower():
                        # Increment the count for this section
                        section_counts[section] += 1
                        
                        # For dihedrals, we need to distinguish between proper and improper
                        if section == '[ dihedrals ]':
                            if section_counts[section] == 1:
                                # First occurrence - proper dihedrals
                                section_lines['[ proper dihedrals ]'] = i
                            elif section_counts[section] == 2:
                                # Second occurrence - improper dihedrals
                                section_lines['[ improper dihedrals ]'] = i
                        else:
                            # For other sections, just store the line number
                            section_lines[section] = i
        
        # Print a summary of what we found
        print(f"Found {len(section_lines)} sections in the topology file:")
        for section in ['[ atoms ]', '[ bonds ]', '[ pairs ]', '[ angles ]', '[ proper dihedrals ]', '[ improper dihedrals ]']:
            if section in section_lines:
                print(f"  {section}: Line {section_lines[section]}")
            else:
                print(f"  {section}: Not found")
        
        # Return the dictionary of section lines
        return section_lines
        
    except Exception as e:
        # Handle any errors that might occur
        print(f"Error reading topology file: {e}")
        return {}


def extract_atom_names(topology_file, section_lines):
    """
    Extracts atom names, types, and residue information from the atoms section of the topology file.
    
    Args:
        topology_file: Path to the topology file
        section_lines: Dictionary with section line numbers
        
    Returns:
        A dictionary mapping atom numbers to dictionaries with atom name, type, and residue information
    """
    try:
        # Initialize a dictionary to store atom information
        atom_info = {}
        
        # Check if we have the atoms section
        if '[ atoms ]' not in section_lines:
            print("Atoms section not found in topology file")
            return atom_info
        
        # Get the start line of the atoms section
        atoms_start = section_lines['[ atoms ]']
        
        # Find the end line of the atoms section
        atoms_end = float('inf')
        for section, line in section_lines.items():
            if line > atoms_start and line < atoms_end:
                atoms_end = line
        
        # Open the topology file
        with open(topology_file, 'r') as file:
            # Skip to the atoms section
            for _ in range(atoms_start):
                next(file)
            
            # Read the atoms section
            line_num = atoms_start + 1
            for line in file:
                # Check if we've reached the end of the atoms section
                if line_num >= atoms_end:
                    break
                
                # Parse the line
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith(';'):
                    line_num += 1
                    continue
                
                # Split the line into tokens
                tokens = line.split()
                
                # Check if we have enough tokens
                # Format: nr type resnr residue atom cgnr charge mass typeB chargeB massB
                if len(tokens) >= 5:
                    atom_num = int(tokens[0])
                    atom_type = tokens[1]
                    resnr = tokens[2]
                    residue = tokens[3]
                    atom_name = tokens[4]
                    
                    # Store atom information
                    atom_info[atom_num] = {
                        'name': atom_name,
                        'type': atom_type,
                        'resnr': resnr,
                        'residue': residue
                    }
                
                line_num += 1
        
        print(f"Extracted information for {len(atom_info)} atoms")
        return atom_info
        
    except Exception as e:
        # Handle any errors that might occur
        print(f"Error extracting atom information: {e}")
        return {}


def identify_atoms_from_context(error, section_lines, topology_file, atom_info=None):
    """
    Identifies atoms involved in an error based on the error line and section.
    
    Args:
        error: Dictionary with error information
        section_lines: Dictionary with section line numbers
        topology_file: Path to the topology file
        atom_info: Dictionary mapping atom numbers to atom information (optional)
        
    Returns:
        A tuple containing:
        - A list of atoms involved in the error
        - A list of atom names if available
        - A list of residue information strings if available
        - A list of atom types if available
    """
    try:
        # Get the error line number
        error_line = error['line_number']
        
        # Determine which section the error is in
        error_section = None
        for section, start_line in section_lines.items():
            # If the error line is after this section's start line
            if error_line >= start_line:
                # Check if it's before the next section's start line
                is_last_section = True
                for next_section, next_start_line in section_lines.items():
                    if next_start_line > start_line and error_line >= next_start_line:
                        is_last_section = False
                        break
                
                if is_last_section:
                    error_section = section
                    break
        
        # If we couldn't determine the section, return empty lists
        if error_section is None:
            print(f"Could not determine section for error at line {error_line}")
            return [], [], [], []
        
        # Store the section in the error dictionary
        error['section'] = error_section
        
        # Read the error line from the topology file
        with open(topology_file, 'r') as file:
            # Skip to the error line
            for i, line in enumerate(file, 1):
                if i == error_line:
                    error_line_content = line.strip()
                    break
            else:
                # If we didn't find the line
                print(f"Could not find line {error_line} in the topology file")
                return [], [], [], []
        
        # Parse the line based on the section
        atoms = []
        
        # Split the line into tokens
        tokens = error_line_content.split()
        
        # Extract atoms based on the section
        if error_section == '[ bonds ]':
            # bonds: atom1 atom2 bond_type
            if len(tokens) >= 2:
                atoms = [int(tokens[0]), int(tokens[1])]
        
        elif error_section == '[ pairs ]':
            # pairs: atom1 atom2 pair_type
            if len(tokens) >= 2:
                atoms = [int(tokens[0]), int(tokens[1])]
        
        elif error_section == '[ angles ]':
            # angles: atom1 atom2 atom3 angle_type
            if len(tokens) >= 3:
                atoms = [int(tokens[0]), int(tokens[1]), int(tokens[2])]
        
        elif error_section == '[ proper dihedrals ]' or error_section == '[ improper dihedrals ]':
            # dihedrals: atom1 atom2 atom3 atom4 dihedral_type
            if len(tokens) >= 4:
                atoms = [int(tokens[0]), int(tokens[1]), int(tokens[2]), int(tokens[3])]
        
        # Get atom names, residue information, and atom types if available
        atom_name_list = []
        residue_info_list = []
        atom_type_list = []
        
        if atom_info:
            for atom in atoms:
                if atom in atom_info:
                    info = atom_info[atom]
                    atom_name_list.append(info['name'])
                    residue_info_list.append(f"{info['residue']}{info['resnr']}")
                    atom_type_list.append(info['type'])
                else:
                    atom_name_list.append(f"Unknown-{atom}")
                    residue_info_list.append("Unknown")
                    atom_type_list.append("Unknown")
        
        # Print what we found
        print(f"Error at line {error_line} is in section {error_section}")
        print(f"  Line content: {error_line_content}")
        print(f"  Atoms involved: {atoms}")
        if atom_name_list:
            print(f"  Atom names: {atom_name_list}")
        if residue_info_list:
            print(f"  Residues: {residue_info_list}")
        if atom_type_list:
            print(f"  Atom types: {atom_type_list}")
        
        return atoms, atom_name_list, residue_info_list, atom_type_list
    
    except Exception as e:
        # Handle any errors that might occur
        print(f"Error identifying atoms: {e}")
        return [], [], [], []


def display_error_and_atoms(error):
    """
    Displays error information and atoms involved in a formatted way.
    
    Args:
        error: Dictionary with error information
    """
    try:
        # Print error information
        print(f"Error {error['error_num']}:")
        print(f"  Line: {error['line_number']}")
        print(f"  Message: {error['error_msg']}")
        
        # Print atoms involved if available
        if 'atoms' in error and error['atoms']:
            print(f"  Atoms involved: {', '.join(map(str, error['atoms']))}")
            
            # Print atom names if available
            if 'atom_names' in error and error['atom_names']:
                print(f"  Atom names: {', '.join(error['atom_names'])}")
                
            # Print atom types if available
            if 'atom_types' in error and error['atom_types']:
                print(f"  Atom types: {', '.join(error['atom_types'])}")
                
            # Print residue information if available
            if 'residues' in error and error['residues']:
                print(f"  Residues: {', '.join(error['residues'])}")
        else:
            print("  No atoms identified")
        
        # Print a separator for readability
        print("-" * 40)
        
    except Exception as e:
        # Handle any errors that might occur
        print(f"Error displaying information: {e}")
        
        
def save_results(errors, output_file):
    """
    Saves analysis results to an output file.
    
    Args:
        errors: List of dictionaries with error information
        output_file: Path to the output file
    """
    try:
        # Create the output directory if it doesn't exist
        import os
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Open the output file
        with open(output_file, 'w') as file:
            # Write a header
            file.write("Topology Error Analysis Results\n")
            file.write("=" * 30 + "\n\n")
            
            # Write the number of errors found
            file.write(f"Total errors found: {len(errors)}\n\n")
            
            # Write information for each error
            for error in errors:
                file.write(f"Error {error['error_num']}:\n")
                file.write(f"  Line: {error['line_number']}\n")
                file.write(f"  Message: {error['error_msg']}\n")
                
                # Write atoms involved if available
                if 'atoms' in error and error['atoms']:
                    file.write(f"  Atoms involved: {', '.join(map(str, error['atoms']))}\n")
                    
                    # Write atom names if available
                    if 'atom_names' in error and error['atom_names']:
                        file.write(f"  Atom names: {', '.join(error['atom_names'])}\n")
                        
                    # Write atom types if available
                    if 'atom_types' in error and error['atom_types']:
                        file.write(f"  Atom types: {', '.join(error['atom_types'])}\n")
                        
                    # Write residue information if available
                    if 'residues' in error and error['residues']:
                        file.write(f"  Residues: {', '.join(error['residues'])}\n")
                else:
                    file.write("  No atoms identified\n")
                
                # Add a separator
                file.write("\n" + "-" * 30 + "\n\n")
            
            # Write a footer
            file.write("\nAnalysis completed.\n")
        
        print(f"Results saved to {output_file}")
        
    except Exception as e:
        # Handle any errors that might occur
        print(f"Error saving results: {e}")
        return False
    
    return True
