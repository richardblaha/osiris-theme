# ============================================================================
# OSIRIS themes — top-level Makefile
# Thin wrapper over scripts/build.sh + packaging/. See `make help`.
# ============================================================================
SHELL      := /usr/bin/env bash
VERSION    := $(shell cat VERSION 2>/dev/null || echo 0.1.0)
BUILD_DIR  := build
DIST_DIR   := dist
BUILD      := scripts/build.sh

.DEFAULT_GOAL := help
.PHONY: help all tokens vscode gtk gnome plasma desktop grub wallpapers pages \
        deb rpm dist install-local clean distclean lint

help: ## Show this help
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | \
	  awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

all: tokens vscode desktop grub wallpapers pages ## Build every artifact into build/

tokens: ## Verify palette drift (assets/tokens.json vs themes/docs)
	@$(BUILD) tokens

vscode: ## Build the .vsix (build/vscode/, dist/)
	@$(BUILD) vscode

gtk: ## Assemble GTK 3/4 themes (build/themes/)
	@$(BUILD) gtk

gnome: ## Render GNOME Shell themes (build/themes/)
	@$(BUILD) gnome

plasma: ## Assemble KDE Plasma / Qt / Kvantum / Aurorae (build/plasma/)
	@$(BUILD) plasma

desktop: gtk gnome plasma ## All Linux desktop themes

grub: ## Build the GRUB2 theme (build/grub/)
	@$(BUILD) grub

wallpapers: ## Rasterise wallpapers + GNOME/KDE bundles (build/wallpapers/)
	@$(BUILD) wallpapers

pages: ## Stage the docs/preview site for GitHub Pages (build/pages/)
	@$(BUILD) pages

lint: tokens ## Alias for `make tokens`

deb: desktop grub wallpapers ## Build all .deb packages into dist/
	@packaging/debian/build-debs.sh

rpm: desktop grub wallpapers ## Build all .rpm packages into dist/
	@packaging/rpm/build-rpms.sh

dist: vscode deb rpm ## Everything that ships in a GitHub Release -> dist/
	@ls -la $(DIST_DIR)

install-local: desktop wallpapers ## Build + install themes into $$HOME (no root)
	@scripts/install-local.sh desktop --dark

clean: ## Remove build/
	@rm -rf $(BUILD_DIR)

distclean: clean ## Remove build/ and dist/
	@rm -rf $(DIST_DIR)
