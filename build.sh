if command -v pnpm >/dev/null 2>&1; then
  cd client
  pnpm install
  pnpm run build
  cd ..
else
  echo "Warning: pnpm is not installed. You should compile the client manually."
fi

if [ -d "./release" ]; then
  echo "Removing old release directory"
  rm -r "./release"
fi
mkdir -p "./release"
mkdir -p "./release/data"
mkdir -p "./release/data/audio"
mkdir -p "./release/data/models"

cp main.py "./release"
cp ./requirements.txt "./release"
cp ./README.md "./release"
cp .gitignore "./release"
cp LICENSE "./release"
cp -r ./kernel ./release
cp -r ./static ./release
cp -r ./data/config.yml ./release/data
cp -r ./data/sentiment ./release/data
cp ./data/models/facial.pth ./release/data/models/
cp -r ./client/dist ./release/client
cp ./config.py "./release"
cp ./setup.sh "./release"
cp ./setup.ps1 "./release"

zip -r release.zip ./release

mv release.zip ./release

echo "Build complete. You can now run the server by executing 'uvicorn main:app --reload' in the release directory."
