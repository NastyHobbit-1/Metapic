@echo off
echo.
echo ====================================
echo  PUSHING MetaPicPick to GitHub
echo ====================================
echo.

echo Adding any new files...
git add .

echo.
echo Checking if we need to commit new files...
git status --porcelain
if not "%errorlevel%"=="0" (
    echo Committing new files...
    git commit -m "Add GitHub setup instructions"
)

echo.
echo Pushing to GitHub...
git push -u origin main

if "%errorlevel%"=="0" (
    echo.
    echo ✅ SUCCESS! Repository uploaded to GitHub!
    echo.
    echo Visit: https://github.com/NastyHobbit-1/MetaPicPick-Enhanced
    echo.
) else (
    echo.
    echo ❌ Push failed. Make sure:
    echo 1. You created the repository on GitHub.com first
    echo 2. Repository name is exactly: MetaPicPick-Enhanced
    echo 3. You're signed in to GitHub
    echo.
)

pause
