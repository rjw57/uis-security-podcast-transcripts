RENDER_TEMPLATE:=./render-template.py

DATA_FILES=$(wildcard data/*.json)
TRANSCRIPT_FILES=$(DATA_FILES:data/%.json=transcripts/%.html)

all: $(TRANSCRIPT_FILES)
.PHONY: all
.DEFAULT: all

clean:
	rm -f $(TRANSCRIPT_FILES)

transcripts:
	mkdir $@

transcripts/%.html: data/%.json transcripts
	$(RENDER_TEMPLATE) transcript.in.html <$< >$@
