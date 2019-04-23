#!/usr/local/bin/powershell

$username = "test"
$password = "pass"
$server = "ddns.test.org"

$ip_address = Get-NetIPAddress | Where-Object {($_.IPAddress -like "10.19.*")} | Select-Object -Property IPAddress

$postdata = @{subdomain=$server;type="A";content=$ip_address.IPAddress}


$pair = "$($username):$($password)"

$encodedCreds = [System.Convert]::ToBase64String([System.Text.Encoding]::ASCII.GetBytes($pair))

$basicAuthValue = "Basic $encodedCreds"

$Headers = @{
    Authorization = $basicAuthValue
}

$resp = Invoke-RestMethod -Uri "$loginurl"  -Method Post -Body $postdata -Headers $Headers

If($resp.success -eq $true){
    Write-Host "DDNS success"
} 
else {
    Write-Host "DDNS failer"
    Write-Host $resp.message
}

