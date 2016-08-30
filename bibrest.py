#!/usr/bin/env python
# Simple RESTful API to represent bibtex database
# Adds 'Project' field to bibtex source
# Entries can then be filtered based on project
# Nils, SUTD, 2016

from flask import Flask, url_for, jsonify, request
import json
from pybtex.database import parse_file, parse_string

# technically correct, but hard to debug 
#mime='application/x-bibtex'
mime='text'

app = Flask(__name__)
bibfile="bibrest.bib"

def entryToBibtex(entry):
    fields=""
    for f in entry.fields.keys():
        if f.lower()!='project':
            fields+="%s={%s},\n"%(f,entry.fields[f])
    if len(fields)>5:
        fields=fields[:-2]
    return "@%s{%s,\n%s}\n"%(entry.type,entry.key,fields)
    

@app.route('/')
def api_root():
    return 'Welcome to BibRest. This server is intended as API for machines.'

# return all entries in our bibliography in bibtex string
@app.route('/bibs', methods = ['GET', 'POST'])
def api_articles():
    bib_data = parse_file(bibfile)    
    if request.method == 'GET':    
        return bib_data.to_string('bibtex'), 200, {'Content-Type': mime}
    elif request.method == 'POST':
        try:
            data=parse_string(request.data,'bibtex')
            #data.to_file(bibfile)
            for e in data.entries:
                bib_data.entries[e]=data.entries[e]
            bib_data.to_file('foo.bib')
            return "%s\n"%(bib_data.to_string('bibtex'))
        except Exception, e:
            return "Bad Request: Error while parsing entry", 400
    else:
        return "HTTP method not supported", 405

# return specific entry in bibtex string
@app.route('/bib/<articleids>')
def api_article(articleids):
    bib_data = parse_file(bibfile)
    rval=""
    for articleid in articleids.split(','):
        rval+=entryToBibtex(bib_data.entries[articleid])
    return rval, 200, {'Content-Type': mime}

# return all project keys as JSON
@app.route('/projects')
def api_projects():
    bib_data = parse_file(bibfile)
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
# There might be a problem if one projects's name is a substring of another project name
@app.route('/project/<projectids>')
def api_project(projectids):
    bib_data = parse_file(bibfile)
    rval=""
    for projectid in projectids.split(','):
        for entry in bib_data.entries.values():
            if entry.fields['project'] and entry.fields['project'].upper()==projectid.upper():
                rval+=entryToBibtex(entry)
    return rval, 200, {'Content-Type': mime}

# return all authors as JSON
@app.route('/authors')
def api_authors():
    bib_data = parse_file(bibfile)
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
    

# return all entries belonging to certain author
# There might be a problem if one author's name is a substring of another author's name
@app.route('/author/<authorids>')
def api_author(authorids):
    bib_data = parse_file(bibfile)
    rval=""
    for authorid in authorids.split(','):
        for entry in bib_data.entries.values():
            if entry.fields['author'] and authorid.upper() in entry.fields['author'].upper():
                rval+=entryToBibtex(entry)
    return rval, 200, {'Content-Type': mime}


if __name__ == '__main__':
    app.run(debug=True)
