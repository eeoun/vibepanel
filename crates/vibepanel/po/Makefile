DOMAIN := vibepanel
POT := $(DOMAIN).pot
LOCALE_DIR := locale-dist

# Collect Rust source files recursively.
RS_FILES := $(shell find ../src -type f -name '*.rs')

PO_FILES := $(wildcard *.po)
MO_FILES := $(patsubst %.po,$(LOCALE_DIR)/%/LC_MESSAGES/$(DOMAIN).mo,$(PO_FILES))

.PHONY: all pot po mo clean

all: pot po mo

# Extract translatable strings from Rust source.
pot:
	xgettext \
                --package-name=$(DOMAIN) \
		--language=Rust \
		--keyword=gettext \
		--from-code=UTF-8 \
		--output=$(POT) \
		$(RS_FILES)

# Merge the latest POT into all PO files.
po: pot
	@for file in $(PO_FILES); do \
		msgmerge --update --backup=none "$$file" $(POT); \
	done

# Compile all PO files into MO files.
mo: $(MO_FILES)

$(LOCALE_DIR)/%/LC_MESSAGES/$(DOMAIN).mo: %.po
	mkdir -p $(@D)
	msgfmt --check --check-format -o $@ $<

clean:
	rm -rf $(LOCALE_DIR)
