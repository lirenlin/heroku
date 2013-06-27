import os
from flask import Flask

import hashlib
import binascii
import evernote.edam.userstore.constants as UserStoreConstants
import evernote.edam.type.ttypes as Types
from evernote.edam.notestore.ttypes import NoteFilter
from evernote.edam.notestore.ttypes import NotesMetadataResultSpec
from evernote.api.client import EvernoteClient
import weather

app = Flask(__name__)

@app.route('/')

def hello():
    auth_token = "S=s1:U=6eb51:E=146ce55b0ee:C=13f76a484f1:P=1cd:A=en-devtoken:V=2:H=5d05df82a62652c0ed8f2e544df37758"

    if auth_token == "":
        print "Please fill in your developer token"
        print "To get a developer token, visit " \
            "https://sandbox.evernote.com/api/DeveloperToken.action"
        exit(1)

    client = EvernoteClient(token=auth_token, sandbox=True)
    user_store = client.get_user_store()

    version_ok = user_store.checkVersion(
        "Evernote EDAMTest (Python)",
        UserStoreConstants.EDAM_VERSION_MAJOR,
        UserStoreConstants.EDAM_VERSION_MINOR
    )
    #print "Is my Evernote API version up to date? ", str(version_ok)
    #print ""
    if not version_ok:
        exit(1)

    note_store = client.get_note_store()

    # List all of the notebooks in the user's account
    notebooks = note_store.listNotebooks()
    nb = None
    #print "Found ", len(notebooks), " notebooks:"
    for notebook in notebooks:
        print "  * ", notebook.name
        if notebook.name == "Note":
            nb = notebook;
            break

    if not nb:
        print "Note book is not found in your account"
        exit(1)

    filter = NoteFilter()
    filter.notebookGuid = nb.guid
    filter.order = Types.NoteSortOrder.CREATED

    spec = NotesMetadataResultSpec()
    spec.includeTitle = True

    noteML = note_store.findNotesMetadata(auth_token, filter, 0, 10, spec)
    output = ""
    for note in noteML.notes:
        noteID = note.guid
        content = note_store.getNoteContent(auth_token, noteID);
        output += "%s\n"%note.title
        output += "%s\n"%content
    figure = getAndDraw()
    return output+figure

