PLUGIN_NAME = fylr-plugin-linked-object-use-once
BUILD_DIR = build

ZIP_NAME ?= "${PLUGIN_NAME}.zip"

COFFEE_FILES = src/webfrontend/$(PLUGIN_NAME).coffee
JS = src/webfrontend/$(PLUGIN_NAME).js

L10N_FILES = l10n/l10n.csv
L10N_GOOGLE_KEY = 1Z3UPJ6XqLBp-P8SUf-ewq4osNJ3iZWKJB83tc6Wrfn0
L10N_GOOGLE_GID = 1350551470
GOOGLE_URL = https://docs.google.com/spreadsheets/d/$(L10N_GOOGLE_KEY)/export?format=csv&gid=

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

all: build ## build

google-csv: ## get loca CSV from google
	curl --silent -L -o - "$(GOOGLE_URL)$(L10N_GOOGLE_GID)" | tr -d "\r" > $(L10N_FILES)

build: clean code buildinfojson ## build all (creates build folder)
	mkdir -p $(BUILD_DIR)/$(PLUGIN_NAME)/webfrontend
	cp manifest.master.yml $(BUILD_DIR)/$(PLUGIN_NAME)/manifest.yml
	cp -r src/server $(BUILD_DIR)/$(PLUGIN_NAME)
	cp $(JS) $(BUILD_DIR)/$(PLUGIN_NAME)/webfrontend
	cp -r l10n $(BUILD_DIR)/$(PLUGIN_NAME)
	cp build-info.json $(BUILD_DIR)/$(PLUGIN_NAME)

code: $(JS) ## build Coffeescript code

${JS}: $(subst .coffee,.coffee.js,${COFFEE_FILES})
	mkdir -p $(dir $@)
	cat $^ > $@

%.coffee.js: %.coffee
	coffee -b -p --compile "$^" > "$@" || ( rm -f "$@" ; false )

clean: ## clean build files
	rm -f build-info.json
	rm -f src/server/*.pyc
	rm -rf src/server/__pycache__/
	rm -f src/webfrontend/*.js
	rm -f src/server/fylr_lib_plugin_python3/*.pyc
	rm -rf src/server/fylr_lib_plugin_python3/__pycache__/
	rm -rf $(BUILD_DIR)

zip: build ## build zip file for publishing
	cd $(BUILD_DIR) && zip ${ZIP_NAME} -r $(PLUGIN_NAME) -x *.git*

buildinfojson:
	repo=`git remote get-url origin | sed -e 's/\.git$$//' -e 's#.*[/\\]##'` ;\
	rev=`git show --no-patch --format=%H` ;\
	lastchanged=`git show --no-patch --format=%ad --date=format:%Y-%m-%dT%T%z` ;\
	builddate=`date +"%Y-%m-%dT%T%z"` ;\
	echo '{' > build-info.json ;\
	echo '  "repository": "'$$repo'",' >> build-info.json ;\
	echo '  "rev": "'$$rev'",' >> build-info.json ;\
	echo '  "lastchanged": "'$$lastchanged'",' >> build-info.json ;\
	echo '  "builddate": "'$$builddate'"' >> build-info.json ;\
	echo '}' >> build-info.json
