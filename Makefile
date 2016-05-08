
DATA_DIR=data/
MAIN_PY=Spidee.py
ICONS=`pwd`/cards.icns

all:
	py2applet --iconfile=${ICONS} ${MAIN_PY} ${DATA_DIR}

clean:
	rm -r Spidee

