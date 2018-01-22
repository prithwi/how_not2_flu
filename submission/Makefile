latex:
	latex main_plos
	bibtex main_plos
	latex main_plos
	bibtex main_plos
	latex main_plos
	latex main_plos

clean:
	rm -f *.log *.synctex.gz *.fdb*
	rm -f *.aux *.bbl *.blg *.dvi
	rm -f *.ps  *.out *.bak

all: clean latex
	dvipdf main_plos

final:clean
	latex main_plos
	latex main_plos
	dvipdf main_plos

