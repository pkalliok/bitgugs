
stamps/build-deps: Makefile
	sudo apt install python3-argparse-manpage
	touch $@

bitgugs.1: bitgugs.py stamps/build-deps
	argparse-manpage --pyfile $< --function get_parser \
		--author 'Panu Kalliokoski' --project-name bitgugs \
		--author-email panu.kalliokoski@sange.fi \
		--url https://github.com/pkalliok/bitgugs > $@
