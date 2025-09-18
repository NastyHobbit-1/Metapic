# Build and zip a Windows release
param(
[string]$Name = "MetaPicPick"
)


python -m pip install --upgrade pip
pip install -U pyinstaller
pyinstaller MetaPicPick.spec


$dist = Join-Path -Path (Resolve-Path .) -ChildPath "dist/$Name"
$zip = "$Name.zip"
if (Test-Path $zip) { Remove-Item $zip -Force }
Compress-Archive -Path "$dist/*" -DestinationPath $zip
Write-Host "Release packed: $zip"