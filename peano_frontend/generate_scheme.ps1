# Invoke-WebRequest "http://127.0.0.1:17713/api/openapi.json" -o ./scheme.json
# npx openapi-typescript ./scheme.json --output "./src/api/scheme.ts"

# java -jar .\openapi-generator-cli.jar generate -g typescript-axios -i "http://127.0.0.1:17713/api/openapi.json" -o "./src/api/scheme.ts"

npx openapi --input "http://127.0.0.1:17713/api/openapi.json" --output ./src/api --client axios  --useOptions --useUnionTypes
