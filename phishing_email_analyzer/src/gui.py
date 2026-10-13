import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from .parser import parse_eml
from .pdf_generator import generate_print_report, generate_fillable_report

class PhishingEmailAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Phishing Email Analyzer")
        self.root.geometry("600x400")

        self.eml_file_path = tk.StringVar()
        self.output_dir_path = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        # Frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(main_frame, text="Phishing Email Analyzer", font=("Helvetica", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # EML File Selection
        ttk.Label(main_frame, text="Select EML File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.eml_file_path, width=50).grid(row=1, column=1, padx=10, pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_eml).grid(row=1, column=2, pady=5)

        # Output Directory Selection
        ttk.Label(main_frame, text="Select Output Directory:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.output_dir_path, width=50).grid(row=2, column=1, padx=10, pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_out_dir).grid(row=2, column=2, pady=5)

        # Generate Button
        self.generate_btn = ttk.Button(main_frame, text="Analyze & Generate Reports", command=self.generate_reports)
        self.generate_btn.grid(row=3, column=0, columnspan=3, pady=20)

        # Status Label
        self.status_label = ttk.Label(main_frame, text="Status: Ready", foreground="blue")
        self.status_label.grid(row=4, column=0, columnspan=3, pady=10)

    def browse_eml(self):
        filename = filedialog.askopenfilename(
            title="Select an EML file",
            filetypes=(("EML files", "*.eml"), ("All files", "*.*"))
        )
        if filename:
            self.eml_file_path.set(filename)

    def browse_out_dir(self):
        dirname = filedialog.askdirectory(title="Select Output Directory")
        if dirname:
            self.output_dir_path.set(dirname)

    def update_status(self, message, is_error=False):
        self.status_label.config(text=f"Status: {message}", foreground="red" if is_error else "green")
        self.root.update_idletasks()

    def generate_reports(self):
        eml_path = self.eml_file_path.get()
        out_dir = self.output_dir_path.get()

        if not eml_path:
            messagebox.showerror("Error", "Please select an EML file.")
            return
        if not os.path.exists(eml_path):
            messagebox.showerror("Error", "Selected EML file does not exist.")
            return
        if not out_dir:
            messagebox.showerror("Error", "Please select an output directory.")
            return
        if not os.path.exists(out_dir):
            messagebox.showerror("Error", "Selected output directory does not exist.")
            return

        self.update_status("Parsing EML file...")
        self.generate_btn.config(state=tk.DISABLED)

        try:
            # 1. Parse EML
            parsed_data = parse_eml(eml_path)

            # Base name for output files
            base_name = os.path.splitext(os.path.basename(eml_path))[0]

            # Paths
            fillable_pdf_path = os.path.join(out_dir, f"{base_name}_fillable_report.pdf")
            print_pdf_path = os.path.join(out_dir, f"{base_name}_print_report.pdf")

            # 2. Generate Print PDF
            self.update_status("Generating Print Report...")
            generate_print_report(parsed_data, print_pdf_path)

            # 3. Generate Fillable PDF
            self.update_status("Generating Fillable Report...")
            generate_fillable_report(parsed_data, fillable_pdf_path)

            self.update_status(f"Success! Reports saved to:\n{out_dir}")
            messagebox.showinfo("Success", f"Reports generated successfully:\n- {fillable_pdf_path}\n- {print_pdf_path}")

        except Exception as e:
            self.update_status(f"Error: {e}", is_error=True)
            messagebox.showerror("Error", f"An error occurred during processing:\n{e}")
        finally:
            self.generate_btn.config(state=tk.NORMAL)

def run_gui():
    root = tk.Tk()
    app = PhishingEmailAnalyzerApp(root)
    root.mainloop()
