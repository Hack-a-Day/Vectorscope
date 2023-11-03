all: supercon_menu interactive

supercon_menu: supercon_menu.py
	mpremote cp $^ :

menudemo: menudemo.py
	mpremote cp $^ :

vectorscope: vectorscope.py
	mpremote cp $^ :

lissajous: lissajous.py
	mpremote cp $^ :

libs: 
	mpremote cp *.py :

bitflip: bit_flip_pio.py
	mpremote reset 
	sleep 1
	mpremote run $^

interactive: RUNME
	mpremote resume

RUNME: vectoros.py
	mpremote reset
	sleep 1
	mpremote run $^


%.png: %.dot
	dot  -T png -o $@ < $^
	sxiv $@

.PHONY: RUNME
