param(
    [string]$Url = "https://www2.mmm.ucar.edu/wrf/src/wps_files/geog_low_res_mandatory.tar.gz",
    [string]$ArchivePath = "data/downloads/geog_low_res_mandatory.tar.gz",
    [string]$TargetDir = "data/geog"
)

$ErrorActionPreference = "Stop"

New-Item -ItemType Directory -Force -Path (Split-Path $ArchivePath) | Out-Null
New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null

Write-Host "Checking WPS geog package:"
Write-Host $Url
$head = Invoke-WebRequest -Uri $Url -Method Head -UseBasicParsing
$length = [int64]$head.Headers["Content-Length"]
Write-Host ("Remote size: {0:n0} bytes" -f $length)

if (-not (Test-Path $ArchivePath)) {
    Write-Host "Downloading geog archive to $ArchivePath"
    Invoke-WebRequest -Uri $Url -OutFile $ArchivePath -UseBasicParsing
} else {
    Write-Host "Archive already exists: $ArchivePath"
}

$hasExtractedData = Get-ChildItem -Path $TargetDir -Directory -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $hasExtractedData) {
    Write-Host "Extracting archive to $TargetDir"
    tar -xzf $ArchivePath -C $TargetDir
} else {
    Write-Host "Geog directory already contains data: $TargetDir"
}

Write-Host "Geog preparation complete."
