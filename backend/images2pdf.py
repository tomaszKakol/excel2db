import time
import os
import io

from reportlab.platypus import SimpleDocTemplate, Image, PageBreak
from reportlab.lib.pagesizes import A4, landscape, letter
from reportlab.pdfgen import canvas
from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger
from reportlab.pdfgen.canvas import Canvas
from pdfrw import PdfReader
from pdfrw.toreportlab import makerl
from pdfrw.buildxobj import pagexobj
from textwrap import wrap



from backend import labels

from PIL import Image as pilImage

# Obsługiwane typy obrazów
__allow_type = [".jpg", ".jpeg", ".bmp", ".png", ".tif"]
__rootDir = ""


def mergerPDFs(pdfs, result_file, file_path):
    # skrypt zawiera instrukcje obsługujące tworzenie oraz edycję plików pdf
    merger = PdfFileMerger()
    for pdf in pdfs:
        merger.append(pdf)

    _output = '%s/%s.pdf' % (file_path, result_file)
    merger.write(_output)
    footer(_output, _output, result_file)
    merger.close()


def convert_images2PDF_file(file_dir, save_name=None, filename_sort_fn=None):
    book_pages = []
    for parent, dirnames, filenames in os.walk(file_dir):
        if parent != file_dir:
            continue
        # Filtruj wszystkie obrazy
        for file_name in filenames:
            file_path = os.path.join(parent, file_name)
            # jeśli obrazek
            if __isAllow_file(file_path):
                book_pages.append(file_path)

        # Wpisz nazwę bieżącego katalogu jako tytuł
        if save_name == None:
            save_name = os.path.join(file_dir, (os.path.basename(file_dir) + ".pdf"))
        else:
            save_name = os.path.join(file_dir, save_name)

        if len(book_pages) > 0:
            # Start konwersji
            print("[*] [Konwertuj PDF]: Start. [Zapisz ścieżkę]> [%s]" % save_name)
            begin_time = time.clock()
            __converted(save_name, book_pages, filename_sort_fn)
            end_time = time.clock()
            print("[*] [Konwertuj PDF]: Koniec. [Zapisz ścieżkę]> [%s], Czas% f s" % (save_name, (end_time - begin_time)))
        else:
            print("W tym katalogu nie znaleziono plików graficznych. "
                  "Jeśli jest to katalog wielokrotny, spróbuj użyć funkcji convert_images2PDF_more_dirs")


def convert_images2PDF_dir(dirPath):
    __dirs = {}
    for parent, dirnames, filenames in os.walk(dirPath):
        for dirname in dirnames:
            # Załóżmy, że pod każdym folderem znajduje się obraz
            dirData = {"name": "", "pages": [], "isBook": False}
            dirName = dirname.split('/')[0]
            dirData['name'] = dirName
            __dirs[dirName] = dirData

            # Dowiedz się, czy są jakieś zdjęcia
        for filename in filenames:
            real_filename = os.path.join(parent, filename)
            # Wpisz nazwę folderu nadrzędnego jako tytuł
            parentDirName = real_filename.split('\\')[-2]

            if parentDirName in __dirs.keys():
                dirJsonData = __dirs[parentDirName]
            else:
                continue

            # Sprawdź, czy to zdjęcie
            if __isAllow_file(real_filename):
                dirJsonData['pages'].append(real_filename)
                if not dirJsonData['isBook']:
                    dirJsonData['isBook'] = True

    index = 1
    for dirName in __dirs.keys():
        dirData = __dirs[dirName]
        if dirData['isBook']:
            # print("[*] [Konwertuj PDF]: Start. [Nazwa]> [%s]" % (dirName))
            # beginTime = time.clock()
            # print((dirData['name'] + ".pdf"))
            __converted(os.path.join(dirPath, (dirData['name'] + ".pdf")), dirData['pages'])
            # endTime = time.clock()
            # print("[*] [Konwertuj PDF]: Koniec [Nazwa]> [%s], Upływ czasu %f s" % (dirName, (endTime - beginTime)))
            index += 1

    print("[*] [Wszystkie konwersje zakończone]:"
          " Ta konwersja pobiera liczbę katalogów %d, przekonwertowanego pliku PDF %d" % (len(__dirs), index - 1))


def __isAllow_file(filepath):
    if filepath and (os.path.splitext(filepath)[1] in __allow_type):
        return True
    return False


def __converted(save_book_name, book_pages=[], filename_sort_fn=None):
    # A4 format
    __a4_w, __a4_h = landscape(A4)

    if (filename_sort_fn == None):
        book_pages.sort()
    else:
        book_pages = sorted(book_pages, key=lambda name: int(filename_sort_fn(name)))

    bookPagesData = []
    bookDoc = SimpleDocTemplate(save_book_name, pagesize=A4, rightMargin=1, leftMargin=1, topMargin=2, bottomMargin=2)

    for page in book_pages:
        # print(page)
        img = pilImage.open(page)
        img_w, img_h = img.size

        if __a4_w / img_w < __a4_h / img_h:
            ratio = __a4_w / img_w / 1.5
        else:
            ratio = __a4_h / img_h

        data = Image(page, img_w * ratio, img_h * ratio)
        bookPagesData.append(data)
        #bookPagesData.append(PageBreak())
    try:
        bookDoc.build(bookPagesData)
        # print("Konwertowane >>>> " + save_book_name)

        packet = io.BytesIO()

        # utwórz nowy plik PDF za pomocą Reportlab
        # zawieramy w każdym pliku pdf podstawowe informacje o pochodzeniu danych
        can = canvas.Canvas(packet, pagesize=letter)
        can.setFont('Helvetica-Bold', 12)
        # can.drawString(10, 820, save_book_name)

        year = "--"
        term = "--"
        department = "--"
        user = "--"
        course = "--"
        commentsType = "--"

        try:
            year = save_book_name.split('/')[1]
            year = year.split(" ", 1)[1].split("_", 1)[0]
            try:
                start = int(year)
                end = start + 1
                year = str(start) + ' / ' + str(end)
            except:
                pass
        except:
            pass

        try:
            term = save_book_name.split('/')[2]
            if (term.find("let") != -1 and term.find("zim") == -1):
                term = labels.SUMMER
            elif (term.find("let") == -1 and term.find("zim") != -1):
                term = labels.WINTER
        except:
            pass

        try:
            department = save_book_name.split('/')[3]
        except:
            pass

        try:
            user = save_book_name.split('/')[4]
        except:
            pass

        try:
            course = save_book_name.split('/komentarze ')[1].split('\\')[0]
        except:
            pass
        try:
            commentsType = save_book_name.split('\\')[1].split('.pdf')[0]
        except:
            pass

        can.drawString(10, 760, "Rok:                           " + year)
        can.drawString(10, 730, "Semestr:                     " + term)
        can.drawString(10, 700, "Wydzial:                     " + department)
        can.drawString(10, 670, "Prowadzacy:              " + user)
        can.drawString(10, 640, "Przedmiot:                  " + course)
        can.drawString(10, 610, "Typ komentarzy:        " + commentsType)
        can.save()

        new_pdf = PdfFileReader(packet)
        existing_pdf = PdfFileReader(save_book_name)
        output = PdfFileWriter()
        output.addPage(new_pdf.getPage(0))
        output.addPage(existing_pdf.getPage(0))

        # na koniec zapisujemy „wynik” do prawdziwego pliku
        outputStream = open(save_book_name, "wb")
        output.write(outputStream)
        outputStream.close()
    except Exception as err:
        print("[*] [Konwertuj PDF]: Błąd. [Nazwa] > [%s]" % (save_book_name,))
        print("[*] Exception >>>> ", err)


def footer(input_file, output_file, info):
    # uzyskaj strony
    reader = PdfReader(input_file)
    pages = [pagexobj(p) for p in reader.pages]

    # zapisujemy dodatkowe informacje na istniejącym pliku
    canvas = Canvas(output_file)

    for page_num, page in enumerate(pages, start=1):
        # Add page
        canvas.setPageSize((page.BBox[2], page.BBox[3]))
        canvas.doForm(makerl(canvas, page))

        # Draw footer
        footer_text = "Strona %s z %s" % (page_num, len(pages))
        x = 128
        x_2 = 580
        canvas.saveState()
        canvas.setStrokeColorRGB(0, 0, 0)
        canvas.setLineWidth(0.5)
        canvas.line(66, 78, page.BBox[2] - 66, 78)
        canvas.setFont('Times-Roman', 10)
        canvas.drawString(page.BBox[2] - x, 65, footer_text)
        if len(info) < 109:
            canvas.drawString(page.BBox[2] - x_2, 45, info)
        else:
            _footer_text_part_1 = info[0:108]
            _footer_text_part_2 = info[108:]
            canvas.drawString(page.BBox[2] - x_2, 45, _footer_text_part_1)
            canvas.drawString(page.BBox[2] - x_2, 30, _footer_text_part_2)
        canvas.restoreState()
        canvas.showPage()

    canvas.save()


def getImageSize(imagePath):
    img = pilImage.open(imagePath)
    return img.size