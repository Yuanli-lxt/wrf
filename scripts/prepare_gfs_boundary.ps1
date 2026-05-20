param(
    [string]$Date = "20241001",
    [string]$Cycle = "00",
    [string]$Resolution = "1p00",
    [string]$TargetRoot = "data/raw_boundary"
)

$ErrorActionPreference = "Stop"

$ForecastHours = 0..72 | Where-Object { $_ % 3 -eq 0 }
$TargetDir = Join-Path $TargetRoot "gfs.$Date.$Cycle.$Resolution"
New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null

foreach ($hour in $ForecastHours) {
    $forecast = "{0:d3}" -f $hour
    $fileName = "gfs.t${Cycle}z.pgrb2.${Resolution}.f$forecast"
    $url = "https://noaa-gfs-bdp-pds.s3.amazonaws.com/gfs.$Date/$Cycle/atmos/$fileName"
    $target = Join-Path $TargetDir $fileName

    Write-Host "Checking $fileName"
    $head = Invoke-WebRequest -Uri $url -Method Head -UseBasicParsing
    $length = [int64]$head.Headers["Content-Length"]

    if ((Test-Path $target) -and ((Get-Item $target).Length -eq $length)) {
        Write-Host ("Already downloaded: {0} ({1:n0} bytes)" -f $fileName, $length)
        continue
    }

    Write-Host ("Downloading {0} ({1:n0} bytes)" -f $fileName, $length)
    Invoke-WebRequest -Uri $url -OutFile $target -UseBasicParsing
}

Write-Host "GFS boundary preparation complete: $TargetDir"
