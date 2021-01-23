# pentatonic.py - create guitar pentatonic diagrams.
#
# Copyright (C) 2021 Alex Ellwein

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from pyx import canvas, color, deco, document, path, style, text


class Pentatonic:
    fret_width = 2
    fret_height = 1
    dot_rad = 0.1
    note_rad = 0.3
    frets = 16
    tuning = ('E', 'A', 'D', 'G', 'B', 'E')
    tones = ('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B')
    tones2 = ('C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B')
    dotted = (3, 5, 7, 9, 15, 17, 19, 21)
    double_dotted = (12, 24)

    def __init__(self, x=0, y=0, ptype='Am'):
        self.x = x
        self.y = y
        self.ptype = self._parse(ptype)
        self.fretboard = self._fretboard()
        self.penta = self._penta()
        # print(self.penta)

    def render(self, c, intervals=False):
        c.stroke(self.fretboard, [style.linewidth.Thick])
        # self._dots(c)
        self._frets_legend(c)
        self._penta_dots(c, intervals)

    def _fretboard(self):
        p = path.path()
        for i in range(0, self.frets):
            p.extend(self._fret(self.x + i*self.fret_width, self.y))
        return p

    def _fret(self, x, y):
        p = path.path(
            path.moveto(x, y),
            path.lineto(x, y+5*self.fret_height),
            path.moveto(x+self.fret_width, y),
            path.lineto(x+self.fret_width, y+5*self.fret_height),
        )
        for i in range(0, 6):
            p.append(path.moveto(x, y+i*self.fret_height))
            p.append(path.lineto(x+self.fret_width, y+i*self.fret_height))
        return p

    def _frets_legend(self, c):
        for i in range(1, self.frets + 1):
            if i in self.dotted:
                c.text(
                    self.x + (i - 1)*self.fret_width +
                    float(self.fret_width/2),
                    self.y + 5.5 * self.fret_height,
                    str(i)
                )
            if i in self.double_dotted:
                c.text(
                    self.x + (i - 1)*self.fret_width +
                    float(self.fret_width/2),
                    self.y + 5.5 * self.fret_height,
                    str(i),
                    [color.rgb.blue]
                )

    def _dots(self, c):
        for i in range(1, self.frets + 1):
            if i in self.dotted:
                c.fill(
                    path.circle(self.x + (i - 1)*self.fret_width + float(self.fret_width/2),
                                self.y + 2.5 * self.fret_height, self.dot_rad)
                )
            elif i in self.double_dotted:
                c.fill(path.circle(self.x + (i-1) * self.fret_width +
                                   float(self.fret_width/2), self.y + 1.5 * self.fret_height, self.dot_rad))
                c.fill(path.circle(self.x + (i-1)*self.fret_width +
                                   float(self.fret_width/2), self.y + 3.5 * self.fret_height, self.dot_rad))

    def _parse(self, ptype):
        if not ptype:
            raise AttributeError('May not be empty')
        minors = ptype.count('m')
        if minors > 1 or (minors == 1 and not ptype.endswith('m')):
            raise AttributeError(
                'Minor type must be only once at last position')
        minor = minors == 1
        tone = ptype[:-1] if minor else ptype
        if tone in self.tones:
            note = self.tones.index(tone)
        elif tone in self.tones2:
            note = self.tones2.index(tone)
        else:
            raise AttributeError(
                f'Tone must be one of: {set(*self.tones, *self.tones2)}')
        return dict(tone=tone, note=note, minor=minor)

    def _interval(self, base, pos):
        idx = (base + pos) % 12
        return dict(tone=self.tones[idx], note=idx)

    def _penta(self):
        # pentatonic means we get 1,2,3,5,6 from major root
        # or 1,m3,4,5,m7 from minor root
        if 'minor' in self.ptype and self.ptype['minor']:
            return (
                self.ptype,
                self._interval(self.ptype['note'], 3),  # minor 3rd
                self._interval(self.ptype['note'], 5),  # 4th
                self._interval(self.ptype['note'], 7),  # 5th
                self._interval(self.ptype['note'], 10),  # minor 7th
            )
        else:
            return (
                self.ptype,
                self._interval(self.ptype['note'], 2),  # major 2th
                self._interval(self.ptype['note'], 4),  # major 3rd
                self._interval(self.ptype['note'], 7),   # fifth
                self._interval(self.ptype['note'], 9),  # major 6th
            )

    def _penta_dots(self, c, intervals=False):
        penta_notes = tuple([i['note'] for i in self.penta])

        def ival_by_idx(idx, minor):
            return ('6', '1', '2', '3', '5')[idx] if minor else ('1', '2', '3', '5', '6')[idx]

        for fret in range(0, self.frets + 1):
            for string in range(0, 6):
                note = self._interval(
                    self.tones.index(self.tuning[string]), fret)
                if note['note'] in penta_notes:
                    idx = penta_notes.index(note['note'])
                    fret_x = self.x if fret == 0 else (
                        fret - 1) * self.fret_width + float(self.fret_width/2)
                    if idx != 0:
                        styles = [style.linewidth.Thick, deco.filled(
                            [color.rgb.black])] if not intervals else [style.linewidth.Thick, deco.filled([color.rgb.white])]
                        c.stroke(path.circle(fret_x, self.y + string *
                                             self.fret_height, self.note_rad), styles)
                        if intervals:
                            c.text(fret_x - self.dot_rad*1.2, self.y + string *
                                   self.fret_height - self.dot_rad, ival_by_idx(idx, self.ptype['minor']))

                    else:
                        # root note
                        styles = [style.linewidth.Thick, deco.filled(
                            [color.rgb.black])] if not intervals else [style.linewidth.Thick, deco.filled([color.rgb.white])]

                        c.stroke(path.circle(fret_x, self.y + string * self.fret_height,
                                             self.note_rad), [style.linewidth.Thick, deco.filled([color.rgb.red])])
                        if intervals:
                            c.text(fret_x - self.dot_rad*1.2, self.y + string *
                                   self.fret_height - self.dot_rad, ival_by_idx(idx, self.ptype['minor']), [color.rgb.white])


def main():
    A4_lsc = document.paperformat(
        document.paperformat.A4.height, document.paperformat.A4.width)

    text.set(text.UnicodeEngine, fontname="cmss12", size=12)

    pages = []
    for i in (
        ('C', 'Am', 'C#', 'A#m'),
        ('D', 'Bm', 'D#', 'Cm'),
        ('E', 'C#m', 'F', 'Dm'),
        ('F#', 'D#m', 'G', 'Em'),
        ('G#', 'Fm', 'A', 'F#m'),
        ('A#', 'Gm', 'B', 'G#m')
    ):
        c = canvas.canvas()
        c.text(0, 32, f'{i[0]} Pentatonic Scale')
        Pentatonic(0, 26, i[0]).render(c, intervals=True)

        c.text(0, 24, f'{i[1]} Pentatonic Scale')
        Pentatonic(0, 18, i[1]).render(c, intervals=True)

        c.text(0, 16, f'{i[2]} Pentatonic Scale')
        Pentatonic(0, 10, i[2]).render(c, intervals=True)

        c.text(0, 8, f'{i[3]} Pentatonic Scale')
        Pentatonic(0, 2, i[3]).render(c, intervals=True)

        page = document.page(c, paperformat=A4_lsc, fittosize=1, margin=2)
        pages.append(page)

    doc = document.document(pages=pages)
    doc.writePDFfile("pentatonic")


if __name__ == "__main__":
    main()
