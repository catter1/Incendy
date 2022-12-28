#!/bin/bash

# $1 = https://github.com/Stardust-Labs-MC/{project}.git
# $2 = Datapack Version

# Python
# 1. Create directory, put datapack `.`
# Bash
# 2. Move datapack out
# 3. `git clone $1`
# 4. Remove all files/dirs except `.git`
# 5. Move datapack in and extract to `.`
# 6. Create `.gitignore`
# 7. `git add .`
# 8. `git commit -m $2`
# 9. `git push`

#####################################################

# 1. INIT from Python
repo_dir="$PWD/temp_repo"
zip_files=$(find $repo_dir -name "*.zip")

for file in $zip_files; do
    zip_name=$(basename "$file")
done

# 2. Move datapack out
mv "$repo_dir/$zip_name" "$repo_dir/../resources/."

# 3. `git clone $1`
git clone $1 $repo_dir

# 4. Remove all files/dirs except `.git`
dead_stuff=$(find $repo_dir -maxdepth 1 -not -path "*/.git*" -not -wholename "$repo_dir")
rm -rf $dead_stuff

# 5. Move datapack in and extract to `.`
mv "$repo_dir/../resources/$zip_name" "$repo_dir/."
unzip "$repo_dir/$zip_name" -d "$repo_dir/."

# 6. Create `.gitignore`
touch "$repo_dir/.gitignore"

echo ".gitignore" >> "$repo_dir/.gitignore"
echo $zip_name >> "$repo_dir/.gitignore"
echo "__MACOSX" >> "$repo_dir/.gitignore"

# 7. `git add .`
cd $repo_dir
git add .

# 8. `git commit -m $2`
git commit -m "Updated to $2"

# 9. `git push`
git push

cd -