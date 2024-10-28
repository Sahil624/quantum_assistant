def print_dp_matrix(matrix, row_labels=None, col_labels=None):
    """
    Print a DP matrix in a readable format for debugging.
    
    Args:
    matrix (List[List]): The 2D DP matrix to print
    row_labels (List[str], optional): Labels for rows
    col_labels (List[str], optional): Labels for columns
    """
    if not matrix:
        print("Empty matrix")
        return
    
    # Determine the maximum width needed for each column
    max_width = max(len(str(item)) for row in matrix for item in row)
    max_width = max(max_width, 5)  # Ensure minimum width of 5
    
    # Print column labels if provided
    if col_labels:
        print(" " * (max_width + 1), end="")
        for label in col_labels:
            print(f"{str(label):^{max_width}} ", end="")
        print()
    
    # Print the matrix with row labels (if provided)
    for i, row in enumerate(matrix):
        if row_labels:
            print(f"{str(row_labels[i]):<{max_width}} ", end="")
        for item in row:
            print(f"{str(item):^{max_width}} ", end="")
        print()