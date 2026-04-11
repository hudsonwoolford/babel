

T_PATH = "input/Transcription.txt"
F_PATH = "output/transcription.tex"
SPEAKERS = ["Me", "Client"]

transcript = ""
with open(T_PATH, encoding='utf-8') as f:
    transcript = f.read().strip()

lines = transcript.split("\n\n")

with open(F_PATH, mode='w', encoding='utf-8') as f:
    f.write("")

with open(F_PATH, mode='a', encoding='utf-8') as f:
    f.write(r"""
\documentclass[12pt]{article}

\begin{document}
            
{\centering \Huge{Client interview}}

\setlength{\parindent}{0pt}
\setlength{\parskip}{8pt}
""")
    

    for i in range(len(lines)):
        f.write("\\textbf{" + SPEAKERS[i%len(SPEAKERS)] + "}:\n" + lines[i] + "\n\n")
    
    f.write(r"\end{document}")


