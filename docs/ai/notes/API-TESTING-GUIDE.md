# API Testing Guide with HTTPie

## Prerequisites
1. Install HTTPie: `pip install httpie` or `brew install httpie`
2. Create a Personal Access Token via the UI (Settings page)
3. Copy the token when displayed (it won't be shown again)

## Testing with Personal Access Tokens

### 1. Test GET Request (Read Items)

```bash
# Basic GET request
http GET http://localhost:8000/api/items "Authorization: Bearer YOUR_TOKEN_HERE"

# With query parameters
http GET http://localhost:8000/api/items skip==0 limit==10 "Authorization: Bearer YOUR_TOKEN_HERE"
```

Expected response:
```json
[
  {
    "id": 1,
    "title": "Sample Item",
    "description": "Description here",
    "owner_id": 1
  }
]
```

### 2. Test POST Request (Create Item)

```bash
http POST http://localhost:8000/api/items \
  "Authorization: Bearer YOUR_TOKEN_HERE" \
  title="My New Item" \
  description="Created via HTTPie with PAT"
```

Expected response:
```json
{
  "id": 2,
  "title": "My New Item",
  "description": "Created via HTTPie with PAT",
  "owner_id": 1
}
```

### 3. Test PUT Request (Update Item)

```bash
http PUT http://localhost:8000/api/items/2 \
  "Authorization: Bearer YOUR_TOKEN_HERE" \
  title="Updated Title" \
  description="Updated description"
```

Expected response:
```json
{
  "id": 2,
  "title": "Updated Title",
  "description": "Updated description",
  "owner_id": 1
}
```

### 4. Test DELETE Request

```bash
http DELETE http://localhost:8000/api/items/2 \
  "Authorization: Bearer YOUR_TOKEN_HERE"
```

Expected response:
```json
{
  "id": 2,
  "title": "Updated Title",
  "description": "Updated description",
  "owner_id": 1
}
```

## Testing Current User Endpoint

```bash
# Get current user info
http GET http://localhost:8000/api/users/me \
  "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Testing Token Management

```bash
# List your tokens
http GET http://localhost:8000/api/users/me/tokens \
  "Authorization: Bearer YOUR_TOKEN_HERE"

# Create a new token
http POST http://localhost:8000/api/users/me/tokens \
  "Authorization: Bearer YOUR_TOKEN_HERE" \
  name="CI/CD Token" \
  scopes="read,write" \
  expires_in_days:=30

# Revoke a token
http DELETE http://localhost:8000/api/users/me/tokens/3 \
  "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Common Error Responses

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```
**Solution**: Check that your token is valid and not expired

### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```
**Solution**: Check that your token has the required scopes (e.g., 'write' for POST/PUT)

### 404 Not Found
```json
{
  "detail": "Item not found"
}
```
**Solution**: Verify the resource ID exists

## Tips

1. **Save your token**: Store it in an environment variable for convenience
   ```bash
   export API_TOKEN="your_token_here"
   http GET http://localhost:8000/api/items "Authorization: Bearer $API_TOKEN"
   ```

2. **Use HTTPie sessions** for repeated requests:
   ```bash
   http --session=api http://localhost:8000/api/items "Authorization: Bearer YOUR_TOKEN"
   # Subsequent requests in the same session will reuse the token
   http --session=api http://localhost:8000/api/items
   ```

3. **Pretty print JSON**: HTTPie does this by default, but you can control it:
   ```bash
   http --pretty=all GET http://localhost:8000/api/items "Authorization: Bearer YOUR_TOKEN"
   ```

4. **Verbose output** for debugging:
   ```bash
   http -v GET http://localhost:8000/api/items "Authorization: Bearer YOUR_TOKEN"
   ```

## Scope Requirements

| Endpoint | Method | Required Scope |
|----------|--------|----------------|
| `/api/items` | GET | `read` |
| `/api/items` | POST | `write` |
| `/api/items/{id}` | GET | `read` |
| `/api/items/{id}` | PUT | `write` |
| `/api/items/{id}` | DELETE | `write` |
| `/api/users/me` | GET | `read` |
| `/api/users/me/tokens` | GET | `read` |
| `/api/users/me/tokens` | POST | `write` |
| `/api/users/me/tokens/{id}` | DELETE | `write` |
