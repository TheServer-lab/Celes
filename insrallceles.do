say "========================================="
say "     Server-Lab Program Installer"
say "========================================="
say ""
say "Server-Lab Open-Control License (SOCL) 1.0"
say "===================================="
say "Copyright (c) 2025 Sourasish Das"
say ""
say "Permission is hereby granted, free of charge..."
say "Use, copy, modify, merge, publish, distribute..."
say ""
say "THE SOFTWARE IS PROVIDED 'AS IS'"
say ""
say "Type YES to accept the license and continue."
say "Type NO to cancel."
say ""

ask agree "Do you agree to the license? "

if agree == "YES"
    say "License accepted."
else_if agree == "yes"
    say "License accepted."
else
    say "Installation cancelled."
    exit 1
end_if

say ""
say "Preparing install folder..."

make folder "C:\Server-lab"

say "Downloading package..."

download "https://github.com/TheServer-lab/Celes/archive/refs/heads/main.zip" to "C:\Server-lab\celes.zip"

say "Extracting package..."

execute_command "powershell" "-Command" "Expand-Archive -Path 'C:\Server-lab\celes.zip' -DestinationPath 'C:\Server-lab' -Force"

say "Cleaning up..."

delete "C:\Server-lab\celes.zip"

say ""
say "========================================="
say "Installation Complete!"
say "Installed to:"
say "C:\Server-lab"
say "========================================="

pause