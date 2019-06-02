from core import app
from model import Note,NoteType
from flask import render_template

import sqlalchemy.sql.functions as funcs


@app.route('/')
def note_index():
    # get all notes out of the index
    notes = Note.query.order_by(Note.created.desc()).all()
    return render_template(
        'note_index.html',
        notes=notes
    )