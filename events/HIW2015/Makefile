HIW.pdf: HIW.tex
	 pdflatex HIW.tex

HIW.tex: HIW.md Makefile
	pandoc -s HIW.md -f markdown+pipe_tables -t beamer -o HIW.tex

