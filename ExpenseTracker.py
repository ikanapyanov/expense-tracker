import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        
        # Setup frame for buttons and listbox
        self.frame = ttk.Frame(root)
        self.frame.pack(padx=10, pady=10, fill='x', expand=True)
        self.root.state('zoomed')
        
        # Upload button
        self.upload_btn = ttk.Button(self.frame, text="Upload CSV", command=self.upload_and_process_file)
        self.upload_btn.pack(fill='x', expand=True)
        
        # Listbox with scrollbar to display expenses
        self.list_frame = ttk.Frame(root)
        self.list_frame.pack(padx=10, pady=10, fill='both', expand=True)
        
        self.scrollbar = ttk.Scrollbar(self.list_frame)
        self.scrollbar.pack(side='right', fill='y')
        
        self.listbox = tk.Listbox(self.list_frame, yscrollcommand=self.scrollbar.set)
        self.listbox.pack(side='left', fill='both', expand=True)
        self.scrollbar.config(command=self.listbox.yview)

    def upload_and_process_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
    
        try:
            # Manually specify column names since the CSV has no headers
            column_names = ['Date', 'Description', 'Amount']
            df = pd.read_csv(file_path, header=None, names=column_names)
        
            # Convert 'Amount' column to numeric, errors='coerce' will convert non-numeric values to NaN
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
        
            # Filter for expenses (assuming negative amounts)
            expenses = df[df['Amount'] < 0]
        
            # Clear previous items from the listbox
            self.listbox.delete(0, 'end')
        
            # Add expenses to the listbox
            for index, row in expenses.iterrows():
                self.listbox.insert('end', f"{row['Date']} - {row['Description']} - {abs(row['Amount'])}")
    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process file. Ensure it is in the correct format.\nError: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()