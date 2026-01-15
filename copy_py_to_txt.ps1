# PowerShell Script: Copy .py files to .py.txt recursively
# Save this as copy_py_to_txt.ps1 and run in PowerShell

# Get all .py files recursively from current directory
$pyFiles = Get-ChildItem -Path . -Recurse -Filter "*.py" -File -ErrorAction SilentlyContinue

if ($pyFiles.Count -eq 0) {
    Write-Host "No .py files found." -ForegroundColor Yellow
    Pause
    exit
}

Write-Host "Found $($pyFiles.Count) .py files. Copying..." -ForegroundColor Cyan

foreach ($file in $pyFiles) {
    try {
        $newFile = "$($file.FullName).txt"  # Append .txt to original name
        Copy-Item -Path $file.FullName -Destination $newFile -Force
        Write-Host "Copied: $($file.FullName) -> $newFile" -ForegroundColor Green
    }
    catch {
        Write-Host "Error copying $($file.FullName): $_" -ForegroundColor Red
    }
}

Write-Host "`n✅ Copying complete." -ForegroundColor Cyan

# Ask user if they want to delete the new .py.txt files
$deleteChoice = Read-Host "Do you want to delete all newly created .py.txt files? (y/n)"
if ($deleteChoice -match '^[Yy]$') {
    try {
        Get-ChildItem -Path . -Recurse -Filter "*.py.txt" -File | Remove-Item -Force
        Write-Host "🗑 Deleted all .py.txt files." -ForegroundColor Red
    }
    catch {
        Write-Host "Error deleting files: $_" -ForegroundColor Red
    }
}

Pause
