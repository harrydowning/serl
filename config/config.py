r"""
name: gantt

rules:
  text: |
    [a-zA-Z0-9 ]*
  title: (text) \n
  <->: \ *
  milestone: |
    (?| \* (text) | () (?: text))
  -----: ---+ \n
  bar: (<-> =*)
  row: |
    (text) \| bar milestone \n
  rows: |
    (?: row)+
  titles: |
    (?: <-> \| (text))+ \n

tokens:
  gantt: |
    title
    -----
    titles
    rows
"""

doc = lambda content: r'''
\documentclass{article}
\usepackage[utf8]{inputenc}
\usepackage{pgfgantt}

\begin{document}

%s

\end{document}
''' % content

content = ''

gantt = lambda width, content: r'''
\noindent\resizebox{\textwidth}{!}{
\begin{ganttchart}[
vgrid, 
hgrid, 
x unit = 1cm, 
y unit chart= 1.1cm, 
bar/.append style={fill = lightgray}]{1}{%s}

%s

\end{ganttchart}
}''' % (width, content)

gantt_title = lambda title, width: r'\gantttitle{%s}{%s}' % (title, width)
gantt_bar = lambda label, start, end: r'\ganttbar{%s}{%s}{%s}' % (label, start, end)
gantt_milestone = lambda text, pos: r'\ganttmilestone[inline]{%s}{%s}' % (text, pos)

def gantt(captures):
    _, title, titles, labels, bars, milestones = captures
    width = len(max(bars, key=len))
    width += len(titles) - (width % len(titles))
    t_width = width // len(titles)

    rows = len(labels)

    _content = gantt_title(title[0].strip(), width) + r'\\' + '\n'

    for title in titles:
        _content += gantt_title(title.strip(), t_width)

    _content += r'\\' + '\n'

    for row in range(rows):
        label = labels[row].strip()
        start = bars[row].find('=')
        end = len(bars[row])
        m = milestones[row]

        if start != -1:
            _content += gantt_bar(label, start + 1, end)

        if m != '':
            _content += gantt_milestone(m[1:].strip(), end)
        
        if row == rows - 1:
            _content += '\n'
        else:
            _content += r'\\' + '\n'

    content += gantt(width, _content)

def default():
    pass

def result():
    document = doc(content)
    with open(f'{src.split(".")[0]}.tex', 'w') as file:
      file.write(document)

print(__doc__)