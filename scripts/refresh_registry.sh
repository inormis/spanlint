#!/bin/sh
# Copies the GenAI attribute registry out of semantic-conventions-genai at a
# pinned commit. Bump the commit, run this, and look at the diff.
set -eu
commit=e6658f14c9d9ea0760825f029cb82e7673f48fab
curl -fsSL "https://raw.githubusercontent.com/open-telemetry/semantic-conventions-genai/$commit/model/gen-ai/registry.yaml" \
  -o "$(dirname "$0")/../src/spanlint/data/gen_ai.yaml"
