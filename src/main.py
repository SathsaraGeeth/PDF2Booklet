import tkinter as tk
from tkinter import filedialog, messagebox
import os
from datetime import datetime
from booklet import Booklet

def process_pdf():
    input_file = file_path_var.get()
    output_name = output_name_var.get()
    booklet_type = type_var.get()

    if not input_file:
        messagebox.showerror("Error", "Please select an input PDF file.")
        return

    try:
        # Initialize booklet
        booklet = Booklet(input_file)

        # Generate the selected booklet type
        if booklet_type == 1:
            booklet.convert_to_type1()
        elif booklet_type == 2:
            booklet.convert_to_type2()

        # Define output file name
        if not output_name:
            base, ext = os.path.splitext(os.path.basename(input_file))
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            output_name = f"{base}_booklet_{timestamp}{ext}"
        # Save the file
        output_dir = os.path.dirname(input_file)
        booklet.save(file_name=output_name, file_path=output_dir)

        messagebox.showinfo("Success", f"File saved successfully to:\n{os.path.join(output_dir, output_name)}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred:\n{str(e)}")

def browse_file():
    """
    Open file dialog to select the input PDF file.
    """
    file_path = filedialog.askopenfilename(
        title="Select PDF File",
        filetypes=[("PDF Files", "*.pdf")],
    )
    if file_path:
        file_path_var.set(file_path)

# GUI Initialization
root = tk.Tk()
root.title("PDF2Booklet")
root.geometry("680x225")

# Variables
file_path_var = tk.StringVar()
output_name_var = tk.StringVar()
type_var = tk.IntVar(value=1)
compress_var = tk.BooleanVar(value=False)

# Layout
tk.Label(root, text="PDF Booklet Generator", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=3, pady=10)

# File Selection
tk.Label(root, text="Input PDF File:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
tk.Entry(root, textvariable=file_path_var, width=40).grid(row=1, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=browse_file).grid(row=1, column=2, padx=5, pady=5)

# Booklet Type
tk.Label(root, text="Select Booklet Type:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
tk.Radiobutton(root, text="Sheet-Wise: for large books.", variable=type_var, value=1).grid(row=2, column=1, sticky="w", padx=5)
tk.Radiobutton(root, text="Continous: for small books.", variable=type_var, value=2).grid(row=3, column=1, sticky="w", padx=5)

# Output File Name
tk.Label(root, text="Output File Name (optional):").grid(row=4, column=0, sticky="e", padx=5, pady=5)
tk.Entry(root, textvariable=output_name_var, width=40).grid(row=4, column=1, padx=5, pady=5)

# Process Button
tk.Button(
    root, text="Start", command=process_pdf, bg="green", fg="red", font=("Arial", 12)
).grid(row=6, column=0, columnspan=3, pady=10)

# Start the GUI
root.mainloop()
