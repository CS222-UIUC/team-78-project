# Git Instructions

| Command       | Notes    |
|:---------------|:--------------:|
| git branch   | check what branch you are on, make sure you are on the right one before working!   | 
| git checkout yourBranchName   | switch branches if needed   | 
| git pull origin main   | gets the latest changes from main branch of origin (remote repo) and merges changes into your curr branch   | 

###### when you are working on your own branch it is good to pull any updated changes from main as in the future we will have tests in GitHub Actions to ensure main has the best working version

### Pushing Code
| Command       | Note      |
|:---------------|:--------------:|
| git status   |  see all the files you changes so you can determine what to push  |
| git add .   | adds all files you changed, if you want to stash changes and only want to push a few manually do git add nameOfFile for all   |
| git commit -m "your commit message here"   |  have a short but descriptive commit message to track your progress  |
| git push origin branchYouWantToPushTo   | ex: git push origin main pushes code to main   |


<!-- Command + Shift + V in VSCode for Preview -->