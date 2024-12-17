from PyPDF2 import PdfReader, PdfWriter, PageObject
from PyPDF2 import Transformation
from datetime import datetime
from PyPDF2.generic import RectangleObject
import io
import os
import copy

class Booklet:
    """A class to generate booklet."""

    def __init__(self, file_path):
        try:
            self.input_path = file_path
            with open(file_path, 'rb') as file:
                file_content = file.read()
            self.pdf_reader = PdfReader(io.BytesIO(file_content))  # Reader object
            self.pdf_writer = PdfWriter()  # Writer object
            print("File loaded successfully.")
        except Exception as e:
            raise Exception(f"An error occurred while loading the file: {str(e)}")

    @property
    def no_pages(self):
        """Returns the total number of pages."""
        return len(self.pdf_reader.pages)

    @property
    def page_size(self):
        """Returns the size of pages assuming constant size through the PDF."""
        return tuple(map(float, (self.pdf_reader.pages[0].mediabox.width, self.pdf_reader.pages[0].mediabox.height)))

    def blank_page(self):
        """Returns a fresh blank page."""
        width, height = self.page_size
        return PageObject.create_blank_page(None, width, height)

    def blank_booklet_page(self):
        """Returns a fresh blank booklet page."""
        width, height = self.page_size
        return PageObject.create_blank_page(None, height, width)

    def merge_pages(self, left_page, right_page, inner_margin = 0, scale = None):
        """Merge two pages into one page, returns it."""
        if not scale:
            scale = 0.75 # min((height / 2 - inner_margin) / height, (width - inner_margin) / width)   # todo1: fix this formula for optimal scaling factor
        width, height = self.page_size
        ret_page = self.blank_booklet_page()

        # Copy pages to avoid mutability issues <- this is crucial otherwise the scaling will be wrong # todo3: find out why and think of a workaround
        left_page = copy.deepcopy(left_page)
        right_page = copy.deepcopy(right_page)

        # Transformations
        tx_l, ty_l = (0.0 - inner_margin, 0.0)
        tx_r, ty_r = (height/2 + inner_margin, 0.0)

        transformation_left = Transformation().scale(scale).translate(tx_l, ty_l)
        transformation_right = Transformation().scale(scale).translate(tx_r, ty_r)

        left_page.mediabox = RectangleObject([tx_l, ty_l, height, width])
        right_page.mediabox = RectangleObject([tx_r, ty_r, height, width])
        left_page.add_transformation(transformation_left)
        right_page.add_transformation(transformation_right)

        ret_page.merge_page(left_page)
        ret_page.merge_page(right_page)
        return ret_page


    def convert_to_type1(self):
        """ Convert to Type1 booklet: Each sheet itself is a booklet (4 pages per sheet). """
        self.pdf_writer = PdfWriter()
        num_pages = self.no_pages
        pages = self.pdf_reader.pages

        for i in range(0, num_pages, 4):
            sheet_indices = [i + 3, i, i + 1, i + 2]
            sheet = [pages[j] if j < num_pages else self.blank_page() for j in sheet_indices]

            for k in range(0, 4, 2):
                left_page = sheet[k]
                right_page = sheet[k + 1]
                merged_page = self.merge_pages(left_page, right_page)
                self.pdf_writer.add_page(merged_page)

        print("Successfully converted to Type1 booklet.")

    # todo2: check whether if this produce the desired booklet type
    def convert_to_type2(self):
        """ Convert to Type2 booklet: The entire set of sheets forms a single booklet(4 pages per sheet). """
        self.pdf_writer = PdfWriter()
        num_pages = self.no_pages
        pages = self.pdf_reader.pages
        total_sheets = (num_pages + 3) // 4

        for sheet in range(total_sheets):
            page_indices = [
                (4 * total_sheets - 1) - (2 * sheet),
                (2 * sheet),
                (2 * sheet + 1),
                (4 * total_sheets - 2) - (2 * sheet)
            ]
            sheet_pages = [pages[i] if 0 <= i < num_pages else self.blank_page() for i in page_indices]

            for k in range(0, 4, 2):
                left_page = sheet_pages[k]
                right_page = sheet_pages[k + 1]
                merged_page = self.merge_pages(left_page, right_page)
                self.pdf_writer.add_page(merged_page)

        print("Successfully converted to Type2 booklet.")

    def output(self):
        """ Returns the created PDF as a memory file. """
        try:
            # Create a BytesIO object to hold the output PDF in memory
            memory_file = io.BytesIO()
            self.pdf_writer.write(memory_file)

            # Seek to the beginning of the file before returning it
            memory_file.seek(0)
            return memory_file
        except Exception as e:
            raise Exception(f"An error occurred while generating the memory file: {str(e)}")

    # def save(self, file_name=None, file_path=None):
    #     """Saves the PDF."""
    #     if file_name is None:
    #         base, ext = os.path.splitext(self.input_path)
    #         timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    #         file_name = f"{os.path.basename(base)}_booklet_{timestamp}{ext}"

    #     if file_path is None:
    #         file_path = os.getcwd()

    #     full_path = os.path.join(file_path, file_name)

    #     try:
    #         with open(full_path, "wb") as out_file:
    #             self.pdf_writer.write(out_file)
    #         print(f"Successfully saved file to {full_path}")
    #     except Exception as e:
    #         raise Exception(f"An error occurred while saving the file: {str(e)}")