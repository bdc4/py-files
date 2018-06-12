cd ..
pyinstaller -F -w --distpath builds/mac main.py
cp -r data builds/mac/data
rm -rf build
rm -rf main.spec