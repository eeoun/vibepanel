# Translation workflow. Requires GNU gettext and `xtr` (cargo install xtr).
#
#   make        update vibepanel.pot, merge it into every <lang>.po and compile
#   make pot    extract strings marked with tr!() into vibepanel.pot
#   make po     merge vibepanel.pot into every <lang>.po
#   make mo     compile <lang>.po into locale/<lang>/vibepanel.mo (embedded in the binary)
#   make check  verify catalogs are in sync (used by CI)
#
# New language: msginit -i vibepanel.pot -l <lang> -o <lang>.po, then add the
# catalog to CATALOGS in src/i18n.rs.

SHELL := /bin/bash
DOMAIN := vibepanel
POT := $(DOMAIN).pot

PO_FILES := $(wildcard *.po)
MO_FILES := $(patsubst %.po,locale/%/$(DOMAIN).mo,$(PO_FILES))

.PHONY: all pot po mo

# pot -> po -> mo must run in order.
.NOTPARALLEL:

all: po mo

pot:
	xtr ../src/main.rs --package-name $(DOMAIN) --add-location file -o $(POT)

po: pot
	@for file in $(PO_FILES); do \
		msgmerge --update --backup=none --no-wrap "$$file" $(POT); \
	done

mo: $(MO_FILES)

locale/%/$(DOMAIN).mo: %.po
	mkdir -p $(@D)
	msgfmt --check -o $@ $<

# CI check: catalogs match the source and embedded .mo files are current.
# Untranslated/fuzzy entries only warn; they show in English at runtime.
.PHONY: check
check:
	@set -e; status=0; \
	norm() { msgcat --no-location --no-wrap --sort-output "$$1" | grep -v '^"POT-Creation-Date:'; }; \
	xtr ../src/main.rs --package-name $(DOMAIN) --add-location file -o $(POT).new; \
	if ! diff <(norm $(POT)) <(norm $(POT).new); then \
		echo "::error file=crates/vibepanel/po/$(POT)::out of date, run 'make -C crates/vibepanel/po'"; status=1; fi; \
	rm -f $(POT).new; \
	for po in $(PO_FILES); do \
		lang=$${po%.po}; f=crates/vibepanel/po/$$po; \
		msgfmt --check -o /dev/null "$$po" || status=1; \
		if ! diff <(norm "$$po") <(msgmerge -q --no-wrap "$$po" $(POT) -o - | norm /dev/stdin); then \
			echo "::error file=$$f::not merged with $(POT), run 'make -C crates/vibepanel/po'"; status=1; fi; \
		if ! diff <(msgfmt -o - "$$po" | msgunfmt) <(msgunfmt locale/$$lang/$(DOMAIN).mo); then \
			echo "::error file=$$f::locale/$$lang/$(DOMAIN).mo is stale, run 'make -C crates/vibepanel/po'"; status=1; fi; \
		n=$$(msgattrib --untranslated --no-obsolete "$$po" | grep -c '^msgid ' || true); \
		[ "$$n" -le 1 ] || echo "::warning file=$$f::$$((n - 1)) untranslated entries"; \
		n=$$(msgattrib --only-fuzzy --no-obsolete "$$po" | grep -c '^msgid ' || true); \
		[ "$$n" -eq 0 ] || echo "::warning file=$$f::$$n fuzzy entries"; \
	done; \
	exit $$status
