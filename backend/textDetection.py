# Bibliografia:
# https://www.pyimagesearch.com/2018/08/20/opencv-text-detection-east-text-detector/

# istrukcja uruchomienia skryptu:
# python textDetection.py --image images/a.tif --east frozen_east_text_detection.pb

from backend import images2pdf as imgs2pdf, labels, findFiles as files

from imutils.object_detection import non_max_suppression
from trans import trans
import numpy as np
import time
import cv2
import os


def list_and_detection(east, min_confidence, width, height):
	# przeszukanie struktury katalogów
	# w tym przypadku musimy tymczasowo zmienić ścieżki dostępu do plików przez usunięcie polskich znaków, gdyż
	# biblioteka do detekcji tekstu obsługuje wyłącznie znaki z angielskie alfabetu. Jednak zaraz po wykonaniu detekcji
	# przywracami wcieśniejsze ścieżki do plików. Zamianę polskich znaków na ich ang odpowiedniki wykonujemy za pomocą
	# biblioteki 'trans'
	years = files.all_folders_in_path(labels.ROOT_DATA_FOLDER)
	for year in years:
		year_path = '%s/%s' % (labels.ROOT_DATA_FOLDER, year)
		trans_year = trans(year)
		trans_year_path = '%s/%s' % (labels.ROOT_DATA_FOLDER, trans_year)
		if year != trans_year:
			os.rename(year_path, trans_year_path)
		terms = files.all_folders_in_path(trans_year_path)
		# print(terms)

		# substring "Ankiety 2014_15" -> "2014"
		_yearValue = year.split(" ", 1)[1].split("_", 1)[0]

		for term in terms:
			termName = None
			if (term.find("let") != -1 and term.find("zim") == -1):
				termName = labels.SUMMER
			elif (term.find("let") == -1 and term.find("zim") != -1):
				termName = labels.WINTER
			elif (term.find("let") != -1 and term.find("zim") != -1):
				termName = labels.OUTSTANDING
			else:
				termName = labels.INVALID

			term_path = '%s/%s' % (trans_year_path, term)
			trans_term = trans(term)
			trans_term_path = '%s/%s' % (trans_year_path, trans_term)
			if term != trans_term:
				os.rename(term_path, trans_term_path)
			departments = files.all_folders_in_path(trans_term_path)
			if departments:
				for department in departments:
					department_path = '%s/%s' % (trans_term_path, department)
					trans_department = trans(department)
					trans_department_path = '%s/%s' % (trans_term_path, trans_department)
					if department != trans_department:
						os.rename(department_path, trans_department_path)
					users = files.all_folders_in_path(trans_department_path)
					# print(users)
					if users:
						for user in users:
							user_path = '%s/%s' % (trans_department_path, user)
							trans_user = trans(user)
							trans_user_path = '%s/%s' % (trans_department_path, trans_user)
							if user != trans_user:
								os.rename(user_path, trans_user_path)

							courses_folders = files.all_folders_in_path(trans_user_path)
							if courses_folders:
								for course in courses_folders:
									course_path = '%s/%s' % (trans_user_path, course)
									trans_course = trans(course)
									trans_course_path = '%s/%s' % (trans_user_path, trans_course)

									if course != trans_course:
										os.rename(course_path, trans_course_path)
									course_folders = files.all_folders_in_path(trans_course_path)

									if course_folders:
										for folder in course_folders:
											folder_path = '%s/%s' % (trans_course_path, folder)
											trans_folder = trans(folder)
											trans_folder_path = '%s/%s' % (trans_course_path, trans_folder)
											if folder != trans_folder:
												os.rename(folder_path , trans_folder_path)

											img_files = files.all_files_in_path(trans_folder_path)

											if img_files:
												for img_file in img_files:
													img_file_path = '%s/%s' % (trans_folder_path, img_file)
													trans_img_file = trans(img_file)
													trans_img_file_path = '%s/%s' % (trans_folder_path, trans_img_file)

													if img_file != trans_img_file:
														os.rename(img_file_path, trans_img_file_path)
													# print(trans_img_file_path)

													# W tym miejscu wywołujemy obiekt instrukcji text_detection,
													# w którym rostrzygamy czy na obrazku jest tekst i czy przenosimy
													# go do folderu 'bin', gdy nie znajdziemy tekstu
													text_detection(trans_img_file_path, east, min_confidence, width, height)
									try:
										print(trans_course_path)
										# W tym miejscu scalamy wszystkie pliki graficzne
										# z komentarzami w jeden plik pdf
										imgs2pdf.convert_images2PDF_dir(trans_course_path)
									except FileNotFoundError:
										# katalog nie istnieje
										pass
									try:
										try:
											# W tym miejscu scalamy wszystkie obrazki, które zostały przeniesione
											# do kosza podczas detekcji i stwierdzeniu, ze nie ma na nich tekstu
											print('%s/%s' % (labels.BIN_FOLDER, trans_course_path))
											imgs2pdf.convert_images2PDF_dir('%s/%s' % (
												labels.BIN_FOLDER, trans_course_path))
										except:
											print("Nie udało się przenieść pliku do 'kosza', "
												  "gyż istnieje już plik o podanej ścieżce")
									except FileNotFoundError:
										# katalog nie istnieje
										pass

									# W tym miejscu wykonujemy scalenia różnych typów komentarzy w jeden plik pdf
									pdfs_file_name = "komentarze_" + _yearValue + '_' + trans_term + '_' + \
													 trans_department + '_' + trans_user + '_' + trans_course
									pdfs = []
									_files = files.all_files_in_path(trans_course_path)
									if files:
										for file in _files:
											if file.find('.pdf') != -1:
												pdfs.append(trans_course_path + '/' + file)
									# print(pdfs)
									if pdfs:
										if not os.path.exists(labels.COMMENTS_FOLDER_PATH):
											os.makedirs(labels.COMMENTS_FOLDER_PATH)
										imgs2pdf.mergerPDFs(pdfs, pdfs_file_name, labels.COMMENTS_FOLDER_PATH)

									#Tutaj przywracamy orginalne nazwy ścieżek do plików
									if course != trans_course:
										os.rename(trans_course_path, course_path)

							if user != trans_user:
								os.rename(trans_user_path, user_path)

						if department != trans_department:
							os.rename(trans_department_path, department_path)

				if term != trans_term:
					os.rename(trans_term_path, term_path)

		if year != trans_year:
			os.rename(trans_year_path, year_path)


def text_detection(image_path, east, min_confidence, width, height):
	args = {'image': image_path, 'east': east, 'min_confidence' : min_confidence , 'width': width, 'height': height}

	# załaduj obraz wejściowy i uchwyć wymiary obrazu
	image = cv2.imread(args[u"image"])
	orig = image.copy()
	(H, W) = image.shape[:2]

	# ustaw nową szerokość i wysokość, a następnie określ zmienny stosunek zarówno dla szerokości
	# jak i wysokości obrazka
	(newW, newH) = (args["width"], args["height"])
	rW = W / float(newW)
	rH = H / float(newH)

	# zmień rozmiar obrazu i uchwyć nowe wymiary obrazu
	image = cv2.resize(image, (newW, newH))
	(H, W) = image.shape[:2]

	# zdefiniuj dwie nazwy warstw wyjściowych dla modelu detektora EAST
	# pierwszą jest prawdopodobieństwo na wyjściu,
	# a drugą można wykorzystać do uzyskania współrzędnych ramki granicznej tekstu
	layerNames = [
		"feature_fusion/Conv_7/Sigmoid",
		"feature_fusion/concat_3"]


	# załaduj wstępnie nauczony detektor tekstu EAST
	# print("[INFO] ładowanie detektora tekstu...")
	net = cv2.dnn.readNet(args["east"])

	# zbuduj obiekt blob z obrazu,
	blob = cv2.dnn.blobFromImage(image, 2.0, (W, H),
		(128.0, 32.0, 128.0), swapRB=True, crop=False)

	start = time.time()
	net.setInput(blob)
	(scores, geometry) = net.forward(layerNames)
	end = time.time()

	print("[INFO] Detekcja tekstu trwała {:.6f} sekund".format(end - start))

    # po przeprowadzeniu detekcji w wyniku dostajemy x wierszy i x kolumn gdzie może znajdować się tekst
	# (poziom ufności), na tej podstawie łączymy wierzchołki i tworzymy prostokąty

	(numRows, numCols) = scores.shape[2:4]
	rects = []
	confidences = []

	# pętla po wszystkich wierszach podzielonego obrazka
	for y in range(0, numRows):
		# extract the scores (probabilities), followed by the geometrical data used to derive potential bounding box coordinates that surround text
		# wyodrębnienie wyników (prawdopodobieństwa),
		# następnie używamy współrzędnych do zbudowania ramkek otaczających tekst
		scoresData = scores[0, 0, y]
		xData0 = geometry[0, 0, y]
		xData1 = geometry[0, 1, y]
		xData2 = geometry[0, 2, y]
		xData3 = geometry[0, 3, y]
		anglesData = geometry[0, 4, y]

		# pętla po wszystkich kolumnach podzielonego obrazka
		for x in range(0, numCols):
			# jeśli wynik nie ma wystarczającego prawdopodobieństwa to ignorujemy ​​go
			if scoresData[x] < args["min_confidence"]:
				continue

			# obliczamy współczynnik przesunięcia,
			# ponieważ nasze wynikowe mapy obiektów będą czterokrotnie mniejsze niż obraz wejściowy
			(offsetX, offsetY) = (x * 4.0, y * 4.0)

			# wyodrębnienie kąta obrotu dla predykcji
			angle = anglesData[x]
			cos = np.cos(angle)
			sin = np.sin(angle)

			# korzystamy z objętości , aby uzyskać szerokość i wysokość ramki
			h = xData0[x] + xData2[x]
			w = xData1[x] + xData3[x]

			# obliczamy początkowe i końcowe (x, y) współrzędne dla ramki, gdzie przewidujemy że jest tekst
			endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
			endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
			startX = int(endX - w)
			startY = int(endY - h)

			# dodajemy współrzędne ramki i wynik prawdopodobieństwa do odpowiednich list
			rects.append((startX, startY, endX, endY))
			confidences.append(scoresData[x])

	# tłumimy nakładające się ramki
	boxes = non_max_suppression(np.array(rects), probs=confidences)

	'''
	#rysujemy ramki na obrazku, gdzie znajduje się tekst
	loop over the bounding boxes
	for (startX, startY, endX, endY) in boxes:
		startX = int(startX * rW)
		startY = int(startY * rH)
		endX = int(endX * rW)
		endY = int(endY * rH)
		cv2.rectangle(orig, (startX, startY), (endX, endY), (0, 255, 0), 2)
	'''

	# jeżeli przypuszczamy, że na obrazku nie ma tekst, to przenosimy go do kosza
	if len(boxes) != 0:
		cv2.imwrite(image_path, orig)
	else:
		if not os.path.exists(labels.BIN_FOLDER):
			os.makedirs(labels.BIN_FOLDER)
		path = '%s/%s' % (labels.BIN_FOLDER, image_path.rsplit("/", 1)[0])
		# print(path)
		os.makedirs(path, exist_ok=True)
		try:
			os.rename(image_path, '%s/%s' % (labels.BIN_FOLDER, image_path))
			os.remove(image_path)
		except FileNotFoundError:
			pass
