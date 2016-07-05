#!/usr/bin/env python
# Simple RESTful API to represent bibtex database
# Adds 'Project' field to bibtex source
# Entries can then be filtered based on project
# Nils, SUTD, 2016
from flask import Flask, url_for, jsonify
import json
from pybtex.database import parse_file

# technically correct, but hard to debug 
#mime='application/x-bibtex'
mime='text'

app = Flask(__name__)


def entryToBibtex(entry):
    fields=""
    for f in entry.fields.keys():
        if f.lower() is not 'project':
            fields+="%s={%s},\n"%(f,entry.fields[f])
    if len(fields)>5:
        fields=fields[:-2]
    return "@%s{%s,\n%s}\n"%(entry.type,entry.key,fields)
    

@app.route('/')
def api_root():
    return 'Welcome'

# return all entries in our bibliography in bibtex string
@app.route('/bibs')
def api_articles():
    bib_data = parse_file('../research/bibs/tippenhauer.bib')    
    return bib_data.to_string('bibtex'), 200, {'Content-Type': mime}

# return specific entry in bibtex string
@app.route('/bib/<articleid>')
def api_article(articleid):
    bib_data = parse_file('../research/bibs/tippenhauer.bib')
    return entryToBibtex(bib_data.entries[articleid]), 200, {'Content-Type': mime}

# return all project keys as JSON
@app.route('/projects')
def api_projects():
    bib_data = parse_file('../research/bibs/test.bib')
    projects={}
    for entry in bib_data.entries.values():
        if 'project' in entry.fields:
            p=entry.fields['project'].upper()
            if p in projects.keys():
                projects[p]+=1
            else:
                projects[p]=1
    rval="Available projects in database:\n"
    for p in projects.keys():
        rval+="- %s (%d)\n"%(p,projects[p])
    return rval, 200, {'Content-Type': 'text'}
    

# return all entries belonging to certain project
@app.route('/project/<projectid>')
def api_project(projectid):
    bib_data = parse_file('../research/bibs/test.bib')
    rval=""
    for entry in bib_data.entries.values():
        if entry.fields['project'] and entry.fields['project'].upper()==projectid.upper():
           rval+=entryToBibtex(entry)
    return rval, 200, {'Content-Type': mime}

if __name__ == '__main__':
    app.run(debug=True)
