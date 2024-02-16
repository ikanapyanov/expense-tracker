import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")

        self.frame = ttk.Frame(root)
        self.frame.pack(padx=10, pady=10, fill='x', expand=True)

        # Button to upload .csv file
        self.upload_btn = ttk.Button(self.frame, text="Upload CSV", command=self.upload_and_process_file)
        self.upload_btn.pack(side='left', fill='x', expand=True)

        # Button to show pie chart
        self.chart_btn = ttk.Button(self.frame, text="Show Chart", command=self.show_pie_chart)
        self.chart_btn.pack(side='left', fill='x', expand=True)

        self.tree_frame = ttk.Frame(root)
        self.tree_frame.pack(padx=10, pady=10, fill='both', expand=True)

        self.tree_scroll = ttk.Scrollbar(self.tree_frame)
        self.tree_scroll.pack(side='right', fill='y')

        # Define the Treeview
        self.tree = ttk.Treeview(self.tree_frame, yscrollcommand=self.tree_scroll.set, selectmode="browse", columns=("Date", "Category", "Description", "Amount"), show="headings")
        self.tree.pack(side='left', fill='both', expand=True)
        
        # Configure the scrollbar
        self.tree_scroll.config(command=self.tree.yview)

        # Define Treeview columns
        self.tree.column("Date", anchor='w', width=100)
        self.tree.column("Category", anchor='w', width=100)
        self.tree.column("Description", anchor='w', width=200)
        self.tree.column("Amount", anchor='e', width=100)

        # Define Treeview headings
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col, command=lambda _col=col: self.treeview_sort_column(self.tree, _col, False))

        # Store the latest expenses data frame for charting
        self.expenses = pd.DataFrame()

        # Create the keyword to category mapping
        self.keyword_to_category = self.build_keyword_to_category_map()

    def build_keyword_to_category_map(self):
        # Define categories with their associated keywords
        categories = {
            'Credit payment': ['Barclays', 'Novuna'],
            'Entertainment': ['DisneyPlus', 'PlayStation', 'Netflix', 'Now', 'Spotify'],
            'Groceries': ['Aldi', 'Amazon Fresh', 'Asda', 'Azuolas', 'Gopuff', 'GreenChef', 'Marks&Spencer', 'Morrisons', 'Tesco', 'Sainsburys', 'Waitrose', 'Zapp'],
            'Health': ['Boots', 'iHerb'],
            'Investments': ['Vanguard'],
            'Pets': ['Bow Wow', 'Grooming', 'PetBuddy', 'Piddlepatch'],
            'Transportation': ['Bolt', 'SWTrains', 'TfL', 'Uber'],
            'Restaurants': ['Bar', 'Beverages', 'Beer', 'Burger King', 'Coffee', 'Deliveroo', 'Greggs', 'Inamo', 'Laduree', 'McDonalds', 'Nathalie', 'Ole and Steen', 'Pret a Manger', 'Starbucks', 'Wagamama', 'Windjammer', 'Wine'],
            'Tax': ['HMRC'],
            'Utilities': ['EE Limited', 'HomeGround', 'Newham', 'Octopus', 'Service charge', 'Thames Water', 'TV licence'],
            'Work': ['Canva', 'Go Daddy', 'LinkedIn']
        }

        # Flatten the category structure into a keyword-to-category mapping
        keyword_to_category = {}
        for category, keywords in categories.items():
            for keyword in keywords:
                # Ensure keywords are lowercase for case-insensitive matching
                keyword_to_category[keyword.lower()] = category
        return keyword_to_category

    def categorize_expense(self, description):
        # Lowercase the description for case-insensitive comparison
        description_lower = description.lower()
        
        # Find the first matching category for the description
        for keyword, category in self.keyword_to_category.items():
            if keyword in description_lower:
                return category
        return 'Other'

    def upload_and_process_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        try:
            column_names = ['Date', 'Description', 'Amount']
            self.expenses = pd.read_csv(file_path, header=None, names=column_names)
            self.expenses['Amount'] = pd.to_numeric(self.expenses['Amount'], errors='coerce')
            self.expenses = self.expenses[self.expenses['Amount'] < 0]
            self.expenses['Category'] = self.expenses['Description'].apply(self.categorize_expense)

            # Clear existing entries in the Treeview
            for i in self.tree.get_children():
                self.tree.delete(i)

            # Insert new expenses into the Treeview
            for index, row in self.expenses.iterrows():
                self.tree.insert('', 'end', values=(row['Date'], row['Category'], row['Description'], f"{abs(row['Amount']):.2f}"))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process file. Ensure it is in the correct format.\nError: {e}")

    def show_pie_chart(self):
        if self.expenses.empty:
            messagebox.showinfo("Info", "No data to display. Please upload a CSV file first.")
            return
    
        # Calculate sum of expenses per category
        category_sums = self.expenses.groupby('Category')['Amount'].sum().abs()

        # Create a pie chart
        fig, ax = plt.subplots()
        ax.pie(category_sums, labels=category_sums.index, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures the pie chart is circular.

        # Create a new Tk window for the chart
        chart_window = tk.Toplevel(self.root)
        chart_window.title("Expenses by Category")

        # Embed the pie chart in the Tk window
        canvas = FigureCanvasTkAgg(fig, master=chart_window)  # Pass the figure and the new Tk window
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def treeview_sort_column(self, tv, col, reverse):
            l = [(tv.set(k, col), k) for k in tv.get_children('')]
            l.sort(reverse=reverse)

            # rearrange items in sorted positions
            for index, (val, k) in enumerate(l):
                tv.move(k, '', index)

            # reverse sort next time
            tv.heading(col, command=lambda: self.treeview_sort_column(tv, col, not reverse))

# Properly handle application exit
def on_closing(root):
    root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root))  # Ensure application exits properly
    root.mainloop()
