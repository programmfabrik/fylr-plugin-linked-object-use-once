PLUGIN_NAME = fylr-plugin-linked-object-use-once
BUILD_DIR = build

ZIP_NAME ?= "${PLUGIN_NAME}.zip"

COFFEE_FILES = src/webfrontend/fylr-plugin-linked-object-use-once.coffee

include easydb-library/tools/base-plugins.make

all: build ## build

build: clean code buildinfojson ## build all (creates build folder)
	mkdir -p $(BUILD_DIR)/$(PLUGIN_NAME)
	cp manifest.master.yml $(BUILD_DIR)/$(PLUGIN_NAME)/manifest.yml
	cp -r src/server $(BUILD_DIR)/$(PLUGIN_NAME)
	cp -r l10n $(BUILD_DIR)/$(PLUGIN_NAME)
	cp build-info.json $(BUILD_DIR)/$(PLUGIN_NAME)
	mv $(BUILD_DIR)/webfrontend $(BUILD_DIR)/$(PLUGIN_NAME)

code: $(JS)

clean: ## clean build files
	rm -f build-info.json
	rm -f src/server/*.pyc
	rm -rf src/server/__pycache__/
	rm -f src/server/fylr_lib_plugin_python3/*.pyc
	rm -rf src/server/fylr_lib_plugin_python3/__pycache__/
	rm -rf $(BUILD_DIR)

zip: build ## build zip file for publishing
	cd $(BUILD_DIR) && zip ${ZIP_NAME} -r $(PLUGIN_NAME) -x *.git*

