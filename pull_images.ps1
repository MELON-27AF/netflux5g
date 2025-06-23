# Script to pull required Docker images for NetFlux5G
# This ensures all necessary images are available before running the simulation

Write-Host "Pulling required Docker images for NetFlux5G..." -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Yellow

# List of required images
$images = @(
    "gradiant/open5gs:2.7.5",    # Open5GS 5G Core components
    "gradiant/ueransim:3.2.7",   # UERANSIM gNB and UE components
    "mongo:4.4"                  # MongoDB for Open5GS
)

# Pull each image
foreach ($image in $images) {
    Write-Host "Pulling $image..." -ForegroundColor Cyan
    try {
        docker pull $image
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Successfully pulled $image" -ForegroundColor Green
        } else {
            Write-Host "✗ Failed to pull $image" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "✗ Error pulling $image" -ForegroundColor Red
    }
    Write-Host
}

Write-Host "============================================================" -ForegroundColor Yellow
Write-Host "Image pulling completed!" -ForegroundColor Green

# List pulled images
Write-Host
Write-Host "Available NetFlux5G images:" -ForegroundColor Cyan
foreach ($image in $images) {
    try {
        $result = docker images $image --format "table {{.Repository}}:{{.Tag}}`t{{.Size}}" | Select-Object -Skip 1
        if ($result) {
            Write-Host "✓ $result" -ForegroundColor Green
        } else {
            Write-Host "✗ $image - Not available" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "✗ $image - Not available" -ForegroundColor Red
    }
}

Write-Host
Write-Host "Now you can run NetFlux5G:" -ForegroundColor Yellow
Write-Host "  .\netflux5g.sh" -ForegroundColor White
