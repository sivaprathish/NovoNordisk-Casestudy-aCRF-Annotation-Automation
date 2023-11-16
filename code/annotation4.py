import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
import threading
import PyPDF2
import hashlib

# Function to hash the content of a page using SHA-256
def hash_page_content(page):
    text = page.extract_text()
    if text:
        return hashlib.sha256(text.encode()).hexdigest()
    return None

# Function to copy annotations from the source PDF to the destination PDF
def copy_annotations(source_pdf_path, destination_pdf_path, progress_label, append_terminal_output):
    # Open both the source and destination PDF files in binary mode
    with open(source_pdf_path, "rb") as source_pdf, open(destination_pdf_path, "rb") as destination_pdf:
        # Create PdfReader objects for both source and destination PDFs
        pdf_reader_source = PyPDF2.PdfReader(source_pdf)
        pdf_reader_destination = PyPDF2.PdfReader(destination_pdf)
        
        # Create a PdfWriter object to write the modified PDF
        pdf_writer = PyPDF2.PdfWriter()

        # Initialize a flag to track whether annotations were copied
        annotations_copied = False

        # Calculate and store hash values for pages in the source PDF
        source_hashes = [hash_page_content(page) for page in pdf_reader_source.pages]

        # Loop through pages in the destination PDF
        for dest_page_number, dest_page in enumerate(pdf_reader_destination.pages):
            dest_hash = hash_page_content(dest_page)
            
            # Check if the hash of the destination page matches any source page
            if dest_hash in source_hashes:
                source_page_number = source_hashes.index(dest_hash)
                source_page = pdf_reader_source.pages[source_page_number]
                
                # Check if the source page has annotations
                if '/Annots' in source_page:
                    annotations = source_page['/Annots']
                    if isinstance(annotations, PyPDF2.generic.IndirectObject):
                        annotations = annotations.get_object()
                    
                    # Copy annotations to the destination page
                    dest_page[PyPDF2.generic.NameObject("/Annots")] = annotations

                    annotations_copied = True

                    append_terminal_output(f"Annotations copied from Source Page {source_page_number} to Destination Page {dest_page_number}")
                else:
                    append_terminal_output(f"No annotations found in Source Page {source_page_number}")

            # Add the destination page to the PdfWriter
            pdf_writer.add_page(dest_page)

        # Write the modified PDF to the output file
        with open("output4.pdf", "wb") as output_pdf:
            pdf_writer.write(output_pdf)

        # Check if annotations were copied and print a message
        if annotations_copied:
            append_terminal_output("Annotations detected and copied to the output file")


class PDFCopyApp:
    def __init__(self, master):
        self.master = master
        self.master.title("PDF Annotation Copier")
        self.master.geometry("800x600")
        
        style = ttk.Style(master)
        style.configure('TButton', font=('Arial', 18),  background='blue')
        style.configure('TLabel', font=('Arial', 18), foreground='black')
        style.configure('TLabel', font=('Arial', 18), foreground='black')
        style.configure('TFrame', background='lightgrey')

        self.frame = ttk.Frame(master)
        self.frame.pack(expand=True, fill='both')

        self.source_label = ttk.Label(master, text="Source PDF:")
        self.source_label.pack(pady=(20, 0))

        self.source_btn = ttk.Button(master, text="Select Source", command=self.select_source)
        self.source_btn.pack(pady=(0, 10))
        
        self.source_filename_label = ttk.Label(master, text="Source File: None")
        self.source_filename_label.pack(pady=(0, 10))

        self.dest_label = ttk.Label(master, text="Destination PDF:")
        self.dest_label.pack(pady=(20, 0))

        self.dest_btn = ttk.Button(master, text="Select Destination", command=self.select_destination)
        self.dest_btn.pack(pady=(0, 10))
        
        self.dest_filename_label = ttk.Label(master, text="Destination File: None")
        self.dest_filename_label.pack(pady=(0, 10))

        self.copy_btn = ttk.Button(master, text="Click To Copy Annotation", command=self.copy_annotations)
        self.copy_btn.pack(pady=(0,30))

        self.progress_label = ttk.Label(master, text="")
        self.progress_label.pack(pady=(20, 0))

        self.terminal_output = tk.Text(master, wrap=tk.WORD, font=('Arial', 12), height=10, state=tk.DISABLED)
        self.terminal_output.pack(pady=(10, 0), padx=10, fill=tk.BOTH, expand=True)

        self.source_path = None
        self.dest_path = None

    def select_source(self):
        self.source_path = filedialog.askopenfilename(title="Select Source PDF", filetypes=[("PDF Files", "*.pdf")])
        self.source_filename_label.config(text=f"Source File: {self.source_path}")
    
    def append_terminal_output(self, message):
        self.terminal_output.config(state=tk.NORMAL)
        self.terminal_output.insert(tk.END, message + "\n")
        self.terminal_output.config(state=tk.DISABLED)
        self.terminal_output.see(tk.END)

    def select_destination(self):
        self.dest_path = filedialog.askopenfilename(title="Select Destination PDF", filetypes=[("PDF Files", "*.pdf")])
        self.dest_filename_label.config(text=f"Destination File: {self.dest_path}")

    def copy_annotations(self):
        if self.source_path and self.dest_path:
            progress_thread = threading.Thread(target=self.run_copy_annotations)
            progress_thread.start()

    def run_copy_annotations(self):
        self.progress_label.config(text="Copying annotations...")
        try:
            copy_annotations(self.source_path, self.dest_path, self.progress_label, self.append_terminal_output)
            messagebox.showinfo("Success", "Annotations copied successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            self.progress_label.config(text="")

def run_app():
    root = tk.Tk()
    app = PDFCopyApp(root)
    root.mainloop()

if __name__ == "__main__":
    run_app()
