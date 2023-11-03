all: badge_2023.html
THEME=moon

%.html: %.md
	# pandoc -t revealjs -V theme:${THEME} -s $^ -o $@
	pandoc -t revealjs -S -i -s $^ -o $@
#	pandoc -t dzslides  -s $^ -o $@


%.pdf: %.md 
	pandoc -t beamer -V theme:metropolis -s $^ -o $@

clean:
	rm *.pdf *.html

