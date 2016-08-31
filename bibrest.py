#!/usr/bin/env python
# Simple RESTful API to represent bibtex database
# Requires 'project' field in bibtex source
# Entries can then be filtered based on project
# Nils, SUTD, 2016

from flask import Flask, url_for, jsonify, request
import json
from pybtex.database import parse_file, parse_string

mime='application/x-bibtex'

app = Flask(__name__)
bibfile="/home/ubuntu/bibrest/bibrest.bib"

# Why does this have to be so complicated?
def entryToBibtex(entry):
    fields="author={"
    persons=[]
    for p in entry.persons['author']:
        name=str(p)[9:-2].replace("\\\\","\\")# this is so dirty
        persons.append(name) 
    fields+=" and ".join(persons)
    fields+="},\n"
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
    reverse=False
    bib_data = parse_file(bibfile)
    if request.args.get('reverse'):
        reverse=True        
    if request.method == 'GET':
        print("detected GET")
        if request.args.get('author') and request.args.get('project'):
            return api_author_project(request.args.get('author'),request.args.get('project'),reverse)
        elif request.args.get('project'):
            return api_project(request.args.get('project'),reverse)
        elif request.args.get('author'):
            return api_author(request.args.get('author'),reverse)
        else:        
            return bib_data.to_string('bibtex'), 200, {'Content-Type': mime, 'Content-Disposition': 'attachment; filename=bib.bib'}
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
    return rval, 200, {'Content-Type': mime, 'Content-Disposition': 'attachment; filename=bib.bib'}

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
# The current route is somewhat unrestful
#@app.route('/project/<projectids>')
def api_project(projectids,reverse):
    bib_data = parse_file(bibfile)
    rval=""
    rbibs=[]
    for projectid in projectids.split(','):
        for entry in bib_data.entries.values():
            if entry.fields['project'] and entry.fields['project'].upper()==projectid.upper():
                if not entry in rbibs:
                    rbibs.append(entry)
                continue
    # sort if required
    # This assumes all entries have a year field
    rbibs.sort(key=lambda x: x.fields['year'], reverse=reverse)
    # now output as bibtex
    for entry in rbibs:
        rval+=entryToBibtex(entry)        
    return rval, 200, {'Content-Type': mime, 'Content-Disposition': 'attachment; filename=bib.bib'}

# return all authors as JSON
@app.route('/authors')
def api_authors():
    bib_data = parse_file(bibfile)
    authors={}
    for entry in bib_data.entries.values():
        if 'author' in entry.fields:
            p=entry.fields['author']
            if p in authorss.keys():
                authors[p]+=1
            else:
                authors[p]=1
    rval="Available authors in database:\n"
    for p in authors.keys():
        rval+="- %s (%d)\n"%(p,authors[p])
    return rval, 200, {'Content-Type': 'text'}    

# return all entries belonging to certain author
# There might be a problem if one author's name is a substring of another author's name
# The current route is somewhat unrestful
#@app.route('/author/<authorids>')
def api_author(authorids,reverse):
    bib_data = parse_file(bibfile)
    rval=""
    rbibs=[]
    for authorid in authorids.split(','):
        for entry in bib_data.entries.values():
            if entry.fields['author'] and authorid.upper() in entry.fields['author'].upper():
                if not entry in rbibs:
                    rbibs.append(entry)
                continue
    # sort if required
    # This assumes all entries have a year field
    rbibs.sort(key=lambda x: x.fields['year'], reverse=reverse)
    # now output as bibtex
    for entry in rbibs:
        rval+=entryToBibtex(entry)        
    return rval, 200, {'Content-Type': mime, 'Content-Disposition': 'attachment; filename=bib.bib'}

# Somewhat of a dirty hack: author and project was specified
def api_author_project(authorids,projectids,reverse):
    bib_data = parse_file(bibfile)
    rval=""
    rbibs=[]
    for authorid in authorids.split(','):
        for projectid in projectids.split(','):        
            for entry in bib_data.entries.values():
                if entry.fields['author'] and (authorid.upper() in entry.fields['author'].upper()) and entry.fields['project'] and entry.fields['project'].upper()==projectid.upper():
                    title=entry.fields['title']
                    if not title in rbibs:
                        rbibs=entry
                    continue
    # sort if required
    # This assumes all entries have a year field
    rbibs.sort(key=lambda x: x.fields['year'], reverse=reverse)
    # now output as bibtex
    for entry in rbibs:
        rval+=entryToBibtex(entry)        
    return rval, 200, {'Content-Type': mime, 'Content-Disposition': 'attachment; filename=bib.bib'}


if __name__ == '__main__':
    app.run(host="0.0.0.0",port=8080,debug=True)
