RENDER=../../tools/booklet/render.py
PRELUDE=../../tools/booklet/prelude.tex

.PHONY : all
all : hiw-schedule.html hiw-schedule.pdf

.PHONY : clean
clean :
	rm -f hiw-schedule.html hiw-schedule.pdf

%.html : %.txt
	$(RENDER) html $< >$@

%.pdf : %.txt
	($(RENDER) latex $<; echo '\end{document}') | pdflatex -jobname $* $(PRELUDE)
	rm -f $*.aux $*.log
