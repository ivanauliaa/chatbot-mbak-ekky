import re
import string
import json
import nltk
import mysql.connector
import math
import html2text
import types
import os
from bs4 import BeautifulSoup
from collections import Counter
from flask import Flask, jsonify, request
from flask_cors import CORS
from nltk.tokenize import word_tokenize
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory, StopWordRemover, ArrayDictionary
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

app = Flask(__name__)

app.config.from_object(__name__)

CORS(app, resources={r"/*": {'origins': "*"}})
#CORS(app, resources={r'/*':{'origins':'http://localhost:8080', "allow_headers":"Access-Control-Allow-Origin"}})

# Connection to database
mydb = mysql.connector.connect(host=os.environ['DB_HOST'],
                               port=os.environ['DB_PORT'],
                               user=os.environ['DB_USER'],
                               password=os.environ['DB_PASSWORD'],
                               database=os.environ['DB_NAME'],
                               auth_plugin='mysql_native_password',
                               )

factory = StemmerFactory()
stemmer = factory.create_stemmer()


def text_processing_akademik(text):
    text = text_prepo(text)
    text = text_mining(text)
    text = check_synonim(text)
    answer = get_answer(text)
    return answer


def text_processing_data(text, id):
    text = text_prepo(text)
    text = text_mining(text)
    text = check_synonim(text)
    answer = get_data(text, id)
    return answer


def text_prepo(text):
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = text.strip()
    return text


def text_mining(text):
    more_stopword = ['tanya', 'dong', 'mau', 'pens']
    factory = StopWordRemoverFactory()
    stopword_dictionary = factory.get_stop_words()
    data = stopword_dictionary + more_stopword
    dictionary = ArrayDictionary(data)
    stopword = StopWordRemover(dictionary)
    text = stopword.remove(text)

    text = stemmer.stem(text)

    return text


def check_synonim(text):
    text = word_tokenize(text)
    text2 = " "
    with open('dictionary.txt') as f:
        data = f.read()

    this_dict = json.loads(data)
    new_text = []
    temp = ""
    for t in text:
        isbreak = False
        for d in this_dict:
            if t in this_dict[d]:
                temp = d
                temp = word_tokenize(temp)
                for k in temp:
                    new_text.append(k)
                isbreak = True
        if (isbreak == False):
            new_text.append(t)
    text2 = text2.join(new_text)
    return (text2)


def read_keyword():
    keyword_file = open("keyword_lists.txt", "r")
    keyword_lists = []
    for line in keyword_file:
        line = line.rstrip()
        keyword_lists.append(line)
    keyword_file.close()
    return keyword_lists


def word_comp(text):
    keyword_lists = read_keyword()

    tokens = word_tokenize(text)
    keywords = []

    print("token awal : ", tokens)
    for t in tokens:
        if t in keyword_lists:
            keywords.append(t)

    print((len(keywords) / len(tokens)))
    if ((len(keywords) / len(tokens)) < 0.5):
        answer = text_mining(text)
        return answer
    else:
        print("tidak perlu text mining : ", keywords)
        answer = get_answer(keywords)
        return answer


def get_answer(text):
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM response")
    myresult = mycursor.fetchall()
    user_tk = text
    print(user_tk)
    user_tk_vector = text_to_vector(user_tk)
    max = 0
    id_save = 0
    for x in myresult:
        db_tk = x[1]
        print(db_tk)
        db_tk_vector = text_to_vector(db_tk)
        cosine_result = get_cosine(user_tk_vector, db_tk_vector)
        print(cosine_result)

        if cosine_result > max:
            max = cosine_result
            id_save = x[0]
        print("similarity: ", cosine_result)
        print("max: ", max)
        print("id: ", id_save)
    if max > 0.3:
        sql = """SELECT jawaban FROM response WHERE response_id = %s"""
        mycursor.execute(sql, (id_save,))

    else:
        sql = "SELECT jawaban FROM response WHERE keyword = 'none'"
        mycursor.execute(sql)
    myresult2 = mycursor.fetchone()
    for x in myresult2:
        answer = str(x)
    answer = html2text.html2text(answer)
    answer = answer[:answer.rfind('\n')]
    print(answer)
    return answer


def get_cosine(vec1, vec2):
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x]**2 for x in vec1.keys()])
    sum2 = sum([vec2[x]**2 for x in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator


def text_to_vector(text):
    word = re.compile(r'\w+')
    words = word.findall(text)
    return Counter(words)


def get_from_database(context, id, semester):
    mycursor = mydb.cursor()
    kelas = ''
    semester_per_kelas = ''
    text = ''

    if(semester == 0):
        text = ''
        for i in range(1, 9):
            if(i % 2 != 0):
                kelas = int((i + 1)/2)
                semester_per_kelas = 1
            else:
                kelas = int(i/2)
                semester_per_kelas = 2
            if context == 'nilai':
                text += '#Data nilai kelas ' + \
                    str(kelas) + ' semester ' + \
                    str(semester_per_kelas) + '#\n\n'
                sql = """SELECT matakuliah.KODE, matakuliah.MATAKULIAH, nilai.NH FROM nilai JOIN kuliah ON nilai.KULIAH = kuliah.NOMOR JOIN matakuliah ON kuliah.MATAKULIAH = matakuliah.NOMOR WHERE nilai.MAHASISWA = %s AND matakuliah.KELAS=%s AND matakuliah.SEMESTER = %s"""
                mycursor.execute(sql, (id, kelas, semester_per_kelas,))
                data = mycursor.fetchall()
                if data == []:
                    text += "(Data belum tersedia)\n\n"
                else:
                    for row in data:
                        for column in row:
                            if column == row[-1]:
                                text += ' : ' + column
                            else:
                                text += ' ' + column
                        if row == data[-1]:
                            text += '\n'
                        text += '\n'
            if context == 'jadwal':
                text += '#Data jadwal kelas ' + \
                    str(kelas) + ' semester ' + \
                    str(semester_per_kelas) + '#\n\n'
                sql = """SELECT matakuliah.MATAKULIAH, pegawai.NAMA, jam.JAM, ruang.RUANG FROM nilai JOIN kuliah ON nilai.KULIAH = kuliah.NOMOR JOIN matakuliah ON kuliah.MATAKULIAH = matakuliah.NOMOR JOIN jam ON kuliah.JAM = jam.NOMOR JOIN ruang ON kuliah.RUANG = ruang.NOMOR JOIN pegawai ON kuliah.DOSEN = pegawai.NOMOR WHERE nilai.MAHASISWA = %s AND matakuliah.KELAS=%s AND matakuliah.SEMESTER = %s"""
                mycursor.execute(sql, (id, kelas, semester_per_kelas,))
                data = mycursor.fetchall()
                if data == []:
                    text += "(Data belum tersedia)\n\n"
                else:
                    for row in data:
                        for column in row:
                            if column == row[0] or column == row[2]:
                                text += column + '\n'
                            elif column == row[1]:
                                text += column + ' - '
                            else:
                                text += column + '\n'
                        if row == data[-1]:
                            text += '\n'
                        text += '\n'
            if context == 'rekap presensi':
                text += '#Data rekap presensi ' + \
                    str(kelas) + ' semester ' + \
                    str(semester_per_kelas) + ' (minggu ke-)#\n\n'
                sql = """SELECT matakuliah.KODE, matakuliah.MATAKULIAH, GROUP_CONCAT(absensi_mahasiswa.MINGGU, ".", absensi_mahasiswa.STATUS ORDER BY absensi_mahasiswa.MINGGU) FROM absensi_mahasiswa JOIN kuliah ON absensi_mahasiswa.KULIAH = kuliah.NOMOR JOIN matakuliah ON kuliah.MATAKULIAH = matakuliah.NOMOR WHERE absensi_mahasiswa.MAHASISWA = %s AND matakuliah.KELAS=%s AND matakuliah.SEMESTER = %s GROUP BY absensi_mahasiswa.KULIAH"""
                mycursor.execute(sql, (id, kelas, semester_per_kelas,))
                data = mycursor.fetchall()
                print(data)
                if data == []:
                    text += "(Data belum tersedia)\n\n"
                else:
                    for row in data:
                        for column in row:
                            if column == row[-1]:
                                column = column.replace(",", " ")
                                text += ' :\n ' + column + '\n'
                            else:
                                text += ' ' + column
                        if row == data[-1]:
                            text += '\n'
                        text += '\n'
    else:
        if(semester % 2 != 0):
            kelas = int((semester + 1)/2)
            semester_per_kelas = 1
        else:
            kelas = int(semester/2)
            semester_per_kelas = 2

        if context == 'nilai':
            text = '#Data nilai kelas ' + \
                str(kelas) + ' semester ' + str(semester_per_kelas) + '#\n\n'
            sql = """SELECT matakuliah.KODE, matakuliah.MATAKULIAH, nilai.NH FROM nilai JOIN kuliah ON nilai.KULIAH = kuliah.NOMOR JOIN matakuliah ON kuliah.MATAKULIAH = matakuliah.NOMOR WHERE nilai.MAHASISWA = %s AND matakuliah.KELAS=%s AND matakuliah.SEMESTER = %s"""
            mycursor.execute(sql, (id, kelas, semester_per_kelas,))
            data = mycursor.fetchall()
            if data == []:
                text += "(Data belum tersedia)"
            else:
                for row in data:
                    for column in row:
                        if column == row[-1]:
                            text += ' : ' + column
                        else:
                            text += ' ' + column
                    text += '\n'
        if context == 'jadwal':
            text = '#Data jadwal kelas ' + \
                str(kelas) + ' semester ' + str(semester_per_kelas) + '#\n\n'
            sql = """SELECT matakuliah.MATAKULIAH, pegawai.NAMA, jam.JAM, ruang.RUANG FROM nilai JOIN kuliah ON nilai.KULIAH = kuliah.NOMOR JOIN matakuliah ON kuliah.MATAKULIAH = matakuliah.NOMOR JOIN jam ON kuliah.JAM = jam.NOMOR JOIN ruang ON kuliah.RUANG = ruang.NOMOR JOIN pegawai ON kuliah.DOSEN = pegawai.NOMOR WHERE nilai.MAHASISWA = %s AND matakuliah.KELAS=%s AND matakuliah.SEMESTER = %s"""
            mycursor.execute(sql, (id, kelas, semester_per_kelas,))
            data = mycursor.fetchall()
            if data == []:
                text += "(Data belum tersedia)"
            else:
                for row in data:
                    for column in row:
                        if column == row[0] or column == row[2]:
                            text += column + '\n'
                        elif column == row[1]:
                            text += column + ' - '
                        else:
                            text += column + '\n'
                    text += '\n'
        if context == 'rekap presensi':
            text = '#Data rekap presensi ' + \
                str(kelas) + ' semester ' + \
                str(semester_per_kelas) + ' (minggu ke-)#\n\n'
            sql = """SELECT matakuliah.KODE, matakuliah.MATAKULIAH, GROUP_CONCAT(absensi_mahasiswa.MINGGU, ".", absensi_mahasiswa.STATUS ORDER BY absensi_mahasiswa.MINGGU) FROM absensi_mahasiswa JOIN kuliah ON absensi_mahasiswa.KULIAH = kuliah.NOMOR JOIN matakuliah ON kuliah.MATAKULIAH = matakuliah.NOMOR WHERE absensi_mahasiswa.MAHASISWA = %s AND matakuliah.KELAS=%s AND matakuliah.SEMESTER = %s GROUP BY absensi_mahasiswa.KULIAH"""
            mycursor.execute(sql, (id, kelas, semester_per_kelas,))
            data = mycursor.fetchall()
            print(data)
            if data == []:
                text += "(Data belum tersedia)"
            else:
                for row in data:
                    for column in row:
                        if column == row[-1]:
                            column = column.replace(",", " ")
                            text += ' :\n ' + column + '\n'
                        else:
                            text += ' ' + column
                    text += '\n'
    return text


def get_data(text, id):
    mycursor = mydb.cursor()
    print("hasil filtering", text)
    semester = [int(s) for s in text.split() if s.isdigit()]

    with open('keyword.txt') as f:
        data = f.read()

    this_keyword = json.loads(data)
    user_tk = text
    user_tk_vector = text_to_vector(user_tk)
    max = 0
    key = ''
    for x in this_keyword:
        db_tk = x
        db_tk_vector = text_to_vector(db_tk)
        cosine_result = get_cosine(user_tk_vector, db_tk_vector)

        if cosine_result > max:
            max = cosine_result
            key = x
        print("similarity: ", cosine_result)
        print("max: ", max)
        print("key: ", key)
    if (key == ''):
        sql = "SELECT jawaban FROM response WHERE keyword = 'none'"
        mycursor.execute(sql)
        myresult2 = mycursor.fetchone()
        for x in myresult2:
            answer = str(x)
        answer = html2text.html2text(answer)
        answer = answer[:answer.rfind('\n')]
        answer_to_json = {
            "response": answer
        }
        return answer_to_json
    if "semua semester" in text:
        answer = get_from_database(key, id, 0)
        answer_to_json = {
            "response": answer
        }
    elif semester == []:
        #sql = """SELECT jawaban FROM response WHERE response_id = %s"""
        #mycursor.execute(sql, (id_save,))
        answer = this_keyword[key]
        answer_to_json = {
            "response": answer,
            "context": key
        }

    else:
        answer = get_from_database(key, id, semester[0])
        answer_to_json = {
            "response": answer
        }
    #myresult2 = mycursor.fetchone()
    # for x in myresult2 :
        #answer = str(x)
    #answer = html2text.html2text(answer)
    #answer = answer[:answer.rfind('\n')]
    print(answer)

    return answer_to_json


def login(name, nrp):
    mycursor = mydb.cursor()
    sql = """SELECT NOMOR FROM mahasiswa WHERE NAMA = %s AND NRP = %s"""
    mycursor.execute(sql, (name, nrp,))
    data = mycursor.fetchone()
    if(data != None):
        data_json = {
            "nama": name,
            "nomor": data[0]
        }
    else:
        data_json = {
            "nama": '',
            "nomor": ''
        }
    return data_json

# Routing


@app.route('/greeting', methods=['GET'])
def greetings():
    return("Halo selamat datang di chatbot PENS! \nAjukan pertanyaan seputar peraturan akademik dan data mahasiswa (Jadwal, Nilai, Rekap presensi)")


@app.route('/question-type', methods=['GET'])
def question_type():
    return("Pilih jenis pertanyaan yang ingin anda ajukan : \n1. Peraturan akademik\n2. Data mahasiswa\n*(ketikkan \"ganti\" jika anda ingin mengganti jenis pertanyaan)")


def question_type():
    return("Pilih jenis pertanyaan yang ingin anda ajukan : \n1. Peraturan akademik\n2. Data mahasiswa")


@app.route('/response-akademik', methods=['POST'])
def response_akademik():
    post_data = request.get_json()
    message = post_data.get('content')
    answer = text_processing_akademik(message)
    return(answer)


@app.route('/login', methods=['POST'])
def auth_login():
    post_data = request.get_json()
    name = post_data.get('name')
    nrp = post_data.get('nrp')
    answer = login(name, nrp)
    return(answer)


@app.route('/response-data', methods=['POST'])
def response_data():
    post_data = request.get_json()
    id = post_data.get('id')
    message = post_data.get('content')
    answer = text_processing_data(message, id)
    return(answer)


if __name__ == "__main__":
    app.run(debug=True)
