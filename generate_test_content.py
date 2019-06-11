import random
import lorem
import model

import datetime

current_time = datetime.datetime.utcnow()

def get_time():
  global current_time
  delta = datetime.timedelta(seconds=random.randint(1,50))
  current_time += delta
  return current_time

# We're going to generate some data
notes = []

for n in range(0,250):
  note = model.Note(type=model.NoteType.Text)
  if(n < 10 or random.randint(0,100)>80):
    note.parent = None
  else:
    note.parent = random.choice(notes)
  note.data = {'value':lorem.paragraph()}
  note.created = get_time()
  notes.append(note)
  model.db.session.add(note)

model.db.session.commit()