from core import app
from model import Note,NoteType
from flask import render_template, redirect, abort

import sqlalchemy.sql.functions as funcs


@app.route('/')
def note_index():
    # get all notes out of the index
    notes = Note.query.filter(Note.child_count == 0).order_by(Note.created.desc()).all()
    return render_template(
        'note_index.html',
        notes=notes
    )

@app.route('/viewthread/<thread_id>')
def view_thread(thread_id):
    # Display a thread. 
    # We want all the items in the thread, but we want to make sure that they are compressed
    # down a bit.
    # We're going to walk through each item and compare the "downstream" items.
    #
    # Where a branch occurs (A note has more than one child), we get the thread continuation that has
    # The longest as the "next" item to continue. This means that small off-shoots are compressed
    # but still visible if that note's parent is the focal point of the view.
    # 
    # When there is more than one child, we should continue towards the newest tip.
    thread_root = Note.query.filter_by(thread_id = thread_id, parent_id = None).one_or_none()
    if(thread_root is None):
        abort(404)

    # This will contain a list of note IDs which should have their contents displayed as compressed.
    summarized_ids = []
    # this will contain the list of Notes which should be displayed in their totality.
    thread_items = []

    current_note = thread_root
    while(current_note is not None):
        thread_items.append(current_note)
        if(current_note.child_count == 0):
            current_note = None
        elif(current_note.child_count == 1):
            current_note = current_note.children[0]
        else:
            # We want to get the newest 'tip' of the thread.
            # To do this, we're going to get the newest tip from each child
            # and find the newest child.
            max_tip = lambda note: max(note.thread_tips, key=lambda tip:tip.created)
            children_sorted = sorted(current_note.children, key=lambda t:max_tip(t).created, reverse=True)
            current_note = children_sorted[0]
            # Get the ids for the notes that should be summarized
            summarized_ids += list(map(lambda k: k.id, children_sorted[1::]))

    return render_template('note_index.html', notes=thread_items)


def note_add():
    # We're going to be handed some content! Yay!

    pass