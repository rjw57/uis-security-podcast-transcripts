RENDER_TEMPLATE:=./render-template.py

DATA_FILES=$(wildcard data/*.json)
TRANSCRIPT_FILES=$(DATA_FILES:data/%.json=transcripts/%.html)

all: html
.PHONY: all
.DEFAULT: all

html: $(TRANSCRIPT_FILES)
.PHONY: html

clean:
	rm -f $(TRANSCRIPT_FILES)

transcripts:
	mkdir $@

transcripts/%.html: data/%.json transcripts
	$(RENDER_TEMPLATE) transcript.in.html <$< >$@
