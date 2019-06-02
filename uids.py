import nanoid
import nanoid_dictionary

def thread_id():
    return 'th'+nanoid.generate(nanoid_dictionary.human_alphabet, size=16)

def note_id():
    return 'no'+nanoid.generate(nanoid_dictionary.human_alphabet, size=24)
