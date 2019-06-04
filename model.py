from core import app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.event import listens_for
from sqlalchemy_utils import JSONType
from sqlalchemy.ext.hybrid import hybrid_property
import enum
import datetime

import uids

db = SQLAlchemy(app)

class NoteType(enum.Enum):
    Unknown = 0
    Text = 1
    URL = 2
    File = 3


class Note(db.Model):
    """
    The core data structure in the model. 
    """
    id = db.Column(db.String(32), primary_key=True, default=uids.note_id)
    type = db.Column(db.Enum(NoteType), default=NoteType.Unknown, nullable=False)
    data = db.Column(JSONType, nullable=False, default={"data":None})
    parent_id = db.Column(db.String(32), db.ForeignKey('note.id'))
    children = db.relationship('Note', backref=db.backref('parent', remote_side=id),
    cascade='all, delete-orphan')
    thread_id = db.Column(db.String(32), default=uids.thread_id, nullable=False)


    @property
    def thread_size(self):
        return self.query.filter(__class__.thread_id == self.thread_id).count()
    
    
    @property
    def is_root(self):
        """True if there is no parent to this item, False otherwise"""
        return self.parent_id is None
    
    @property
    def thread_up(self):
        """The thread, from this point to the root of the thread."""
        if self.parent_id is None:
            return [self]
        else:
            cur_note = self
            while(cur_note != None):
                yield cur_note
                cur_note = cur_note.parent

    @hybrid_property
    def child_count(self):
        return self.children.count()
    

    @child_count.expression
    def child_count(cls):
        from sqlalchemy import func, select
        from sqlalchemy.orm import aliased
        child_alias = aliased(__class__)
        return (
            select([func.count(child_alias.id)]).
            where(child_alias.parent_id == cls.id).
            label('child_count')
        )
    
    @hybrid_property
    def deep_child_count(self):
        return sum([child.child_count for child in self.children])

    @property
    def thread_root(self):
        return self.parent == None

    created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    def append(self, child):
        child.parent = self
        child.thread_id = self.thread_id

    def __repr__(self):
        return f'<Note({self.id}) of type {self.type.name} in thread {self.thread_id}>'


    #
    # There are some things that need to be cleared up here
    # Specifically, the CSS and front-end properties of the note itself. 
    # This lets use be lazy and put some of the actual logic here in the model
    # rather than in the view. 
    #

    @property
    def fe_template(self):
        return (f'note/card_body/{self.type.name.lower()}.html', 'note/card_body/fallback.html')
    
    
    @property
    def fe_preview_template(self):
        return (f'note/preview/{self.type.name.lower()}.html', 'note/preview/fallback.html')
    
    @property
    def ui_icon(self):
        return 'mdi-note'
    
    @property
    def ui_label(self):
        return 'Note'

@listens_for(Note, 'before_insert')
@listens_for(Note, 'before_update')
def note_set_thread(mapper, connection, note):
    # check that the note has a parent
    if(note.parent is not None):
        # force it to have the same thread ID as its parent
        note.thread_id = note.parent.thread_id
        # and make sure each of its children have the same thread ID
        for child in note.children:
            if(child.thread_id != note.thread_id):                
                child.thread_id = note.thread_id
                # make sure that the child is added to the update because it has been modified
                # outside of the standard model.
                # This will also cascade any changes to the database. 
                db.session.add(child)

