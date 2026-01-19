@echo off
echo Initializing Git repository...
git init
git add .
git commit -m "Initial commit of Data Analysis Agent"
git branch -M main
git remote add origin https://github.com/rohanjangra07/data-analysis-agent.git
echo Pushing to GitHub...
git push -u origin main
echo Done!
pause
