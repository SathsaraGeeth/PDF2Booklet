from PyPDF2 import PdfReader, PdfWriter
from PyPDF2 import PageObject
from PyPDF2 import Transformation
from datetime import datetime
import io
import os

class Booklet:
    ' A class to generate booklet. '
    ##### **************************************** work **************************************** #####
    def __init__(self, file_path):
        try:
            self.input_path = file_path
            with open(file_path, 'rb') as file:
                file_content = file.read() # read the whole file into the memory
            self.pdf_reader = PdfReader(io.BytesIO(file_content)) # reader object
            self.pdf_writer = PdfWriter()  # initiate a writer object
            print("File loaded successfully.")
        except Exception as e:
            raise Exception(f"An error occurred while loading the file: {str(e)}")
    ##### **************************************** .... **************************************** #####  
        

    ##### **************************************** work **************************************** #####
      
    @property
    def no_pages(self):
        """ Returns the total number of pages. """
        return len(self.pdf_reader.pages)

    ##### **************************************** .... **************************************** #####  
    
    ##### **************************************** work **************************************** #####
    
    @property
    def page_size(self):
        """ Returns the size of pages assuming constant size through the PDF, in the format width * height. """
        return tuple(map(float, (self.pdf_reader.pages[0].mediabox.width, self.pdf_reader.pages[0].mediabox.height)))

    ##### **************************************** .... **************************************** #####

    ##### **************************************** work **************************************** #####

    def blank_page(self):
        """ Returns a blank page. """
        width, height = self.page_size
        return PageObject.create_blank_page(None, width, height)

    ##### **************************************** .... **************************************** #####
    
    ##### **************************************** work **************************************** #####

    def blank_booklet_page(self):
        """ Returns a blank booklet page. """
        width, height = self.page_size
        return PageObject.create_blank_page(None, height, width)

    ##### **************************************** .... **************************************** #####


    ##### **************************************** work **************************************** #####
    
    def merge_pages(self, left_page, right_page, scale = 0.5, inner_margin = 0):
        """ Merge two pages into one page, returns it. """

        width, height = self.page_size
        ret_page = self.blank_booklet_page()
        

        # trnasformations
        tx_l, ty_l = tuple(map(float, (0.0 - inner_margin, 0.0)))
        tx_r, ty_r = tuple(map(float, (inner_margin, 0.0)))


        # apply trnasformations, and merge
        transformation_right = Transformation().scale(scale).translate(tx_r, ty_r)
        transformation_left = Transformation().scale(scale).translate(tx_l, ty_l)
        
        left_page.add_transformation(transformation_left)
        right_page.add_transformation(transformation_right)

        ret_page.merge_page(left_page)
        ret_page.merge_page(right_page)
        
        return ret_page

    ##### **************************************** .... **************************************** #####

    ##### **************************************** work **************************************** #####

    def convert_to_type1(self):
        """
            Convert to type1 booklet and returns it.
            Type1 -> Each sheet itself is a booklet (4 pages per sheet).
        """
        self.pdf_writer = PdfWriter()  # reset the writer object to avoid potential conflicts
        num_pages = self.no_pages
        blank_page = self.blank_page()
        pages = self.pdf_reader.pages

        for i in range(0, num_pages, 4):
            # collect 4 pages (or blank pages if index is out of range, i.e., when the no of pages are not a mulitple of 4)
            sheet_indices = [i + 3, i, i + 1, i + 2]
            sheet = [pages[j] if j < num_pages else blank_page for j in sheet_indices]

            # merge and add the pages to the PDF: booklet
            for k in range(0, 4, 2):
                left_page = sheet[k]
                right_page = sheet[k + 1]
                if left_page and right_page:
                    merged_page = self.merge_pages(left_page, right_page)
                    self.pdf_writer.add_page(merged_page)

        print("Successfully converted to Type1 booklet.")
        
    ##### **************************************** .... **************************************** #####

    def convert_to_type2(self):
        """Type2: The entire set of sheets forms a single booklet (4 pages per sheet)."""
        self.pdf_writer = PdfWriter()  # Reset the writer object to avoid potential conflicts
        num_pages = self.no_pages
        blank_page = self.blank_page()
        pages = self.pdf_reader.pages

        # Calculate the total number of sheets (each sheet has 4 logical pages)
        total_sheets = (num_pages + 3) // 4  # Round up to account for incomplete sheets

        # Rearrange pages for booklet format
        for sheet in range(total_sheets):
            # Logical page indices for each sheet in booklet format
            page_indices = [
                (4 * total_sheets - 1) - (2 * sheet),     # Back side, left (last page in booklet order)
                (2 * sheet),                             # Front side, right (first page in booklet order)
                (2 * sheet + 1),                         # Front side, left (second page)
                (4 * total_sheets - 2) - (2 * sheet)     # Back side, right (second-to-last page)
            ]

            # Collect pages or blank pages if the index is out of range
            sheet_pages = [pages[i] if 0 <= i < num_pages else blank_page for i in page_indices]

            # Merge pages in pairs to form physical sheets
            for k in range(0, 4, 2):  # Merge [0 & 1], then [2 & 3]
                left_page = sheet_pages[k]
                right_page = sheet_pages[k + 1]
                merged_page = self.merge_pages(left_page, right_page)
                self.pdf_writer.add_page(merged_page)

        print("Successfully converted to Type2 booklet.")

    ##### **************************************** work **************************************** #####
        
    def save(self, file_name = None, file_path = None):
        """
            Saves the PDF, reutrns None.
            file_name (optional) -> unless specified an unique name will be assigned,
            file_path (optional) -> defaults to current directory.
        """
        if file_name is None:
            base, ext = os.path.splitext(self.input_path)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            file_name = f"{os.path.basename(base)}_booklet_{timestamp}{ext}"

        if file_path is None:
            file_path = os.getcwd()

        full_path = os.path.join(file_path, file_name)

        try:
            with open(full_path, "wb") as out_file:
                self.pdf_writer.write(out_file)
            print(f"Successfully saved file to {full_path}")
        except Exception as e:
            raise Exception(f"An error occurred while saving the file: {str(e)}")
            
    ##### **************************************** .... **************************************** #####

