$TENANT_ID = "00000000-0000-0000-0000-000000000001"

Write-Host "================ 1. Healthcheck ================"
curl.exe -s http://localhost:8000/api/v1/health
Write-Host "`n"

Write-Host "================ 2. Contexto de Tenant ================"
curl.exe -s -H "X-Tenant-ID: $TENANT_ID" http://localhost:8000/api/v1/debug/tenant-context
Write-Host "`n"

Write-Host "================ 3. Crear cuenta contable ================"
$code = "1110" + (Get-Random -Minimum 100 -Maximum 999)
$accFile = "$env:TEMP\acc.json"
Set-Content -Path $accFile -Value "{`"code`": `"$code`", `"name`": `"Cuenta de prueba`", `"account_type`": `"asset`"}"
curl.exe -s -X POST http://localhost:8000/api/v1/accounting/accounts -H "Content-Type: application/json" -H "X-Tenant-ID: $TENANT_ID" -d "@$accFile"
Write-Host "`n"

Write-Host "================ 4. Listar cuentas contables ================"
curl.exe -s -H "X-Tenant-ID: $TENANT_ID" "http://localhost:8000/api/v1/accounting/accounts?page=1&page_size=2"
Write-Host "`n"

Write-Host "================ 5. Crear archivo y subir documento ================"
$tempFile = "$env:TEMP\boleta.txt"
Set-Content -Path $tempFile -Value "boleta de prueba"
$docJson = curl.exe -s -X POST http://localhost:8000/api/v1/documents -H "X-Tenant-ID: $TENANT_ID" -F "file=@$tempFile"
Write-Host $docJson
$docObj = $docJson | ConvertFrom-Json
$DOCUMENT_ID = $docObj.id
Write-Host "Document ID: $DOCUMENT_ID`n"

Write-Host "================ 6. Crear gasto vinculado al documento ================"
$expenseFile = "$env:TEMP\exp.json"
$expJsonContent = @"
{
  "expense_date": "2026-09-27",
  "amount": "1500.00",
  "currency": "CLP",
  "document_id": "$DOCUMENT_ID",
  "description": "Gasto de prueba",
  "merchant": "Proveedor demo"
}
"@
Set-Content -Path $expenseFile -Value $expJsonContent
curl.exe -s -X POST http://localhost:8000/api/v1/expenses -H "Content-Type: application/json" -H "X-Tenant-ID: $TENANT_ID" -d "@$expenseFile"
Write-Host "`n"

Write-Host "================ 7. Crear DTE borrador ================"
$randomFolio = Get-Random -Minimum 10000 -Maximum 99999
$dteFile = "$env:TEMP\dte.json"
$dteJsonContent = @"
{
  "dte_type": "33",
  "folio": $randomFolio,
  "issue_date": "2026-09-27",
  "currency": "CLP",
  "recipient_rut": "76000000-9",
  "recipient_name": "Cliente Demo",
  "total": "11900.00"
}
"@
Set-Content -Path $dteFile -Value $dteJsonContent
$dteJson = curl.exe -s -X POST http://localhost:8000/api/v1/invoicing/dte -H "Content-Type: application/json" -H "X-Tenant-ID: $TENANT_ID" -d "@$dteFile"
Write-Host $dteJson
$dteObj = $dteJson | ConvertFrom-Json
$DTE_ID = $dteObj.id
Write-Host "DTE ID: $DTE_ID`n"

Write-Host "================ 8. Emitir DTE vía Stub SII ================"
curl.exe -s -X POST "http://localhost:8000/api/v1/invoicing/dte/$DTE_ID/issue" -H "X-Tenant-ID: $TENANT_ID"
Write-Host "`n"
