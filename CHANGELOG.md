# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

- Started changelog tracking

## [0.86.1] - 2025-08-13

### Added
- feat: Add openrouter entries for new models
- feat: Add Gemini 2.5 Flash and Flash-Lite models to settings
- feat: Add settings for new OpenAI models
- feat: add missing openrouter anthropic model entries
- feat: update models.py for Claude 4.5/4.6
- feat: Add Claude 4.5/4.6 models to model-settings.yml
- feat: Add gemini-3-flash-preview model entries
- Add gpt-5.2 models

### Fixed
- fix: Update model names in test_models.py
- fix: Remove non-existent openrouter anthropic model versions
- fix: Update openrouter model version numbers to use dots
- fix: Update python version in Dockerfile site-packages permissions
- fix: exclude regular classes that end with `Error`
- fix: Add ImageFetchError to aider's exceptions list
- fix: Add ErrorEventError to aider's exceptions list
- fix: Add BadGatewayError to exceptions list

### Changed
- refactor: Update flash alias to point to gemini/gemini-flash-latest
- Update polyglot_leaderboard.yml with medium and low reasoning
- Update polyglot_leaderboard.yml

## [0.86.0] - 2025-08-09

### Added
- feat: Add reasoning_effort setting to gpt-5 models
- feat: Add EthicalAds script and ad placement
- feat: Add flash-lite model alias
- add test results for gpt-oss-120b (high) to polyglot leaderboard

### Fixed
- fix: Adjust ad placement for narrow screens

### Changed
- refactor: Remove unused ad styles from head_custom.html

## [0.85.5] - 2025-08-07

### Added
- feat: blame: Detect aider commits using co-authored-by
- feat: Add OpenAI and OpenRouter GPT-5 model settings
- feat: Add GPT-5 model family settings

### Fixed
- fix: Remove editor settings from models using gpt-5 nano weak model

## [0.85.4] - 2025-08-07

### Added
- feat: Add reasoning_effort setting support for GPT-5 models
- feat: Enforce diff edit format for GPT-5 models

### Fixed
- fix: Accurately match gpt-5 and gpt-5-2025-08-07 models

## [0.85.3] - 2025-08-07

### Added
- feat: Disable temperature for GPT-5 models

### Fixed
- fix: Adapt to new PostHog SDK capture method signature

## [0.85.2] - 2025-07-15

### Changed
- Update polyglot_leaderboard.yml

## [0.85.1] - 2025-06-30

### Added
- feat: Add Kimi K2 model data to polyglot leaderboard
- Add source for openrouter kimi-k2 information. Remove `reminder: sys`.
- Add kimi-k2 to model resources.
- feat: Add Grok-4 and Gemini Flash Lite, enhance CLI, fix model settings
- feat: Add openrouter/x-ai/grok-4 model setting
- feat: Add xai/grok-4 model settings
- Add gemini 2.5 flash lite preview 06-17

### Fixed
- fix: Display first line of commit messages in /undo output
- fix: add missing output for clear command
- fix: Remove existing model settings before adding new ones

### Changed
- Update model-metadata.json

## [0.85.0] - 2025-06-27

### Added
- feat: Display model announcements with no-arg /model command

## [0.84.0] - 2025-05-30

### Added
- feat: Enable co-authored-by by default
- feat: better place to create history file dirs (InputOutput ctr)
- add Gemini 2.5 non-preview Vertex models
- add MATLAB tags to enable repo map support
- feat: Auto-create parent directories for chat history files
- Add meta data for `openrouter/google/gemini-2.5-pro`
- Support model `openrouter/google/gemini-2.5-pro` official
- Add gemini model metadata

### Fixed
- fix: Update Co-authored-by email to aider@aider.chat
- fix: Create parent directories for history files and improve error handling
- fix: check for input_history_file none
- fix: Resolve literal paths correctly in /read-only command
- fix: Ensure pip is available before installation
- fix: Vertex AI model names use vertex_ai/ prefix
- fix: Adjust analytics repo file count condition
- fix: Remove unused mock_stdout in tests

### Changed
- refactor: Remove -n short flag from benchmark --new option
- refactor: Remove unused head variable in ChatSummary
- refactor: update HEAD regex to accept optional closing tag in search blocks When working with HTML text, the network has
- Update analytics.md
- Update gemini models in model-settings.yml

