"""Speaker notes, Labs 1-4: remove the "New word: … Say it with me: …" lines (lecturer, 24/10/2026: the new word is on
the slide in the callout; the script does not need it). Only the notes change, never the slide. Safe to run again."""
import re
from pptx import Presentation

HCM = '/Users/mac/Tra/SE9_ElecCircuitLab/HCM'
LINE = re.compile(r'^\s*New word[s]?:.*$', re.M)


def run():
    for n in (1, 2, 3, 4):
        path = f'{HCM}/Lab{n}/HCM Electronic Circuit Lab {n}.pptx'
        p = Presentation(path); k = 0
        for s in p.slides:
            if not s.has_notes_slide:
                continue
            tf = s.notes_slide.notes_text_frame; old = tf.text
            new = re.sub(r'\n{2,}', '\n', LINE.sub('', old)).strip()
            if new != old.strip():
                tf.text = new; k += 1
        if k:
            p.save(path)
        print(f'Lab {n}: New word removed from {k} notes')


if __name__ == '__main__':
    run()
