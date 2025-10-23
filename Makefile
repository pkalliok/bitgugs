PREFIX=/usr/local
BASE=$(DESTDIR)$(PREFIX)
EXEDIR=$(BASE)/bin
MANDIR=$(BASE)/share/man/man1
DOCDIR=$(BASE)/share/doc/bitgugs
SCRIPTS=bitgugs.py
MANPAGES=$(SCRIPTS:.py=.1)
DOCS=README.md $(wildcard docs/*) LICENSE-CC0-1.0.md
INSTALL=install -c

.PHONY: all install
all: bitgugs.1

stamps/build-deps: Makefile
	sudo apt install python3-argparse-manpage
	touch $@

bitgugs.1: bitgugs.py stamps/build-deps
	argparse-manpage --pyfile $< --function get_parser \
		--author 'Panu Kalliokoski' --project-name bitgugs \
		--author-email panu.kalliokoski@sange.fi \
		--url https://github.com/pkalliok/bitgugs > $@

install: all
	$(INSTALL) -m 755 -d $(EXEDIR) $(MANDIR) $(DOCDIR)
	$(INSTALL) -m 755 bitgugs.py $(EXEDIR)/bitgugs
	$(INSTALL) -m 644 $(MANPAGES) $(MANDIR)
	$(INSTALL) -m 644 $(DOCS) $(DOCDIR)

