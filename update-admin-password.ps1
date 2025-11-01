# Update admin password to admin123
Write-Host "Updating admin password to 'admin123'..." -ForegroundColor Cyan

$body = @{
    password = 'admin123'
} | ConvertTo-Json

# First login with current password
$loginBody = @{username='admin@example.com'; password='changethis'}
try {
    $loginResp = Invoke-RestMethod -Uri 'http://localhost:8000/api/auth/login' -Method POST -Body $loginBody -ContentType 'application/x-www-form-urlencoded'
    $token = $loginResp.access_token
    
    # Update password
    $headers = @{
        Authorization="Bearer $token"
        'Content-Type'='application/json'
    }
    $updateResp = Invoke-RestMethod -Uri 'http://localhost:8000/api/users/me' -Method PUT -Body $body -Headers $headers
    
    Write-Host "✓ Password updated successfully!" -ForegroundColor Green
    Write-Host "  New password: admin123" -ForegroundColor Yellow
} catch {
    Write-Host "✗ Error: $($_.Exception.Message)" -ForegroundColor Red
}
