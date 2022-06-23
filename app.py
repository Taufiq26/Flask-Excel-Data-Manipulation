from flask import Flask, render_template, request, redirect
import pandas as pd
from openpyxl import load_workbook
	
app = Flask("Excel_Web-App")
	
@app.route("/", methods=["GET", "POST"])
def home():
    filename="data/DataSetWisataLembang.xlsx"
    dataset = pd.read_excel(filename)

    # Data tempat wisata yang ada di file excel
    places = dataset['Wisata']
    places = list(dict.fromkeys(places))

    # Nilai bawaan
    curr_index = request.args.get('idx', default = 0, type = int)
    curr_place = request.args.get('place', default = places[0], type = str)

    selected_place = curr_place
    if request.method == "POST" and "place" in request.form:
        selected_place = request.form.get('place')

    # Filter komentar sesuai tempat wisata
    comments = []
    total_positive = 0
    total_negative = 0
    total_n_a = 0
    for idx, ds in enumerate(dataset['Wisata']):
        if ds == selected_place:
            comments.append({
                'origin_index': idx,
                'account': dataset['Akun'][idx],
                'comment': dataset['Komentar'][idx],
                'response': dataset['Respon'][idx]
            })

            if dataset['Respon'][idx] == 'Positif':
                total_positive += 1
            elif dataset['Respon'][idx] == 'Negatif':
                total_negative += 1
            else:
                total_n_a += 1


    if curr_index < 0: 
        # kondisi jika menekan tombol sebelumnya pada data pertama
        curr_index = len(comments) - 1

    if curr_index > len(comments) - 1: 
        # kondisi jika menekan tombol selanjutnya pada data terakhir
        curr_index = 0

    return render_template(
        "home.html", 
        places=places, 
        selected_place=selected_place, 
        comments=comments,
        total_positive=round(total_positive / len(comments) * 100, 2),
        total_negative=round(total_negative / len(comments) * 100, 2),
        total_n_a=round(total_n_a / len(comments) * 100, 2),
        curr_index=curr_index
    )


@app.route("/change_response", methods=["GET"])
def changeResponse():
    curr_index = request.args.get('idx', default = 0, type = int)
    curr_place = request.args.get('place', default = "", type = str)
    origin_index = request.args.get('origin_index', default = -1, type = int)
    response = request.args.get('response', default = "", type = str)

    if origin_index > -1:
        df = pd.DataFrame({
                'Respon': [response]
            })

        filename="data/DataSetWisataLembang.xlsx"
        writer = pd.ExcelWriter(filename, engine='openpyxl', mode='a')

        # buka workbook yang sudah ada
        writer.book = load_workbook(filename)
        # copy sheets yang ada
        writer.sheets = dict((ws.title, ws) for ws in writer.book.worksheets)
        # timpa sheet yang lama dengan yang baru
        df.to_excel(writer, index=False, header=False, startcol=3, startrow=origin_index+1)

        writer.close()

    query = "?idx="+str(curr_index)+"&place="+curr_place
    return redirect("/"+query, code=302)