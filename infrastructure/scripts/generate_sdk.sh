#!/bin/bash
set -euo pipefail

# Generate OpenAPI spec statically from the FastAPI app
echo "Generating OpenAPI spec..."
python -c "
import json
from dialectica_api.main import app
spec = app.openapi()
with open('openapi.json', 'w') as f:
    json.dump(spec, f, indent=2)
print('OpenAPI spec written to openapi.json')
"

# Generate TypeScript types using openapi-typescript (lightweight alternative)
echo "Generating TypeScript types..."
npx openapi-typescript openapi.json -o packages/sdk-typescript/src/generated/api-types.ts

echo "TypeScript SDK generated in packages/sdk-typescript/"
