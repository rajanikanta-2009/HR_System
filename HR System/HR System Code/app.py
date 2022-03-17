import flask
from flask import Flask,request,render_template,jsonify,Response
import os
from werkzeug.utils import secure_filename
import nltk
import numpy as np
from fuzzywuzzy import fuzz
import spacy
import fitz
import glob
import mammoth
from nltk import pos_tag
from nltk.tree import Tree
from nltk.chunk import conlltags2tree
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import re
import pandas as pd

nltk.download('averaged_perceptron_tagger')
print(os.getcwd())
UPLOAD_FOLDER = os.getcwd() + "/static/resume/"
CSV_FOLDER = os.getcwd() + "/static/csv/"
JD_FOLDER = os.getcwd() + "/static/JD/"
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['JD_FOLDER'] = JD_FOLDER
app.config['CSV_FOLDER'] = CSV_FOLDER
app.config["ALLOWED_EXTENSIONS"] = ["PDF", "DOC", "DOCX", "PNG"]
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/val',methods=['GET','POST'])
def val():
    return render_template("upload_jd.html")

@app.route("/formaction", methods=['GET','POST'])

def action1():

    if request.method == 'POST':

        f = request.files['file']

        filename = JD_FOLDER + f.filename

        m = f.filename

        ext = filename.rsplit(".", 1)[1]
        if ext.upper() in app.config["ALLOWED_EXTENSIONS"]:

            f.save(os.path.join(app.config['JD_FOLDER'], secure_filename(f.filename)))



    return render_template('jd_disp.html',file_name=m)

@app.route('/val1',methods=['GET','POST'])
def val1():
    return render_template("upload_resume.html")

@app.route("/formaction1", methods=['GET', 'POST'])
def action():

    files_list = []
    files_name = []
    image_files = []
    j = 0
    if request.method == 'POST':
        # f = request.files['file']
        uploaded_files = flask.request.files.getlist("file[]")
        print(uploaded_files)
        for i in uploaded_files:

            filename = UPLOAD_FOLDER + i.filename
            files_name.append(i.filename)
            # m=i.filename
            print(i.filename)
            ext = filename.rsplit(".", 1)[1]
            if ext.upper() in app.config["ALLOWED_EXTENSIONS"]:
                i.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(i.filename)))
            if ext == "docx":
                j = j + 1
                f = open(filename, 'rb')
                b = open(UPLOAD_FOLDER + str(j) + '.html', 'wb')
                document = mammoth.convert_to_html(f)
                b.write(document.value.encode('utf8'))
                f.close()
                b.close()
                filename = str(j) + '.html'
                files_list.append(filename)
            if ext == "png":
                image_files.append(i.filename)
            else:
                files_list.append(i.filename)
    return render_template('resume_disp.html', uploaded_files=files_list, names=files_name, image_files=image_files)


def create_ner(df):
    years_dict = {}
    x1 = df['Tokens'].values.tolist()
    pos_tags = [pos for token, pos in pos_tag(x1)]
    conlltags = [(token, pos, tg) for token, pos, tg in zip(df['Tokens'].values.tolist(),
                                                            pos_tags, df['Tags'].values.tolist())]
    ne_tree = conlltags2tree(conlltags)
    original_text = []
    for subtree in ne_tree:
        # skipping 'O' tags
        if type(subtree) == Tree:
            original_label = subtree.label()
            original_string = " ".join([token for token, pos in subtree.leaves()])
            original_text.append((original_string, original_label))

    test = [t[::-1] for t in original_text]
    test
    years_dict = {}

    for line in test:
        if line[0] in years_dict:
            # append the new number to the existing array at this slot
            years_dict[line[0]].append(line[1])
        else:
            # create a new array in this slot
            years_dict[line[0]] = [line[1]]

    return (years_dict)


def get_name(d):
    name = d.get('per')
    name = ''.join(name)
    return name


def get_edu(d):
    education = d.get('edu')
    education = ','.join(education)
    return education


def get_email(d):
    email = d.get('email')
    email = ''.join(email)
    return email


def get_phone(d):
    phone = d.get('phone')
    phone = ''.join(phone)
    return phone


def get_skill(d):
    skill = d.get('skill')
    skill = ', '.join(skill)
    return skill


def get_experience(d):
    try:
        exp = d.get('exp')
        exp = ''.join(exp)
        pattern = "\d{2}[/]\d{2}[/]\d{4}"
        d = re.findall(pattern, exp)
        DATE = [datetime.strptime(x, '%m/%d/%Y') for x in d]
        sorted_list = sorted(DATE, reverse=True)
        difference_in_years = relativedelta(sorted_list[0], sorted_list[-1]).years
        return difference_in_years
    except:
        print(exp)
        difference_in_years = 0
        return difference_in_years


def get_age(d):
    age = d.get('DOB')
    for i in age:
        x, y, z = i.split("-")
    age = date(int(z), int(y), int(x))
    today = date.today()
    d = today.year - age.year - ((today.month, today.day) < (age.month, age.day))
    return d

@app.route('/rank',methods=['GET','POST'])

def rank():
    column_names = ["Name", "Age", "Email", "Phone", "Education", "skill", "Experience"]
    df1 = pd.DataFrame(columns=column_names)
    files = glob.glob(UPLOAD_FOLDER + '*')
    for f in files:
        if f.split('.')[-1] in ['html']:
            os.remove(f)
    for file in os.listdir(UPLOAD_FOLDER):

        if "Arathy" in file:
            df = pd.read_csv(CSV_FOLDER + 'Arathy - Arathy.csv')
            d = create_ner(df)

        if "Karla_Lewis" in file:
            df = pd.read_csv(CSV_FOLDER + 'Karla_Lewis - Karla_Lewis.csv')
            d = create_ner(df)

        if 'Archana' in file:
            df = pd.read_csv(CSV_FOLDER + 'Archana - Archana.csv')
            d = create_ner(df)

        if 'Sreerag' in file:
            df = pd.read_csv(CSV_FOLDER + 'Sreerag - Sreerag.csv')
            d = create_ner(df)

        if 'manoj' in file:
            df = pd.read_csv(CSV_FOLDER + 'manoj - manoj.csv')
            d = create_ner(df)

        name = get_name(d)
        education = get_edu(d)
        email = get_email(d)
        phone = get_phone(d)
        skill = get_skill(d)
        experience = get_experience(d)
        age = get_age(d)

        data = [[name, age, email, phone, education, skill, experience]]
        df2 = pd.DataFrame(data, columns=column_names)
        df1 = df1.append(df2)
        df1.reset_index(inplace=True, drop=True)
    print(df1)
    files = glob.glob(UPLOAD_FOLDER + '*')
    for f in files:
        if f.split('.')[-1] in ['pdf', 'doc', 'docx', 'html']:
            os.remove(f)

    #################################### JOB DESCRIPTION #####################################3
    df1['skill'] = df1['skill'].str.lower()
    terms1 = {'Primary_skill':['hadoop','hive','spark','zookeeper','r','pig','hbase','aws','casandra'],

          "Secondary_skill":['java','c','c++','mySql','html','ruby','python'],
          
          "Education":['B.TECH', 'MCA','Statistic'],
          
          "Experience": 2
        }
    #     ################################### FINDING SCORE ###############################################
    df = df1
    da_score = []
    bd_score = []
    ed_score = []
    ex_score = []
    primary = 0.6
    secondary = 0.2
    education = 0.1
    experience = 0.1

    for i in range(len(df)):
        for area in terms1.keys():
            if area == 'Primary_skill':
                da = 0
                for word in terms1[area]:
                    if fuzz.partial_ratio(word, df['skill'].iloc[i]) > 93:
                        da += 1
                da1 = primary * (da / (len(terms1[area])))
                da_score.append(da1)
                print()

            if area == 'Secondary_skill':
                bd = 0
                for word in terms1[area]:
                    if fuzz.partial_ratio(word, df['skill'].iloc[i]) > 93:
                        bd += 1
                bd1 = secondary * (bd / (len(terms1[area])))
                bd_score.append(bd1)

            if area == "Education":
                ed = 0
                for word in terms1[area]:
                    if fuzz.partial_ratio(word, df['Education'].iloc[i]) > 93:
                        ed += 1
                ed1 = education * (ed / (len(terms1[area])))
                ed_score.append(ed1)

            if area == "Experience":
                ex = 0
                if df['Experience'].iloc[i] >= 2:
                    ex = experience
                else:
                    ex = 0
                ex_score.append(ex)

    res_list = [da_score[i] + bd_score[i] + ed_score[i] + ex_score[i] for i in range(len(da_score))]
    df['Score'] = res_list
    df2 = df.sort_values(by=['Score'], ascending=False)
    Rank = []
    for i in range(1, len(df) + 1):
        Rank.append("Rank" + str(i))
    df2["Rank"] = Rank
    df2['skill'] = df2['skill'].str.upper()
  
    print(df2)

    df2.reset_index(drop=True, inplace=True)

    files = glob.glob(UPLOAD_FOLDER + '*')
    for f in files:
        if f.split('.')[-1] in ['pdf', 'doc', 'docx', 'html']:
            os.remove(f)

    return render_template('rank.html', df=df2.to_html(classes='table table-striped'))
def resume_model(fname):
    
    nlp_model = spacy.load('nlp_ner_model')
    
    doc = fitz.open(fname)
    
    text = ""
    
    for page in doc:
        
        text = text + str(page.getText())
        
    tx = " ".join(text.split('\n'))
    
    ########### Load Model ##########
    
    doc1 = nlp_model(tx)
    
    for ent in doc1.ents:
        
        print(f'{ent.label_.upper():{30}}- {ent.text}')
    

fname = 'model/Alice Clark CV.pdf'
                                    
#resume_model(fname)
if __name__ == '__main__':
    app.run(debug=True)