"""
Functions to generate dummy parameters for dihedrals and angle types.
"""

def generate_angle_dummy(atom_types):
    """
    Generates a dummy angle type parameter for the given atom types.
    
    Args:
        atom_types: List of atom types involved in the angle
        
    Returns:
        A string with the dummy angle type parameter
    """
    if len(atom_types) != 3:
        return None
    
    # Default values for angle parameters
    theta0 = 120.0
    ktheta = 200.0
    ub0 = 0.0
    kub = 0.0
    
    # Format the angle type parameter
    return f"{atom_types[0]:>8} {atom_types[1]:>8} {atom_types[2]:>8}     1   {theta0:10.6f}   {ktheta:10.6f}   {ub0:10.8f}   {kub:10.2f} ;"


def generate_dihedral_dummy(atom_types):
    """
    Generates a dummy dihedral type parameter for the given atom types.
    
    Args:
        atom_types: List of atom types involved in the dihedral
        
    Returns:
        A string with the dummy dihedral type parameter
    """
    if len(atom_types) != 4:
        return None
    
    # Default values for dihedral parameters
    phi0 = 0.0
    kphi = 0.0
    mult = 1
    
    # Format the dihedral type parameter
    return f"{atom_types[0]:>8} {atom_types[1]:>8} {atom_types[2]:>8} {atom_types[3]:>8}\t\t9     {phi0:10.6f}     {kphi:10.6f}     {mult} ;"


def process_errors_for_dummies(errors):
    """
    Processes errors to generate dummy parameters.
    
    Args:
        errors: List of dictionaries with error information
        
    Returns:
        A dictionary with dummy parameters for angles and dihedrals
    """
    angle_dummies = set()
    dihedral_dummies = set()
    
    # Counters for statistics
    total_errors = len(errors)
    processed_errors = 0
    skipped_no_atom_types = 0
    skipped_unknown_error = 0
    skipped_wrong_atom_count = 0
    
    print(f"\nProcessing {total_errors} errors for dummy parameters...")
    
    for error in errors:
        # Check if we have atom types
        if 'atom_types' not in error or not error['atom_types']:
            skipped_no_atom_types += 1
            continue
        
        # Check the error message to determine what kind of dummy to generate
        error_msg = error['error_msg'].lower()
        error_line = error['line_number']
        section = None
        
        # Determine the section based on the error line
        if 'section' in error:
            section = error['section']
        
        # For angle errors - look for specific error messages or section information
        if ('no default u-b types' in error_msg or 
            'angle type' in error_msg or 
            (section and 'angle' in section.lower())):
            
            # Check if we have the right number of atom types
            if len(error['atom_types']) == 3:
                dummy = generate_angle_dummy(error['atom_types'])
                if dummy:
                    angle_dummies.add(dummy)
                    processed_errors += 1
                    print(f"Generated angle dummy for error at line {error_line}: {error['atom_types']}")
                else:
                    skipped_wrong_atom_count += 1
            else:
                skipped_wrong_atom_count += 1
                print(f"Skipped angle error at line {error_line} - wrong atom count: {len(error['atom_types'])}")
        
        # For dihedral errors - look for specific error messages or section information
        elif ('no default dihedral type' in error_msg or 
              'dihedral type' in error_msg or 
              (section and 'dihedral' in section.lower())):
            
            # Check if we have the right number of atom types
            if len(error['atom_types']) == 4:
                dummy = generate_dihedral_dummy(error['atom_types'])
                if dummy:
                    dihedral_dummies.add(dummy)
                    processed_errors += 1
                    print(f"Generated dihedral dummy for error at line {error_line}: {error['atom_types']}")
                else:
                    skipped_wrong_atom_count += 1
            else:
                skipped_wrong_atom_count += 1
                print(f"Skipped dihedral error at line {error_line} - wrong atom count: {len(error['atom_types'])}")
        
        # Unknown error type
        else:
            skipped_unknown_error += 1
            print(f"Skipped unknown error type at line {error_line}: {error_msg[:50]}...")
    
    # Print statistics
    print(f"\nDummy parameter generation statistics:")
    print(f"  Total errors: {total_errors}")
    print(f"  Processed errors: {processed_errors}")
    print(f"  Skipped (no atom types): {skipped_no_atom_types}")
    print(f"  Skipped (unknown error type): {skipped_unknown_error}")
    print(f"  Skipped (wrong atom count): {skipped_wrong_atom_count}")
    print(f"  Generated angle dummies: {len(angle_dummies)}")
    print(f"  Generated dihedral dummies: {len(dihedral_dummies)}")
    
    return {
        'angles': sorted(list(angle_dummies)),
        'dihedrals': sorted(list(dihedral_dummies))
    }


def save_dummies(dummies, output_file):
    """
    Saves dummy parameters to an output file.
    
    Args:
        dummies: Dictionary with dummy parameters
        output_file: Path to the output file
    """
    try:
        # Create the output directory if it doesn't exist
        import os
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Open the output file
        with open(output_file, 'w') as file:
            # Write a header
            file.write("; Dummy parameters generated for topology errors\n\n")
            
            # Write angle types if available
            if dummies['angles']:
                file.write("[ angletypes ]\n")
                file.write(";      i        j        k  func       theta0       ktheta          ub0          kub\n")
                for angle in dummies['angles']:
                    file.write(f"{angle}\n")
                file.write("\n")
            
            # Write dihedral types if available
            if dummies['dihedrals']:
                file.write("[ dihedraltypes ]\n")
                file.write(";      i        j        k        l  func         phi0         kphi  mult\n")
                for dihedral in dummies['dihedrals']:
                    file.write(f"{dihedral}\n")
                file.write("\n")
            
            # Write a footer
            file.write("; End of dummy parameters\n")
        
        print(f"Dummy parameters saved to {output_file}")
        
    except Exception as e:
        # Handle any errors that might occur
        print(f"Error saving dummy parameters: {e}")
        return False
    
    return True
