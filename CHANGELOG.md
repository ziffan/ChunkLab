# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-04-18

### Added
- Initial Open Source release of ChunkLab.
- Browser-based sandbox for text chunking experimentation.
- Support for multiple tokenization strategies (Tiktoken, Character, Words).
- Regex-based splitting patterns with live preview.
- Metadata extraction (titles, headers, keywords).
- Mock integration for OpenAI, Gemini, and Anthropic.
- Responsive React-based frontend with TailwindCSS.
- FastAPI backend for efficient text processing.

### Fixed
- Improved regex robustness for multi-line headers.
- Optimized token counting for large text files.

### Changed
- Refactored chunking service for better extensibility.
- Updated documentation for Open Source compliance.
